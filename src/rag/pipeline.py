"""
RAG retrieval and generation pipeline
"""
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .embeddings import EmbeddingManager, VectorDatabase
from .document_processor import DocumentChunker, DocumentLoader


class RAGPipeline:
    """End-to-end RAG pipeline"""
    
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        vector_db_path: str = "./data/embeddings",
        llm_model: str = "gpt-3.5-turbo",
        openai_api_key: Optional[str] = None
    ):
        """Initialize RAG pipeline components"""
        self.embedding_manager = EmbeddingManager(model_name=embedding_model)
        self.vector_db = VectorDatabase(db_path=vector_db_path)
        self.document_chunker = DocumentChunker()
        self.document_loader = DocumentLoader()
        
        # LLM for generation
        if openai_api_key:
            self.llm = ChatOpenAI(
                model=llm_model,
                api_key=openai_api_key,
                temperature=0.7
            )
        else:
            self.llm = ChatOpenAI(model=llm_model, temperature=0.7)
        
        # RAG prompt template
        self.rag_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful assistant. Use the following context to answer the question.
If you don't know the answer, say so.

Context:
{context}

Question: {question}

Answer:"""
        )
    
    def ingest_document(self, file_path: str, metadata: Dict = None) -> int:
        """
        Load document, chunk it, embed it, and add to vector DB
        
        Args:
            file_path: Path to document file
            metadata: Optional metadata for document
            
        Returns:
            Number of chunks added
        """
        # Load document
        text = self.document_loader.load_document(file_path)
        
        # Chunk document
        chunks = self.document_chunker.chunk_text(
            text,
            metadata={
                **(metadata or {}),
                "source": file_path
            }
        )
        
        # Generate embeddings
        chunk_texts = [chunk["content"] for chunk in chunks]
        embeddings = self.embedding_manager.embed_texts(chunk_texts)
        
        # Add to vector database
        self.vector_db.add_documents(chunks, embeddings)
        
        return len(chunks)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant documents for query
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with scores
        """
        # Embed query
        query_embedding = self.embedding_manager.embed_single(query)
        
        # Search vector database
        results = self.vector_db.search(query_embedding, top_k=top_k)
        
        return results
    
    def generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using LLM with context
        
        Args:
            question: User question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        prompt = self.rag_prompt.format(context=context, question=question)
        response = self.llm.invoke(prompt)
        return response.content
    
    def query(self, question: str, top_k: int = 5) -> Dict:
        """
        Full RAG query pipeline: retrieve + generate
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with answer and retrieved documents
        """
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(question, top_k=top_k)
        
        # Prepare context
        context = "\n\n".join([
            f"[{doc['metadata'].get('source', 'Unknown')}]\n{doc['content']}"
            for doc in retrieved_docs
        ])
        
        # Generate answer
        answer = self.generate_answer(question, context)
        
        return {
            "question": question,
            "answer": answer,
            "retrieved_documents": retrieved_docs,
            "context": context
        }
