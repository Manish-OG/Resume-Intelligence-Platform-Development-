import csv
import io

from src.database.models import Candidate, Job, Resume, Score
from tests.conftest import TestSessionLocal


def test_download_nonexistent_job_returns_404(client):
    response = client.get("/download", params={"job_id": 999})

    assert response.status_code == 404


def test_download_invalid_fmt_returns_422(client):
    db = TestSessionLocal()
    try:
        job = Job(title="Backend Engineer", description="Looking for a backend engineer")
        db.add(job)
        db.commit()
        job_id = job.id
    finally:
        db.close()

    response = client.get("/download", params={"job_id": job_id, "fmt": "xlsx"})

    assert response.status_code == 422


def test_download_existing_job_never_ranked_returns_header_only_csv(client):
    db = TestSessionLocal()
    try:
        job = Job(title="Backend Engineer", description="Looking for a backend engineer")
        db.add(job)
        db.commit()
        job_id = job.id
    finally:
        db.close()

    response = client.get("/download", params={"job_id": job_id})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"] == (
        f'attachment; filename="results_job_{job_id}.csv"'
    )
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert rows == []


def _job_with_scored_candidates(scores: list[tuple[str, float]]) -> int:
    db = TestSessionLocal()
    try:
        job = Job(title="Backend Engineer", description="Looking for a backend engineer")
        db.add(job)
        db.flush()

        for name, final_score in scores:
            candidate = Candidate(name=name, email=None)
            db.add(candidate)
            db.flush()

            resume = Resume(candidate_id=candidate.id, file_name="r.pdf", raw_text="text")
            db.add(resume)
            db.flush()

            db.add(
                Score(
                    job_id=job.id,
                    resume_id=resume.id,
                    semantic_score=final_score,
                    skill_score=final_score,
                    experience_score=final_score,
                    education_score=final_score,
                    final_score=final_score,
                )
            )

        db.commit()
        return job.id
    finally:
        db.close()


def test_download_returns_csv_rows_ordered_by_final_score_descending(client):
    job_id = _job_with_scored_candidates(
        [("Low Match", 0.2), ("High Match", 0.8), ("Mid Match", 0.5)]
    )

    response = client.get("/download", params={"job_id": job_id})

    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert [r["candidate_name"] for r in rows] == ["High Match", "Mid Match", "Low Match"]
    assert rows[0]["final_score"] == "0.8"
    assert rows[0]["job_id"] == str(job_id)


def test_download_omits_resumes_with_no_score_row_for_this_job(client):
    db = TestSessionLocal()
    try:
        job = Job(title="Backend Engineer", description="Looking for a backend engineer")
        db.add(job)

        scored_candidate = Candidate(name="Scored Candidate", email=None)
        unscored_candidate = Candidate(name="Unscored Candidate", email=None)
        db.add(scored_candidate)
        db.add(unscored_candidate)
        db.flush()

        scored_resume = Resume(
            candidate_id=scored_candidate.id, file_name="a.pdf", raw_text="text a"
        )
        unscored_resume = Resume(
            candidate_id=unscored_candidate.id, file_name="b.pdf", raw_text="text b"
        )
        db.add(scored_resume)
        db.add(unscored_resume)
        db.flush()

        db.add(
            Score(
                job_id=job.id,
                resume_id=scored_resume.id,
                semantic_score=0.5,
                skill_score=0.5,
                experience_score=0.5,
                education_score=0.5,
                final_score=0.5,
            )
        )
        db.commit()
        job_id = job.id
    finally:
        db.close()

    response = client.get("/download", params={"job_id": job_id})

    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert [r["candidate_name"] for r in rows] == ["Scored Candidate"]
