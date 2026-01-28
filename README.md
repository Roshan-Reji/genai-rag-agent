# 🚀 GenAI RAG + Agent System

A **production-ready Generative AI application** combining **Retrieval-Augmented Generation (RAG)**, **autonomous AI agents**, and a **comprehensive evaluation framework**, built using **Python, FastAPI, vector databases, and Docker**, and deployable on **AWS**.

---

## 🎯 Project Overview

This project implements an **end-to-end GenAI system** that enables intelligent question answering over custom documents using RAG and AI agents.

### Key Capabilities

* 📚 **RAG Pipeline** – Document ingestion, semantic chunking, embeddings, vector search
* 🤖 **AI Agent System** – Tool-calling agents with state management and orchestration
* 📊 **Evaluation Framework** – Automated benchmarking and performance metrics
* 🌐 **FastAPI Service** – REST APIs for RAG, agents, evaluation, and system health
* 🐳 **Dockerized Deployment** – Cloud-ready (AWS / ECS / EC2)

---

## 🧠 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
│        (API Routes, Logging, Health Checks)                 │
└───────────────┬────────────────────────────────────────────┘
                │
        ┌───────┼─────────┬─────────────┬──────────────┐
        │       │         │             │              │
        ▼       ▼         ▼             ▼              ▼
 ┌─────────┐ ┌─────────┐ ┌───────────┐ ┌────────────┐
 │  RAG    │ │  Agent  │ │ Evaluation│ │ System Mgmt│
 │Pipeline │ │ Executor│ │ Framework │ │ & Config   │
 └────┬────┘ └────┬────┘ └────┬──────┘ └────────────┘
      │           │           │
      └───────────┴───────────┴──────────────┐
                                              ▼
                      ┌─────────────────────────────┐
                      │ Vector DB & LLM Providers    │
                      │ (Chroma / Pinecone / OpenAI) │
                      └─────────────────────────────┘
```

---

## 🛠️ Tech Stack

* **Language**: Python 3.10+
* **LLMs**: OpenAI / Claude / Gemini (configurable)
* **Frameworks**: FastAPI, LangChain
* **Vector DB**: Chroma (DuckDB backend)
* **Agents**: Tool-calling agents (LangChain-style)
* **Deployment**: Docker, Docker Compose, AWS (ECS/EC2)
* **Testing**: Pytest

---

## ⚡ Quick Start

### Prerequisites

* Python 3.10+
* Docker
* OpenAI API Key
* 4 GB RAM minimum

---

### 1️⃣ Clone & Setup Environment

```bash
git clone https://github.com/your-username/genai-rag-agent.git
cd genai-rag-agent

python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux / Mac
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```ini
OPENAI_API_KEY=your_api_key
LLM_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small
```

---

### 4️⃣ Run Application (Local)

```bash
uvicorn src.api.main:app --reload
```

📍 API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📚 Core Components

### 🔹 1. RAG Pipeline (`src/rag/`)

**Features**

* PDF / TXT / DOCX ingestion
* Recursive semantic chunking
* Embedding generation
* Vector similarity search
* Source-aware answers

```python
from src.rag import RAGPipeline

rag = RAGPipeline()
rag.ingest_document("data/documents/sample.pdf")
response = rag.query("What is machine learning?")
```

---

### 🔹 2. AI Agent System (`src/agent/`)

**Capabilities**

* Autonomous decision-making
* Tool selection & execution
* State management
* Conversation history tracking

```python
from src.agent import AIAgent, ToolRegistry

tools = ToolRegistry(rag_pipeline=rag)
agent = AIAgent(tool_registry=tools)

agent.execute_query("Find AI info and calculate 5 * 6")
```

---

### 🔹 3. Evaluation Framework (`src/evaluation/`)

**Metrics**

* Retrieval relevance
* Accuracy, Precision, Recall, F1
* Tool-selection correctness
* Latency tracking

```python
from src.evaluation import BenchmarkRunner

runner = BenchmarkRunner(rag, agent)
runner.run_all()
```

---

## 🌐 API Endpoints

### RAG

* `POST /rag/query`
* `POST /rag/ingest`

### Agent

* `POST /agent/query`
* `GET /agent/tools`

### Evaluation

* `POST /evaluation/run`
* `GET /evaluation/dashboard`

### System

* `GET /health`
* `POST /system/reset`

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t genai-rag-agent .
```

### Run Container

```bash
docker run -p 8000:8000 \
-e OPENAI_API_KEY=your_key \
genai-rag-agent
```

### Docker Compose

```bash
docker-compose up -d
```

---

## ☁️ AWS Deployment (Overview)

* Push Docker image to **ECR**
* Deploy using **ECS Fargate or EC2**
* Configure environment variables
* Attach Load Balancer (optional)

---

## 🧪 Testing

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest --cov=src --cov-report=html
```

---

## 📁 Project Structure

```
genai-rag-agent/
├── src/
│   ├── api/
│   ├── rag/
│   ├── agent/
│   ├── evaluation/
│   └── config/
├── data/
│   ├── documents/
│   └── embeddings/
├── tests/
├── scripts/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔐 Security Best Practices

* Environment variables for secrets
* No API keys in code
* Rate limiting (recommended)
* HTTPS in production
* CORS restrictions

---

## 📈 Performance Optimizations

* Chunk overlap tuning
* Smaller embedding models for speed
* Caching repeated queries
* Reduced TOP-K retrieval
* Streaming LLM responses





