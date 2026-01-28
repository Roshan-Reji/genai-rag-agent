"""
Configuration settings for RAG GenAI Application
"""
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # LLM Configuration
    llm_model: str = "gpt-4"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    max_tokens: int = 2048
    temperature: float = 0.7
    
    # Embedding Configuration
    embedding_model: str = "text-embedding-3-small"
    
    # RAG Configuration
    chunk_size: int = 1024
    chunk_overlap: int = 200
    top_k_retrieval: int = 5
    similarity_threshold: float = 0.7
    vector_db_path: str = "./data/embeddings"
    
    # Database Configuration
    database_url: str = "sqlite:///./rag.db"
    
    # Agent Configuration
    agent_timeout: int = 30
    max_retries: int = 3
    agent_log_level: str = "INFO"
    
    # Evaluation Configuration
    evaluation_batch_size: int = 10
    similarity_metric: str = "cosine"
    
    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
