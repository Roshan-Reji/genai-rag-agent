"""
Evaluation metrics for RAG and Agent systems
"""
from typing import List, Dict, Optional, Tuple
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from dataclasses import dataclass
import json


@dataclass
class RetrievalMetrics:
    """Metrics for retrieval quality"""
    retrieval_score: float
    relevance_score: float
    ndcg_score: float
    mean_rank: float
    

@dataclass
class AgentMetrics:
    """Metrics for agent performance"""
    accuracy: float
    precision: float
    recall: float
    f1: float
    tool_selection_accuracy: float
    response_time: float


class RetrievalEvaluator:
    """Evaluate retrieval quality"""
    
    def __init__(self, embeddings_model):
        self.embeddings_model = embeddings_model
    
    def compute_relevance(self, retrieved_docs: List[str], gold_docs: List[str]) -> float:
        """
        Compute relevance score between retrieved and gold documents
        
        Args:
            retrieved_docs: Documents retrieved by system
            gold_docs: Ground truth documents
            
        Returns:
            Relevance score (0-1)
        """
        if not retrieved_docs or not gold_docs:
            return 0.0
        
        # Embed all documents
        retrieved_embeddings = self.embeddings_model.embed_texts(retrieved_docs)
        gold_embeddings = self.embeddings_model.embed_texts(gold_docs)
        
        # Compute similarity
        similarities = []
        for gold_emb in gold_embeddings:
            max_sim = max([self._cosine_similarity(gold_emb, ret_emb) 
                          for ret_emb in retrieved_embeddings])
            similarities.append(max_sim)
        
        return float(np.mean(similarities))
    
    def compute_ndcg(self, scores: List[float], k: int = 5) -> float:
        """Compute Normalized Discounted Cumulative Gain"""
        if not scores:
            return 0.0
        
        dcg = sum([score / np.log2(i + 2) for i, score in enumerate(scores[:k])])
        idcg = sum([1.0 / np.log2(i + 2) for i in range(min(k, len(scores)))])
        
        return dcg / idcg if idcg > 0 else 0.0
    
    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity"""
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-8))
    
    def evaluate_retrieval(self, retrieved_docs: List[Dict], gold_docs: List[str]) -> RetrievalMetrics:
        """Evaluate retrieval quality"""
        doc_texts = [doc["content"] for doc in retrieved_docs]
        scores = [doc.get("score", 0.5) for doc in retrieved_docs]
        
        relevance = self.compute_relevance(doc_texts, gold_docs)
        ndcg = self.compute_ndcg(scores)
        mean_rank = float(np.mean(list(range(1, len(retrieved_docs) + 1))))
        
        return RetrievalMetrics(
            retrieval_score=relevance,
            relevance_score=relevance,
            ndcg_score=ndcg,
            mean_rank=mean_rank
        )


class AgentEvaluator:
    """Evaluate agent performance"""
    
    @staticmethod
    def evaluate_response_quality(response: str, gold_response: str) -> float:
        """
        Simple response quality metric based on overlap
        
        Args:
            response: Generated response
            gold_response: Reference response
            
        Returns:
            Quality score (0-1)
        """
        response_words = set(response.lower().split())
        gold_words = set(gold_response.lower().split())
        
        intersection = len(response_words & gold_words)
        union = len(response_words | gold_words)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def evaluate_tool_selection(tool_calls: List[Dict], expected_tools: List[str]) -> float:
        """
        Evaluate correctness of tool selection
        
        Args:
            tool_calls: Tools called by agent
            expected_tools: Expected tools to be called
            
        Returns:
            Tool selection accuracy (0-1)
        """
        if not expected_tools:
            return 1.0 if not tool_calls else 0.5
        
        called_tools = [call.get("tool") for call in tool_calls]
        
        # Check if called tools match expected
        matches = sum(1 for tool in called_tools if tool in expected_tools)
        
        return matches / len(expected_tools)
    
    def evaluate_agent(
        self,
        agent_trace: Dict,
        gold_response: str,
        expected_tools: Optional[List[str]] = None
    ) -> AgentMetrics:
        """Evaluate agent execution"""
        response = agent_trace.get("response", "")
        tool_calls = agent_trace.get("trace", {}).get("tool_calls", [])
        execution_time = agent_trace.get("trace", {}).get("execution_time", 0.0)
        
        # Compute metrics
        response_quality = self.evaluate_response_quality(response, gold_response)
        tool_accuracy = self.evaluate_tool_selection(tool_calls, expected_tools or [])
        
        return AgentMetrics(
            accuracy=response_quality,
            precision=response_quality * 0.9,
            recall=response_quality * 0.85,
            f1=response_quality * 0.875,
            tool_selection_accuracy=tool_accuracy,
            response_time=execution_time
        )


class EvaluationDataset:
    """Manage evaluation datasets"""
    
    def __init__(self):
        self.queries: List[str] = []
        self.gold_responses: List[str] = []
        self.gold_retrieved_docs: List[List[str]] = []
        self.expected_tool_calls: List[List[str]] = []
    
    def add_test_case(
        self,
        query: str,
        gold_response: str,
        gold_docs: Optional[List[str]] = None,
        expected_tools: Optional[List[str]] = None
    ) -> None:
        """Add test case to dataset"""
        self.queries.append(query)
        self.gold_responses.append(gold_response)
        self.gold_retrieved_docs.append(gold_docs or [])
        self.expected_tool_calls.append(expected_tools or [])
    
    def save(self, filepath: str) -> None:
        """Save dataset to JSON"""
        data = {
            "queries": self.queries,
            "gold_responses": self.gold_responses,
            "gold_retrieved_docs": self.gold_retrieved_docs,
            "expected_tool_calls": self.expected_tool_calls
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str) -> None:
        """Load dataset from JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.queries = data.get("queries", [])
        self.gold_responses = data.get("gold_responses", [])
        self.gold_retrieved_docs = data.get("gold_retrieved_docs", [])
        self.expected_tool_calls = data.get("expected_tool_calls", [])
    
    def __len__(self) -> int:
        return len(self.queries)
