# Sentence matcher

## Author

Role R2; Tristan Duquesne

## Description

This folder contains the work for the sentence matcher microservice. The sentence matcher microservice is responsible for matching user-provided sentences with a list of predefined sentences (corresponding to scenarios and options of rAIson projects).

## Initial Research Summary

### Approaches

Sentence-matching in this context is a fuzzy process. The TLDR of our research is that there are basically three approaches we can take:
- **Embedding-based**: Use a model that can embed full sentences into a high-dimensional space and then compare the distance or angle between them. This is great for nuanced prompts and complex sentences, but can be overkill for simple word matching.  
- **Lexicon-based**: Use a lexical database to match words and synonyms. This is great for simple word matching and synonyms, but struggles with complex sentences and idioms.  
- **LLM-based**: Use a Large Language Model and prompt engineering to query the model's opinion on whether the input string (i.e., the user prompt) matches some base document (i.e., project data).  


### Tools

We identified some tools which, alone or combined, can help match sentences in an approximate but effective way:

- **SBERT**: SBERT (Sentence Bidirectional Encoder Representations from Transformers) is a trained model that embeds sentence vectors into a high-dimensional space. SBERT can be obtained by doing `python3 -m pip install sentence-transformers`.
  - Pros:
    - Captures contextual meaning, not just word overlap.
    - Great for nuanced prompts: "Looking to repair my computer" could match "Buying spare electronic parts".
    - Fast once embeddings are computed.
  - Cons:
    - Needs a pretrained model (like SBERT) — might be overkill if you just want simple word matching.
    - Can struggle with very short prompts where context is limited.

- **Universal Sentence Encoder (USE)**: Similar to SBERT, a powerful model also used for sentence embedding. It has a large and a lite version. Info about this model can be found here https://www.kaggle.com/models/google/universal-sentence-encoder/tensorFlow2 . We did not manage to get it to work though.

- **WordNet**: WordNet is an English lexical database developed by Princeton university. It can match words to their synonyms and help define distance between lexical fields. It can be found as part of the NLTK library. You can install it by doing `python3 -m pip install nltk` and then runnning `nltk.download('wordnet')` and `nltk.download('omw-1.4')` within a Python script.
  - Pros:
    - Excellent for handling synonyms and basic concept relationships.
    - Doesn't need massive neural models (purely rule-based), so very cheap.
  - Cons:
    - Doesn't capture nuanced meanings or complex sentences.
    - Struggles with phrases and idioms ("My computer seems to have kick the bucket" won't link to "My computer is broken").

- **TF-IDF**: TF-IDF (Term Frequency-Inverse Document Frequency) is a standard NLP algorithms. It scores words based on how often they appear in a sentence versus the whole document set. Rare words weigh more, so "electronic" counts more than "buying". While not specifically adapted to our problem on its own, it could help isolate the most relevant words and improve matching speed and/or reduce errors due to noise in casual text. TF-IDF can be found as a part of the scikit-learn library. You can install it by doing `python3 -m pip install scikit-learn`.
  - Pros:
    - Simple and interpretable (shows how important a word is to a document).
    - Very fast, especially for larger corpora.
  - Cons:
    - Ignores word order ("My computer needs a repair." and "My repair needs a computer." are the same to TF-IDF).
    - No sense of synonymy of lexical closeness ("treasure" and "gold" aren't linked).
    - Will need some sort of default text corpus to baseline against (e.g. the NLTK Brown corpus for English).

- **Distance Matching**: by this, we mean raw string distance algorithms (Levenshtein distance, etc.). Again, while not directly useful to our problem, if we provide the user with the list of scenarios for the rAIson project, and the user has to select some scenarios, this can provide a pretty accurate and cheap way to ensure matching while also allowing for spelling mistakes, etc.
  - Pros:
    - Good for matching noisy inputs or typos.
    - Lightweight, no model training needed.
  - Cons:
    - Doesn't capture *any* meaning, only surface-level text.

- **Word2Vec**: Word2Vec is a model that embeds words into a high-dimensional space. It can be used to compare words and find synonyms. It can be found as part of the gensim library. You can install it by doing `python3 -m pip install gensim`.
  - Pros:
    - Great for finding synonyms and related words.
    - Can be used to find word analogies
  - Cons:
    - Only works at the lexicon level.

- **GloVe**: GloVe is another word embedding model, similar to Word2Vec. Unlike Word2Vec, it is trained on word co-occurrences so encodes a minimal amount of context. It can be found as part of the gensim library. You can install it by doing `python3 -m pip install gensim`.
  - Pros:
	- Great for finding synonyms and related words.
	- Can be used to find word analogies.
  - Cons:
	- Only works at the lexicon level.


- **LLMs**: Large Language Models are models like GPT-4o, LLaMa 3, etc. They can be used for sentence matching by providing a base document and a prompt, and then querying the model for its opinion on whether the prompt matches the document. This is a very powerful tool, but it can be expensive to use and requires a lot of data to train.
  - Pros:
	- Can be very powerful and flexible.
	- Can often handle complex sentences and nuanced meanings.
  - Cons:
	- Expensive and slow to train and run.
	- Generally unexplainable, so hard to fix if it doesn't have desirable results.
	- Needs data to fine-tune.
	- Getting the right outputs needs prompt engineering, data engineering, and solid benchmarking.





Dov2Vec
InferSent

## Implementation

We thus tried to use SBERT and WordNet in particular.
