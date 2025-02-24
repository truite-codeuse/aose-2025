from __future__ import annotations

import torch
import nltk
from nltk.corpus import wordnet as wn
from sentence_transformers import SentenceTransformer, util

from .project_data import ProjectID




EXPAND_PROMPTS = False

def get_synonyms(word : str) -> set[str]:
	"""
	Fetch synonyms for a word using WordNet.
	"""
	synonyms = set()
	for syn in wn.synsets(word):
		for lemma in syn.lemmas():
			synonyms.add(lemma.name().replace('_', ' '))
	return synonyms

def expand_sentence(sentence : str) -> str:
	"""
	Expand a sentence by adding synonyms for each word.
	"""
	words = sentence.split()
	expanded = []
	for word in words:
		expanded.append(word)
		expanded.extend(get_synonyms(word))
	return ' '.join(set(expanded))

def compute_similarity_scores(
	documents   : dict[ProjectID, list[str]],
	user_prompt : str,
) -> dict[ProjectID, float]:
	"""
	Compute normalized similarity scores between prompt and project scenarios.
	"""
	prompt = expand_sentence(user_prompt) if EXPAND_PROMPTS else user_prompt
	prompt_embedding = model.encode(prompt, convert_to_tensor=True)

	scores = {}
	for doc_id, sentences in documents.items():
		sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
		cosine_scores       = util.pytorch_cos_sim(prompt_embedding, sentence_embeddings)
		max_score           = torch.max(cosine_scores).item()
		scores[doc_id]      = max_score

	max_overall_score = max(scores.values(), default=1.0)
	for doc_id in scores:
		scores[doc_id] /= max_overall_score

	return scores


if __name__ == '__main__':
	nltk.download('wordnet')
	nltk.download('omw-1.4')  # Open Multilingual WordNet; necessary for newer versions of wordnet
	model = SentenceTransformer('all-MiniLM-L6-v2') # https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

	documents = {
		'doc1': ['The miner extracted the ore.', 'The scout analyzed the cave.'],
		'doc2': ['A borer widened the tunnel.', 'The robot transported minerals.'],
	}
	prompt = 'Find and carry the minerals.'

	scores = compute_similarity_scores(documents, prompt)
	print(scores)
