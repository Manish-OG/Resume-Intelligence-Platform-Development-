import csv
import io

import fitz
import pytest

from src.database.models import Feedback, Score
from src.scorer.weighted_scorer import ScoreComponents, compute_score
from tests.conftest import TestSessionLocal

pytestmark = pytest.mark.slow


def _make_pdf_bytes(lines: list[str]) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    y = 72
    for line in lines:
        page.insert_text((72, y), line)
        y += 18
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_rank_ranks_relevant_candidate_above_unrelated_one(client):
    # First genuine whole-system test: real ingestion, real embeddings,
    # real ranking, all composed together — not mocked anywhere.
    backend_resume = _make_pdf_bytes(
        [
            "John Smith",
            "john@example.com",
            "",
            "Experience",
            "Backend engineer with 5 years of Python, FastAPI, and REST API development.",
            "",
            "Skills",
            "Languages: Python, SQL, Java.",
        ]
    )
    chef_resume = _make_pdf_bytes(
        [
            "Mary Baker",
            "mary@example.com",
            "",
            "Experience",
            "Pastry chef specializing in French desserts and cake decoration for five-star hotels.",
            "",
            "Skills",
            "Baking, Cake Decoration, French Cuisine.",
        ]
    )
    job_pdf = _make_pdf_bytes(
        [
            "Senior Backend Engineer",
            "Looking for an experienced backend engineer skilled in Python and REST APIs.",
        ]
    )

    r1 = client.post(
        "/upload-resume",
        files={"file": ("backend.pdf", io.BytesIO(backend_resume), "application/pdf")},
    )
    r2 = client.post(
        "/upload-resume",
        files={"file": ("chef.pdf", io.BytesIO(chef_resume), "application/pdf")},
    )
    job_response = client.post(
        "/upload-job",
        data={"title": "Senior Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(job_pdf), "application/pdf")},
    )
    job_id = job_response.json()["job_id"]

    response = client.post("/rank", params={"job_id": job_id})

    assert response.status_code == 200
    body = response.json()
    candidates = body["candidates"]

    assert len(candidates) == 2
    rankings = [c["ranking"] for c in candidates]
    names_in_order = [r["candidate_name"] for r in rankings]
    assert names_in_order[0] == "John Smith"
    assert names_in_order[1] == "Mary Baker"
    assert rankings[0]["semantic_score"] > rankings[1]["semantic_score"]

    # skill_score: John's Python (1 of 3 listed skills) appears in the
    # JD; none of Mary's baking-related skills do.
    assert rankings[0]["skill_score"] == pytest.approx(1 / 3)
    assert rankings[1]["skill_score"] == 0.0

    # experience_score/education_score: neither resume's Experience
    # section has a standalone date line (same shape as the real
    # sample resume hand-traced during design), and the JD states no
    # years/degree requirement — both honestly 0.0 for both
    # candidates, not fabricated.
    assert rankings[0]["experience_score"] == 0.0
    assert rankings[1]["experience_score"] == 0.0
    assert rankings[0]["education_score"] == 0.0
    assert rankings[1]["education_score"] == 0.0

    # final_score is now the actual sort key — confirm the response
    # order agrees with it (not just semantic_score, which happens to
    # agree here too since John also leads on skill_score).
    assert rankings[0]["final_score"] >= rankings[1]["final_score"]

    # Each candidate also carries feedback now (Session 23) — sanity
    # check it's present and non-empty, not just structurally there.
    assert candidates[0]["feedback"]["recommendation"] != ""


def test_rank_scores_are_deterministic_across_calls(client):
    resume = _make_pdf_bytes(
        ["Jane Doe", "jane@example.com", "", "Experience", "Backend engineer with Python experience."]
    )
    job_pdf = _make_pdf_bytes(["Backend Engineer", "Looking for a Python backend engineer."])

    client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(resume), "application/pdf")},
    )
    job_response = client.post(
        "/upload-job",
        data={"title": "Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(job_pdf), "application/pdf")},
    )
    job_id = job_response.json()["job_id"]

    first = client.post("/rank", params={"job_id": job_id}).json()
    second = client.post("/rank", params={"job_id": job_id}).json()

    first_score = first["candidates"][0]["ranking"]["semantic_score"]
    second_score = second["candidates"][0]["ranking"]["semantic_score"]
    assert first_score == second_score


def test_rank_semantic_scores_within_valid_cosine_range(client):
    resume = _make_pdf_bytes(
        ["Jane Doe", "jane@example.com", "", "Experience", "Backend engineer with Python experience."]
    )
    job_pdf = _make_pdf_bytes(["Backend Engineer", "Looking for a Python backend engineer."])

    client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(resume), "application/pdf")},
    )
    job_response = client.post(
        "/upload-job",
        data={"title": "Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(job_pdf), "application/pdf")},
    )
    job_id = job_response.json()["job_id"]

    response = client.post("/rank", params={"job_id": job_id})

    candidate = response.json()["candidates"][0]["ranking"]
    assert -1.0 <= candidate["semantic_score"] <= 1.0
    assert 0.0 <= candidate["skill_score"] <= 1.0
    assert 0.0 <= candidate["experience_score"] <= 1.0
    assert 0.0 <= candidate["education_score"] <= 1.0
    assert 0.0 <= candidate["final_score"] <= 1.0


def test_rank_computes_real_experience_and_education_scores_end_to_end(client):
    resume = _make_pdf_bytes(
        [
            "Jane Doe",
            "jane@example.com",
            "",
            "Experience",
            "Acme Corp",
            "2019 - 2023",
            "Built backend services.",
            "",
            "Education",
            "State University",
            "2015 - 2019",
            "Bachelor of Science in Computer Science",
        ]
    )
    job_pdf = _make_pdf_bytes(
        [
            "Backend Engineer",
            "Requires 3+ years of experience and a Bachelor's degree.",
        ]
    )

    client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(resume), "application/pdf")},
    )
    job_response = client.post(
        "/upload-job",
        data={"title": "Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(job_pdf), "application/pdf")},
    )
    job_id = job_response.json()["job_id"]

    response = client.post("/rank", params={"job_id": job_id})

    candidate = response.json()["candidates"][0]["ranking"]
    assert candidate["experience_score"] == 1.0
    assert candidate["education_score"] == 1.0

    expected_final = compute_score(
        ScoreComponents(
            semantic=candidate["semantic_score"],
            skills=candidate["skill_score"],
            experience=candidate["experience_score"],
            education=candidate["education_score"],
        )
    )
    assert candidate["final_score"] == pytest.approx(expected_final)

    # Persisted as a real Score row, not just returned in the response.
    db = TestSessionLocal()
    try:
        score_row = db.query(Score).filter_by(job_id=job_id).one()
        assert score_row.resume_id == candidate["resume_id"]
        assert score_row.final_score == pytest.approx(candidate["final_score"])
        assert score_row.experience_score == 1.0
        assert score_row.education_score == 1.0
    finally:
        db.close()


def test_rank_upserts_score_rows_instead_of_duplicating_on_repeated_calls(client):
    resume = _make_pdf_bytes(
        ["Jane Doe", "jane@example.com", "", "Experience", "Backend engineer with Python experience."]
    )
    job_pdf = _make_pdf_bytes(["Backend Engineer", "Looking for a Python backend engineer."])

    client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(resume), "application/pdf")},
    )
    job_response = client.post(
        "/upload-job",
        data={"title": "Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(job_pdf), "application/pdf")},
    )
    job_id = job_response.json()["job_id"]

    client.post("/rank", params={"job_id": job_id})
    client.post("/rank", params={"job_id": job_id})

    db = TestSessionLocal()
    try:
        rows = db.query(Score).filter_by(job_id=job_id).all()
        assert len(rows) == 1  # not 2 — the second /rank call updated, didn't insert
    finally:
        db.close()


def test_results_returns_exactly_what_rank_persisted(client):
    # /results must read genuinely persisted data end-to-end, not
    # recompute or silently drift from what /rank actually returned.
    resume = _make_pdf_bytes(
        [
            "Jane Doe",
            "jane@example.com",
            "",
            "Experience",
            "Acme Corp",
            "2019 - 2023",
            "Built backend services.",
            "",
            "Education",
            "State University",
            "2015 - 2019",
            "Bachelor of Science in Computer Science",
        ]
    )
    job_pdf = _make_pdf_bytes(
        ["Backend Engineer", "Requires 3+ years of experience and a Bachelor's degree."]
    )

    client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(resume), "application/pdf")},
    )
    job_response = client.post(
        "/upload-job",
        data={"title": "Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(job_pdf), "application/pdf")},
    )
    job_id = job_response.json()["job_id"]

    rank_response = client.post("/rank", params={"job_id": job_id})
    results_response = client.get("/results", params={"job_id": job_id})

    assert results_response.status_code == 200
    rank_candidate = rank_response.json()["candidates"][0]
    results_candidate = results_response.json()["candidates"][0]
    assert results_candidate == rank_candidate


def test_results_before_any_rank_call_returns_empty_list_for_valid_job(client):
    job_pdf = _make_pdf_bytes(["Backend Engineer", "Looking for a Python backend engineer."])

    job_response = client.post(
        "/upload-job",
        data={"title": "Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(job_pdf), "application/pdf")},
    )
    job_id = job_response.json()["job_id"]

    response = client.get("/results", params={"job_id": job_id})

    assert response.status_code == 200
    assert response.json()["candidates"] == []


def test_download_csv_matches_what_rank_persisted(client):
    # /download must read genuinely persisted data end-to-end, not
    # recompute or silently drift from what /rank actually returned.
    resume = _make_pdf_bytes(
        ["Jane Doe", "jane@example.com", "", "Experience", "Backend engineer with Python experience."]
    )
    job_pdf = _make_pdf_bytes(["Backend Engineer", "Looking for a Python backend engineer."])

    client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(resume), "application/pdf")},
    )
    job_response = client.post(
        "/upload-job",
        data={"title": "Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(job_pdf), "application/pdf")},
    )
    job_id = job_response.json()["job_id"]

    rank_response = client.post("/rank", params={"job_id": job_id})
    download_response = client.get("/download", params={"job_id": job_id})

    assert download_response.status_code == 200
    assert download_response.headers["content-type"].startswith("text/csv")

    rank_candidate = rank_response.json()["candidates"][0]["ranking"]
    rows = list(csv.DictReader(io.StringIO(download_response.text)))
    assert len(rows) == 1
    row = rows[0]
    assert row["job_id"] == str(job_id)
    assert row["resume_id"] == str(rank_candidate["resume_id"])
    assert row["candidate_name"] == rank_candidate["candidate_name"]
    assert float(row["final_score"]) == pytest.approx(rank_candidate["final_score"])
    assert float(row["semantic_score"]) == pytest.approx(rank_candidate["semantic_score"])


def test_download_before_any_rank_call_returns_header_only_csv_for_valid_job(client):
    job_pdf = _make_pdf_bytes(["Backend Engineer", "Looking for a Python backend engineer."])

    job_response = client.post(
        "/upload-job",
        data={"title": "Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(job_pdf), "application/pdf")},
    )
    job_id = job_response.json()["job_id"]

    response = client.get("/download", params={"job_id": job_id})

    assert response.status_code == 200
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert rows == []


def test_rank_persists_real_honest_feedback_content(client):
    # Same real hand-traced case as test_generate_feedback_real_sample_
    # resume_against_real_electronics_jd (unit test), but end-to-end
    # through the real /rank route and real persisted DB row.
    resume = _make_pdf_bytes(
        [
            "Jane Doe",
            "jane@example.com",
            "",
            "Experience",
            "Did some backend work, no dates listed.",
            "",
            "Education",
            "State University",
            "2015 - 2019",
            "Bachelor of Science in Computer Science",
        ]
    )
    job_pdf = _make_pdf_bytes(
        [
            "Backend Engineer",
            "Requires 3+ years of experience and a Bachelor's degree.",
        ]
    )

    client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(resume), "application/pdf")},
    )
    job_response = client.post(
        "/upload-job",
        data={"title": "Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(job_pdf), "application/pdf")},
    )
    job_id = job_response.json()["job_id"]

    client.post("/rank", params={"job_id": job_id})

    db = TestSessionLocal()
    try:
        score_row = db.query(Score).filter_by(job_id=job_id).one()
        feedback_row = db.query(Feedback).filter_by(score_id=score_row.id).one()

        assert "Meets the stated education requirement." in feedback_row.strengths
        assert "date ranges we could parse" in feedback_row.weaknesses
        assert "insufficient" not in feedback_row.weaknesses.lower()
        assert feedback_row.missing_skills is None
        assert feedback_row.recommendation != ""
    finally:
        db.close()


def test_rank_upserts_feedback_rows_instead_of_duplicating_on_repeated_calls(client):
    resume = _make_pdf_bytes(
        ["Jane Doe", "jane@example.com", "", "Experience", "Backend engineer with Python experience."]
    )
    job_pdf = _make_pdf_bytes(["Backend Engineer", "Looking for a Python backend engineer."])

    client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(resume), "application/pdf")},
    )
    job_response = client.post(
        "/upload-job",
        data={"title": "Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(job_pdf), "application/pdf")},
    )
    job_id = job_response.json()["job_id"]

    client.post("/rank", params={"job_id": job_id})
    client.post("/rank", params={"job_id": job_id})

    db = TestSessionLocal()
    try:
        score_row = db.query(Score).filter_by(job_id=job_id).one()
        rows = db.query(Feedback).filter_by(score_id=score_row.id).all()
        assert len(rows) == 1  # not 2 — the second /rank call updated, didn't insert
    finally:
        db.close()
