from dataclasses import dataclass

from src.database.models import Candidate, Job, Resume
from src.job_pipeline import build_job_embedding
from src.pipeline import (
    build_resume_education,
    build_resume_embedding,
    build_resume_experience,
    build_resume_skills,
)
from src.scorer.education_matcher import compute_education_score
from src.scorer.experience_matcher import compute_experience_score
from src.scorer.skill_matcher import compute_skill_score
from src.scorer.weighted_scorer import ScoreComponents, compute_score
from src.similarity.compute import cosine_similarity


@dataclass(frozen=True)
class RankedCandidate:
    resume_id: int
    candidate_id: int
    candidate_name: str
    semantic_score: float
    skill_score: float
    experience_score: float
    education_score: float
    final_score: float


def rank_resumes_against_job(
    job: Job, resume_candidate_pairs: list[tuple[Resume, Candidate]]
) -> list[RankedCandidate]:
    """
    Rank every given (Resume, Candidate) pair against a Job, exposing
    semantic similarity and skill overlap as independent signals.

    All four ScoreComponents signals (semantic, skills, experience,
    education) are real, and final_score is their weighted blend via
    src/scorer/weighted_scorer.py's compute_score() (DEFAULT_WEIGHTS,
    unchanged from scaffold — no evidence-based reason found to
    reweight them). Computed here, not in the route, since this
    function already owns assembling every other scoring signal for a
    candidate — final_score is simply the natural completion of that,
    not a separate responsibility (see PROJECT_BIBLE.md Section 11,
    cross-reviewed).

    Sort order is by final_score descending — changed from
    semantic_score-only (Sessions 15/16/18's interim behavior, kept
    only because no legitimate composite existed yet). An endpoint
    named /rank should rank by the actual composite once one
    legitimately exists.

    This function stays DB-session-free (takes already-fetched rows,
    never queries, never writes) even though its output is now
    persisted — persistence is the caller's (the /rank route's)
    responsibility, keeping this module a pure, easily-unit-tested
    business-logic function. See Section 11.

    experience_score/education_score both honestly reflect data gaps
    rather than guessing: hand-traced against the real sample resume,
    its EXPERIENCE section contains zero standalone date lines at
    all, so compute_experience_score() correctly returns 0.0 for it —
    a real, documented limitation of the source data (Section 11), not
    a bug here.

    Compares against every (Resume, Candidate) pair the caller passes
    in. Until an application/job-assignment concept exists in the
    schema, callers are expected to pass every Resume row in the
    system — there is no principled way to define a subset from the
    current data model (see Section 11).

    DB-session-free: takes already-fetched rows, never queries.
    Embeddings and skill lists are both computed fresh on every call,
    not cached or persisted (see Section 11). Never raises; returns
    [] for an empty input list.
    """

    if not resume_candidate_pairs:
        return []

    job_vector = build_job_embedding(job.description)

    ranked = []
    for resume, candidate in resume_candidate_pairs:
        resume_vector = build_resume_embedding(resume.raw_text, resume.file_name)
        resume_skills = build_resume_skills(resume.raw_text, resume.file_name)
        resume_education = build_resume_education(resume.raw_text, resume.file_name)
        resume_experience = build_resume_experience(resume.raw_text, resume.file_name)

        semantic_score = cosine_similarity(job_vector, resume_vector)
        skill_score = compute_skill_score(resume_skills, job.description)
        experience_score = compute_experience_score(resume_experience, job.description)
        education_score = compute_education_score(resume_education, job.description)
        final_score = compute_score(
            ScoreComponents(
                semantic=semantic_score,
                skills=skill_score,
                experience=experience_score,
                education=education_score,
            )
        )

        ranked.append(
            RankedCandidate(
                resume_id=resume.id,
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                semantic_score=semantic_score,
                skill_score=skill_score,
                experience_score=experience_score,
                education_score=education_score,
                final_score=final_score,
            )
        )

    return sorted(ranked, key=lambda c: c.final_score, reverse=True)
