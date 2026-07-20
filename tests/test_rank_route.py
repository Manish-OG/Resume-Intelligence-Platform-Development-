from src.database.models import Job
from tests.conftest import TestSessionLocal


def test_rank_nonexistent_job_returns_404(client):
    response = client.post("/rank", params={"job_id": 999})

    assert response.status_code == 404


def test_rank_no_resumes_returns_empty_list(client):
    db = TestSessionLocal()
    try:
        job = Job(title="Backend Engineer", description="Looking for a backend engineer")
        db.add(job)
        db.commit()
        job_id = job.id
    finally:
        db.close()

    response = client.post("/rank", params={"job_id": job_id})

    assert response.status_code == 200
    body = response.json()
    assert body["job_id"] == job_id
    assert body["candidates"] == []
