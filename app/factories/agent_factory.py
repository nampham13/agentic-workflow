"""
Agent Factory

Tạo agents theo Factory Pattern.
"""

from app.agents.base import Agent
from app.agents.planner import PlannerAgent
from app.agents.generator import GeneratorAgent
from app.agents.ranker import RankerAgent
from typing import Dict, Any


class AgentFactory:
    """
    Factory để tạo agents.
    
    Đảm bảo pipeline không phụ thuộc vào concrete implementations.
    Agents có thể được swap mà không cần thay đổi pipeline code.
    """
    
    @staticmethod
    def create_planner(**kwargs) -> Agent:
        """
        Tạo Planner Agent.
        
        Args:
            **kwargs: Parameters cho PlannerAgent (rounds, top_k, etc.)
            
        Returns:
            PlannerAgent instance
        """
        return PlannerAgent(**kwargs)
    
    @staticmethod
    def create_generator(**kwargs) -> Agent:
        """
        Tạo Generator Agent.
        
        Args:
            **kwargs: Parameters cho GeneratorAgent
            
        Returns:
            GeneratorAgent instance
        """
        return GeneratorAgent(**kwargs)
    
    @staticmethod
    def create_ranker(**kwargs) -> Agent:
        """
        Tạo Ranker Agent.
        
        Args:
            **kwargs: Parameters cho RankerAgent
            
        Returns:
            RankerAgent instance
        """
        return RankerAgent(**kwargs)
    
    @staticmethod
    def create_agent(agent_type: str, **kwargs) -> Agent:
        """
        Generic factory method.
        
        Args:
            agent_type: "planner", "generator", hoặc "ranker"
            **kwargs: Parameters cho agent
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: Nếu agent_type không hợp lệ
        """
        factories = {
            "planner": AgentFactory.create_planner,
            "generator": AgentFactory.create_generator,
            "ranker": AgentFactory.create_ranker
        }
        
        factory = factories.get(agent_type)
        if not factory:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return factory(**kwargs)
