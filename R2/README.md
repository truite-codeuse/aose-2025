# Sentence matcher

## Description

This folder contains the work for the sentence matcher microservice. The sentence matcher microservice is responsible for matching user-provided sentences with a list of predefined sentences (corresponding to scenarios and options of rAIson projects).

## Initial Research Summary

Sentence-matching in this context is a fuzzy process. We identified 4 tools to help match sentences in an approximate but effective way:

- **SBERT**: SBERT (Sentence Bidirectional Encoder Representations from Transformers) is a trained model that embeds vectors into a high-dimensional space. SBERT can be obtained by doing `python3 -m pip install sentence-transformers`.
  - Pros:
    - Captures contextual meaning, not just word overlap.
    - Great for nuanced prompts: "Looking to repair my computer" could match "Buying spare electronic parts".
    - Fast once embeddings are computed.
  - Cons:
    - Needs a pretrained model (like SBERT) — might be overkill if you just want simple word matching.
    - Can struggle with very short prompts where context is limited.

- **WordNet**: WordNet is an English lexical database developed by Princeton university. It can match words to their synonyms and help define distance between lexical fields. It can be found as part of the NLTK library. You can install it by doing `python3 -m pip install nltk` and then runnning `nltk.download('wordnet')` within a Python script.
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

- **Distance Matching**: by this, we mean raw string distance algorithms (Levenshtein distance, etc.). Again, while not directly useful to our problem, if we provide the user with the list of scenarios for the rAIson project, and the user has to select some scenarios, this can provide a pretty accurate and cheap way to ensure matching while also allowing for spelling mistakes, etc.
  - Pros:
    - Good for matching noisy inputs or typos.
    - Lightweight, no model training needed.
  - Cons:
    - Doesn't capture *any* meaning, only surface-level text.


## Implementation

We thus tried to use SBERT and WordNet in particular.
