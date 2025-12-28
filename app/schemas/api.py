"""
API Schemas

Pydantic models cho request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# Request schemas
class RunCreateRequest(BaseModel):
    """Request để tạo run mới."""
    rounds: Optional[int] = Field(default=3, ge=1, le=10)
    candidates_per_round: Optional[int] = Field(default=50, ge=10, le=200)
    top_k: Optional[int] = Field(default=5, ge=1, le=20)
    max_violations: Optional[int] = Field(default=1, ge=0, le=5)
    scoring_penalty: Optional[float] = Field(default=0.1, ge=0.0, le=1.0)


# Response schemas
class RunStatusResponse(BaseModel):
    """Response cho run status."""
    run_id: str
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    current_round: Optional[int] = None
    progress_message: Optional[str] = None
    rounds: Optional[int] = None
    candidates_per_round: Optional[int] = None
    top_k: Optional[int] = None
    max_violations: Optional[int] = None
    scoring_penalty: Optional[float] = None
    
    class Config:
        from_attributes = True


class MoleculeResponse(BaseModel):
    """Response cho molecule."""
    smiles: str
    valid: bool
    round: int
    properties: Optional[Dict[str, Any]]
    screening_result: Optional[Dict[str, Any]]
    score: Optional[float]
    rank: Optional[int]
    
    class Config:
        from_attributes = True


class RunResultsResponse(BaseModel):
    """Response cho run results."""
    run_id: str
    status: str
    molecules: List[MoleculeResponse]
    total_molecules: int
    top_molecules: List[MoleculeResponse]
    
    class Config:
        from_attributes = True


class TraceEventResponse(BaseModel):
    """Response cho trace event."""
    actor: str
    action: str
    round: Optional[int]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class RunTraceResponse(BaseModel):
    """Response cho run trace."""
    run_id: str
    events: List[TraceEventResponse]
    total_events: int
    
    class Config:
        from_attributes = True


class RunCreateResponse(BaseModel):
    """Response khi tạo run."""
    run_id: str
    status: str
    message: str
