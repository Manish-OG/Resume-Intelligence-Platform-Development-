import io

import fitz

from src.database.models import Job, Upload
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


def test_upload_job_returns_job_id_and_title(client):
    pdf_bytes = _make_pdf_bytes(["Senior Backend Engineer", "Requirements", "3+ years Python"])

    response = client.post(
        "/upload-job",
        data={"title": "Senior Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Senior Backend Engineer"
    assert isinstance(body["job_id"], int)
    assert "created_at" in body


def test_upload_job_response_does_not_leak_description(client):
    pdf_bytes = _make_pdf_bytes(["Senior Backend Engineer", "3+ years Python"])

    response = client.post(
        "/upload-job",
        data={"title": "Senior Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )

    assert "description" not in response.json()


def test_upload_job_persists_job_and_upload(client):
    pdf_bytes = _make_pdf_bytes(["Senior Backend Engineer", "3+ years Python required"])

    response = client.post(
        "/upload-job",
        data={"title": "Senior Backend Engineer"},
        files={"file": ("job.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    body = response.json()

    db = TestSessionLocal()
    try:
        job = db.get(Job, body["job_id"])
        uploads = db.query(Upload).all()
    finally:
        db.close()

    assert job.title == "Senior Backend Engineer"
    assert "3+ years Python required" in job.description
    assert len(uploads) == 1
    assert uploads[0].file_name == "job.pdf"


def test_upload_job_missing_title_returns_422(client):
    pdf_bytes = _make_pdf_bytes(["Senior Backend Engineer"])

    response = client.post(
        "/upload-job",
        files={"file": ("job.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )

    assert response.status_code == 422


def test_upload_job_empty_pdf_returns_422(client):
    doc = fitz.open()
    doc.new_page()
    empty_pdf_bytes = doc.tobytes()
    doc.close()

    response = client.post(
        "/upload-job",
        data={"title": "Senior Backend Engineer"},
        files={"file": ("empty.pdf", io.BytesIO(empty_pdf_bytes), "application/pdf")},
    )

    assert response.status_code == 422
