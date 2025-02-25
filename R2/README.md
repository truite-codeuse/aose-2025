## Sentence matcher

### Author

Role R2; Tristan Duquesne

### General description

This section contains the work for the sentence matcher microservice. The sentence matcher microservice is responsible for matching user-provided sentences with a list of sentences. These sentences can either be provided via an HTTP POST message, or if ignored, are automatically set to correspond to descriptions, scenarios and options of the students' rAIson projects.



### Initial Research Summary

#### Approaches

Sentence-matching in this context is a fuzzy process. The TLDR of our research is that there are basically three approaches we can take:
- **Embedding-based**: Use a model that can embed full sentences into a high-dimensional space and then compare the distance or angle between them. This is great for nuanced prompts and complex sentences, but can be overkill for simple word matching.  
- **Lexicon-based**: Use a lexical database to match words and synonyms. This is great for simple word matching and synonyms, but struggles with complex sentences and idioms.  
- **LLM-based**: Use a Large Language Model and prompt engineering to query the model's opinion on whether the input string (i.e., the user prompt) matches some base document (i.e., project data).  


#### Tools

We identified some tools which, alone or combined, can help match sentences in an approximate but effective way:

##### SBERT

SBERT (Sentence Bidirectional Encoder Representations from Transformers) is a trained model that embeds sentence vectors into a high-dimensional space. SBERT can be obtained by doing `python3 -m pip install sentence-transformers`.
- Pros:  
  - Captures contextual meaning, not just word overlap.  
  - Great for nuanced prompts: "Looking to repair my computer" could match "Buying spare electronic parts".  
  - Fast once embeddings are computed.  
- Cons:  
  - Needs a pretrained model (like SBERT) — might be overkill if you just want simple word matching.  
  - Can struggle with very short prompts where context is limited.  

##### Universal Sentence Encoder (USE)

Similar to SBERT, Google's USE is a powerful model also used for sentence embedding. It has a large and a lite version. Info about this model can be found here https://www.kaggle.com/models/google/universal-sentence-encoder/tensorFlow2 . We did not manage to get it to work though.

##### WordNet

WordNet is an English lexical database developed by Princeton university. It can match words to their synonyms and help define distance between lexical fields. It can be found as part of the NLTK library. You can install it by doing `python3 -m pip install nltk` and then runnning `nltk.download('wordnet')` and `nltk.download('omw-1.4')` within a Python script.
- Pros:  
  - Excellent for handling synonyms and basic concept relationships.  
  - Doesn't need massive neural models (purely rule-based), so very cheap.  
- Cons:  
  - Doesn't capture nuanced meanings or complex sentences.  
  - Struggles with phrases and idioms ("My computer seems to have kick the bucket" won't link to "My computer is broken").  

##### TF-IDF

TF-IDF (Term Frequency-Inverse Document Frequency) is a standard NLP algorithms. It scores words based on how often they appear in a sentence versus the whole document set. Rare words weigh more, so "electronic" counts more than "buying". While not specifically adapted to our problem on its own, it could help isolate the most relevant words and improve matching speed and/or reduce errors due to noise in casual text. TF-IDF can be found as a part of the scikit-learn library. You can install it by doing `python3 -m pip install scikit-learn`.

- Pros:  
  - Simple and interpretable (shows how important a word is to a document).  
  - Very fast, especially for larger corpora.  
- Cons:  
  - Ignores word order ("My computer needs a repair." and "My repair needs a computer." are the same to TF-IDF).  
  - No sense of synonymy of lexical closeness ("treasure" and "gold" aren't linked).  
  - Will need some sort of default text corpus to baseline against (e.g. the NLTK Brown corpus for English).  

##### Distance Matching

By this, we mean raw string distance algorithms (Levenshtein distance, etc.). Again, while not directly useful to our problem, if we provide the user with the list of scenarios for the rAIson project, and the user has to select some scenarios, this can provide a pretty accurate and cheap way to ensure matching while also allowing for spelling mistakes, etc.
- Pros:  
  - Good for matching noisy inputs or typos.  
  - Lightweight, no model training needed.  
- Cons:  
  - Doesn't capture *any* meaning, only surface-level text.  

##### Word2Vec

Word2Vec is a model that embeds words into a high-dimensional space. It can be used to compare words and find synonyms. It can be found as part of the gensim library. You can install it by doing `python3 -m pip install gensim`.
- Pros:  
  - Great for finding synonyms and related words.  
  - Can be used to find word analogies  
- Cons:  
  - Only works at the lexicon level.  

##### GloVe

GloVe is another word embedding model, similar to Word2Vec. Unlike Word2Vec, it is trained on word co-occurrences so encodes a minimal amount of context. It can be found as part of the gensim library. You can install it by doing `python3 -m pip install gensim`.
- Pros:  
  - Great for finding synonyms and related words.  
  - Can be used to find word analogies.  
- Cons:  
  - Only works at the lexicon level.  

##### LLMs

Large Language Models are models like GPT-4o, LLaMa 3, etc. They can be used for sentence matching by providing a base document and a prompt, and then querying the model for its opinion on whether the prompt matches the document. This is a very powerful tool, but it can be expensive to use and requires a lot of data to train.
- Pros:  
  - Can be very powerful and flexible.  
  - Can often handle complex sentences and nuanced meanings.  
- Cons:  
  - Expensive and slow to train and run.  
  - Generally unexplainable, so hard to fix if it doesn't have desirable results.  
  - Needs data to fine-tune.  
  - Getting the right outputs needs prompt engineering, data engineering, and solid benchmarking.  

<!--
Dov2Vec
InferSent
-->



### Implementation

Because we wanted to aim for speed, cheapness, measurability and consistency, we thus concentrated our efforts on non-LLM approaches. We provided studied 2 lexicon-based approaches (synset distances and word embeddings) and 1 sentence-based approach (SBERT). We also tried to use Google USE, but failed to get it working.

#### Commonalities: similarity matrices, extrema and averaging

The core of our approach was to build all comparisons between a set of input strings, and a set of baseline strings. This can be understood as a weighted bipartite graph, and represented as a similarity matrix, where rows correspond to baseline sentences, and columns correspond to input sentences. Each cell in the matrix is the similarity score between the corresponding baseline and input sentence. In one case (wordnet) this score is a distance, in the other cases (word embeddings, sentence embeddings) this score is a cosine similarity.

We then computed the extrema of these matrices over the columns. For distances, a minimum; for similarities, a maximum. The idea here is that if a string is similar to *any* of the strings in the baseline, it should be considered a match. This gives us a good way to notice matches and remove noise.

Finally, since the amount of words in the input might not be the same everywhere, combining the scores for the various strings in the input needed some clever resolution, one that would not be sensitive to changes in prompt length. We thus averaged the scores in various ways to get a final score for each input sentence. The three averages we provided are arithmetic, softmax and harmonic.

The arithmetic mean is the most basic, the softmax mean gives more weight to higher scores, and the harmonic mean is a way to create distance between matches which are consistently strong and penalize those that are only partly good matches.

#### Specific to lexicon-based approaches: TF-IDF

We tried to use TF-IDF to filter out noise and only keep rare words (those potentially relevant to thematic matchings only), limit the amount of tokens to cross for the 2 lexicon-based matchers, and improve the overall score. Since the lexicon-based matchers proved to be less performant than the sentence-based matcher, this part of the code is mostly unused. It is still present in the sentence matcher file. This portion of the code could still be interesting to use and study, especially if someone were to try to improve the word embeddings approach, which looked like it could be useful if more work was done on it.

#### Synset distances: WordNet

The idea of the approach here was to use WordNet, a knowledge graph of English words, to find synonyms and related words. We used the NLTK library to access WordNet and compute the distance between synsets. The distance was computed using the shortest path between two synsets in the WordNet graph. The idea was to compare the distance between the synsets of the words in the input and the baseline, and then average these distances in the way described above.

We fudged around with the various choices of distance metrics available through wordnet, but never got to a point where we found the order of distances to match the order of relevance that we thought was semantically true. We thus abandoned this approach, but left the code in place for future reference. It is also testable via the API.


#### Word embeddings: Word2Vec, GloVe

This approach fared a bit better. We used the `gensim` library to load Word2Vec and GloVe models to provide our word embeddings for our TF-IDF filtered words. We then computed the cosine similarity between the vectors of the words in the input and the baseline. We then averaged these similarities in the way described above.

The results were far more semantically consistent. However, there was little difference in score between results, whether they were really relevant, somewhat relevant, or not relevant. So this was too imperfect for a threshold-based approach.


#### Sentence embeddings: SBERT

(Note, we also tried to use Google USE, but failed to get it working.)

This approach was the most successful. We used the `sentence-transformers` library to load the SBERT model and compute the sentence embeddings for the input and baseline sentences. We then computed the cosine similarity between these embeddings, and averaged them in the way described above.

The results were semantically consistent, and the scores were more spread out. This was the most promising approach, and the one we chose to keep as the default for the final microservice. The code is still present for the other approaches, and can be tested via the API. However, there needs to be further testing to figure out thresholds appropriately.



### Results and limitations

We found cosine similarity with SBERT to work the best, because it was the most semantically consistent and had the most spread out scores.

Admittedly, our testing is quite minimal. We need a lot more fine-grained testing to establish which choice of model, which similarity metric, and which averaging function are best. We are not confident as to which is the best approach, in general, and for this use case. However, our approach is good enough for a prototype, so we stopped there. The kind of benchmarking required to improve upon this would need a dataset of prompts and expected matches, and a way to measure the performance of the various approaches. Because this is a complex, time-consuming task, we considered it to be out of scope.

Also, we did not try the LLM approach, but once such a dataset of comparison baselines is available, it would be very interesting to compare it with the one given. Although LLMs are not explainable, they are very powerful: with some explainable alternate model to compare against, this could mitigate some of the trustworthiness issues of LLM outputs (hallucinations). Potentially, we could also fine-tune a SotA model to provide a more accurate and nuanced matching.



### Running

When running this microservice for the first time, it will download the appropriate models from the Internet: this will take a while (a few minutes). 

When running this microservice again, it will load the models from the local cache, which is much faster, but still takes a while (20-30 seconds or so).

The version of Python used for development is 3.10, but some other (recent-ish) versions of Python 3 should also work fine.


#### Installation

At the root of the R2 directory, you should add a file called `.env` containing a rAIson API key. The syntax for it is as follows (where `...` is to be replaced by the key):

```py
RAISON_API_KEY = "..."
```

You can install the necessary dependencies by running:

```sh
python3 -m pip install -r requirements.txt
```

You can also set up a `venv` for this purpose if necessary.

If you don't want to use a `venv`, but might have version conflicts with other python packages locally, you can run:

```sh
python3 -m pip install -U -r requirements.txt
```



#### Testing

If you want to test the sentence matcher on its own, you can do so by running the following command:

```sh
python3 -m src.sentence_matcher
```

This will call the `if __name__ == "__main__":` block in `src/sentence_matcher.py` and run the sentence matcher on some predefined sentences. This can be edited for quick debugging.

#### Microservice / agent

Since there are some data and models to be loaded before the sentence matcher microservice is online, you cannot launch it with `uvicorn src.role2_service:app --port=8002`, you should instead do`python3.10 -m src.role2_service`, which will read the `if __name__ == "__main__":` block in `src/role2_service.py` (where the data loaders are called), then launch the microservice. Calling uvicorn immediately ignores the data loading and will cause issues with the microservice.

You can then test its behavior with something like this:

```sh
curl -X POST 0.0.0.0:8002/match_for_scenario -H "Content-Type: application/json" -d "{\"user_input\": \"I'm wondering if I should ban someone from my discord server\", \"get_max\": true}"
```

### API

The sentence matcher microservice exposes 3 routes:

- `/match`: the general route which calls the sentence matcher general request handler. This route takes a somewhat complex set of arguments, and can thus let the sentence matcher serve for various purposes:  
  - `user_input : str` : required, the user input which we need to compare to a set of baseline documents.
  - `documents : DocumentDict`: optional, a dictionary of document IDs and document content (list of sentence). If not provided, this is automatically filled with a dictionary of the rAIson project's description, scenarios and options.  
  - `model : ModelQueryKey`: optional, the model/method to use for the matching. If not provided, this is automatically set to `"sbert"`.  
  - `mean_mode : MeanMode_Literal`: optional, one of `"arithmetic"`, `"softmax"`, or `"harmonic"`. This sets the average used to harmonize sets of word comparisons. If not provided, this is automatically set to `"harmonic"`.  
  - `dist_mode : WNDistanceMode_Literal`: optional, only applies to the `"wordnet"` model. If not provided, this is automatically set to `"path"`.  
  - `alpha : float`: optional, only applies to the `"softmax"` mean. If not provided, this is automatically set to `1.5`.  
  - `epsilon : float`: optional, only applies to the `"harmonic"` mean. If not provided, this is automatically set to `1e-6`.  
- `/match_for_ad`: a simplified call to help R7.  
- `/match_for_scenario`: a simplified call to help R5.  


### Code structure

The code for R2 is structured as follows:
- `project_data.py`: Contains utils to manipulate metadata and data of the rAIson projects. Some of this metadata is not provided by the rAIson API (project title and a description), so it is hardcoded in this file. The rest is obtained by querying the rAIson API (elements and options).  
- `sentence_matcher.py`: Contains the sentence matcher utility functions. This file is responsible for matching user-provided sentences with a list of predefined sentences (corresponding to scenarios and options of rAIson projects). It is structured in sections, as follows:  
  - Typing and constants: some semantic type aliasing and default values.  
  - Similarity scoring utils: various functions, types and constants to help define the degree of similarity between words and sentences. The functions in question help to study similarity (cosine), dissimilarity (distance), and to average scores over multiples inputs when crossing multiple input words or sentences with multiple baseline words or sentences.  
  - TF-IDF utils: functions to compute the TF-IDF score of a sentence, and filter words based on this analysis. I kept it here because it was important for the study of the different methods, but the chosen SBERT matcher does not use it.  
  - User input vs basline comparison functions: these are the three functions providing an output based on our approaches (one for WordNet, one for word-embedding cosine similarities, and the final, which acts as our default, the sentence-embedding cosine similarities).  
  - Model loaders: utils to load the SBERT model and the WordNet database. As mentioned, USE, while present, does not work.  
  - Request handler: the core function that handles the POST requests for the microservice, and acts as a sort of gateway for the various ways one can call the sentence matcher.  
  - Main: a small block for direct testing of the code in this file.
- `role2_service.py`: Contains the FastAPI microservice for the sentence matcher. This file is responsible for exposing the sentence matcher as a microservice, and is structured as follows:  
  - Typing and constants: some semantic typing and default values, using Pydantic, to help FastAPI handle the JSON data.  
  - Request handlers: the FastAPI routes for the sentence matcher microservice. There are 3: `match`, the general route which calls the sentence matcher general request handler; `match_for_ad` which is a simplified call to help R7; `match_for_scenario` which is a simplified call to help R5.  
  - Main: loading the requisite data models, and launching the FastAPI/uvicorn app.


### TODOs

- Add an LLM similarity matcher: a comparison function which does some prompt engineering and then calls R1 (and corresponding API route)  
- Fix Google USE  
