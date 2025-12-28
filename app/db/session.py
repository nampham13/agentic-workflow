"""
Database Session Management

SQLAlchemy session setup và lifecycle.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.models import Base
import os

# Database URL (SQLite by default)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./life_ai_agentic.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True để log SQL queries
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize database.
    
    Tạo tất cả tables nếu chưa tồn tại.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Get database session.
    
    Sử dụng như dependency trong FastAPI:
        def endpoint(db: Session = Depends(get_db)):
            ...
    
    Yields:
        SQLAlchemy Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get database session (non-generator version).
    
    Sử dụng trong background tasks.
    MUST close manually sau khi dùng xong.
    
    Returns:
        SQLAlchemy Session
    """
    return SessionLocal()
