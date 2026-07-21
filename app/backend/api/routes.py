import shutil
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from app.backend.api.schemas import (
    CandidateAssessment,
    RankResponse,
    ResultsResponse,
    UploadJobResponse,
    UploadResumeResponse,
)
from app.backend.config import UPLOAD_DIR
from src.database.db import get_db
from src.database.models import Candidate, Feedback, Job, Resume, Score, Upload
from src.export.csv_exporter import export_ranked_candidates_to_csv
from src.feedback.generator import GeneratedFeedback, generate_feedback
from src.job_pipeline import parse_job_description
from src.parser.pdf_parser import PDFParseError
from src.pipeline import (
    build_resume_education,
    build_resume_experience,
    build_resume_skills,
    process_resume,
)
from src.ranking import RankedCandidate, rank_resumes_against_job

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


@router.post("/rank", response_model=RankResponse)
async def rank_candidates(job_id: int, db: Session = Depends(get_db)) -> RankResponse:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    pairs = (
        db.query(Resume, Candidate)
        .join(Candidate, Resume.candidate_id == Candidate.id)
        .all()
    )

    ranked = rank_resumes_against_job(job, pairs)
    resume_by_id = {resume.id: resume for resume, _ in pairs}
    assessments: list[CandidateAssessment] = []

    # Score is derived/cached data: each candidate's row is fully
    # recomputed and overwritten on every /rank call for this
    # (job_id, resume_id) pair, never merged with a prior value.
    # Upserted at the application level (query-then-update-or-insert);
    # Score.__table_args__'s UniqueConstraint(job_id, resume_id) is a
    # data-integrity backstop against this logic having a bug, not an
    # expected path — see PROJECT_BIBLE.md Section 11.
    for candidate in ranked:
        existing_score = (
            db.query(Score)
            .filter_by(job_id=job.id, resume_id=candidate.resume_id)
            .one_or_none()
        )
        if existing_score is not None:
            existing_score.semantic_score = candidate.semantic_score
            existing_score.skill_score = candidate.skill_score
            existing_score.experience_score = candidate.experience_score
            existing_score.education_score = candidate.education_score
            existing_score.final_score = candidate.final_score
            score = existing_score
        else:
            score = Score(
                job_id=job.id,
                resume_id=candidate.resume_id,
                semantic_score=candidate.semantic_score,
                skill_score=candidate.skill_score,
                experience_score=candidate.experience_score,
                education_score=candidate.education_score,
                final_score=candidate.final_score,
            )
            db.add(score)
            db.flush()  # need score.id before a Feedback row can reference it

        # Feedback: pure explanation, computed independently of ranking
        # (Section 7/11) — resume_skills/education/experience are
        # rebuilt here rather than threaded through from
        # rank_resumes_against_job(), an accepted, named tradeoff
        # (cheap regex/text work, not a model call — see Section 11).
        resume = resume_by_id[candidate.resume_id]
        resume_skills = build_resume_skills(resume.raw_text, resume.file_name)
        resume_education = build_resume_education(resume.raw_text, resume.file_name)
        resume_experience = build_resume_experience(resume.raw_text, resume.file_name)
        feedback_data = generate_feedback(
            resume_skills, resume_education, resume_experience, job.description
        )

        existing_feedback = db.query(Feedback).filter_by(score_id=score.id).one_or_none()
        if existing_feedback is not None:
            existing_feedback.strengths = "\n".join(feedback_data.strengths)
            existing_feedback.weaknesses = "\n".join(feedback_data.weaknesses)
            existing_feedback.missing_skills = (
                "\n".join(feedback_data.missing_skills)
                if feedback_data.missing_skills is not None
                else None
            )
            existing_feedback.recommendation = feedback_data.recommendation
        else:
            db.add(
                Feedback(
                    score_id=score.id,
                    strengths="\n".join(feedback_data.strengths),
                    weaknesses="\n".join(feedback_data.weaknesses),
                    missing_skills=(
                        "\n".join(feedback_data.missing_skills)
                        if feedback_data.missing_skills is not None
                        else None
                    ),
                    recommendation=feedback_data.recommendation,
                )
            )

        # feedback_data already exists in memory from generating it
        # above — no extra query needed to build the response, unlike
        # GET /results (see _candidate_assessments_for_job()).
        assessments.append(CandidateAssessment(ranking=candidate, feedback=feedback_data))
    db.commit()

    return RankResponse(job_id=job.id, candidates=assessments)


def _ranked_candidates_for_job(db: Session, job: Job) -> list[RankedCandidate]:
    """
    Reads persisted Score rows for a job directly — never recomputes.
    Shared by GET /results and GET /download (a genuine second caller
    as of GET /download — see PROJECT_BIBLE.md Section 11). Kept here,
    not in src/ranking.py: this is a DB query + ORM mapping, not
    business logic, and src/ranking.py deliberately stays
    DB-session-free (Section 11).
    """

    rows = (
        db.query(Score, Candidate)
        .join(Resume, Score.resume_id == Resume.id)
        .join(Candidate, Resume.candidate_id == Candidate.id)
        .filter(Score.job_id == job.id)
        .order_by(Score.final_score.desc())
        .all()
    )

    return [
        RankedCandidate(
            resume_id=score.resume_id,
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            semantic_score=score.semantic_score,
            skill_score=score.skill_score,
            experience_score=score.experience_score,
            education_score=score.education_score,
            final_score=score.final_score,
        )
        for score, candidate in rows
    ]


def _split_or_empty(text: str) -> list[str]:
    """
    "".split("\n") returns [""], not [] — verified directly, not
    assumed, since this is the first read path for Feedback's
    newline-joined columns (Session 23). A blank column must
    deserialize back to an empty list, not a list containing one
    empty string.
    """

    return text.split("\n") if text else []


def _generated_feedback_from_row(feedback_row: Feedback) -> GeneratedFeedback:
    """Reverses the serialization /rank's persistence loop applies (Session 22)."""

    return GeneratedFeedback(
        strengths=_split_or_empty(feedback_row.strengths),
        weaknesses=_split_or_empty(feedback_row.weaknesses),
        missing_skills=(
            _split_or_empty(feedback_row.missing_skills)
            if feedback_row.missing_skills is not None
            else None
        ),
        recommendation=feedback_row.recommendation,
    )


def _candidate_assessments_for_job(db: Session, job: Job) -> list[CandidateAssessment]:
    """
    Reads persisted Score + Feedback rows for a job directly — never
    recomputes. Used by GET /results only; GET /download keeps using
    _ranked_candidates_for_job() unchanged (Section 11 — CSV
    serialization of feedback's list fields is a separate, undecided
    formatting question, not bundled in here).

    Inner join on Feedback, not outer: every Score row has exactly one
    Feedback row by construction (/rank creates both in the same
    transaction — see its persistence loop above). If that invariant
    is ever violated, the bug is elsewhere; this read path doesn't
    quietly paper over it (cross-reviewed with ChatGPT, Session 23).

    Overlaps substantially with _ranked_candidates_for_job()'s query —
    an accepted, named duplication for now (Session 23), not unified
    into a shared read model. Watch item, not solved: if a third
    similarly-shaped query appears (e.g. a future export-with-feedback
    or dashboard endpoint), that's the trigger to introduce one
    instead of continuing to duplicate joins.
    """

    rows = (
        db.query(Score, Feedback, Candidate)
        .join(Feedback, Feedback.score_id == Score.id)
        .join(Resume, Score.resume_id == Resume.id)
        .join(Candidate, Resume.candidate_id == Candidate.id)
        .filter(Score.job_id == job.id)
        .order_by(Score.final_score.desc())
        .all()
    )

    return [
        CandidateAssessment(
            ranking=RankedCandidate(
                resume_id=score.resume_id,
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                semantic_score=score.semantic_score,
                skill_score=score.skill_score,
                experience_score=score.experience_score,
                education_score=score.education_score,
                final_score=score.final_score,
            ),
            feedback=_generated_feedback_from_row(feedback_row),
        )
        for score, feedback_row, candidate in rows
    ]


@router.get("/results", response_model=ResultsResponse)
async def get_results(job_id: int, db: Session = Depends(get_db)) -> ResultsResponse:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return ResultsResponse(job_id=job.id, candidates=_candidate_assessments_for_job(db, job))


@router.get("/download")
async def download_results(
    job_id: int, fmt: Literal["csv"] = "csv", db: Session = Depends(get_db)
) -> Response:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    candidates = _ranked_candidates_for_job(db, job)
    csv_text = export_ranked_candidates_to_csv(candidates, extra_columns={"job_id": job.id})

    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="results_job_{job.id}.csv"'},
    )
