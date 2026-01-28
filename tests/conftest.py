"""
Test configuration for evaluation
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluation import EvaluationDataset


def create_test_evaluation_dataset():
    """Create sample evaluation dataset"""
    dataset = EvaluationDataset()
    
    # Add test cases
    dataset.add_test_case(
        query="What is machine learning?",
        gold_response="Machine learning is a type of artificial intelligence",
        gold_docs=["Machine Learning is a subset of AI"],
        expected_tools=["knowledge_base_search"]
    )
    
    dataset.add_test_case(
        query="What is 2 + 2?",
        gold_response="The answer is 4",
        expected_tools=["calculator"]
    )
    
    dataset.add_test_case(
        query="Tell me about RAG",
        gold_response="RAG combines retrieval and generation",
        gold_docs=["RAG is a technique that combines retrieval and generation"],
        expected_tools=["knowledge_base_search"]
    )
    
    return dataset


if __name__ == "__main__":
    dataset = create_test_evaluation_dataset()
    dataset.save("evaluation_dataset.json")
    print(f"Created evaluation dataset with {len(dataset)} test cases")
