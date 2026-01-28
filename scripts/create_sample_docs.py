"""
Sample documents for RAG testing
"""

SAMPLE_DOCUMENTS = {
    "ai_basics.txt": """
Artificial Intelligence Fundamentals

Introduction to AI
Artificial Intelligence (AI) is the simulation of human intelligence processes by computer systems.
These processes include learning, reasoning, and self-correction. AI has become increasingly important
in modern technology and society.

Machine Learning
Machine Learning (ML) is a subset of AI that enables systems to learn and improve from experience
without being explicitly programmed. ML algorithms build mathematical models based on sample data,
known as training data, to make predictions or decisions without following explicit instructions.

Deep Learning
Deep Learning is a subset of machine learning based on artificial neural networks with multiple layers.
The term "deep" refers to the multiple layers in the neural network. Deep learning models have been 
successful in areas such as computer vision, natural language processing, and speech recognition.

Natural Language Processing
Natural Language Processing (NLP) is a subfield of linguistics, computer science, and artificial 
intelligence concerned with the interactions between computers and human language. NLP helps computers
understand, interpret, and generate human language in a meaningful and useful way.
""",
    
    "rag_guide.txt": """
Retrieval-Augmented Generation (RAG)

What is RAG?
RAG is a technique that combines retrieval and generation to enhance the capabilities of language models.
It works by first retrieving relevant documents from a knowledge base, then using these documents as
context to generate more accurate and informed responses.

How RAG Works
1. Query Processing: The user's query is processed and converted into embeddings
2. Document Retrieval: Similar documents are retrieved from the vector database
3. Context Creation: Retrieved documents are combined to create context
4. Generation: The language model generates a response using the context

Benefits of RAG
- Reduces hallucinations by grounding responses in real data
- Enables access to up-to-date information
- Allows easy updates to knowledge without retraining models
- Improves factual accuracy of responses

RAG Applications
- Question Answering Systems
- Document Summarization
- Knowledge-based Chatbots
- Research Assistants
- Customer Support Systems
""",
    
    "agent_framework.txt": """
AI Agents and Autonomous Systems

Introduction to Agents
An AI agent is a software entity that perceives its environment through sensors and acts upon that
environment through actuators. Agents operate autonomously to achieve their designed goals.

Agent Architectures
There are several common agent architectures:

Reactive Agents: Respond immediately to environmental stimuli without internal state
Deliberative Agents: Use internal models to plan and reason about actions
Hybrid Agents: Combine reactive and deliberative approaches

Agent Communication
Multi-agent systems require agents to communicate and coordinate:
- Message passing: Direct communication between agents
- Publish-subscribe: Agents publish and subscribe to events
- Shared data structures: Agents access common knowledge bases

Agent Tools and Capabilities
Agents can be equipped with tools to accomplish their goals:
- Information retrieval tools
- Calculation and data processing tools
- External API integration
- Decision-making frameworks

Agent Evaluation
Agents should be evaluated on:
- Task success rate
- Response time and efficiency
- Resource utilization
- Learning and improvement over time
""",
}


def create_sample_documents(output_dir: str = "./data/documents"):
    """Create sample documents in the specified directory"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    for filename, content in SAMPLE_DOCUMENTS.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Created: {filepath}")
    
    return list(SAMPLE_DOCUMENTS.keys())


if __name__ == "__main__":
    files = create_sample_documents()
    print(f"\nCreated {len(files)} sample documents")
