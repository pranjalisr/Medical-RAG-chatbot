# 🩺 MediBot — RAG-Powered Medical Chatbot

A production-ready **Retrieval-Augmented Generation (RAG)** chatbot that answers medical questions grounded strictly in a trusted knowledge base — and refuses to guess when it doesn't know.

> ⚠️ **Disclaimer:** This chatbot is for informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.

---

## 💡 What Makes This Different

Most LLM chatbots will confidently hallucinate an answer to anything. MediBot is engineered to know what it doesn't know.

| Feature | How it works |
|---|---|
| 🔒 Hallucination refusal | Answers grounded strictly in retrieved documents — refuses to speculate beyond them |
| 💊 Medication guardrails | Never recommends specific drugs or dosages — always defers to a doctor |
| 📚 Source citation | Every answer cites the exact document section it came from |
| 🔁 Conversation memory | History-aware retriever — follow-up questions work without repeating context |
| ❓ Uncertainty acknowledgment | Explicitly says "I don't have enough information" rather than fabricating |

---

## 🖥️ Demo

**Accurate answer with source citation:**

> *"What is the treatment for asthma?"*
> → Grounded answer + `*(Based on: Gale Encyclopedia of Medicine – Asthma)*`

**Multi-turn conversation memory:**

> *"What causes hypertension?"* → detailed answer
> *"What lifestyle changes can help manage it?"* → bot correctly understands "it" = hypertension, no need to repeat context

**Hallucination refusal:**

> *"What is the exact dosage of metformin for a 60kg adult with stage 3 kidney disease?"*
> → *"I don't have enough information in my knowledge base to answer this reliably. Dosage depends on many factors including kidney function, and only a qualified healthcare professional can determine the correct dose."*

> *"What did the 2023 AHA guidelines say about statins?"*
> → *"I don't have enough information in my knowledge base to answer this reliably."*

**Medication guardrail:**

> *"What medication should I take for high blood pressure?"*
> → *"I cannot recommend specific medications or dosages. Only a licensed healthcare professional can determine the right treatment for your individual condition..."*

---

## 🏗️ Architecture

```
User Query
    │
    ▼
Flask API (/get)
    │
    ▼
History-Aware Retriever
    ├── Reformulates follow-up questions into standalone queries
    └── HuggingFace Embeddings → Pinecone similarity search (top-k=5)
    │
    ▼
DeepSeek LLM (deepseek-chat)
    └── Structured system prompt with safety guardrails
    │
    ▼
Grounded Answer + Source Citations
```

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/pranjalisr/Medical-RAG-chatbot.git
cd Medical-RAG-chatbot
```

### 2. Create environment

```bash
conda create -n medibot python=3.10 -y
conda activate medibot
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file in the project root:

```env
PINECONE_API_KEY=your_pinecone_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
```

Get your keys:
- Pinecone → [pinecone.io](https://www.pinecone.io) → API Keys
- DeepSeek → [platform.deepseek.com](https://platform.deepseek.com) → API Keys

### 5. Create Pinecone index

In your Pinecone dashboard, create an index with:

| Setting | Value |
|---|---|
| Index name | `medical-chatbot` |
| Dimensions | `384` |
| Metric | `cosine` |
| Capacity mode | Serverless |
| Cloud / Region | AWS `us-east-1` |

> Dimension `384` matches the `all-MiniLM-L6-v2` embedding model used in this project.

### 6. Ingest your data

Place PDFs in the `data/` folder, then:

```bash
python store_index.py
```

This chunks the PDFs, generates embeddings, and upserts into Pinecone. Run once, or re-run whenever you change the knowledge base.

### 7. Run the app

```bash
python app.py
```

Open [http://localhost:5001](http://localhost:5001)

---

## 🧠 Prompt Engineering

The system prompt in `src/prompt.py` is structured around 6 explicit rules:

1. **Context-only answers** — model is instructed to answer only from retrieved passages, never from training knowledge
2. **Explicit uncertainty** — if context is insufficient, say so; never fabricate
3. **Source citation** — end every answer with `*(Based on: [document section])*`
4. **No drug recommendations** — redirect all medication/dosage questions to a doctor
5. **No diagnosis** — describe conditions from the knowledge base but never diagnose
6. **Emergency caveat** — prepend `⚠️` for any life-threatening symptoms

The history-aware retriever (`contextualize_q_system_prompt`) reformulates follow-up questions into standalone queries before hitting Pinecone — so multi-turn conversations retrieve the right context even when the user says "it" or "that condition".

---

## 🔌 Swapping the Data Source

MediBot works with any PDF corpus. To change the knowledge base:

1. Replace PDFs in the `data/` folder
2. Update `index_name` in `store_index.py` and `app.py` if needed
3. Re-run `python store_index.py`

**Tested sources:**
- Gale Encyclopedia of Medicine (default)
- WHO Clinical Guidelines
- PubMed article exports
- Custom internal documents

---

## 🐳 Docker

```bash
docker build -t medibot .
docker run -p 5001:5001 --env-file .env medibot
```

---

## ☁️ AWS Deployment (CI/CD via GitHub Actions)

The `.github/workflows/` pipeline automatically:
1. Builds the Docker image
2. Pushes it to Amazon ECR
3. SSHs into EC2 and pulls + runs the new image on every push to `main`

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret |
| `AWS_DEFAULT_REGION` | e.g. `us-east-1` |
| `ECR_REPO` | Your ECR repository URI |
| `PINECONE_API_KEY` | Pinecone API key |
| `DEEPSEEK_API_KEY` | DeepSeek API key |

---

## 🗂️ Project Structure

```
Medical-RAG-chatbot/
├── .github/workflows/       # CI/CD — build, push to ECR, deploy to EC2
├── data/                    # PDF knowledge base
├── research/                # Jupyter notebooks for experimentation
├── src/
│   ├── helper.py            # HuggingFace embedding loader
│   └── prompt.py            # System prompt + safety guardrails
├── templates/
│   └── chat.html            # Custom chat UI
├── app.py                   # Flask app + RAG chain + session memory
├── store_index.py           # PDF ingestion + Pinecone upsert
├── Dockerfile
└── requirements.txt
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | DeepSeek (`deepseek-chat`) |
| Orchestration | LangChain |
| Vector DB | Pinecone (Serverless) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Backend | Flask |
| Frontend | Custom HTML/CSS/JS |
| Containerisation | Docker |
| Cloud | AWS EC2 + ECR |
| CI/CD | GitHub Actions |

---

## 📄 License

[Apache 2.0](LICENSE)
