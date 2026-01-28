# GenAI RAG + Agent System

A production-ready Generative AI application combining Retrieval-Augmented Generation (RAG) pipelines, autonomous AI agents, and comprehensive evaluation frameworks.

## 🎯 Project Overview

This system implements an end-to-end GenAI solution with:

- **RAG Pipeline**: Document ingestion, semantic chunking, embedding generation, and intelligent retrieval
- **AI Agents**: Autonomous agents with tool calling, state management, and decision-making capabilities
- **Evaluation Framework**: Comprehensive metrics for retrieval quality, agent accuracy, and system performance
- **FastAPI Application**: RESTful API for all components with health checks and monitoring
- **Docker Deployment**: Containerized application ready for cloud deployment (AWS, GCP, Azure)

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│              (Endpoints, Health Checks, Logging)             │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┬──────────────┬──────────────┐
    │                 │              │              │
    ▼                 ▼              ▼              ▼
┌─────────┐    ┌──────────┐    ┌──────────┐   ┌──────────────┐
│   RAG   │    │  Agent   │    │ Eval     │   │  System      │
│Pipeline │    │ Executor │    │Framework │   │  Management  │
└────┬────┘    └────┬─────┘    └────┬─────┘   └──────────────┘
     │              │              │
     ├──────────────┴──────────────┤
     │                             │
     ▼                             ▼
┌────────────────┐    ┌──────────────────────┐
│ Vector DB      │    │ LLM APIs             │
│ (Chroma/       │    │ (OpenAI/Claude/      │
│  Pinecone)     │    │  Bedrock)            │
└────────────────┘    └──────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key (or compatible LLM provider)
- Docker (for containerized deployment)
- 4GB RAM minimum

### Installation

1. **Clone and Setup**
```bash
cd c:\Users\hp\Desktop\rag
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

4. **Create Sample Data**
```bash
python scripts/create_sample_docs.py
```

### Running the Application

**Locally (Development):**
```bash
python -m uvicorn src.api.main:app --reload
```

**Docker (Production):**
```bash
docker-compose up -d
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## 📚 Core Components

### 1. RAG Pipeline (`src/rag/`)

**DocumentProcessor** - Intelligent document handling
- Loads: TXT, PDF, DOCX files
- Semantic chunking with overlap
- Metadata preservation
- Configurable chunk sizes

**EmbeddingManager** - Text embeddings
- Sentence-transformers for fast local embeddings
- Batch processing support
- Cosine similarity computation

**VectorDatabase** - Persistent vector storage
- Chroma DB with DuckDB backend
- Scalable to millions of documents
- Metadata filtering support

**RAGPipeline** - End-to-end RAG
```python
from src.rag import RAGPipeline

pipeline = RAGPipeline()
pipeline.ingest_document("documents/sample.pdf")
result = pipeline.query("What is machine learning?")
```

### 2. AI Agent (`src/agent/`)

**AIAgent** - Autonomous agent with tool calling
- State management (IDLE, RUNNING, THINKING, TOOL_CALLING, COMPLETED)
- Tool integration and execution
- Conversation history tracking
- Execution trace logging

**ToolRegistry** - Tool management
- Knowledge base search
- Calculator (math operations)
- Web search (simulated/real)
- Extensible tool system

```python
from src.agent import AIAgent, ToolRegistry

tool_registry = ToolRegistry(rag_pipeline=pipeline)
agent = AIAgent(tool_registry=tool_registry)
result = agent.execute_query("Search for information about AI")
```

### 3. Evaluation Framework (`src/evaluation/`)

**Metrics**
- Retrieval: Relevance, NDCG, Mean Rank
- Agent: Accuracy, Precision, Recall, F1, Tool Selection
- Response time tracking

**BenchmarkRunner** - Automated evaluation
```python
from src.evaluation import BenchmarkRunner, EvaluationDataset

dataset = EvaluationDataset()
dataset.add_test_case("Query", "Gold Answer", ["Gold Doc"])

runner = BenchmarkRunner(rag_pipeline, agent)
runner.dataset = dataset
retrieval_metrics = runner.benchmark_retrieval()
agent_metrics = runner.benchmark_agent()
```

## 🔌 API Endpoints

### RAG Endpoints

**POST /rag/query** - Query RAG pipeline
```json
{
  "query": "What is artificial intelligence?",
  "top_k": 5
}
```

**POST /rag/ingest** - Ingest documents
```json
{
  "file_path": "./data/documents/sample.pdf",
  "metadata": {"category": "technology"}
}
```

### Agent Endpoints

**POST /agent/query** - Query AI agent
```json
{
  "query": "Search for AI information",
  "verbose": false
}
```

**GET /agent/tools** - List available tools

### Evaluation Endpoints

**POST /evaluation/run** - Run evaluation
```json
{
  "eval_type": "both",
  "dataset_path": "evaluation_dataset.json"
}
```

**GET /evaluation/dashboard** - Get dashboard data

### System Endpoints

**GET /health** - Health check
**GET /system/config** - System configuration
**POST /system/reset** - Reset system data

## 📊 Configuration

Edit `.env` file:

```ini
# LLM Configuration
OPENAI_API_KEY=your_key_here
LLM_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small
MAX_TOKENS=2048
TEMPERATURE=0.7

# RAG Configuration
CHUNK_SIZE=1024
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5
SIMILARITY_THRESHOLD=0.7

# Agent Configuration
AGENT_TIMEOUT=30
MAX_RETRIES=3

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
```

## 🧪 Testing

**Run Unit Tests**
```bash
pytest tests/ -v
```

**Run Specific Tests**
```bash
pytest tests/test_rag.py -v
pytest tests/test_agent.py -v
```

**With Coverage**
```bash
pytest tests/ --cov=src --cov-report=html
```

## 📈 Performance Metrics

### Retrieval Metrics
- **Relevance Score**: 0-1 (higher is better)
- **NDCG (Normalized DCG)**: 0-1 (ranking quality)
- **Mean Rank**: Position of relevant documents

### Agent Metrics
- **Accuracy**: Correctness of responses (0-1)
- **Tool Selection**: Correct tool usage rate (0-1)
- **Response Time**: Latency in seconds
- **F1 Score**: Harmonic mean of precision/recall

## 🐳 Docker Deployment

**Build Image**
```bash
docker build -t genai-rag-agent:latest .
```

**Run Container**
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -v ./data:/app/data \
  genai-rag-agent:latest
```

**Docker Compose**
```bash
# Set OPENAI_API_KEY in .env or docker-compose.yml
docker-compose up -d

# View logs
docker-compose logs -f rag-api

# Stop
docker-compose down
```

## ☁️ AWS Deployment

### ECR (Elastic Container Registry)
```bash
# Create repository
aws ecr create-repository --repository-name genai-rag-agent

# Push image
docker tag genai-rag-agent:latest \
  your-account.dkr.ecr.us-east-1.amazonaws.com/genai-rag-agent:latest

docker push \
  your-account.dkr.ecr.us-east-1.amazonaws.com/genai-rag-agent:latest
```

### ECS (Elastic Container Service)
1. Create ECS cluster
2. Create task definition referencing ECR image
3. Create service in the cluster
4. Configure load balancer
5. Set environment variables in task definition

### Infrastructure as Code (Terraform Example)
```hcl
resource "aws_ecs_service" "genai_service" {
  name            = "genai-rag-agent"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.genai.arn
  desired_count   = 2
  launch_type     = "FARGATE"
}
```

## 📁 Project Structure

```
rag/
├── src/
│   ├── api/              # FastAPI application
│   │   ├── main.py       # FastAPI app
│   │   ├── models.py     # Request/response models
│   │   └── __init__.py
│   ├── rag/              # RAG pipeline
│   │   ├── pipeline.py   # Main RAG pipeline
│   │   ├── document_processor.py
│   │   ├── embeddings.py
│   │   └── __init__.py
│   ├── agent/            # AI Agent
│   │   ├── agent.py      # Main agent
│   │   ├── tools.py      # Tool definitions
│   │   └── __init__.py
│   └── evaluation/       # Evaluation framework
│       ├── benchmark.py
│       ├── metrics.py
│       └── __init__.py
├── config/
│   ├── settings.py       # Configuration
│   └── __init__.py
├── data/
│   ├── documents/        # Input documents
│   └── embeddings/       # Vector database
├── tests/                # Unit tests
│   ├── test_rag.py
│   ├── test_agent.py
│   └── conftest.py
├── scripts/              # Utility scripts
│   └── create_sample_docs.py
├── deployment/           # Deployment configs
│   └── aws_config.yaml
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container image
├── docker-compose.yml    # Multi-container setup
├── .env.example          # Environment template
└── README.md            # This file
```

## 🔐 Security Considerations

1. **API Keys**: Use environment variables, never commit to git
2. **Database**: Encrypt vector database at rest
3. **Authentication**: Implement JWT/OAuth for API (recommended)
4. **Rate Limiting**: Add rate limiting to prevent abuse
5. **HTTPS**: Use TLS in production
6. **CORS**: Configure appropriately for your domain

## 🚨 Troubleshooting

### Issue: OpenAI API errors
- Check API key is valid and has sufficient quota
- Verify rate limits aren't exceeded
- Check model name is available in your region

### Issue: Vector DB errors
- Ensure `data/embeddings` directory exists and is writable
- Clear database: `rm -rf data/embeddings/*`
- Reingest documents

### Issue: High latency
- Reduce `CHUNK_SIZE` for faster retrieval
- Increase `SIMILARITY_THRESHOLD` to return fewer results
- Use smaller embedding model
- Enable caching in production

### Issue: Memory issues
- Reduce batch size for embeddings
- Use smaller LLM model
- Enable vector DB compression
- Implement pagination for large result sets

## 📊 Example Usage

### Python Client
```python
from src.rag import RAGPipeline
from src.agent import AIAgent, ToolRegistry
import os

# Initialize RAG
rag = RAGPipeline(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Ingest documents
rag.ingest_document("data/documents/ai_basics.txt")

# Query RAG
result = rag.query("What is machine learning?")
print(f"Answer: {result['answer']}")
print(f"Sources: {[d['metadata'].get('source') for d in result['retrieved_documents']]}")

# Initialize Agent
tools = ToolRegistry(rag_pipeline=rag)
agent = AIAgent(
    llm_model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    tool_registry=tools
)

# Run Agent
agent_result = agent.execute_query("Find information about AI and calculate 2+2", verbose=True)
print(f"Agent Response: {agent_result['response']}")
```

### cURL API Requests
```bash
# Health check
curl http://localhost:8000/health

# RAG Query
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?", "top_k": 5}'

# Agent Query
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?"}'

# Run Evaluation
curl -X POST http://localhost:8000/evaluation/run \
  -H "Content-Type: application/json" \
  -d '{"eval_type": "both"}'
```

## 📈 Performance Optimization

### Embedding Optimization
- Use `all-MiniLM-L6-v2` for speed (384 dimensions)
- Use `all-mpnet-base-v2` for quality (768 dimensions)
- Batch embed documents (10-100 at a time)
- Cache embeddings for frequent queries

### Retrieval Optimization
- Use smaller `TOP_K_RETRIEVAL` (3-5) for speed
- Increase `SIMILARITY_THRESHOLD` to filter noise
- Implement LRU caching for repeated queries
- Use approximate nearest neighbor search

### LLM Optimization
- Use smaller models (GPT-3.5-turbo vs GPT-4)
- Reduce `MAX_TOKENS` when appropriate
- Implement response caching
- Use streaming for long responses
- Implement prompt compression

## 📝 Evaluation Datasets

Create evaluation datasets for benchmarking:

```python
from src.evaluation import EvaluationDataset

dataset = EvaluationDataset()

# Add test cases
dataset.add_test_case(
    query="What is RAG?",
    gold_response="RAG combines retrieval and generation",
    gold_docs=["RAG integrates document retrieval..."],
    expected_tools=["knowledge_base_search"]
)

# Save for later use
dataset.save("evaluation_dataset.json")
```

## 🎓 Learning Resources

- [LangChain Documentation](https://python.langchain.com/)
- [RAG Papers and Techniques](https://arxiv.org/search/?query=retrieval+augmented+generation)
- [Vector Database Comparison](https://blog.pinecone.io/vector-databases-for-llm-applications/)
- [Agent Frameworks Review](https://github.com/langchain-ai/langgraph)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 📞 Support

For issues, questions, or suggestions:
- Open GitHub Issues for bugs
- Check existing documentation
- Review example notebooks
- Contact development team

## 🎉 Next Steps

1. **Deploy to AWS**: Use docker-compose or AWS CDK
2. **Add Authentication**: Implement JWT tokens for API
3. **Advanced RAG**: Implement multi-hop retrieval, query expansion
4. **Multi-Agent System**: Implement agent orchestration
5. **Monitoring**: Add LangSmith, Weights & Biases integration
6. **Cost Optimization**: Implement token usage tracking and caching

---

**Built with ❤️ for the Midoc AI Challenge**

Version 1.0.0 | Last Updated: January 2026
#   g e n a i - r a g - a g e n t  
 