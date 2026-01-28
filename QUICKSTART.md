"""
Quick start guide for running the GenAI RAG + Agent System
"""

# 1. Install dependencies
pip install -r requirements.txt

# 2. Create sample documents
python scripts/create_sample_docs.py

# 3. Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Run tests
pytest tests/ -v

# 5. Run locally (CLI)
python main.py

# 6. Run API server
python -m uvicorn src.api.main:app --reload

# 7. Run with Docker
docker-compose up -d

# 8. Access API docs
# Visit http://localhost:8000/docs

# 9. Example API calls
# RAG Query:
# curl -X POST http://localhost:8000/rag/query \
#   -H "Content-Type: application/json" \
#   -d '{"query": "What is AI?", "top_k": 5}'

# Agent Query:
# curl -X POST http://localhost:8000/agent/query \
#   -H "Content-Type: application/json" \
#   -d '{"query": "Tell me about machine learning"}'
