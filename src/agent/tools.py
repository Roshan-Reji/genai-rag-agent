"""
Tool definitions for AI agent
"""
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime
import json


class ToolResult(BaseModel):
    """Result from tool execution"""
    success: bool
    output: Any
    error: str = None


class SearchToolInput(BaseModel):
    """Input for RAG search tool"""
    query: str = Field(description="Search query")
    top_k: int = Field(default=5, description="Number of results to return")


class CalculatorToolInput(BaseModel):
    """Input for calculator tool"""
    expression: str = Field(description="Mathematical expression")


class KnowledgeBaseTool:
    """Search knowledge base using RAG"""
    
    def __init__(self, rag_pipeline):
        self.rag = rag_pipeline
        self.name = "knowledge_base_search"
        self.description = "Search the knowledge base for relevant information"
    
    def execute(self, query: str, top_k: int = 5) -> ToolResult:
        """Execute knowledge base search"""
        try:
            results = self.rag.retrieve(query, top_k=top_k)
            return ToolResult(
                success=True,
                output={
                    "query": query,
                    "results": results,
                    "count": len(results)
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=str(e)
            )


class CalculatorTool:
    """Simple calculator tool"""
    
    def __init__(self):
        self.name = "calculator"
        self.description = "Perform mathematical calculations"
    
    def execute(self, expression: str) -> ToolResult:
        """Execute calculator"""
        try:
            # Simple eval with allowed names
            result = eval(expression, {"__builtins__": {}}, {"abs": abs, "round": round})
            return ToolResult(
                success=True,
                output={
                    "expression": expression,
                    "result": result
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=f"Calculation error: {str(e)}"
            )


class WebSearchTool:
    """Web search simulation tool"""
    
    def __init__(self):
        self.name = "web_search"
        self.description = "Search the web for information"
    
    def execute(self, query: str) -> ToolResult:
        """Execute web search (simulated)"""
        try:
            # In real implementation, use actual web search API
            result = {
                "query": query,
                "results": [
                    {
                        "title": f"Result 1 for '{query}'",
                        "snippet": "This is a simulated search result.",
                        "url": "https://example.com/result1"
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }
            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=str(e)
            )


class ToolRegistry:
    """Registry and executor for agent tools"""
    
    def __init__(self, rag_pipeline=None):
        self.tools = {}
        self._register_default_tools(rag_pipeline)
    
    def _register_default_tools(self, rag_pipeline):
        """Register default tools"""
        if rag_pipeline:
            self.register(KnowledgeBaseTool(rag_pipeline))
        self.register(CalculatorTool())
        self.register(WebSearchTool())
    
    def register(self, tool) -> None:
        """Register a tool"""
        self.tools[tool.name] = tool
    
    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a registered tool"""
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                output=None,
                error=f"Tool '{tool_name}' not found"
            )
        
        tool = self.tools[tool_name]
        return tool.execute(**kwargs)
    
    def get_tool_descriptions(self) -> str:
        """Get descriptions of all tools"""
        descriptions = []
        for name, tool in self.tools.items():
            descriptions.append(f"- {name}: {tool.description}")
        return "\n".join(descriptions)
    
    def list_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tools.keys())
