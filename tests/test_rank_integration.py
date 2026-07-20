import io

import fitz
import pytest

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
    names_in_order = [c["candidate_name"] for c in candidates]
    assert names_in_order[0] == "John Smith"
    assert names_in_order[1] == "Mary Baker"
    assert candidates[0]["semantic_score"] > candidates[1]["semantic_score"]

    # skill_score: John's Python (1 of 3 listed skills) appears in the
    # JD; none of Mary's baking-related skills do.
    assert candidates[0]["skill_score"] == pytest.approx(1 / 3)
    assert candidates[1]["skill_score"] == 0.0


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

    assert first["candidates"][0]["semantic_score"] == second["candidates"][0]["semantic_score"]


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

    score = response.json()["candidates"][0]["semantic_score"]
    assert -1.0 <= score <= 1.0

    skill_score = response.json()["candidates"][0]["skill_score"]
    assert 0.0 <= skill_score <= 1.0
