"""
Ranker Agent

Scores, sorts và selects top candidate molecules.
"""

from typing import Any, Dict, List
from app.agents.base import Agent


class RankerAgent(Agent):
    """
    Agent chịu trách nhiệm scoring và ranking molecules.
    
    Input:
        - molecules: danh sách molecules với properties và screening results
        - scoring_penalty: penalty cho violations
        - top_k: số molecules top cần chọn
        
    Output:
        - ranked_molecules: danh sách molecules đã được sort theo score
        - top_molecules: top_k molecules tốt nhất
    """
    
    def __init__(self, name: str = "ranker"):
        super().__init__(name)
    
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rank và select top molecules.
        
        Args:
            context:
                - molecules: List[Dict] với properties và screening_result
                - scoring_penalty: float
                - top_k: int
                
        Returns:
            Dictionary với ranked và top molecules
        """
        molecules = context.get("molecules", [])
        scoring_penalty = context.get("scoring_penalty", 0.1)
        top_k = context.get("top_k", 5)
        
        # Calculate scores
        scored_molecules = []
        for mol in molecules:
            score = self._calculate_score(mol, scoring_penalty)
            mol_copy = mol.copy()
            mol_copy["score"] = score
            scored_molecules.append(mol_copy)
        
        # Sort by score (descending)
        ranked = sorted(scored_molecules, key=lambda x: x["score"], reverse=True)
        
        # Select top_k
        top_molecules = ranked[:top_k]
        
        return {
            "ranked_molecules": ranked,
            "top_molecules": top_molecules,
            "agent": self.name,
            "n_ranked": len(ranked),
            "n_top": len(top_molecules)
        }
    
    def _calculate_score(self, molecule: Dict[str, Any], penalty: float) -> float:
        """
        Calculate score cho molecule.
        
        Formula: score = QED - penalty * violations
        
        Args:
            molecule: Dictionary chứa properties và screening_result
            penalty: penalty per violation
            
        Returns:
            float score
        """
        qed = molecule.get("properties", {}).get("qed", 0.0)
        violations = molecule.get("screening_result", {}).get("violations", 0)
        
        score = qed - (penalty * violations)
        return round(score, 4)
