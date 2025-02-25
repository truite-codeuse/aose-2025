from __future__ import annotations
from typing import TypedDict, Literal, Callable, cast


import torch
import nltk
import tensorflow_hub as hub
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer

from .project_data import ProjectID



MODE_SBERT     = True
GUSE_LITE      = True
EXPAND_PROMPTS = False

DEFAULT_ALPHA   = 1.5
DEFAULT_EPSILON = 1e-6

SBERT_MODEL_STR = "all-MiniLM-L6-v2"  ## https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
GUSE_MODEL_STR  = (
	"https://tfhub.dev/google/universal-sentence-encoder-lite/2"
	if GUSE_LITE else
	"https://tfhub.dev/google/universal-sentence-encoder/4"
)

PayloadFor_AdAgent = TypedDict(
	"PayloadFor_AdAgent",
	{
		"user_prompt"  : str,
		"similarities" : dict[ProjectID, float],
	}
)

PayloadFor_ScenarioMatchingAgent = TypedDict(
	"PayloadFor_ScenarioMatchingAgent",
	{
		"project_id": ProjectID,
		"user_input": list[str],  # input sentences, but split into a list
	}
)



#######################################################################
#
# Similarity scoring utils
#
#######################################################################

MeanMode_Literal        = Literal[
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
SimilarityMode_Literal  = Literal[
	"distance",
	"cosine",
]

DEFAULT_MODE_MEAN = "harmonic"
DEFAULT_MODE_WN   = "path"
DEFAULT_MODE_SIM  = "cosine"


def score_mean(
	similarity_matrix : torch.Tensor,
	sim_mode          : SimilarityMode_Literal,
) -> float:
	"""
	Arithmetic mean to smooth out scores regardless of the amount of infrequent words
	in the input sentence.

	Pros: Smooth and comparable across prompts.
	Cons: Too forgiving — a lot of weak matches can look better than a few very strong ones.
	"""
	get_extreme = torch.min if sim_mode == "distance" else torch.max
	ext_scores  = get_extreme(similarity_matrix, dim=1).values
	result      = torch.mean(ext_scores).item()
	return result

def score_softmax_mean(
	similarity_matrix : torch.Tensor,
	sim_mode          : SimilarityMode_Literal,
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
	weights     = softmax(ext_scores, alpha)
	result      = torch.sum(weights * ext_scores).item()
	return result

def score_harmonic_mean(
	similarity_matrix : torch.Tensor,
	sim_mode          : SimilarityMode_Literal,
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
	user_words  : list[str],
	match_words : list[str],
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
			similarity_matrix[i, j] = distance_fn(
				wordnet.synsets(user_word  )[0],
				wordnet.synsets(match_word )[0],
			)
	return similarity_matrix


def compute_cosine_similarity_matrix_by_sentences(
	user_prompt : list[str],
	match_strs  : list[str],
	model       : SentenceTransformer | hub.KerasLayer,
) -> torch.Tensor:
	"""
	Compute cosine similarity between a prompt and a list of sentences.
	Note that the user_prompt is a list so that this can work with word lists as well.
	"""
	user_sentences   = sum([nltk.sent_tokenize(user_str)  for user_str  in user_prompt ], cast(list[str], []))
	match_sentences  = sum([nltk.sent_tokenize(match_str) for match_str in match_strs  ], cast(list[str], []))
	user_embeddings  = model.encode(user_sentences,  convert_to_tensor = True)
	match_embeddings = model.encode(match_sentences, convert_to_tensor = True)
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
# User input vs baseline comparison compute functions
#
#######################################################################

def compute_distance_scores_by_lexicon(
	user_prompt : list[str],
	documents   : dict[ProjectID, list[str]],
	distance    : WNDistanceMode_Literal,
	mean_mode   : MeanMode_Literal,
	alpha       : float                   = DEFAULT_ALPHA,
	epsilon     : float                   = DEFAULT_EPSILON,
) -> dict[ProjectID, float]:
	"""
	Compute similarity scores based on WordNet distance.
	Optimal results are the minimal ones, which are given at the beginning of the results list.
	"""
	mean_fn : Callable[[torch.Tensor], float] = {
		"arithmetic" : lambda x: score_mean          (x, "distance"),
		"softmax"    : lambda x: score_softmax_mean  (x, "distance", alpha),
		"harmonic"   : lambda x: score_harmonic_mean (x, "distance", epsilon),
	}[mean_mode]
	user_words = sum([nltk.word_tokenize(sentence) for sentence in user_prompt], cast(list[str], []))
	user_words = list(set(user_words))
	doc_scores = {}
	for doc_id, doc_sentences in documents.items():
		match_words        = sum([nltk.word_tokenize(sentence) for sentence in doc_sentences], cast(list[str], []))
		match_words        = list(set(match_words))
		similarity_matrix  = compute_distance_similarity_matrix_by_lexicon(user_words, match_words, distance)
		score              = mean_fn(similarity_matrix)
		doc_scores[doc_id] = score
	doc_scores_sorted = sorted(doc_scores.items(), key=lambda x: x[1])
	result = {doc_id: score for doc_id, score in doc_scores_sorted}
	return result

def compute_cosine_scores_by_lexicon(
	user_prompt : list[str],
	documents   : dict[ProjectID, list[str]],
	model       : SentenceTransformer | hub.KerasLayer,
	mean_mode   : MeanMode_Literal,
	alpha       : float                   = DEFAULT_ALPHA,
	epsilon     : float                   = DEFAULT_EPSILON,
) -> dict[ProjectID, float]:
	"""
	Compute similarity scores based on cosine similarity.
	Optimal results are the maximal ones, which are given at the beginning of the results list.
	"""
	mean_fn : Callable[[torch.Tensor], float] = {
		"arithmetic" : lambda x: score_mean          (x, "cosine"),
		"softmax"    : lambda x: score_softmax_mean  (x, "cosine", alpha),
		"harmonic"   : lambda x: score_harmonic_mean (x, "cosine", epsilon),
	}[mean_mode]
	user_words = sum([nltk.word_tokenize(sentence) for sentence in user_prompt], cast(list[str], []))
	user_words = list(set(user_words))
	doc_scores = {}
	for doc_id, doc_sentences in documents.items():
		match_words        = sum([nltk.word_tokenize(sentence) for sentence in doc_sentences], cast(list[str], []))
		match_words        = list(set(match_words))
		similarity_matrix  = compute_cosine_similarity_matrix_by_sentences(user_words, match_words, model)
		score              = mean_fn(similarity_matrix)
		doc_scores[doc_id] = score
	doc_scores_sorted = sorted(doc_scores.items(), key=lambda x: x[1])
	result = {doc_id: score for doc_id, score in doc_scores_sorted}
	return result

def compute_cosine_scores_by_sentences(
	user_prompt : list[str],
	documents   : dict[ProjectID, list[str]],
	model       : SentenceTransformer | hub.KerasLayer,
	mean_mode   : MeanMode_Literal,
	alpha       : float                   = DEFAULT_ALPHA,
	epsilon     : float                   = DEFAULT_EPSILON,
) -> dict[ProjectID, float]:
	"""
	Compute similarity scores based on cosine similarity.
	Optimal results are the maximal ones, which are given at the beginning of the results list.
	"""
	mean_fn : Callable[[torch.Tensor], float] = {
		"arithmetic" : lambda x: score_mean          (x, "cosine"),
		"softmax"    : lambda x: score_softmax_mean  (x, "cosine", alpha),
		"harmonic"   : lambda x: score_harmonic_mean (x, "cosine", epsilon),
	}[mean_mode]

	user_words = sum([nltk.word_tokenize(sentence) for sentence in user_prompt], cast(list[str], []))
	user_words = list(set(user_words))
	doc_scores = {}
	for doc_id, doc_sentences in documents.items():
		similarity_matrix  = compute_cosine_similarity_matrix_by_sentences(user_words, doc_sentences, model)
		score              = mean_fn(similarity_matrix)
		doc_scores[doc_id] = score
	doc_scores_sorted = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
	result = {doc_id: score for doc_id, score in doc_scores_sorted}
	return result



if __name__ == '__main__':
	nltk.download('wordnet')
	nltk.download('omw-1.4')  # Open Multilingual WordNet; necessary for newer versions of wordnet
	nltk.download('brown')	# Brown corpus; necessary for a TF-IDF baseline
	from nltk.corpus import wordnet
	from nltk.corpus import brown
	sbert_model = SentenceTransformer(SBERT_MODEL_STR)
	guse_model  = hub.load(GUSE_MODEL_STR)

	documents = {
		'doc1': ['The miner extracted the ore.', 'The scout analyzed the cave.'],
		'doc2': ['A borer widened the tunnel.', 'The robot transported minerals.'],
		'doc3': ["I'd like a salad for lunch", "I'd like some dessert, too."],
		'doc4': ["I like tilling the earth.", "Planting seeds into the soil is nice too."],
	}
	prompt = 'Find and carry the minerals.'

	scores = compute_similarity_scores(documents, prompt)
	print(scores)

	vectorizer = get_tfidf_brown_vectorizer()
	relevant_words = get_rare_words(vectorizer, prompt)
	print(relevant_words)
