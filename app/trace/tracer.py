"""
Structured Trace Logger

Logs agent và tool actions cho observability và auditability.
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime


class Tracer:
    """
    Structured trace logger.
    
    Mỗi action được log với:
        - actor: agent/tool name
        - action: mô tả hành động
        - timestamp: thời điểm
        - run_id: ID của run
        - round: round number (nếu có)
        - metadata: additional data
    """
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
    
    def log(
        self,
        actor: str,
        action: str,
        run_id: str,
        round_num: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log một trace event.
        
        Args:
            actor: Tên của actor (agent/tool)
            action: Mô tả action
            run_id: Run ID
            round_num: Round number (optional)
            metadata: Additional data (optional)
        """
        event = {
            "actor": actor,
            "action": action,
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "round": round_num,
            "metadata": metadata or {}
        }
        
        self.events.append(event)
    
    def get_events(self, run_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lấy trace events.
        
        Args:
            run_id: Filter by run_id (optional)
            
        Returns:
            List of trace events
        """
        if run_id:
            return [e for e in self.events if e["run_id"] == run_id]
        return self.events
    
    def clear(self, run_id: Optional[str] = None) -> None:
        """
        Clear events.
        
        Args:
            run_id: Clear events cho specific run (optional)
        """
        if run_id:
            self.events = [e for e in self.events if e["run_id"] != run_id]
        else:
            self.events = []
    
    def log_agent_action(
        self,
        agent_name: str,
        action: str,
        run_id: str,
        round_num: Optional[int] = None,
        result: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Helper method để log agent action.
        
        Args:
            agent_name: Tên agent
            action: Action description
            run_id: Run ID
            round_num: Round number
            result: Agent result data
        """
        metadata = {"result_keys": list(result.keys())} if result else {}
        self.log(
            actor=agent_name,
            action=action,
            run_id=run_id,
            round_num=round_num,
            metadata=metadata
        )
    
    def log_tool_action(
        self,
        tool_name: str,
        action: str,
        run_id: str,
        round_num: Optional[int] = None,
        count: Optional[int] = None
    ) -> None:
        """
        Helper method để log tool action.
        
        Args:
            tool_name: Tên tool
            action: Action description
            run_id: Run ID
            round_num: Round number
            count: Item count (e.g., số molecules processed)
        """
        metadata = {"count": count} if count is not None else {}
        self.log(
            actor=tool_name,
            action=action,
            run_id=run_id,
            round_num=round_num,
            metadata=metadata
        )


# Global tracer instance
_global_tracer = Tracer()


def get_tracer() -> Tracer:
    """Get global tracer instance."""
    return _global_tracer
