"""
Main entry point for running the application
"""
import os
import sys
import logging

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_settings
from src.rag import RAGPipeline
from src.agent import AIAgent, ToolRegistry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main application entry point"""
    logger.info("Starting GenAI RAG + Agent System")
    
    settings = get_settings()
    
    try:
        # Initialize RAG Pipeline
        logger.info("Initializing RAG Pipeline...")
        rag_pipeline = RAGPipeline(
            embedding_model=settings.embedding_model,
            vector_db_path=settings.vector_db_path,
            llm_model=settings.llm_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Ingest sample documents
        docs_dir = "data/documents"
        if os.path.exists(docs_dir):
            logger.info(f"Ingesting documents from {docs_dir}...")
            for doc_file in os.listdir(docs_dir):
                if doc_file.endswith(('.txt', '.pdf', '.docx')):
                    doc_path = os.path.join(docs_dir, doc_file)
                    chunks = rag_pipeline.ingest_document(doc_path)
                    logger.info(f"Ingested {doc_file}: {chunks} chunks")
        
        # Initialize Agent
        logger.info("Initializing AI Agent...")
        tool_registry = ToolRegistry(rag_pipeline=rag_pipeline)
        agent = AIAgent(
            name="GenAI Assistant",
            llm_model=settings.llm_model,
            openai_api_key=settings.openai_api_key,
            tool_registry=tool_registry,
            max_iterations=10
        )
        
        # Interactive loop
        logger.info("Agent ready. Type 'exit' to quit.\n")
        
        while True:
            try:
                query = input("\n🤖 You: ").strip()
                if query.lower() in ['exit', 'quit', 'q']:
                    logger.info("Shutting down...")
                    break
                
                if not query:
                    continue
                
                # Execute agent query
                result = agent.execute_query(query, verbose=True)
                
                print(f"\n✅ Agent: {result['response']}")
                print(f"📊 Iterations: {result['iterations']}")
                
            except KeyboardInterrupt:
                logger.info("Interrupted by user")
                break
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
