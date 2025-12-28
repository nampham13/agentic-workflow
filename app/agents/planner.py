"""
Planner Agent

Định nghĩa chiến lược và tham số cho run.
Không chứa chemistry logic, chỉ quyết định strategy.
"""

from typing import Any, Dict
from app.agents.base import Agent


class PlannerAgent(Agent):
    """
    Agent chịu trách nhiệm lập kế hoạch cho run.
    
    Output:
        - rounds: số vòng chạy
        - candidates_per_round: số molecules mỗi vòng
        - top_k: số molecules top được chọn
        - max_violations: số violations tối đa cho phép
        - scoring_penalty: penalty cho mỗi violation
    """
    
    def __init__(
        self,
        name: str = "planner",
        rounds: int = 3,
        candidates_per_round: int = 50,
        top_k: int = 5,
        max_violations: int = 1,
        scoring_penalty: float = 0.1
    ):
        super().__init__(name)
        self.rounds = rounds
        self.candidates_per_round = candidates_per_round
        self.top_k = top_k
        self.max_violations = max_violations
        self.scoring_penalty = scoring_penalty
    
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tạo plan cho run.
        
        Args:
            context: Có thể chứa user_preferences hoặc override parameters
            
        Returns:
            Dictionary chứa run plan
        """
        # Có thể override từ context nếu user cung cấp
        plan = {
            "rounds": context.get("rounds", self.rounds),
            "candidates_per_round": context.get("candidates_per_round", self.candidates_per_round),
            "top_k": context.get("top_k", self.top_k),
            "max_violations": context.get("max_violations", self.max_violations),
            "scoring_penalty": context.get("scoring_penalty", self.scoring_penalty),
            "agent": self.name
        }
        
        return plan
