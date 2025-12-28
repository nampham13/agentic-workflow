"""
Base Agent Interface

Định nghĩa abstract contract cho tất cả agents trong hệ thống.
Mọi agent phải implement method act() để đảm bảo consistency.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class Agent(ABC):
    """Abstract base class cho tất cả agents."""
    
    def __init__(self, name: str):
        """
        Args:
            name: Tên định danh của agent
        """
        self.name = name
    
    @abstractmethod
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thực hiện hành động dựa trên context.
        
        Args:
            context: Dictionary chứa thông tin cần thiết cho agent
            
        Returns:
            Dictionary chứa kết quả của action
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
