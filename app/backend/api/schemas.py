from dataclasses import dataclass
from datetime import datetime

from src.models import CandidateName, ContactInfo, ResumeEntry, SectionedResume


@dataclass(frozen=True)
class UploadResumeResponse:
    """
    Response body for POST /upload-resume.

    Route-local API schema, not a domain model (src/models/ holds
    pipeline-stage contracts; this holds one route's HTTP contract).
    Deliberately does not include PipelineResult.raw_text — that field
    exists only for persisting a Resume row, not for the API caller.

    resume_id/candidate_id are None when no Resume/Candidate row was
    created (CandidateName.name was None — see the "skip persistence
    when no name" decision in PROJECT_BIBLE.md, Section 11).
    """

    resume_id: int | None
    candidate_id: int | None
    sections: SectionedResume
    contact: ContactInfo
    name: CandidateName
    education: tuple[ResumeEntry, ...]
    experience: tuple[ResumeEntry, ...]


@dataclass(frozen=True)
class UploadJobResponse:
    """
    Response body for POST /upload-job.

    Deliberately excludes the full parsed Job.description text from
    the response — same reasoning as UploadResumeResponse omitting
    raw_text: it's already persisted, and echoing the whole document
    back would only bloat the payload.
    """

    job_id: int
    title: str
    created_at: datetime
