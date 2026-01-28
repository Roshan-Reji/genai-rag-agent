"""
Evaluation framework and benchmark runner
"""
from typing import Dict, List, Optional
import json
import time
from dataclasses import asdict
from .metrics import (
    RetrievalEvaluator, 
    AgentEvaluator, 
    EvaluationDataset,
    RetrievalMetrics,
    AgentMetrics
)


class BenchmarkRunner:
    """Run comprehensive benchmarks on RAG and Agent systems"""
    
    def __init__(
        self,
        rag_pipeline=None,
        agent=None,
        embeddings_model=None
    ):
        self.rag_pipeline = rag_pipeline
        self.agent = agent
        self.retrieval_evaluator = RetrievalEvaluator(embeddings_model) if embeddings_model else None
        self.agent_evaluator = AgentEvaluator()
        self.dataset = EvaluationDataset()
        self.results = {
            "retrieval_results": [],
            "agent_results": [],
            "summary": {}
        }
    
    def benchmark_retrieval(self) -> Dict:
        """Benchmark retrieval quality"""
        if not self.rag_pipeline or not self.dataset or len(self.dataset) == 0:
            return {"error": "RAG pipeline or dataset not available"}
        
        retrieval_scores = []
        
        for i, query in enumerate(self.dataset.queries):
            retrieved_docs = self.rag_pipeline.retrieve(query, top_k=5)
            gold_docs = self.dataset.gold_retrieved_docs[i]
            
            metrics = self.retrieval_evaluator.evaluate_retrieval(retrieved_docs, gold_docs)
            self.results["retrieval_results"].append(asdict(metrics))
            retrieval_scores.append(metrics.relevance_score)
        
        # Compute summary statistics
        if retrieval_scores:
            summary = {
                "avg_relevance": sum(retrieval_scores) / len(retrieval_scores),
                "max_relevance": max(retrieval_scores),
                "min_relevance": min(retrieval_scores),
                "total_queries": len(retrieval_scores)
            }
            self.results["summary"]["retrieval"] = summary
            return summary
        
        return {}
    
    def benchmark_agent(self) -> Dict:
        """Benchmark agent performance"""
        if not self.agent or not self.dataset or len(self.dataset) == 0:
            return {"error": "Agent or dataset not available"}
        
        agent_scores = {"accuracy": [], "tool_accuracy": [], "response_time": []}
        
        for i, query in enumerate(self.dataset.queries):
            start_time = time.time()
            result = self.agent.execute_query(query, verbose=False)
            execution_time = time.time() - start_time
            
            gold_response = self.dataset.gold_responses[i]
            expected_tools = self.dataset.expected_tool_calls[i]
            
            metrics = self.agent_evaluator.evaluate_agent(
                result,
                gold_response,
                expected_tools
            )
            
            self.results["agent_results"].append(asdict(metrics))
            agent_scores["accuracy"].append(metrics.accuracy)
            agent_scores["tool_accuracy"].append(metrics.tool_selection_accuracy)
            agent_scores["response_time"].append(execution_time)
        
        # Compute summary
        summary = {
            "avg_accuracy": sum(agent_scores["accuracy"]) / len(agent_scores["accuracy"]),
            "avg_tool_accuracy": sum(agent_scores["tool_accuracy"]) / len(agent_scores["tool_accuracy"]),
            "avg_response_time": sum(agent_scores["response_time"]) / len(agent_scores["response_time"]),
            "total_queries": len(agent_scores["accuracy"])
        }
        self.results["summary"]["agent"] = summary
        return summary
    
    def generate_report(self) -> Dict:
        """Generate evaluation report"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "retrieval": self.results["summary"].get("retrieval", {}),
            "agent": self.results["summary"].get("agent", {}),
            "total_results": {
                "retrieval_tests": len(self.results["retrieval_results"]),
                "agent_tests": len(self.results["agent_results"])
            }
        }
        return report
    
    def save_results(self, filepath: str) -> None:
        """Save evaluation results to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def save_report(self, filepath: str) -> None:
        """Save evaluation report"""
        report = self.generate_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)


class EvaluationDashboard:
    """Generate evaluation dashboard data"""
    
    def __init__(self, benchmark_runner: BenchmarkRunner):
        self.runner = benchmark_runner
    
    def get_dashboard_data(self) -> Dict:
        """Get data for evaluation dashboard"""
        return {
            "retrieval_metrics": {
                "summary": self.runner.results["summary"].get("retrieval", {}),
                "details": self.runner.results["retrieval_results"]
            },
            "agent_metrics": {
                "summary": self.runner.results["summary"].get("agent", {}),
                "details": self.runner.results["agent_results"]
            },
            "report": self.runner.generate_report()
        }
    
    def print_summary(self) -> None:
        """Print evaluation summary"""
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        
        retrieval = self.runner.results["summary"].get("retrieval", {})
        if retrieval:
            print("\nRETRIEVAL METRICS:")
            print(f"  Average Relevance: {retrieval.get('avg_relevance', 0):.4f}")
            print(f"  Max Relevance: {retrieval.get('max_relevance', 0):.4f}")
            print(f"  Total Queries: {retrieval.get('total_queries', 0)}")
        
        agent = self.runner.results["summary"].get("agent", {})
        if agent:
            print("\nAGENT METRICS:")
            print(f"  Average Accuracy: {agent.get('avg_accuracy', 0):.4f}")
            print(f"  Tool Accuracy: {agent.get('avg_tool_accuracy', 0):.4f}")
            print(f"  Avg Response Time: {agent.get('avg_response_time', 0):.2f}s")
            print(f"  Total Queries: {agent.get('total_queries', 0)}")
        
        print("\n" + "="*60)
