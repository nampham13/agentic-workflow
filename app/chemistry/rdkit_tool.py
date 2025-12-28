"""
RDKit Chemistry Tool

Single source of truth cho chemistry operations.
Validates SMILES và computes molecular properties.
"""

from typing import Dict, Any, Optional
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, QED
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


class RDKitTool:
    """
    Wrapper cho RDKit operations.
    
    Responsibilities:
        - Validate và sanitize SMILES
        - Compute molecular properties:
          * MW (Molecular Weight)
          * LogP (Lipophilicity)
          * HBD (Hydrogen Bond Donors)
          * HBA (Hydrogen Bond Acceptors)
          * TPSA (Topological Polar Surface Area)
          * RotB (Rotatable Bonds)
          * QED (Quantitative Estimate of Drug-likeness)
    """
    
    def __init__(self):
        if not RDKIT_AVAILABLE:
            raise ImportError(
                "RDKit is not installed. "
                "Install with: pip install rdkit"
            )
    
    def validate_smiles(self, smiles: str) -> bool:
        """
        Validate SMILES string.
        
        Args:
            smiles: SMILES string
            
        Returns:
            True nếu valid, False nếu invalid
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            return mol is not None
        except Exception:
            return False
    
    def compute_properties(self, smiles: str) -> Optional[Dict[str, Any]]:
        """
        Compute molecular properties từ SMILES.
        
        Args:
            smiles: SMILES string
            
        Returns:
            Dictionary chứa properties, hoặc None nếu invalid
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None
            
            # Sanitize molecule
            Chem.SanitizeMol(mol)
            
            # Compute properties
            properties = {
                "mw": round(Descriptors.MolWt(mol), 2),
                "logp": round(Descriptors.MolLogP(mol), 2),
                "hbd": Descriptors.NumHDonors(mol),
                "hba": Descriptors.NumHAcceptors(mol),
                "tpsa": round(Descriptors.TPSA(mol), 2),
                "rotatable_bonds": Descriptors.NumRotatableBonds(mol),
                "qed": round(QED.qed(mol), 4)
            }
            
            return properties
            
        except Exception as e:
            # Log error và return None
            print(f"Error computing properties for {smiles}: {e}")
            return None
    
    def process_molecule(self, smiles: str) -> Dict[str, Any]:
        """
        Validate và compute properties trong một call.
        
        Args:
            smiles: SMILES string
            
        Returns:
            Dictionary chứa validation status và properties
        """
        result = {
            "smiles": smiles,
            "valid": False,
            "properties": None,
            "error": None
        }
        
        # Validate
        if not self.validate_smiles(smiles):
            result["error"] = "Invalid SMILES"
            return result
        
        result["valid"] = True
        
        # Compute properties
        properties = self.compute_properties(smiles)
        if properties is None:
            result["error"] = "Failed to compute properties"
            result["valid"] = False
            return result
        
        result["properties"] = properties
        return result
