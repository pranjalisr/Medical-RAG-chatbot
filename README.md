# 🩺 MediBot — RAG-Powered Medical Chatbot

A production-ready **Retrieval-Augmented Generation (RAG)** chatbot that answers medical questions grounded in trusted knowledge sources. Built with LangChain, Pinecone, OpenAI GPT-4o, Flask, and deployed via Docker + AWS CI/CD.

> ⚠️ **Disclaimer:** This chatbot is for informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.

---

## ✨ What Makes This Different

- 🧠 **Structured system prompt** with safety guardrails — the model cites retrieved context and refuses to speculate beyond it
- 📚 **Pluggable data sources** — swap in any PDF corpus (included: Gale Encyclopedia of Medicine)
- 💬 **Custom chat UI** — clean, responsive interface with typing indicators and source attribution
- 🔁 **Conversation memory** — maintains multi-turn context using LangChain's `ConversationBufferWindowMemory`
- 🐳 **Dockerized + CI/CD** — GitHub Actions pipeline deploys to AWS EC2 via ECR

---

## 🏗️ Architecture

```
User Query
    │
    ▼
Flask API (/get)
    │
    ▼
LangChain RAG Chain
    ├── HuggingFace Embeddings (sentence-transformers/all-MiniLM-L6-v2)
    ├── Pinecone Vector Store (similarity search, top-k=5)
    └── GPT-4o (with structured system prompt + safety instructions)
    │
    ▼
Grounded Answer + Source Docs
```

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/pranjalisr/RAG-chatbot.git
cd RAG-chatbot
```

### 2. Create a conda environment

```bash
conda create -n medibot python=3.10 -y
conda activate medibot
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
PINECONE_API_KEY=your_pinecone_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

> Get your keys: [Pinecone](https://www.pinecone.io/) | [OpenAI](https://platform.openai.com/)

### 5. Ingest your data into Pinecone

Place your PDF(s) in the `data/` folder, then run:

```bash
python store_index.py
```

### 6. Run the app

```bash
python app.py
```

Open [http://localhost:5001](http://localhost:5001)

---

## 🔌 Swapping the Data Source

The chatbot is designed to work with **any PDF corpus**. To change the knowledge base:

1. Replace or add PDFs to the `data/` folder
2. Update `index_name` in `store_index.py` and `app.py` if needed
3. Re-run `python store_index.py` to re-embed

**Tested data sources:**
- Gale Encyclopedia of Medicine (default)
- WHO Clinical Guidelines PDFs
- PubMed article exports
- Custom internal documents

---

## 🧠 Prompt Engineering

The system prompt is carefully structured to:

1. **Ground answers in retrieved context** — the model is instructed to answer only from the provided documents
2. **Acknowledge uncertainty** — if the context doesn't contain enough information, the model says so explicitly rather than hallucinating
3. **Cite its source** — responses reference which part of the knowledge base the answer came from
4. **Apply safety guardrails** — the model never recommends specific medications or dosages and always defers to a doctor

See [`src/prompt.py`](src/prompt.py) for the full prompt template.

---

## 🐳 Docker

```bash
docker build -t medibot .
docker run -p 5001:5001 --env-file .env medibot
```

---

## ☁️ AWS Deployment (CI/CD via GitHub Actions)

The `.github/workflows/` pipeline:
1. Builds a Docker image
2. Pushes it to Amazon ECR
3. SSHs into an EC2 instance and pulls + runs the new image

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret |
| `AWS_DEFAULT_REGION` | e.g. `us-east-1` |
| `ECR_REPO` | Your ECR repository URI |
| `PINECONE_API_KEY` | Pinecone API key |
| `OPENAI_API_KEY` | OpenAI API key |

### IAM Permissions Required

- `AmazonEC2ContainerRegistryFullAccess`
- `AmazonEC2FullAccess`

---

## 🗂️ Project Structure

```
RAG-chatbot/
├── .github/workflows/      # CI/CD pipeline
├── data/                   # PDF knowledge base
├── research/               # Notebooks for experimentation
├── src/
│   ├── helper.py           # Embedding loader
│   └── prompt.py           # System prompt + templates
├── static/                 # CSS, JS, assets
├── templates/
│   └── chat.html           # Custom chat UI
├── app.py                  # Flask app + RAG chain
├── store_index.py          # PDF ingestion + Pinecone upsert
├── Dockerfile
└── requirements.txt
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | OpenAI GPT-4o |
| Orchestration | LangChain |
| Vector DB | Pinecone |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Backend | Flask |
| Frontend | HTML/CSS/JS (custom UI) |
| Containerisation | Docker |
| Cloud | AWS EC2 + ECR |
| CI/CD | GitHub Actions |

---

## 📄 License

[Apache 2.0](LICENSE)
