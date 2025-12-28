"""
Screening Rules

Rule-based evaluation và scoring logic.
"""

from typing import Dict, Any, List


class MoleculeScreening:
    """
    Rule-based screening cho molecules.
    
    Rules:
        - Lipinski-like constraints
        - TPSA constraint
        - Configurable max_violations
        
    Scoring:
        score = QED - penalty * violations
    """
    
    # Lipinski Rule of Five + TPSA
    RULES = {
        "mw": {"max": 500, "name": "Molecular Weight <= 500"},
        "logp": {"max": 5, "name": "LogP <= 5"},
        "hbd": {"max": 5, "name": "H-Bond Donors <= 5"},
        "hba": {"max": 10, "name": "H-Bond Acceptors <= 10"},
        "tpsa": {"max": 140, "name": "TPSA <= 140"}
    }
    
    def __init__(self, max_violations: int = 1):
        """
        Args:
            max_violations: Số violations tối đa cho phép
        """
        self.max_violations = max_violations
    
    def screen(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Screen molecule dựa trên properties.
        
        Args:
            properties: Dictionary chứa MW, LogP, HBD, HBA, TPSA, etc.
            
        Returns:
            Dictionary chứa:
                - passed: bool
                - violations: int
                - violated_rules: List[str]
        """
        violations = []
        
        # Check từng rule
        for prop, rule in self.RULES.items():
            value = properties.get(prop)
            if value is None:
                continue
            
            max_val = rule.get("max")
            if max_val and value > max_val:
                violations.append(rule["name"])
        
        n_violations = len(violations)
        passed = n_violations <= self.max_violations
        
        return {
            "passed": passed,
            "violations": n_violations,
            "violated_rules": violations
        }
    
    def score(
        self,
        properties: Dict[str, Any],
        screening_result: Dict[str, Any],
        penalty: float = 0.1
    ) -> float:
        """
        Calculate score cho molecule.
        
        Formula: score = QED - penalty * violations
        
        Args:
            properties: Molecular properties
            screening_result: Screening result
            penalty: Penalty per violation
            
        Returns:
            Numeric score
        """
        qed = properties.get("qed", 0.0)
        violations = screening_result.get("violations", 0)
        
        score = qed - (penalty * violations)
        return round(score, 4)
    
    def evaluate_molecule(
        self,
        properties: Dict[str, Any],
        penalty: float = 0.1
    ) -> Dict[str, Any]:
        """
        Complete evaluation: screening + scoring.
        
        Args:
            properties: Molecular properties
            penalty: Scoring penalty
            
        Returns:
            Dictionary với screening_result và score
        """
        screening_result = self.screen(properties)
        score = self.score(properties, screening_result, penalty)
        
        return {
            "screening_result": screening_result,
            "score": score
        }
