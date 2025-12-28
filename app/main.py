"""
FastAPI Application Entry Point

Creates FastAPI app, includes routers, initializes database.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import runs
from app.db.session import init_db

# Create FastAPI app
app = FastAPI(
    title="Life AI Agentic - Molecule Generation & Screening",
    description="Agentic backend system for molecule generation and screening using RDKit",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(runs.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Life AI Agentic - Molecule Generation & Screening API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
