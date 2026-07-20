from dataclasses import dataclass

from src.database.models import Candidate, Job, Resume
from src.job_pipeline import build_job_embedding
from src.pipeline import build_resume_embedding, build_resume_skills
from src.scorer.skill_matcher import compute_skill_score
from src.similarity.compute import cosine_similarity


@dataclass(frozen=True)
class RankedCandidate:
    resume_id: int
    candidate_id: int
    candidate_name: str
    semantic_score: float
    skill_score: float


def rank_resumes_against_job(
    job: Job, resume_candidate_pairs: list[tuple[Resume, Candidate]]
) -> list[RankedCandidate]:
    """
    Rank every given (Resume, Candidate) pair against a Job, exposing
    semantic similarity and skill overlap as independent signals.

    Deliberately bypasses src/scorer/weighted_scorer.py: ScoreComponents
    expects four signals (semantic, skills, experience, education);
    experience/education still aren't computable (nothing scores
    relevance from ResumeEntry data yet). Feeding compute_score() would
    mean fabricating two of four inputs, the exact placeholder-data
    anti-pattern this project has rejected at every prior decision
    point. semantic_score and skill_score are returned as independent
    fields rather than blended into one number — an aggregate would
    imply a complete ranking methodology that doesn't exist yet. See
    PROJECT_BIBLE.md Section 11. Sort order is by semantic_score only
    (unchanged from before skill_score existed) — adding skill_score
    to the response isn't the same decision as using it to rank.

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

        ranked.append(
            RankedCandidate(
                resume_id=resume.id,
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                semantic_score=cosine_similarity(job_vector, resume_vector),
                skill_score=compute_skill_score(resume_skills, job.description),
            )
        )

    return sorted(ranked, key=lambda c: c.semantic_score, reverse=True)
