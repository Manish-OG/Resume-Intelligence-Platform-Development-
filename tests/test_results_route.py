from src.database.models import Candidate, Feedback, Job, Resume, Score
from tests.conftest import TestSessionLocal


def test_results_nonexistent_job_returns_404(client):
    response = client.get("/results", params={"job_id": 999})

    assert response.status_code == 404


def test_results_existing_job_never_ranked_returns_empty_list(client):
    # No Score rows exist for this job at all — 200/[] represents "no
    # ranking has been computed yet", not an error.
    db = TestSessionLocal()
    try:
        job = Job(title="Backend Engineer", description="Looking for a backend engineer")
        db.add(job)
        db.commit()
        job_id = job.id
    finally:
        db.close()

    response = client.get("/results", params={"job_id": job_id})

    assert response.status_code == 200
    body = response.json()
    assert body["job_id"] == job_id
    assert body["candidates"] == []


def _job_with_scored_candidates(
    scores: list[tuple[str, float]], feedback_strengths: str = "Some strength"
) -> int:
    """Creates a Job plus one Candidate/Resume/Score/Feedback row per
    (name, final_score) pair — Score and Feedback are always created
    together, mirroring /rank's real persistence invariant that
    _candidate_assessments_for_job() relies on (inner join)."""
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

            score = Score(
                job_id=job.id,
                resume_id=resume.id,
                semantic_score=final_score,
                skill_score=final_score,
                experience_score=final_score,
                education_score=final_score,
                final_score=final_score,
            )
            db.add(score)
            db.flush()

            db.add(
                Feedback(
                    score_id=score.id,
                    strengths=feedback_strengths,
                    weaknesses="",
                    missing_skills=None,
                    recommendation=f"Recommendation for {name}",
                )
            )

        db.commit()
        return job.id
    finally:
        db.close()


def test_results_returns_persisted_scores_ordered_by_final_score_descending(client):
    job_id = _job_with_scored_candidates(
        [("Low Match", 0.2), ("High Match", 0.8), ("Mid Match", 0.5)]
    )

    response = client.get("/results", params={"job_id": job_id})

    assert response.status_code == 200
    body = response.json()
    assert body["job_id"] == job_id
    names_in_order = [c["ranking"]["candidate_name"] for c in body["candidates"]]
    assert names_in_order == ["High Match", "Mid Match", "Low Match"]
    assert body["candidates"][0]["ranking"]["final_score"] == 0.8


def test_results_returns_correct_fields_for_a_scored_candidate(client):
    job_id = _job_with_scored_candidates([("Jane Doe", 0.42)])

    response = client.get("/results", params={"job_id": job_id})

    candidate = response.json()["candidates"][0]["ranking"]
    assert candidate["candidate_name"] == "Jane Doe"
    assert candidate["semantic_score"] == 0.42
    assert candidate["skill_score"] == 0.42
    assert candidate["experience_score"] == 0.42
    assert candidate["education_score"] == 0.42
    assert candidate["final_score"] == 0.42
    assert isinstance(candidate["resume_id"], int)
    assert isinstance(candidate["candidate_id"], int)


def test_results_returns_correct_feedback_for_a_candidate(client):
    job_id = _job_with_scored_candidates([("Jane Doe", 0.42)], feedback_strengths="Matches SQL")

    response = client.get("/results", params={"job_id": job_id})

    feedback = response.json()["candidates"][0]["feedback"]
    assert feedback["strengths"] == ["Matches SQL"]
    assert feedback["weaknesses"] == []
    assert feedback["missing_skills"] is None
    assert feedback["recommendation"] == "Recommendation for Jane Doe"


def test_results_deserializes_empty_strengths_as_empty_list_not_list_with_blank_string(client):
    # The Section 2 finding from the plan: "".split("\n") == [""], not
    # [] — a real case already produced by Session 22's own live
    # verification (a candidate with zero detected strengths).
    job_id = _job_with_scored_candidates([("No Strengths", 0.1)], feedback_strengths="")

    response = client.get("/results", params={"job_id": job_id})

    assert response.json()["candidates"][0]["feedback"]["strengths"] == []


def test_results_omits_resumes_with_no_score_row_for_this_job(client):
    # A Resume that exists but was never ranked for this job has no
    # Score row — it must not appear with a null/zero placeholder.
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

        score = Score(
            job_id=job.id,
            resume_id=scored_resume.id,
            semantic_score=0.5,
            skill_score=0.5,
            experience_score=0.5,
            education_score=0.5,
            final_score=0.5,
        )
        db.add(score)
        db.flush()

        db.add(
            Feedback(
                score_id=score.id,
                strengths="",
                weaknesses="",
                missing_skills=None,
                recommendation="",
            )
        )
        db.commit()
        job_id = job.id
    finally:
        db.close()

    response = client.get("/results", params={"job_id": job_id})

    names = [c["ranking"]["candidate_name"] for c in response.json()["candidates"]]
    assert names == ["Scored Candidate"]
