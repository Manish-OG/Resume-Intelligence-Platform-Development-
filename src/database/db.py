from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.backend.config import DATABASE_URL
from src.database.models import Base

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    return SessionLocal()
