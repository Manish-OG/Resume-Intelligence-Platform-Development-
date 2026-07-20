import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.backend.main import app
from src.database.db import get_db
from src.database.models import Base

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


def _get_test_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    TestClient wired to an isolated in-memory DB (not data/app.db) and an
    UPLOAD_DIR redirected to pytest's tmp_path (not the real data/uploads/).
    """
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = _get_test_db
    monkeypatch.setattr("app.backend.api.routes.UPLOAD_DIR", tmp_path)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
