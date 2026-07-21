import httpx
import pytest

from app.frontend.streamlit_app import APIError, rank, upload_job, upload_resume


def _client(handler) -> httpx.Client:
    return httpx.Client(
        base_url="http://backend.test", transport=httpx.MockTransport(handler)
    )


def test_upload_job_sends_title_and_file_returns_json():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        captured["content"] = request.content
        return httpx.Response(200, json={"job_id": 1, "title": "Backend Engineer", "created_at": "now"})

    with _client(handler) as client:
        result = upload_job(client, "Backend Engineer", "job.pdf", b"%PDF-fake-bytes")

    assert captured["method"] == "POST"
    assert captured["path"] == "/upload-job"
    assert b'name="title"' in captured["content"]
    assert b"Backend Engineer" in captured["content"]
    assert b'filename="job.pdf"' in captured["content"]
    assert result == {"job_id": 1, "title": "Backend Engineer", "created_at": "now"}


def test_upload_job_raises_api_error_on_422():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"detail": "Password-protected PDF"})

    with _client(handler) as client:
        with pytest.raises(APIError) as exc_info:
            upload_job(client, "Backend Engineer", "job.pdf", b"%PDF-fake-bytes")

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "Password-protected PDF"


def test_upload_resume_sends_file_returns_json():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        captured["content"] = request.content
        return httpx.Response(
            200,
            json={
                "resume_id": 7,
                "candidate_id": 3,
                "sections": [],
                "contact": {"email": None, "phone": None},
                "name": {"name": "Jane Doe"},
                "education": [],
                "experience": [],
            },
        )

    with _client(handler) as client:
        result = upload_resume(client, "resume.pdf", b"%PDF-fake-bytes")

    assert captured["method"] == "POST"
    assert captured["path"] == "/upload-resume"
    assert b'filename="resume.pdf"' in captured["content"]
    assert result["resume_id"] == 7
    assert result["name"]["name"] == "Jane Doe"


def test_upload_resume_raises_api_error_on_422():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"detail": "Not a valid PDF"})

    with _client(handler) as client:
        with pytest.raises(APIError) as exc_info:
            upload_resume(client, "bad.pdf", b"not-a-pdf")

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "Not a valid PDF"


def test_rank_sends_job_id_query_param_returns_json():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        captured["params"] = dict(request.url.params)
        return httpx.Response(200, json={"job_id": 5, "candidates": []})

    with _client(handler) as client:
        result = rank(client, 5)

    assert captured["method"] == "POST"
    assert captured["path"] == "/rank"
    assert captured["params"] == {"job_id": "5"}
    assert result == {"job_id": 5, "candidates": []}


def test_rank_raises_api_error_on_404():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Job 999 not found"})

    with _client(handler) as client:
        with pytest.raises(APIError) as exc_info:
            rank(client, 999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Job 999 not found"
