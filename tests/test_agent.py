"""
Unit tests for AI Agent
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.tools import ToolRegistry, CalculatorTool
from src.agent.agent import AIAgent, AgentState


class TestToolRegistry:
    """Test tool registry"""
    
    def setup_method(self):
        self.registry = ToolRegistry()
    
    def test_tool_registration(self):
        """Test tool registration"""
        tools = self.registry.list_tools()
        assert len(tools) > 0
    
    def test_calculator_tool(self):
        """Test calculator tool"""
        calc = CalculatorTool()
        result = calc.execute("2 + 2")
        
        assert result.success
        assert result.output["result"] == 4
    
    def test_invalid_calculator_expression(self):
        """Test invalid calculator expression"""
        calc = CalculatorTool()
        result = calc.execute("invalid + expression")
        
        assert not result.success


class TestAgentState:
    """Test agent state management"""
    
    def test_agent_states(self):
        """Test agent state enum"""
        assert AgentState.IDLE.value == "idle"
        assert AgentState.RUNNING.value == "running"
        assert AgentState.COMPLETED.value == "completed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
