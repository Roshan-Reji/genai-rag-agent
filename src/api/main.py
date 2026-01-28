"""
FastAPI application for GenAI RAG + Agent system
"""
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from typing import Optional

from config import get_settings
from src.rag import RAGPipeline
from src.agent import AIAgent, ToolRegistry
from src.evaluation import BenchmarkRunner, EvaluationDashboard, EvaluationDataset
from .models import (
    RAGQueryRequest, RAGQueryResponse,
    DocumentIngestionRequest, DocumentIngestionResponse,
    AgentQueryRequest, AgentQueryResponse,
    HealthResponse,
    EvaluationRequest, EvaluationResponse
)


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
settings = get_settings()
rag_pipeline = None
agent = None
benchmark_runner = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    global rag_pipeline, agent, benchmark_runner
    
    # Startup
    logger.info("Initializing GenAI RAG Agent System...")
    
    try:
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline(
            embedding_model=settings.embedding_model,
            vector_db_path=settings.vector_db_path,
            llm_model=settings.llm_model,
            openai_api_key=settings.openai_api_key
        )
        logger.info("RAG pipeline initialized")
        
        # Initialize agent with tools
        tool_registry = ToolRegistry(rag_pipeline=rag_pipeline)
        agent = AIAgent(
            name="GenAI Assistant",
            llm_model=settings.llm_model,
            openai_api_key=settings.openai_api_key,
            tool_registry=tool_registry,
            max_iterations=10
        )
        logger.info("AI Agent initialized")
        
        # Initialize benchmark runner
        benchmark_runner = BenchmarkRunner(
            rag_pipeline=rag_pipeline,
            agent=agent,
            embeddings_model=rag_pipeline.embedding_manager
        )
        logger.info("Benchmark runner initialized")
        
    except Exception as e:
        logger.error(f"Initialization error: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down GenAI RAG Agent System...")


# Create FastAPI app
app = FastAPI(
    title="GenAI RAG + Agent System",
    description="Comprehensive Generative AI application with RAG, Agents, and Evaluation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Health Check ====================
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    components = {
        "rag_pipeline": "initialized" if rag_pipeline else "not initialized",
        "agent": "initialized" if agent else "not initialized",
        "benchmark_runner": "initialized" if benchmark_runner else "not initialized"
    }
    
    all_ok = all(v == "initialized" for v in components.values())
    
    return HealthResponse(
        status="healthy" if all_ok else "degraded",
        components=components
    )


# ==================== RAG Endpoints ====================
@app.post("/rag/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest):
    """Query RAG pipeline"""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        result = rag_pipeline.query(request.query, top_k=request.top_k)
        return RAGQueryResponse(**result)
    except Exception as e:
        logger.error(f"RAG query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/ingest", response_model=DocumentIngestionResponse)
async def ingest_document(request: DocumentIngestionRequest):
    """Ingest document into RAG pipeline"""
    if not rag_pipeline:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        if not os.path.exists(request.file_path):
            raise ValueError(f"File not found: {request.file_path}")
        
        chunks_added = rag_pipeline.ingest_document(
            request.file_path,
            metadata=request.metadata
        )
        
        return DocumentIngestionResponse(
            success=True,
            chunks_added=chunks_added,
            file_path=request.file_path
        )
    except Exception as e:
        logger.error(f"Document ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Agent Endpoints ====================
@app.post("/agent/query", response_model=AgentQueryResponse)
async def agent_query(request: AgentQueryRequest):
    """Query AI Agent"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        result = agent.execute_query(request.query, verbose=request.verbose)
        return AgentQueryResponse(**result)
    except Exception as e:
        logger.error(f"Agent query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/tools")
async def get_agent_tools():
    """Get available agent tools"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "tools": agent.tool_registry.list_tools(),
        "descriptions": agent.tool_registry.get_tool_descriptions()
    }


# ==================== Evaluation Endpoints ====================
@app.post("/evaluation/run", response_model=EvaluationResponse)
async def run_evaluation(request: EvaluationRequest):
    """Run evaluation"""
    if not benchmark_runner:
        raise HTTPException(status_code=503, detail="Benchmark runner not initialized")
    
    try:
        # Load dataset if provided
        if request.dataset_path:
            if not os.path.exists(request.dataset_path):
                raise ValueError(f"Dataset not found: {request.dataset_path}")
            benchmark_runner.dataset.load(request.dataset_path)
        
        # Run evaluation
        if request.eval_type == "retrieval":
            results = benchmark_runner.benchmark_retrieval()
        elif request.eval_type == "agent":
            results = benchmark_runner.benchmark_agent()
        elif request.eval_type == "both":
            results = {
                "retrieval": benchmark_runner.benchmark_retrieval(),
                "agent": benchmark_runner.benchmark_agent()
            }
        else:
            raise ValueError(f"Unknown eval_type: {request.eval_type}")
        
        report = benchmark_runner.generate_report()
        
        return EvaluationResponse(
            status="completed",
            results=results,
            report=report
        )
    except Exception as e:
        logger.error(f"Evaluation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evaluation/dashboard")
async def get_evaluation_dashboard():
    """Get evaluation dashboard"""
    if not benchmark_runner:
        raise HTTPException(status_code=503, detail="Benchmark runner not initialized")
    
    try:
        dashboard = EvaluationDashboard(benchmark_runner)
        return dashboard.get_dashboard_data()
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== System Endpoints ====================
@app.get("/system/config")
async def get_system_config():
    """Get system configuration"""
    return {
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "top_k_retrieval": settings.top_k_retrieval,
        "max_tokens": settings.max_tokens
    }


@app.post("/system/reset")
async def reset_system():
    """Reset system (clear all data)"""
    global rag_pipeline
    
    try:
        if rag_pipeline:
            rag_pipeline.vector_db.delete_all()
        return {"status": "success", "message": "System reset complete"}
    except Exception as e:
        logger.error(f"Reset error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        debug=settings.debug
    )
