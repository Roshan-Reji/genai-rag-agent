"""
Vector database and embedding management for RAG pipeline
"""
from typing import List, Dict, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings


class EmbeddingManager:
    """Handles text embeddings using sentence-transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding model
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for texts
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings
        """
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings
    
    def embed_single(self, text: str) -> np.ndarray:
        """Embed a single text"""
        return self.embed_texts([text])[0]


class VectorDatabase:
    """Vector database operations using Chroma"""
    
    def __init__(self, db_path: str = "./data/embeddings", collection_name: str = "rag_documents"):
        """
        Initialize vector database
        
        Args:
            db_path: Path to persist database
            collection_name: Name of collection
        """
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Initialize Chroma client
        settings = ChromaSettings(
            chroma_db_impl='duckdb+parquet',
            persist_directory=db_path,
            anonymized_telemetry=False
        )
        self.client = chromadb.Client(settings)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, documents: List[Dict], embeddings: np.ndarray) -> None:
        """
        Add documents with embeddings to database
        
        Args:
            documents: List of document dictionaries with 'content' and 'metadata'
            embeddings: Numpy array of embeddings
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        ids = [f"doc_{i}" for i in range(len(documents))]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        documents_text = [doc["content"] for doc in documents]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents_text,
            metadatas=metadatas
        )
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of matching documents with scores
        """
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        documents = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                score = results['distances'][0][i] if results['distances'] else 0
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                
                documents.append({
                    "content": doc,
                    "score": float(score),
                    "metadata": metadata
                })
        
        return documents
    
    def delete_all(self) -> None:
        """Delete all documents from collection"""
        self.collection.delete(where={})
    
    def count(self) -> int:
        """Get number of documents in collection"""
        return self.collection.count()
