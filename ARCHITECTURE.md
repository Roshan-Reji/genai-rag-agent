# GenAI RAG + Agent System - Technical Architecture

## System Architecture

### High-Level Overview

```
┌────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│         (CLI, REST API, Gradio, Streamlit)                │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│              FastAPI Application Layer                     │
│  - Request handling & validation                          │
│  - CORS & middleware                                      │
│  - Health checks & monitoring                            │
└────────────────────┬─────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐ ┌──────────┐ ┌──────────────┐
   │   RAG   │ │  Agent   │ │ Evaluation   │
   │Pipeline │ │ Executor │ │ Framework    │
   └────┬────┘ └────┬─────┘ └──────────────┘
        │           │
        └──────┬────┘
               ▼
        ┌──────────────────┐
        │ Tool Registry    │
        │ - KB Search      │
        │ - Calculator     │
        │ - Web Search     │
        └──────────────────┘
               │
     ┌─────────┴──────────┐
     ▼                    ▼
┌─────────────┐    ┌──────────────┐
│ Vector DB   │    │ LLM APIs     │
│ (Chroma)    │    │ (OpenAI/     │
│             │    │  Claude)     │
└─────────────┘    └──────────────┘
```

## Component Details

### 1. RAG Pipeline (`src/rag/`)

**Document Processing Pipeline:**
```
Input Document → Load → Clean → Chunk → Embed → Store
     ↓           ↓       ↓        ↓       ↓       ↓
   .txt/.pdf    Read   Remove   Split  Vector  Vector
   .docx files  text   special  text   embeddings DB
```

**Key Classes:**
- `DocumentChunker`: Semantic chunking with configurable overlap
- `DocumentLoader`: Multi-format document loading
- `EmbeddingManager`: Batch embedding generation
- `VectorDatabase`: Vector storage and retrieval
- `RAGPipeline`: End-to-end orchestration

**Query Flow:**
```
Query → Embed → Search VectorDB → Retrieve (top-k) → Format Context → Generate Answer
  ↓      ↓          ↓                ↓                    ↓              ↓
Text   Vector    Similar docs    Ranked results     Combine text    LLM generation
                 search                                              with context
```

### 2. AI Agent (`src/agent/`)

**Agent Loop:**
```
START
  ↓
Input Query
  ↓
LLM Thinking → Decision
  ↓
Tool needed? ─→ YES ─→ Parse tool call → Execute tool ──→ Tool result → Continue
  ↓ NO                                                      ↓
Generate answer ─→ Return Response ─→ END
```

**State Machine:**
```
┌─────────────────────────────────────────────────┐
│                                                 │
▼                                                 │
IDLE ──→ RUNNING ──→ THINKING ──→ TOOL_CALLING ──┘
                        ↓
                    GENERATING ──→ COMPLETED
                        ↓
                      ERROR
```

**Tool Execution:**
```
Agent Response → Parse JSON → Extract Tool Name & Args
                    ↓
            Validate Tool Exists
                    ↓
            Execute Tool with Args
                    ↓
            Capture Output/Error
                    ↓
            Return to Agent Context
```

### 3. Evaluation Framework (`src/evaluation/`)

**Evaluation Pipeline:**
```
Test Dataset
    ↓
    ├─→ Retrieval Evaluation
    │   ├─ Relevance Score
    │   ├─ NDCG Ranking
    │   └─ Mean Rank
    │
    ├─→ Agent Evaluation
    │   ├─ Response Accuracy
    │   ├─ Tool Selection
    │   ├─ F1 Score
    │   └─ Response Time
    │
    └─→ Generate Report
        ├─ Summary Statistics
        ├─ Performance Metrics
        └─ Dashboard Data
```

## Data Flow

### Document Ingestion Flow
```
Document File
     ↓
Load → Clean → Chunk
     ↓         ↓
   Text     Segments
              ↓
          Embed Each
              ↓
          Embeddings
              ↓
        Store in VectorDB
              ↓
        Ready for Retrieval
```

### Query Processing Flow
```
User Query
    ↓
Embed Query
    ↓
Vector Search (VectorDB)
    ↓
Retrieve Top-K Documents
    ↓
Score & Rank Results
    ↓
Format Context
    ↓
Feed to LLM with Context
    ↓
Generate Answer
    ↓
Return to User
```

### Agent Execution Flow
```
User Query
    ↓
Agent receives query
    ↓
Format conversation history
    ↓
Send to LLM
    ↓
Parse LLM Response
    ├─ Has tool call? → YES → Execute Tool → Update History → Loop
    └─ NO → Generate final answer → Return to User
```

## Technology Stack

### Core
- **Python 3.10+**: Runtime
- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **LangChain**: LLM orchestration

### NLP & ML
- **sentence-transformers**: Embeddings
- **scikit-learn**: ML utilities
- **nltk**: Text processing
- **ragas**: Evaluation metrics

### Data Storage
- **Chroma**: Vector database
- **SQLAlchemy**: ORM
- **PostgreSQL**: Optional relational DB

### Cloud & Deployment
- **Docker**: Containerization
- **AWS ECR**: Container registry
- **AWS ECS**: Container orchestration
- **CloudWatch**: Monitoring

### Development
- **pytest**: Testing
- **GitHub Actions**: CI/CD
- **Uvicorn**: ASGI server

## Performance Characteristics

### Latency Expectations
- Document Embedding: ~50-200ms per document
- Vector Search: ~5-50ms (depending on DB size)
- LLM Generation: 1-5 seconds (API dependent)
- Total RAG Query: ~2-6 seconds
- Agent Query: 3-10 seconds (with tool calls)

### Throughput
- RAG Queries/sec: 5-20 (depends on LLM API limits)
- Concurrent Users: 10-50 (with 2 ECS tasks)
- Document Ingestion: 100-500 chunks/second

### Resource Usage
- Memory per Task: 512MB minimum
- Storage: ~1-2GB per million embeddings
- Network: ~100KB per query (varies)

## Scalability Strategy

### Horizontal Scaling
```
Load Balancer
    ↓
    ├─→ Task 1 (Fargate)
    ├─→ Task 2 (Fargate)
    ├─→ Task 3 (Fargate)
    └─→ Task N (Fargate)
         ↓
    Shared Vector DB (AWS OpenSearch/Managed)
    Shared LLM API (OpenAI/Bedrock)
```

### Vertical Scaling
- Increase ECS task CPU/Memory
- Use larger embedding models
- Use faster vector search (approximate methods)

### Caching Strategy
```
Query ──→ Cache Hit? ──→ YES ──→ Return cached result
 ↓           ↓
 NO      VectorDB Search ──→ Cache Result ──→ Return
```

## Monitoring & Observability

### Metrics Tracked
- **Request Metrics**: Latency, throughput, error rate
- **Business Metrics**: Accuracy, relevance, cost
- **System Metrics**: CPU, memory, disk, network
- **LLM Metrics**: Token usage, API latency, cost

### Logging Strategy
```
Application Logs
    ├─ Request logs (FastAPI)
    ├─ Agent execution traces
    ├─ Error/exception logs
    └─ Performance metrics
         ↓
    CloudWatch Logs
         ↓
    Dashboards & Alerts
```

## Security Architecture

### Data Flow Security
```
User Request → HTTPS → API Gateway
                           ↓
                    Authentication/Authorization
                           ↓
                    Rate Limiting
                           ↓
                    Input Validation
                           ↓
                    Process Query
                           ↓
                    Return Response (Filtered)
```

### Secrets Management
```
API Keys → AWS Secrets Manager
             ↓
        Mounted as env vars
             ↓
        Never logged/exposed
```

## Deployment Architecture

### Local Development
```
Docker Container (local)
    ├─ Python app
    ├─ Local vector DB
    └─ Local embeddings cache
```

### AWS Production
```
┌─────────────────────────────────────────────┐
│                ALB (Load Balancer)           │
└────────────────┬────────────────────────────┘
                 │
      ┌──────────┼──────────┐
      ▼          ▼          ▼
   Task 1    Task 2    Task N
   (ECS)     (ECS)     (ECS)
      │          │          │
      └──────────┼──────────┘
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
 OpenSearch         Bedrock/OpenAI
 (Vector DB)        (LLM API)
```

## Cost Optimization

### Strategies
1. **Batch Operations**: Batch embed documents
2. **Caching**: Cache frequent queries
3. **Model Selection**: Use smaller models when possible
4. **Scheduled Jobs**: Process at off-peak times
5. **Approximate Search**: Use faster (less accurate) search for large DBs

### Cost Estimation
- Vector DB: $50-500/month (managed service)
- LLM API: $5-50/month (depends on volume)
- Compute (ECS): $50-200/month
- Data Transfer: $0-100/month
- **Total**: $105-850/month for small-medium scale

## Error Handling & Recovery

### Error Types & Handling
```
API Error → Log → Retry → Backoff → Fallback Response
           │                          │
           └──→ Circuit Breaker ──────┘

LLM Error → Log → Retry → Use Cache → Error Response

Vector DB Error → Log → Reconnect → Rebuild Index
```

### Resilience Patterns
- Circuit breaker for external APIs
- Retry with exponential backoff
- Request timeout & cancellation
- Graceful degradation
- Health checks & auto-recovery

## Disaster Recovery

### Backup Strategy
- **Vector DB**: Periodic snapshots to S3
- **Application Code**: Version control (GitHub)
- **Configuration**: Secrets Manager backups

### Recovery Time Objectives
- RTO (Recovery Time): < 30 minutes
- RPO (Recovery Point): < 1 hour

## Future Enhancements

1. **Multi-Agent Collaboration**: Agent orchestration framework
2. **Advanced RAG**: Multi-hop retrieval, query expansion
3. **Fine-tuning**: Custom LLM fine-tuning pipeline
4. **Real-time Updates**: Streaming embeddings
5. **Federated Learning**: Distributed training
6. **GraphDB Integration**: Knowledge graph support
