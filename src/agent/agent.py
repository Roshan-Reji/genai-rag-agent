"""
AI Agent implementation with tool calling and state management
"""
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from .tools import ToolRegistry, ToolResult


class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    RUNNING = "running"
    THINKING = "thinking"
    TOOL_CALLING = "tool_calling"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class Message:
    """Agent message"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tool_calls: List[Dict] = field(default_factory=list)


@dataclass
class ExecutionTrace:
    """Trace of agent execution"""
    query: str
    steps: List[Dict] = field(default_factory=list)
    tool_calls: List[Dict] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    total_tokens: int = 0
    execution_time: float = 0.0
    status: str = "pending"


class AIAgent:
    """Main AI Agent with tool calling and state management"""
    
    def __init__(
        self,
        name: str = "GenAI Agent",
        llm_model: str = "gpt-3.5-turbo",
        openai_api_key: Optional[str] = None,
        tool_registry: Optional[ToolRegistry] = None,
        max_iterations: int = 10
    ):
        """Initialize AI Agent"""
        self.name = name
        self.max_iterations = max_iterations
        
        # LLM setup
        if openai_api_key:
            self.llm = ChatOpenAI(
                model=llm_model,
                api_key=openai_api_key,
                temperature=0.7
            )
        else:
            self.llm = ChatOpenAI(model=llm_model, temperature=0.7)
        
        # Tool setup
        self.tool_registry = tool_registry or ToolRegistry()
        
        # State management
        self.state = AgentState.IDLE
        self.conversation_history: List[Message] = []
        self.current_trace: Optional[ExecutionTrace] = None
        
        # System prompt
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with tool descriptions"""
        tool_descriptions = self.tool_registry.get_tool_descriptions()
        
        return f"""You are a helpful AI assistant called {self.name}.
You have access to the following tools:

{tool_descriptions}

When you need to use a tool, respond with a JSON object like this:
{{"tool": "tool_name", "args": {{"arg1": "value1", "arg2": "value2"}}}}

Always be helpful, accurate, and honest. If you don't know something, say so."""
    
    def _parse_tool_call(self, response: str) -> Optional[Dict]:
        """Parse tool calls from LLM response"""
        try:
            # Look for JSON pattern
            if "{" in response and "tool" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        return None
    
    def _should_use_tool(self, response: str) -> bool:
        """Check if response indicates tool usage"""
        return "{" in response and "tool" in response
    
    def execute_query(self, query: str, verbose: bool = False) -> Dict:
        """
        Execute query through agent loop
        
        Args:
            query: User query
            verbose: Print execution steps
            
        Returns:
            Final response and execution trace
        """
        import time
        start_time = time.time()
        
        self.state = AgentState.RUNNING
        self.current_trace = ExecutionTrace(query=query)
        self.conversation_history = []
        
        # Add user message
        user_msg = Message(role="user", content=query)
        self.conversation_history.append(user_msg)
        self.current_trace.messages.append(user_msg)
        
        final_response = None
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            if verbose:
                print(f"\n--- Iteration {iteration} ---")
            
            self.state = AgentState.THINKING
            
            # Prepare context
            messages_str = self._format_conversation_history()
            
            # Get LLM response
            self.state = AgentState.GENERATING
            llm_response = self.llm.invoke(messages_str)
            response_text = llm_response.content
            
            if verbose:
                print(f"Agent: {response_text[:200]}...")
            
            # Check for tool calls
            if self._should_use_tool(response_text):
                self.state = AgentState.TOOL_CALLING
                tool_call = self._parse_tool_call(response_text)
                
                if tool_call and verbose:
                    print(f"Tool call: {tool_call['tool']}({tool_call.get('args', {})})")
                
                if tool_call:
                    # Execute tool
                    tool_result = self.tool_registry.execute_tool(
                        tool_call["tool"],
                        **tool_call.get("args", {})
                    )
                    
                    # Record tool call
                    tool_call_record = {
                        "iteration": iteration,
                        "tool": tool_call["tool"],
                        "args": tool_call.get("args", {}),
                        "result": asdict(tool_result) if tool_result else None
                    }
                    self.current_trace.tool_calls.append(tool_call_record)
                    
                    # Add assistant and tool response to history
                    assistant_msg = Message(
                        role="assistant",
                        content=response_text,
                        tool_calls=[tool_call]
                    )
                    self.conversation_history.append(assistant_msg)
                    
                    tool_response = f"Tool executed: {tool_call['tool']}\nResult: {json.dumps(tool_result.output)}"
                    tool_msg = Message(role="system", content=tool_response)
                    self.conversation_history.append(tool_msg)
                    
                    continue
            
            # No tool call - this is the final response
            assistant_msg = Message(role="assistant", content=response_text)
            self.conversation_history.append(assistant_msg)
            final_response = response_text
            self.state = AgentState.COMPLETED
            break
        
        # Prepare output
        execution_time = time.time() - start_time
        self.current_trace.status = "completed" if final_response else "error"
        self.current_trace.execution_time = execution_time
        
        return {
            "query": query,
            "response": final_response or "Failed to generate response",
            "trace": asdict(self.current_trace),
            "iterations": iteration,
            "success": final_response is not None
        }
    
    def _format_conversation_history(self) -> str:
        """Format conversation history for LLM"""
        formatted = self.system_prompt + "\n\n"
        
        for msg in self.conversation_history:
            formatted += f"{msg.role.upper()}: {msg.content}\n"
        
        formatted += "ASSISTANT: "
        return formatted
