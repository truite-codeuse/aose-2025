## R1 LLM Service 

### Author

Daniel Latorre

### General Description

This project provides a FastAPI-based API that leverages a Mistral-based large language model, specifically the Nous‑Hermes‑2‑Mistral‑7B‑DPO, for text generation. In addition to offering robust endpoints for generating text and managing sessions, this repository documents the state of the art in large language models and details the lineage, performance, and advantages of the selected model.

---

### Table of Contents

1. [Overview](#overview)
2. [State of the Art in Large Language Models](#state-of-the-art-in-large-language-models)  
   2.1. [Historical Context and Evolution](#historical-context-and-evolution)  
   2.2. [Diverse Architectures and Alignment Challenges](#diverse-architectures-and-alignment-challenges)  
   2.3. [Advances in Alignment without Reinforcement Learning](#advances-in-alignment-without-reinforcement-learning)  
   2.4. [Criteria for Selecting a Large Language Model](#criteria-for-selecting-a-large-language-model)
3. [Selected Model: Nous‑Hermes‑2‑Mistral‑7B‑DPO](#selected-model-nous‑hermes‑2‑mistral‑7b‑dpo)  
   3.1. [Model Lineage and Core Architecture](#model-lineage-and-core-architecture)  
   3.2. [Performance and Empirical Evaluation](#performance-and-empirical-evaluation)  
   3.3. [Practical Advantages](#practical-advantages)  
   3.4. [Rationale for Selection](#rationale-for-selection)
4. [Project Structure](#project-structure)
5. [Setup Instructions](#setup-instructions)
6. [API Endpoints](#api-endpoints)
7. [References](#references)

---

### Overview

The **R1 LLM Service** is built on FastAPI and provides endpoints for health checking, text generation, and session management. It integrates a state-of-the-art large language model that has been fine-tuned using Direct Preference Optimization (DPO) to ensure robust and aligned outputs. Conversation history is persisted in a PostgreSQL database, which is deployed via Docker Compose.

---

### State of the Art

#### Historical Context and Evolution

The modern era of large language models began with the introduction of the Transformer architecture by Vaswani et al. (2017)[^1]. This breakthrough enabled models to learn complex relationships in text through self-attention mechanisms. Early work with encoder-only models, exemplified by BERT (Devlin et al., 2019) [^2], showcased the potential of bidirectional contextual understanding for a variety of language tasks. Shortly thereafter, the field witnessed a shift toward decoder-only models like GPT‑2 and GPT‑3 (Brown et al., 2020)[^3], which, through unsupervised generative training, demonstrated the capacity to produce coherent and contextually relevant text. As model sizes increased, from billions to hundreds of billions of parameters, there was a marked improvement in capabilities, particularly in zero-shot and few-shot learning. Recent models such as GPT‑4 (OpenAI, 2023)[^4], Google’s Gemini, and Meta’s LLaMA series have further advanced these capabilities, illustrating that even models with relatively modest parameter counts (e.g., 7B–65B) can achieve impressive performance when trained on high-quality data.

#### Diverse Architectures and Alignment Challenges

In addition to the GPT and BERT families, the landscape now includes models from EleutherAI (such as GPT‑Neo and GPT‑J) and the BigScience project’s BLOOM, each offering unique advantages in terms of openness and performance. More recently, the Mistral architecture has emerged as an efficient alternative, emphasizing rapid inference and resource efficiency. Models based on Mistral not only perform strongly on reasoning benchmarks but are also optimized for deployment on less powerful hardware, a key advantage for real-world applications. Despite these architectural advances, a central challenge remains: aligning the model’s outputs with human values and task-specific objectives. Traditional approaches like Reinforcement Learning from Human Feedback (RLHF) involve training a separate reward model followed by a reinforcement learning phase, a process that is often complex, computationally expensive, and sometimes unstable.

#### Advances in Alignment without Reinforcement Learning

Recent innovations have sought to simplify the alignment process by eliminating the need for a separate reward model. Direct Preference Optimization (DPO)[^5] is one such method that reframes the alignment challenge as a classification problem over human preference pairs. Instead of relying on the multi-stage RLHF pipeline, DPO directly adjusts the model’s output probabilities by maximizing the log probability difference between preferred and dispreferred responses relative to a reference policy. This approach significantly reduces computational overhead and the need for extensive hyperparameter tuning, while achieving comparable or superior alignment performance. Empirical studies have shown that DPO-trained models perform exceptionally well in tasks such as sentiment modulation, summarization, and dialogue, offering a more stable and efficient alternative to traditional RLHF methods.

#### Criteria for Selecting a Large Language Model

Selecting an appropriate large language model involves a careful balance of several factors. Performance on standardized benchmarks—such as AGIEval, BigBench, GPT4All, and TruthfulQA—is critical, as these metrics assess the model’s reasoning, generative coherence, and factual accuracy. Equally important is computational efficiency; models with a moderate parameter count that support quantization techniques can be deployed on hardware with limited resources. The alignment and safety of a model are paramount, and approaches like DPO help ensure that outputs adhere to human preferences and reduce the likelihood of generating harmful content. Moreover, the model’s openness, reflected in its permissive license and integration with platforms like Hugging Face, facilitates reproducibility, community collaboration, and seamless deployment. Finally, the use of standardized prompt formats, such as ChatML, streamlines integration into conversational applications.

---

### Selected Model: Nous‑Hermes‑2‑Mistral‑7B‑DPO

#### Model Core Architecture

Nous‑Hermes‑2‑Mistral‑7B‑DPO is a flagship 7B Hermes model. It is derived from Teknium’s OpenHermes‑2.5-Mistral‑7B and has been further refined using Direct Preference Optimization. The model was fine-tuned on one million instructions and chat interactions of GPT‑4 quality or better, primarily using synthetic data as well as other high-quality datasets from the Teknium/OpenHermes‑2.5 repository. 

#### Performance and Empirical Evaluation

Empirical evaluations confirm that Nous‑Hermes‑2‑Mistral‑7B‑DPO has improved performance across all tested benchmarks. On the GPT4All benchmark, it achieves an average accuracy of approximately 73.72%, demonstrating robust generalization and reasoning capabilities. The AGIEval benchmark shows an average score of around 43.63%, indicating its competence in handling complex sentiment and logical reasoning tasks. BigBench evaluations, with an average score near 41.94%, further attest to its proficiency in inference-based and multiple-choice tasks. Additionally, TruthfulQA results underscore its enhanced factual accuracy. Beyond these quantitative metrics, the model’s performance in multi-turn dialogue and instruction-following tasks is exemplary, making it highly effective for practical applications. 

#### Practical Advantages

The practical advantages of Nous‑Hermes‑2‑Mistral‑7B‑DPO are numerous. Its moderate parameter count, combined with support for efficient quantization techniques (e.g., 4-bit mode, which can reduce VRAM usage to around 5GB), makes it accessible for deployment on a variety of hardware configurations. The use of DPO as the training paradigm ensures that the model closely adheres to human preferences, thereby producing reliable and safe outputs. Integration is further facilitated by its use of the ChatML prompt format, which enables structured multi-turn dialogue. 

#### Rationale for Selection

The selection of Nous‑Hermes‑2‑Mistral‑7B‑DPO is justified by its strong empirical performance, efficient resource utilization, and advanced alignment capabilities. The model’s impressive performance across benchmarks such as GPT4All, AGIEval, BigBench, and TruthfulQA demonstrates its robust reasoning and generative abilities. Its efficient design, evidenced by its moderate parameter count and compatibility with quantization, ensures that it can be deployed in environments with limited hardware resources. Finally, the model’s seamless integration with standardized prompt formats and its permissive open-source license make it an ideal choice for conversational AI to content generation.

---

### Project Structure


```
R1/
├── app/
│   └── main.py          # FastAPI application code
├── docker-compose.yml   # Docker Compose configuration for PostgreSQL
├── README.md            # Project documentation (this file)
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (optional)
```

### Setup Instructions

#### Prerequisites

- **Python 3.8+**
- **Docker & Docker Compose**  
  [Get Docker](https://docs.docker.com/get-docker/) | [Docker Compose Installation](https://docs.docker.com/compose/install/)

#### 1. Clone the Repository

```bash
git clone <repository_url>
cd R1
```

#### 2. Create & Activate a Virtual Environment

**On Unix/MacOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables (Optional)

Create a `.env` file in the project root with the following content:

```dotenv
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
```

*Note:* Adjust the values as necessary.

#### 5. Start the PostgreSQL Database with Docker Compose

Ensure Docker is running, then execute:

```bash
docker-compose up -d
```

This command will:
- Download and run the PostgreSQL image.
- Create a database named **db_name** (as specified in the Docker Compose file).
- Expose port `5432` on your host.

#### 6. Run the FastAPI Application

Start the API server using Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Your API should now be accessible at [http://0.0.0.0:8000](http://0.0.0.0:8000).

### API Endpoints

#### Health Check

- **URL:** `/health`
- **Method:** `GET`
- **Description:** Checks if the service is running.
- **Example:**

  ```bash
  curl http://localhost:8000/health
  ```

  **Response:**

  ```json
  {
    "status": "OK"
  }
  ```

#### Generate Text

- **URL:** `/generate`
- **Method:** `POST`
- **Description:** Generates a response from the LLM based on user input.
- **Payload Example:**

  ```json
  {
    "session_id": "example-session",
    "user_message": "Hello, how are you?",
    "max_new_tokens": 200,
    "temperature": 0.7,
    "repetition_penalty": 1.1
  }
  ```

- **Example using curl:**

  ```bash
  curl -X POST "http://localhost:8000/generate" \
       -H "Content-Type: application/json" \
       -d '{
             "session_id": "example-session",
             "user_message": "Hello, how are you?",
             "max_new_tokens": 200,
             "temperature": 0.7,
             "repetition_penalty": 1.1
           }'
  ```

- **Response:**

  ```json
  {
    "response": "Generated response text from the model.",
    "session_id": "example-session"
  }
  ```

#### Clear Session

- **URL:** `/clear_session`
- **Method:** `DELETE`
- **Description:** Clears the session history for the specified session ID by deleting all stored messages from the database. This endpoint is useful for resetting the conversation history.
- **Payload Example:**

  ```json
  {
  "session_id": "example-session"
  }

  ```

- **Example using curl:**

  ```bash
  curl -X DELETE "http://localhost:8000/clear_session" \
     -H "Content-Type: application/json" \
     -d '{"session_id": "example-session"}'
  ```

- **Response:**

  ```json
  {
  "status": "Session cleared",
  "session_id": "example-session",
  "deleted_messages": 5
  }
  ```

  ## References

[^1]: Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). *Attention is All You Need*. Advances in Neural Information Processing Systems. [Link](https://arxiv.org/abs/1706.03762).

[^2]: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*. Proceedings of NAACL‑HLT. [Link](https://arxiv.org/abs/1810.04805).

[^3]: Brown, T., Mann, B., Ryder, N., et al. (2020). *Language Models are Few-Shot Learners*. Advances in Neural Information Processing Systems. [Link](https://arxiv.org/abs/2005.14165).

[^4]: OpenAI. (2023). *GPT‑4 Technical Report*. [arXiv preprint](https://arxiv.org/abs/2303.08774).


[^5]: Rafailov, R., Sharma, A., Mitchell, E., Manning, C. D., Ermon, S., & Finn, C. (2023). *Direct Preference Optimization: Your Language Model is Secretly a Reward Model*. NeurIPS 2023. [Link](https://openreview.net/forum?id=HPuSIXJaa9).

