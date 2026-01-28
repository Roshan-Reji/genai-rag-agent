"""
API models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class RAGQueryRequest(BaseModel):
    """Request model for RAG query"""
    query: str = Field(..., description="Query text")
    top_k: int = Field(default=5, description="Number of documents to retrieve")


class RAGQueryResponse(BaseModel):
    """Response model for RAG query"""
    query: str
    answer: str
    retrieved_documents: List[Dict]
    context: str


class DocumentIngestionRequest(BaseModel):
    """Request model for document ingestion"""
    file_path: str = Field(..., description="Path to document file")
    metadata: Optional[Dict] = Field(default=None, description="Optional metadata")


class DocumentIngestionResponse(BaseModel):
    """Response model for document ingestion"""
    success: bool
    chunks_added: int
    file_path: str


class AgentQueryRequest(BaseModel):
    """Request model for agent query"""
    query: str = Field(..., description="Query for agent")
    verbose: bool = Field(default=False, description="Enable verbose output")


class AgentQueryResponse(BaseModel):
    """Response model for agent query"""
    query: str
    response: str
    iterations: int
    success: bool
    trace: Optional[Dict] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    components: Dict[str, str]


class EvaluationRequest(BaseModel):
    """Request model for evaluation"""
    eval_type: str = Field(..., description="Type of evaluation: 'retrieval', 'agent', or 'both'")
    dataset_path: Optional[str] = Field(default=None, description="Path to evaluation dataset")


class EvaluationResponse(BaseModel):
    """Response model for evaluation"""
    status: str
    results: Dict[str, Any]
    report: Optional[Dict] = None
