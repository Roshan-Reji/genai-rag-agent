"""
Document processing and chunking utilities for RAG pipeline
"""
import re
from typing import List, Dict
from pathlib import Path


class DocumentChunker:
    """Handles document chunking with semantic awareness"""
    
    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with metadata
        
        Args:
            text: Text to chunk
            metadata: Additional metadata for chunks
            
        Returns:
            List of chunk dictionaries with content and metadata
        """
        # Clean text
        text = self._clean_text(text)
        
        # Try semantic chunking first (split by paragraphs/sentences)
        chunks = self._semantic_split(text)
        
        # If chunks are too large, split further
        chunks = self._size_split(chunks)
        
        # Add metadata
        chunk_list = []
        for i, chunk in enumerate(chunks):
            chunk_dict = {
                "content": chunk,
                "chunk_id": i,
                "metadata": metadata or {},
                "length": len(chunk.split())
            }
            chunk_list.append(chunk_dict)
        
        return chunk_list
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text)
        return text.strip()
    
    def _semantic_split(self, text: str) -> List[str]:
        """Split text by semantic boundaries (paragraphs, sentences)"""
        # Split by paragraphs first (double newlines)
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < self.chunk_size:
                current_chunk += " " + para
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _size_split(self, chunks: List[str]) -> List[str]:
        """Split chunks that are too large"""
        result = []
        
        for chunk in chunks:
            words = chunk.split()
            
            if len(words) <= self.chunk_size:
                result.append(chunk)
            else:
                # Split by word count
                sub_chunks = []
                current = []
                
                for word in words:
                    current.append(word)
                    if len(current) >= self.chunk_size:
                        sub_chunks.append(' '.join(current))
                        # Add overlap
                        current = current[-self.chunk_overlap:]
                
                if current:
                    sub_chunks.append(' '.join(current))
                
                result.extend(sub_chunks)
        
        return result


class DocumentLoader:
    """Load documents from various formats"""
    
    @staticmethod
    def load_text_file(file_path: str) -> str:
        """Load text from .txt file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Error loading text file: {str(e)}")
    
    @staticmethod
    def load_pdf(file_path: str) -> str:
        """Load text from PDF file"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            raise ValueError(f"Error loading PDF file: {str(e)}")
    
    @staticmethod
    def load_docx(file_path: str) -> str:
        """Load text from .docx file"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error loading DOCX file: {str(e)}")
    
    @classmethod
    def load_document(cls, file_path: str) -> str:
        """Load document automatically based on file type"""
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == '.txt':
            return cls.load_text_file(file_path)
        elif suffix == '.pdf':
            return cls.load_pdf(file_path)
        elif suffix == '.docx':
            return cls.load_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
