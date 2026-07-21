import pytest
from sqlalchemy.exc import IntegrityError

from src.database.models import Candidate, Feedback, Job, Resume, Score
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


def test_score_unique_constraint_prevents_duplicate_job_resume_pair(client):
    # Proves the (job_id, resume_id) UniqueConstraint on Score is a
    # real DB-level guarantee, not just declared and never checked —
    # bypasses the /rank route's application-level upsert logic
    # entirely and inserts two raw Score rows directly.
    db = TestSessionLocal()
    try:
        job = Job(title="Backend Engineer", description="Looking for a backend engineer")
        candidate = Candidate(name="Jane Doe", email=None)
        db.add(job)
        db.add(candidate)
        db.flush()

        resume = Resume(candidate_id=candidate.id, file_name="r.pdf", raw_text="text")
        db.add(resume)
        db.flush()

        db.add(
            Score(
                job_id=job.id,
                resume_id=resume.id,
                semantic_score=0.1,
                skill_score=0.1,
                experience_score=0.1,
                education_score=0.1,
                final_score=0.1,
            )
        )
        db.commit()

        db.add(
            Score(
                job_id=job.id,
                resume_id=resume.id,
                semantic_score=0.2,
                skill_score=0.2,
                experience_score=0.2,
                education_score=0.2,
                final_score=0.2,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()


def test_feedback_score_id_unique_constraint_prevents_duplicate(client):
    # Proves Feedback.score_id's unique=True is a real DB-level
    # guarantee, not just declared — bypasses the /rank route's
    # application-level upsert logic entirely and inserts two raw
    # Feedback rows referencing the same Score.
    db = TestSessionLocal()
    try:
        job = Job(title="Backend Engineer", description="Looking for a backend engineer")
        candidate = Candidate(name="Jane Doe", email=None)
        db.add(job)
        db.add(candidate)
        db.flush()

        resume = Resume(candidate_id=candidate.id, file_name="r.pdf", raw_text="text")
        db.add(resume)
        db.flush()

        score = Score(
            job_id=job.id,
            resume_id=resume.id,
            semantic_score=0.1,
            skill_score=0.1,
            experience_score=0.1,
            education_score=0.1,
            final_score=0.1,
        )
        db.add(score)
        db.flush()

        db.add(
            Feedback(
                score_id=score.id,
                strengths="",
                weaknesses="",
                missing_skills=None,
                recommendation="first",
            )
        )
        db.commit()

        db.add(
            Feedback(
                score_id=score.id,
                strengths="",
                weaknesses="",
                missing_skills=None,
                recommendation="second",
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()
