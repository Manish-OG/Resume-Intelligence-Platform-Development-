import shutil
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.backend.api.schemas import UploadJobResponse, UploadResumeResponse
from app.backend.config import UPLOAD_DIR
from src.database.db import get_db
from src.database.models import Candidate, Job, Resume, Upload
from src.job_pipeline import parse_job_description
from src.parser.pdf_parser import PDFParseError
from src.pipeline import process_resume

router = APIRouter()


@router.post("/upload-job", response_model=UploadJobResponse)
async def upload_job(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadJobResponse:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = UPLOAD_DIR / f"{uuid.uuid4().hex}_{file.filename}"

    with saved_path.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    try:
        description = parse_job_description(saved_path)
    except PDFParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    job = Job(title=title, description=description)
    db.add(job)
    db.flush()

    db.add(Upload(file_name=file.filename, file_path=str(saved_path)))
    db.commit()

    return UploadJobResponse(job_id=job.id, title=job.title, created_at=job.created_at)


@router.post("/upload-resume", response_model=UploadResumeResponse)
async def upload_resume(
    file: UploadFile, db: Session = Depends(get_db)
) -> UploadResumeResponse:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = UPLOAD_DIR / f"{uuid.uuid4().hex}_{file.filename}"

    with saved_path.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    try:
        result = process_resume(saved_path)
    except PDFParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    resume_id: int | None = None
    candidate_id: int | None = None

    if result.name.name is not None:
        candidate = Candidate(name=result.name.name, email=result.contact.email)
        db.add(candidate)
        db.flush()

        resume = Resume(
            candidate_id=candidate.id,
            file_name=file.filename,
            raw_text=result.raw_text,
        )
        db.add(resume)
        db.flush()

        resume_id, candidate_id = resume.id, candidate.id

    db.add(Upload(file_name=file.filename, file_path=str(saved_path)))
    db.commit()

    return UploadResumeResponse(
        resume_id=resume_id,
        candidate_id=candidate_id,
        sections=result.sections,
        contact=result.contact,
        name=result.name,
        education=result.education,
        experience=result.experience,
    )


@router.post("/rank")
async def rank_candidates(job_id: int):
    raise NotImplementedError


@router.get("/results")
async def get_results(job_id: int):
    raise NotImplementedError


@router.get("/download")
async def download_results(job_id: int, fmt: str = "csv"):
    raise NotImplementedError
