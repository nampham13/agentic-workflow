"""
Generator Agent

Đề xuất candidate molecules (SMILES strings).
Sử dụng rule-based mutations đơn giản.
"""

import random
from typing import Any, Dict, List
from app.agents.base import Agent


class GeneratorAgent(Agent):
    """
    Agent sinh ra candidate molecules.
    
    Chiến lược:
        - Round đầu: generate base molecules
        - Round sau: mutate từ top molecules round trước
    """
    
    # Base SMILES để bắt đầu (drug-like molecules)
    BASE_MOLECULES = [
        "CC(C)Cc1ccc(cc1)C(C)C(O)=O",  # Ibuprofen
        "CC(=O)Oc1ccccc1C(O)=O",  # Aspirin
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
        "c1ccc(cc1)C(=O)O",  # Benzoic acid
        "c1ccccc1",  # Benzene (simple start)
        "CC(C)NCC(COc1ccccc1)O",  # Propranolol-like
        "Cc1ccc(cc1)S(=O)(=O)N",  # Sulfonamide-like
        "CCN(CC)CCNC(=O)c1cc(ccc1OC)N",  # Procainamide-like
    ]
    
    # Simple mutations
    MUTATIONS = [
        ("C", "CC"),  # Add methyl
        ("c1ccccc1", "c1cc(C)ccc1"),  # Add methyl to benzene
        ("C(=O)O", "C(=O)OC"),  # Methylate carboxylic acid
        ("N", "NC"),  # Methylate nitrogen
        ("c1ccccc1", "c1ccc(O)cc1"),  # Add hydroxyl to benzene
    ]
    
    def __init__(self, name: str = "generator"):
        super().__init__(name)
        self.seed_molecules = None
    
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate candidate molecules.
        
        Args:
            context:
                - n_candidates: số molecules cần generate
                - round_num: round hiện tại
                - seed_molecules: molecules từ round trước (nếu có)
                
        Returns:
            Dictionary chứa danh sách SMILES
        """
        n_candidates = context.get("n_candidates", 50)
        round_num = context.get("round_num", 1)
        seed_molecules = context.get("seed_molecules", [])
        
        if round_num == 1 or not seed_molecules:
            # Round đầu: dùng base molecules
            candidates = self._generate_base_candidates(n_candidates)
        else:
            # Round sau: mutate từ seeds
            candidates = self._generate_mutated_candidates(seed_molecules, n_candidates)
        
        return {
            "candidates": candidates,
            "agent": self.name,
            "round": round_num
        }
    
    def _generate_base_candidates(self, n: int) -> List[str]:
        """Generate candidates từ base molecules."""
        candidates = []
        max_attempts = n * 5  # Prevent infinite loop
        attempts = 0
        
        while len(candidates) < n and attempts < max_attempts:
            attempts += 1
            # Lấy random base molecule
            base = random.choice(self.BASE_MOLECULES)
            if base not in candidates:
                candidates.append(base)
            
            # Thêm variants
            if len(candidates) < n:
                variant = self._apply_random_mutation(base)
                if variant and variant not in candidates:
                    candidates.append(variant)
        
        # If still not enough, duplicate to reach n
        while len(candidates) < n:
            candidates.append(random.choice(self.BASE_MOLECULES))
        
        return candidates[:n]
    
    def _generate_mutated_candidates(self, seeds: List[str], n: int) -> List[str]:
        """Generate candidates bằng cách mutate seed molecules."""
        candidates = []
        
        # Keep seeds first
        candidates.extend(seeds[:min(len(seeds), n)])
        
        # Generate mutations with attempt limit
        max_attempts = n * 3
        attempts = 0
        
        while len(candidates) < n and attempts < max_attempts:
            attempts += 1
            seed = random.choice(seeds)
            mutated = self._apply_random_mutation(seed)
            
            # Allow duplicates if we're struggling to generate unique ones
            if mutated and (mutated not in candidates or attempts > n * 2):
                candidates.append(mutated)
                if len(candidates) >= n:
                    break
        
        # Fill remaining with base molecules if needed
        base_idx = 0
        while len(candidates) < n:
            candidates.append(self.BASE_MOLECULES[base_idx % len(self.BASE_MOLECULES)])
            base_idx += 1
        
        return candidates[:n]
    
    def _apply_random_mutation(self, smiles: str) -> str:
        """Apply random mutation to SMILES."""
        try:
            # Random mutation
            old, new = random.choice(self.MUTATIONS)
            if old in smiles:
                return smiles.replace(old, new, 1)
            return smiles
        except Exception:
            return smiles
