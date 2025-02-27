from __future__ import annotations
from typing_extensions import TypedDict, Literal, Callable, Union, cast
from math import inf


import torch
import nltk
from nltk.corpus import wordnet
from nltk.corpus import brown
import tensorflow_hub as hub
from gensim.models import KeyedVectors
import gensim.downloader as gensim_api
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer


from .project_data import ProjectID, ProjectsDict



#######################################################################
#
# Typing and constants
#
#######################################################################

EXPAND_PROMPTS = False

InputText       = list[str]
DocumentID      = str
DocumentContent = list[str]
DocumentDict    = dict[DocumentID, DocumentContent]
ScoresDict      = dict[ProjectID, float]

SentenceModel_Literal = Literal[
	"sbert",
#	"google-use-large",
#	"google-use-lite",
]
LexiconModel_Literal  = Literal[
	"wordnet",
	"word2vec",
	"glove",
]
SentenceModel       = Union[SentenceTransformer, hub.KerasLayer]
LexiconModel        = Union[KeyedVectors]
ModelsDict_Sentence = dict[SentenceModel_Literal, SentenceModel]
ModelsDict_Lexicon  = dict[LexiconModel_Literal,  LexiconModel]
ModelsDict_Both     = TypedDict(
	"ModelsDict_Both",
	{
		"sentence" : ModelsDict_Sentence,
		"lexicon"  : ModelsDict_Lexicon,
	}
)
ModelQueryKey = SentenceModel_Literal | LexiconModel_Literal

DEFAULT_MODEL_SENTENCE = cast(SentenceModel_Literal, "sbert")
DEFAULT_MODEL_LEXICON  = cast(LexiconModel_Literal,  "glove")
SBERT_MODEL_STR        = "all-MiniLM-L6-v2"  ## https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
GUSE_MODEL_STR_LITE    = "https://tfhub.dev/google/universal-sentence-encoder-lite/2"
GUSE_MODEL_STR_LARGE   = "https://tfhub.dev/google/universal-sentence-encoder/4"



#######################################################################
#
# Similarity scoring utils
#
#######################################################################

MeanMode_Literal = Literal[
	"arithmetic",
	"softmax",
	"harmonic",
]
WNDistanceMode_Literal = Literal[
	"path",
	"leacock-chodorow",
	"wu-palmer",
	"resnik",
	"jiang-conrath",
	"lin",
]
ScoreMode_Literal = Literal[
	"distance",
	"cosine",
]

DEFAULT_MODE_MEAN  = cast(MeanMode_Literal, "harmonic")
DEFAULT_MODE_WN    = cast(WNDistanceMode_Literal, "path")
DEFAULT_MODE_SCORE = cast(ScoreMode_Literal, "cosine")
DEFAULT_ALPHA      = 1.5
DEFAULT_EPSILON    = 1e-6

def score_mean(
	similarity_matrix : torch.Tensor,
	sim_mode          : ScoreMode_Literal,
) -> float:
	"""
	Arithmetic mean to smooth out scores regardless of the amount of infrequent words
	in the input sentence.

	Pros: Smooth and comparable across prompts.
	Cons: Too forgiving — a lot of weak matches can look better than a few very strong ones.
	"""
	get_extreme = torch.min if sim_mode == "distance" else torch.max
	ext_scores  = get_extreme(similarity_matrix, dim=1).values
	ext_scores  = ext_scores[torch.isfinite(ext_scores)]
	result      = torch.mean(ext_scores).item()
	return result

def score_softmax_mean(
	similarity_matrix : torch.Tensor,
	sim_mode          : ScoreMode_Literal,
	alpha             : float = DEFAULT_ALPHA,
) -> float:
	"""
	Softmax mean to smooth out scores regardless of the amount of infrequent words
	in the input sentence.

	Use small alpha for a smoother distribution, or large alpha to emphasize top scores.
	This works really well if you want to weigh top matches without discarding weaker ones.

	Pros: Highlights strong matches more, with a tunable alpha to control focus.
	Cons: Needs alpha tuning.
	"""
	def softmax(x: torch.Tensor, alpha : float) -> torch.Tensor:
		exp_x = torch.exp(alpha * x)
		return exp_x / torch.sum(exp_x)
	get_extreme = torch.min if sim_mode == "distance" else torch.max
	ext_scores  = get_extreme(similarity_matrix, dim=1).values
	ext_scores  = ext_scores[torch.isfinite(ext_scores)]
	weights     = softmax(ext_scores, alpha)
	result      = torch.sum(weights * ext_scores).item()
	return result

def score_harmonic_mean(
	similarity_matrix : torch.Tensor,
	sim_mode          : ScoreMode_Literal,
	epsilon           : float                  = DEFAULT_EPSILON,
) -> float:
	"""
	Harmonic mean to give a boost to documents with consistently strong matches.

	Pros: Gives a boost to documents with consistently strong matches — one high
			score alone won't dominate the final score.
	Cons: Can underestimate relevance if there’s only one excellent match.
	"""
	get_extreme = torch.min if sim_mode == "distance" else torch.max
	ext_scores  = get_extreme(similarity_matrix, dim=1).values
	result      = len(ext_scores) / torch.sum(1.0 / (ext_scores + epsilon))
	return result.item()

def compute_distance_similarity_matrix_by_lexicon(
	user_words  : InputText,
	match_words : DocumentContent,
	distance    : WNDistanceMode_Literal,
) -> torch.Tensor:
	"""
	Computes a similarity matrix based on WordNet distance between words.
	"""
	distance_fn = {
		"path"             : wordnet.path_similarity,
		"leacock-chodorow" : wordnet.lch_similarity,
		"wu-palmer"        : wordnet.wup_similarity,
		"resnik"           : wordnet.res_similarity,
		"jiang-conrath"    : wordnet.jcn_similarity,
		"lin"              : wordnet.lin_similarity,
	}[distance]
	similarity_matrix = torch.zeros(len(user_words), len(match_words))
	for i, user_word in enumerate(user_words):
		for j, match_word in enumerate(match_words):
			user_synsets  = wordnet.synsets(user_word)
			match_synsets = wordnet.synsets(match_word)
			if len(user_synsets) == 0 or len(match_synsets) == 0:
				print(f"{user_word=} {match_word=}")
				similarity_matrix[i, j] = inf
			else:
				# print("\033[1;31m", (i,j), "\033[0m")
				similarity_matrix[i, j] = distance_fn(
					user_synsets  [0],
					match_synsets [0],
				)
	print(similarity_matrix)
	return similarity_matrix


def compute_cosine_similarity_matrix(
	user_input  : InputText,
	match_strs  : DocumentContent,
	encoder     : Callable[[list[str]], torch.Tensor],
) -> torch.Tensor:
	"""
	Compute cosine similarity between a prompt and a list of sentences.
	Note that the user_input is a list so that this can work with word lists as well.
	"""
	user_sentences   = sum([nltk.sent_tokenize(user_str)  for user_str  in user_input  ], cast(list[str], []))
	match_sentences  = sum([nltk.sent_tokenize(match_str) for match_str in match_strs  ], cast(list[str], []))
	user_embeddings  = encoder(user_sentences)
	match_embeddings = encoder(match_sentences)
	cosine_scores    = util.pytorch_cos_sim(user_embeddings, match_embeddings)
	return cosine_scores



#######################################################################
#
# TF-IDF utils
#
#######################################################################

def get_synonyms(word : str) -> set[str]:
	"""
	Fetch synonyms for a word using WordNet.
	"""
	synonyms = set()
	for syn in wordnet.synsets(word):
		for lemma in syn.lemmas():
			synonyms.add(lemma.name().replace('_', ' '))
	return synonyms

def add_synonyms(words : list[str]) -> list[str]:
	"""
	Expand a sentence by adding synonyms for each word.
	"""
	expanded = []
	for word in words:
		expanded.append(word)
		expanded.extend(get_synonyms(word))
	result = list(set(expanded))
	return result

def get_tfidf_brown_vectorizer() -> TfidfVectorizer:
	"""
	Train a TF-IDF vectorizer on the Brown corpus.
	"""
	brown_sentences = [' '.join(sent) for sent in brown.sents()]
	vectorizer = TfidfVectorizer(smooth_idf=True)
	vectorizer.fit(brown_sentences)
	return vectorizer

def apply_tfidf_vectorizer(
	vectorizer : TfidfVectorizer,
	sentence   : str,
	threshold  : float | None = None,
) -> dict[str, float]:
	"""
	Apply a TF-IDF vectorizer to a sentence.
	"""
	tfidf_scores  = vectorizer.transform([sentence])
	feature_names = vectorizer.get_feature_names_out()
	word_scores   = tfidf_scores.toarray().flatten()
	result = {
		k: v
		for k,v in zip(feature_names, word_scores)
		if threshold is not None and v > threshold
	}
	return result

def get_rare_words(
	vectorizer : TfidfVectorizer,
	sentence   : str,
	threshold  : float = 0.5,
) -> list[str]:
	"""
	Extract words from a sentence that have a high TF-IDF score in regular English
	as based on the Brown dataset.
	"""
	sentence_scores = apply_tfidf_vectorizer(vectorizer, sentence, threshold)
	relevant_words  = list(sentence_scores.keys())
	return relevant_words



#######################################################################
#
# User input vs baseline comparison functions
#
#######################################################################

def compute_distance_scores_by_lexicon(
	user_input  : InputText,
	documents   : DocumentDict,
	distance    : WNDistanceMode_Literal,
	mean_mode   : MeanMode_Literal,
	alpha       : float                     = DEFAULT_ALPHA,
	epsilon     : float                     = DEFAULT_EPSILON,
) -> ScoresDict:
	"""
	Compute similarity scores based on WordNet distance.
	Optimal results are the minimal ones, which are given at the beginning of the results list.
	"""
	mean_fn : Callable[[torch.Tensor], float] = {
		"arithmetic" : lambda x: score_mean          (x, "distance"),
		"softmax"    : lambda x: score_softmax_mean  (x, "distance", alpha),
		"harmonic"   : lambda x: score_harmonic_mean (x, "distance", epsilon),
	}[mean_mode]
	user_words = sum([nltk.word_tokenize(sentence.lower()) for sentence in user_input], cast(list[str], []))
	user_words = [w for w in set(user_words) if wordnet.synsets(w) != []]
	doc_scores = {}
	for doc_id, doc_sentences in documents.items():
		match_words        = sum([nltk.word_tokenize(sentence.lower()) for sentence in doc_sentences], cast(list[str], []))
		match_words        = [w for w in set(match_words) if wordnet.synsets(w) != []]
		similarity_matrix  = compute_distance_similarity_matrix_by_lexicon(user_words, match_words, distance)
		score              = mean_fn(similarity_matrix)
		doc_scores[doc_id] = score
	doc_scores_sorted = sorted(doc_scores.items(), key=lambda x: x[1])
	result = {doc_id: score for doc_id, score in doc_scores_sorted}
	return result

def compute_cosine_scores_by_lexicon(
	user_input  : InputText,
	documents   : DocumentDict,
	model       : LexiconModel,
	mean_mode   : MeanMode_Literal,
	alpha       : float                      = DEFAULT_ALPHA,
	epsilon     : float                      = DEFAULT_EPSILON,
) -> ScoresDict:
	"""
	Compute similarity scores based on cosine similarity.
	Optimal results are the maximal ones, which are given at the beginning of the results list.
	"""
	mean_fn : Callable[[torch.Tensor], float] = {
		"arithmetic" : lambda x: score_mean          (x, "cosine"),
		"softmax"    : lambda x: score_softmax_mean  (x, "cosine", alpha),
		"harmonic"   : lambda x: score_harmonic_mean (x, "cosine", epsilon),
	}[mean_mode]
	encoder    = lambda x: torch.tensor([model[word] for word in x if word in model])
	user_words = sum([nltk.word_tokenize(sentence.lower()) for sentence in user_input], cast(list[str], []))
	user_words = list(set(user_words))
	doc_scores = {}
	for doc_id, doc_sentences in documents.items():
		match_words        = sum([nltk.word_tokenize(sentence.lower()) for sentence in doc_sentences], cast(list[str], []))
		match_words        = list(set(match_words))
		similarity_matrix  = compute_cosine_similarity_matrix(user_words, match_words, encoder)
		score              = mean_fn(similarity_matrix)
		doc_scores[doc_id] = score
	doc_scores_sorted = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
	result = {doc_id: score for doc_id, score in doc_scores_sorted}
	return result

def compute_cosine_scores_by_sentences(
	user_input  : InputText,
	documents   : DocumentDict,
	model       : SentenceModel,
	mean_mode   : MeanMode_Literal,
	alpha       : float                   = DEFAULT_ALPHA,
	epsilon     : float                   = DEFAULT_EPSILON,
) -> ScoresDict:
	"""
	Compute similarity scores based on cosine similarity.
	Optimal results are the maximal ones, which are given at the beginning of the results list.
	"""
	mean_fn : Callable[[torch.Tensor], float] = {
		"arithmetic" : lambda x: score_mean          (x, "cosine"),
		"softmax"    : lambda x: score_softmax_mean  (x, "cosine", alpha),
		"harmonic"   : lambda x: score_harmonic_mean (x, "cosine", epsilon),
	}[mean_mode]
	encoder    = lambda x: model.encode(x)
	user_words = sum([nltk.sent_tokenize(sentence) for sentence in user_input], cast(list[str], []))
	user_words = list(set(user_words))
	doc_scores = {}
	for doc_id, doc_sentences in documents.items():
		similarity_matrix  = compute_cosine_similarity_matrix(user_words, doc_sentences, encoder)
		score              = mean_fn(similarity_matrix)
		doc_scores[doc_id] = score
	doc_scores_sorted = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
	result = {doc_id: score for doc_id, score in doc_scores_sorted}
	return result



#######################################################################
#
# Model loaders
#
#######################################################################

def load_sentence_model(model_literal : SentenceModel_Literal) -> SentenceModel:
	result : SentenceModel
	if   model_literal == "sbert"            : result = SentenceTransformer(SBERT_MODEL_STR)
	# TODO fix
	# elif model_literal == "google-use-lite"  : result = hub.load(GUSE_MODEL_STR_LITE ).signatures['default']
	# elif model_literal == "google-use-large" : result = hub.load(GUSE_MODEL_STR_LARGE)
	else: raise ValueError(f"Invalid sentence model {model_literal}")
	return result

def load_lexicon_model(model_literal : LexiconModel_Literal) -> LexiconModel:
	addr_str = 'word2vec-google-news-300' if model_literal == "word2vec" else "glove-wiki-gigaword-100"
	if   model_literal == "word2vec" : result = gensim_api.load(addr_str)
	elif model_literal == "glove"    : result = gensim_api.load(addr_str)
	else: raise ValueError(f"Invalid lexicon model {model_literal}")
	assert isinstance(result, KeyedVectors)
	return result

def load_all_models() -> ModelsDict_Both:
	nltk.download('wordnet')
	nltk.download('omw-1.4')  # Open Multilingual WordNet; necessary for newer versions of wordnet
	nltk.download('brown')	  # Brown corpus; necessary for a TF-IDF baseline
	nltk.download('punkt')	  # Punkt tokenizer; necessary for sentence tokenization
	sentence_models : ModelsDict_Sentence = {
		"sbert"           : load_sentence_model("sbert"),
	#	"google-use-lite" : load_sentence_model("google-use-lite"),
	#	"google-use-large": load_sentence_model("google-use-large"),
	}
	lexicon_models : ModelsDict_Lexicon = {
		"word2vec": load_lexicon_model("word2vec"),
		"glove"   : load_lexicon_model("glove"),
	}
	result : ModelsDict_Both = {
		"sentence": sentence_models,
		"lexicon" : lexicon_models,
	}
	return result



#######################################################################
#
# Request handler
#
#######################################################################

def get_sentence_matching_scores(
	models      : ModelsDict_Both,
	documents   : DocumentDict,
	user_input  : InputText,
	model_key   : SentenceModel_Literal | LexiconModel_Literal | None = None,
	mean_mode   : MeanMode_Literal                             | None = None,
	dist_mode   : WNDistanceMode_Literal                       | None = None,
	alpha       : float                                        | None = None,
	epsilon     : float                                        | None = None,
) -> ScoresDict:
	"""
	Compute similarity scores based on the chosen model.
	"""
	safe_model_key = model_key if model_key is not None else DEFAULT_MODEL_SENTENCE
	safe_mean_mode = mean_mode if mean_mode is not None else DEFAULT_MODE_MEAN
	safe_dist_mode = dist_mode if dist_mode is not None else DEFAULT_MODE_WN
	safe_alpha     = alpha     if alpha     is not None else DEFAULT_ALPHA
	safe_epsilon   = epsilon   if epsilon   is not None else DEFAULT_EPSILON
	if   safe_model_key == "wordnet":
		scores = compute_distance_scores_by_lexicon(user_input , documents, safe_dist_mode, safe_mean_mode, safe_alpha, safe_epsilon)
	elif safe_model_key in models["lexicon"]:
		model = models["lexicon"][cast(LexiconModel_Literal, safe_model_key)]
		scores = compute_cosine_scores_by_lexicon(user_input , documents, model, safe_mean_mode, safe_alpha, safe_epsilon)
	elif safe_model_key in models["sentence"]:
		model = models["sentence"][cast(SentenceModel_Literal, safe_model_key)]
		scores = compute_cosine_scores_by_sentences(user_input , documents, model, safe_mean_mode, safe_alpha, safe_epsilon)
	else:
		raise ValueError(f"Invalid model key {safe_model_key}")
	return scores



#######################################################################
#
# Main for testing
#
#######################################################################

if __name__ == '__main__':
	nltk.download('wordnet')
	nltk.download('omw-1.4')  # Open Multilingual WordNet; necessary for newer versions of wordnet
	nltk.download('brown')	# Brown corpus; necessary for a TF-IDF baseline
	nltk.download('punkt')	# Punkt tokenizer; necessary for sentence tokenization
	model_sentence : SentenceModel = load_sentence_model (DEFAULT_MODEL_SENTENCE)
	model_lexicon  : LexiconModel  = load_lexicon_model  (DEFAULT_MODEL_LEXICON)

	documents = {
		'doc1': ['The miner extracted the ore.', 'The scout analyzed the cave.'],
		'doc2': ['A borer widened the tunnel.', 'The robot transported minerals.'],
		'doc3': ["I'd like a salad for lunch", "I'd like some dessert, too."],
		'doc4': ["I like tilling the earth.", "Planting seeds into the soil is nice too."],
	}
	prompt = 'Find and carry the minerals.'

	dist_scores = compute_distance_scores_by_lexicon ([prompt], documents, DEFAULT_MODE_WN, DEFAULT_MODE_MEAN)
	cosl_scores = compute_cosine_scores_by_lexicon   ([prompt], documents, model_lexicon,   DEFAULT_MODE_MEAN)
	coss_scores = compute_cosine_scores_by_sentences ([prompt], documents, model_sentence,  DEFAULT_MODE_MEAN)

	print("Distance scores:",          dist_scores)
	print("Cosine scores (lexicon):",  cosl_scores)  # Threshold seems to around 0.75
	print("Cosine scores (sentence):", coss_scores)  # Threshold seems to around 0.5

	vectorizer = get_tfidf_brown_vectorizer()
	relevant_words = get_rare_words(vectorizer, prompt)
	print(relevant_words)
