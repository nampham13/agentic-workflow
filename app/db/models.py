"""
Database Models

SQLAlchemy models cho Run, Molecule, và TraceEvent.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid() -> str:
    """Generate UUID string."""
    return str(uuid.uuid4())


class Run(Base):
    """
    Model cho Run.
    
    Lưu trữ:
        - Run ID
        - Status (queued, running, completed, failed)
        - Parameters
        - Timestamps
    """
    __tablename__ = "runs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    status = Column(String, default="queued", nullable=False)
    
    # Run parameters
    rounds = Column(Integer, default=3)
    candidates_per_round = Column(Integer, default=50)
    top_k = Column(Integer, default=5)
    max_violations = Column(Integer, default=1)
    scoring_penalty = Column(Float, default=0.1)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Error message nếu failed
    error_message = Column(Text, nullable=True)
    
    # Progress tracking
    current_round = Column(Integer, default=0)
    progress_message = Column(String, nullable=True)
    
    # Relationships
    molecules = relationship("Molecule", back_populates="run", cascade="all, delete-orphan")
    trace_events = relationship("TraceEvent", back_populates="run", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Run(id='{self.id}', status='{self.status}')>"


class Molecule(Base):
    """
    Model cho Molecule.
    
    Lưu trữ:
        - SMILES
        - Properties (MW, LogP, etc.)
        - Screening results
        - Score
        - Rank
    """
    __tablename__ = "molecules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    
    smiles = Column(String, nullable=False)
    valid = Column(Boolean, default=True)
    
    # Round info
    round = Column(Integer, nullable=False)
    
    # Molecular properties (JSON)
    properties = Column(JSON, nullable=True)
    
    # Screening results (JSON)
    screening_result = Column(JSON, nullable=True)
    
    # Score và rank
    score = Column(Float, nullable=True)
    rank = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    run = relationship("Run", back_populates="molecules")
    
    def __repr__(self):
        return f"<Molecule(smiles='{self.smiles}', score={self.score}, rank={self.rank})>"


class TraceEvent(Base):
    """
    Model cho TraceEvent.
    
    Lưu trữ audit trail của agent và tool actions.
    """
    __tablename__ = "trace_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    
    actor = Column(String, nullable=False)  # agent/tool name
    action = Column(Text, nullable=False)  # action description
    round = Column(Integer, nullable=True)  # round number
    
    event_metadata = Column(JSON, nullable=True)  # additional data
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    run = relationship("Run", back_populates="trace_events")
    
    def __repr__(self):
        return f"<TraceEvent(actor='{self.actor}', action='{self.action}')>"
