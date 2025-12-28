"""
API Routes cho Runs

Endpoints:
    POST   /runs              - Tạo run mới
    GET    /runs/{id}/status  - Get run status
    GET    /runs/{id}/results - Get run results
    GET    /runs/{id}/trace   - Get run trace
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.schemas.api import (
    RunCreateRequest,
    RunCreateResponse,
    RunStatusResponse,
    RunResultsResponse,
    MoleculeResponse,
    RunTraceResponse,
    TraceEventResponse
)
from app.db.session import get_db
from app.db.models import Run, Molecule, TraceEvent
from app.runner.pipeline import AgenticPipeline

router = APIRouter(prefix="/runs", tags=["runs"])


def run_pipeline_background(run_id: str, parameters: dict):
    """Background task để chạy pipeline."""
    pipeline = AgenticPipeline()
    pipeline.run(run_id, parameters)


@router.post("", response_model=RunCreateResponse, status_code=202)
async def create_run(
    request: RunCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Tạo run mới và start async execution.
    
    Returns:
        202 Accepted với run_id
    """
    # Create run in database
    run = Run(
        rounds=request.rounds,
        candidates_per_round=request.candidates_per_round,
        top_k=request.top_k,
        max_violations=request.max_violations,
        scoring_penalty=request.scoring_penalty,
        status="queued"
    )
    
    db.add(run)
    db.commit()
    db.refresh(run)
    
    # Start pipeline in background
    parameters = {
        "rounds": request.rounds,
        "candidates_per_round": request.candidates_per_round,
        "top_k": request.top_k,
        "max_violations": request.max_violations,
        "scoring_penalty": request.scoring_penalty
    }
    
    background_tasks.add_task(run_pipeline_background, run.id, parameters)
    
    return RunCreateResponse(
        run_id=run.id,
        status=run.status,
        message="Run created and queued for execution"
    )


@router.get("/{run_id}/status", response_model=RunStatusResponse)
async def get_run_status(run_id: str, db: Session = Depends(get_db)):
    """
    Get run status.
    
    Args:
        run_id: Run ID
        
    Returns:
        RunStatusResponse
    """
    run = db.query(Run).filter(Run.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return RunStatusResponse(
        run_id=run.id,
        status=run.status,
        created_at=run.created_at,
        started_at=run.started_at,
        completed_at=run.completed_at,
        error_message=run.error_message,
        current_round=run.current_round,
        progress_message=run.progress_message,
        rounds=run.rounds,
        candidates_per_round=run.candidates_per_round,
        top_k=run.top_k,
        max_violations=run.max_violations,
        scoring_penalty=run.scoring_penalty
    )


@router.get("/{run_id}/results", response_model=RunResultsResponse)
async def get_run_results(run_id: str, db: Session = Depends(get_db)):
    """
    Get run results.
    
    Args:
        run_id: Run ID
        
    Returns:
        RunResultsResponse với ranked molecules
    """
    run = db.query(Run).filter(Run.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    if run.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Run is not completed. Current status: {run.status}"
        )
    
    # Get molecules, ordered by rank
    molecules = db.query(Molecule).filter(
        Molecule.run_id == run_id
    ).order_by(Molecule.rank).all()
    
    molecule_responses = [
        MoleculeResponse(
            smiles=m.smiles,
            valid=m.valid,
            round=m.round,
            properties=m.properties,
            screening_result=m.screening_result,
            score=m.score,
            rank=m.rank
        )
        for m in molecules
    ]
    
    # Get top molecules
    top_molecules = [m for m in molecule_responses if m.rank and m.rank <= run.top_k]
    
    return RunResultsResponse(
        run_id=run.id,
        status=run.status,
        molecules=molecule_responses,
        total_molecules=len(molecule_responses),
        top_molecules=top_molecules
    )


@router.get("/{run_id}/trace", response_model=RunTraceResponse)
async def get_run_trace(run_id: str, db: Session = Depends(get_db)):
    """
    Get run trace events.
    
    Args:
        run_id: Run ID
        
    Returns:
        RunTraceResponse với trace events
    """
    run = db.query(Run).filter(Run.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Get trace events, ordered by timestamp
    events = db.query(TraceEvent).filter(
        TraceEvent.run_id == run_id
    ).order_by(TraceEvent.timestamp).all()
    
    event_responses = [
        TraceEventResponse(
            actor=e.actor,
            action=e.action,
            round=e.round,
            timestamp=e.timestamp,
            metadata=e.event_metadata
        )
        for e in events
    ]
    
    return RunTraceResponse(
        run_id=run.id,
        events=event_responses,
        total_events=len(event_responses)
    )
