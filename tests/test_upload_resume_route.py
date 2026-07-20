import io

import fitz

from src.database.models import Candidate, Resume, Upload
from tests.conftest import TestSessionLocal


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


def test_upload_resume_returns_sections_and_contact(client):
    pdf_bytes = _make_pdf_bytes(
        [
            "Jane Doe",
            "jane@example.com | (555) 123-4567",
            "",
            "Experience",
            "Backend Engineer at Acme",
            "",
            "Education",
            "BSc Computer Science",
        ]
    )

    response = client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["contact"]["email"] == "jane@example.com"
    assert body["contact"]["phone"] == "(555) 123-4567"
    assert body["name"]["name"] == "Jane Doe"
    assert isinstance(body["resume_id"], int)
    assert isinstance(body["candidate_id"], int)
    section_types = [s["section_type"] for s in body["sections"]["sections"]]
    assert "experience" in section_types
    assert "education" in section_types
    assert len(body["experience"]) == 1
    assert "Backend Engineer at Acme" in body["experience"][0]["details"]
    assert len(body["education"]) == 1
    assert "BSc Computer Science" in body["education"][0]["details"]


def test_upload_resume_response_does_not_leak_raw_text(client):
    pdf_bytes = _make_pdf_bytes(["Jane Doe", "jane@example.com"])

    response = client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )

    assert "raw_text" not in response.json()


def test_upload_resume_persists_upload_row(client):
    pdf_bytes = _make_pdf_bytes(["Jane Doe", "jane@example.com"])

    client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )

    db = TestSessionLocal()
    try:
        uploads = db.query(Upload).all()
    finally:
        db.close()

    assert len(uploads) == 1
    assert uploads[0].file_name == "resume.pdf"


def test_upload_resume_persists_candidate_and_resume(client):
    pdf_bytes = _make_pdf_bytes(
        ["Jane Doe", "jane@example.com | (555) 123-4567", "", "Experience", "Backend Engineer"]
    )

    response = client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    body = response.json()

    db = TestSessionLocal()
    try:
        candidate = db.get(Candidate, body["candidate_id"])
        resume = db.get(Resume, body["resume_id"])
    finally:
        db.close()

    assert candidate.name == "Jane Doe"
    assert candidate.email == "jane@example.com"
    assert resume.candidate_id == candidate.id
    assert resume.file_name == "resume.pdf"
    assert "Jane Doe" in resume.raw_text
    assert "Backend Engineer" in resume.raw_text


def test_upload_resume_skips_candidate_and_resume_when_name_not_found(client):
    # First HEADER line looks like an email, so extract_name() returns None
    # (see src/extraction/name_extractor.py's defensive check).
    pdf_bytes = _make_pdf_bytes(["jane@example.com", "(555) 123-4567"])

    response = client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["resume_id"] is None
    assert body["candidate_id"] is None
    assert body["name"]["name"] is None

    db = TestSessionLocal()
    try:
        candidates = db.query(Candidate).all()
        resumes = db.query(Resume).all()
        uploads = db.query(Upload).all()
    finally:
        db.close()

    assert candidates == []
    assert resumes == []
    assert len(uploads) == 1


def test_upload_resume_segments_multiple_education_entries(client):
    pdf_bytes = _make_pdf_bytes(
        [
            "Jane Doe",
            "jane@example.com",
            "",
            "Education",
            "MIT",
            "Sep 2020 - 2024",
            "BSc Computer Science",
            "Riverside High",
            "May 2016",
            "High School Diploma",
        ]
    )

    response = client.post(
        "/upload-resume",
        files={"file": ("resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    body = response.json()

    assert len(body["education"]) == 2
    assert body["education"][0]["title"] == "MIT"
    assert body["education"][0]["dates"] == "Sep 2020 - 2024"
    assert body["education"][1]["title"] == "Riverside High"
    assert body["education"][1]["dates"] == "May 2016"


def test_upload_resume_empty_pdf_returns_422(client):
    doc = fitz.open()
    doc.new_page()
    empty_pdf_bytes = doc.tobytes()
    doc.close()

    response = client.post(
        "/upload-resume",
        files={"file": ("empty.pdf", io.BytesIO(empty_pdf_bytes), "application/pdf")},
    )

    assert response.status_code == 422
