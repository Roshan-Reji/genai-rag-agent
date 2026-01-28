"""
Unit tests for RAG pipeline
"""
import pytest
import os
import tempfile
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.document_processor import DocumentChunker, DocumentLoader
from src.rag.embeddings import EmbeddingManager, VectorDatabase


class TestDocumentChunker:
    """Test document chunking"""
    
    def setup_method(self):
        self.chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    
    def test_chunk_text(self):
        """Test text chunking"""
        text = "This is a test. " * 50  # Create long text
        chunks = self.chunker.chunk_text(text, metadata={"source": "test"})
        
        assert len(chunks) > 0
        assert all("content" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)
    
    def test_empty_text(self):
        """Test chunking empty text"""
        chunks = self.chunker.chunk_text("")
        assert len(chunks) == 0 or chunks[0]["content"] == ""


class TestEmbeddingManager:
    """Test embedding generation"""
    
    def setup_method(self):
        self.embeddings = EmbeddingManager(model_name="all-MiniLM-L6-v2")
    
    def test_embed_single_text(self):
        """Test embedding a single text"""
        text = "This is a test document"
        embedding = self.embeddings.embed_single(text)
        
        assert embedding is not None
        assert len(embedding) > 0
    
    def test_embed_multiple_texts(self):
        """Test embedding multiple texts"""
        texts = [
            "This is the first document",
            "This is the second document",
            "This is the third document"
        ]
        embeddings = self.embeddings.embed_texts(texts)
        
        assert len(embeddings) == len(texts)


class TestVectorDatabase:
    """Test vector database operations"""
    
    def setup_method(self):
        # Use temporary directory for test
        self.temp_dir = tempfile.mkdtemp()
        self.db = VectorDatabase(db_path=self.temp_dir, collection_name="test")
    
    def teardown_method(self):
        # Clean up
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_add_documents(self):
        """Test adding documents to database"""
        import numpy as np
        
        documents = [
            {"content": "Document 1", "metadata": {"source": "test1"}},
            {"content": "Document 2", "metadata": {"source": "test2"}}
        ]
        embeddings = np.random.rand(2, 384).astype(np.float32)
        
        self.db.add_documents(documents, embeddings)
        assert self.db.count() == 2
    
    def test_search(self):
        """Test searching documents"""
        import numpy as np
        
        documents = [
            {"content": "Hello world", "metadata": {"source": "test"}},
            {"content": "Hello universe", "metadata": {"source": "test"}}
        ]
        embeddings = np.random.rand(2, 384).astype(np.float32)
        
        self.db.add_documents(documents, embeddings)
        
        query_embedding = embeddings[0]
        results = self.db.search(query_embedding, top_k=1)
        
        assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
