from dataclasses import dataclass
from datetime import datetime

from src.feedback.generator import GeneratedFeedback
from src.models import CandidateName, ContactInfo, ResumeEntry, SectionedResume
from src.ranking import RankedCandidate


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


@dataclass(frozen=True)
class CandidateAssessment:
    """
    One candidate's ranking + explanation, paired for the API layer.

    Deliberately not a field on RankedCandidate (src/ranking.py):
    RankedCandidate is reused by GET /download's CSV export via
    _ranked_candidates_for_job(), which has no reason to carry
    GeneratedFeedback along with it — adding feedback directly to
    RankedCandidate would mean every consumer of ranking data
    inherits an explanation whether it wants one or not (cross-review
    finding, Session 22/23). Composition instead of a shared field.

    Lives here, not in src/ranking.py or src/feedback/generator.py:
    it's an API-response shape, and putting it in either business
    module would couple two modules (ranking, feedback) that are
    currently and deliberately independent of each other. See
    PROJECT_BIBLE.md Section 11.
    """

    ranking: RankedCandidate
    feedback: GeneratedFeedback


@dataclass(frozen=True)
class RankResponse:
    """
    Response body for POST /rank.

    candidates is sorted descending by final_score (the weighted
    blend of the other four signals — see src/scorer/weighted_scorer.py).
    Each item pairs a RankedCandidate with the GeneratedFeedback
    computed for it in the same /rank call (Session 23) — both are
    also persisted as a side effect of this route (Score/Feedback,
    each upserted).
    """

    job_id: int
    candidates: list[CandidateAssessment]


@dataclass(frozen=True)
class ResultsResponse:
    """
    Response body for GET /results.

    Reads persisted Score/Feedback rows directly (joined to
    Resume/Candidate) rather than recomputing anything — POST /rank
    computes and persists, GET /results only reads. See
    PROJECT_BIBLE.md Section 11 (cross-reviewed with ChatGPT,
    Sessions 20/23).

    Because Score/Feedback are derived/cached data (Section 11),
    candidates here reflect the state as of the *last* POST /rank call
    for this job, not a live computation — a resume uploaded after
    that call simply has no Score/Feedback row yet and won't appear,
    rather than appearing with a fabricated placeholder. candidates is
    [] both when the job has never been ranked and when it has been
    ranked with zero matching resumes — those two states are
    indistinguishable in this response today; disambiguating them
    (e.g. a future last_ranked_at) was raised in cross-review but
    deliberately not added yet (see Section 16/18).
    """

    job_id: int
    candidates: list[CandidateAssessment]
