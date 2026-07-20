import numpy as np
import pytest

from src.database.models import Candidate, Job, Resume
from src.models import ResumeSkills
from src.ranking import RankedCandidate, rank_resumes_against_job


@pytest.fixture
def fake_embeddings(monkeypatch):
    """
    Replaces build_resume_embedding()/build_job_embedding()/
    build_resume_skills() with controllable fakes, so
    rank_resumes_against_job()'s orchestration/sorting logic can be
    tested fast, without touching the real model. cosine_similarity()
    and compute_skill_score() themselves still run for real (pure
    numpy/regex, no model) — only text-to-vector/text-to-skills is
    faked.
    """

    resume_vectors: dict[str, np.ndarray] = {}
    resume_skills: dict[str, ResumeSkills] = {}

    def fake_build_resume_embedding(raw_text: str, filename: str = "") -> np.ndarray:
        return resume_vectors[raw_text]

    def fake_build_job_embedding(description: str) -> np.ndarray:
        return np.array([1.0, 0.0])

    def fake_build_resume_skills(raw_text: str, filename: str = "") -> ResumeSkills:
        return resume_skills.get(raw_text, ResumeSkills(skills=()))

    monkeypatch.setattr("src.ranking.build_resume_embedding", fake_build_resume_embedding)
    monkeypatch.setattr("src.ranking.build_job_embedding", fake_build_job_embedding)
    monkeypatch.setattr("src.ranking.build_resume_skills", fake_build_resume_skills)

    return resume_vectors, resume_skills


def _job(job_id=1, description="Looking for a backend engineer"):
    return Job(id=job_id, title="Backend Engineer", description=description)


def _pair(resume_id, candidate_id, candidate_name, raw_text):
    resume = Resume(id=resume_id, candidate_id=candidate_id, file_name="r.pdf", raw_text=raw_text)
    candidate = Candidate(id=candidate_id, name=candidate_name, email=None)
    return resume, candidate


def test_rank_empty_list_returns_empty_list(fake_embeddings):
    result = rank_resumes_against_job(_job(), [])

    assert result == []


def test_rank_single_resume(fake_embeddings):
    vectors, _ = fake_embeddings
    vectors["resume text"] = np.array([1.0, 0.0])
    pairs = [_pair(1, 1, "Jane Doe", "resume text")]

    result = rank_resumes_against_job(_job(), pairs)

    assert len(result) == 1
    assert result[0] == RankedCandidate(
        resume_id=1, candidate_id=1, candidate_name="Jane Doe", semantic_score=1.0, skill_score=0.0
    )


def test_rank_sorts_descending_by_semantic_score(fake_embeddings):
    vectors, _ = fake_embeddings
    # job vector is [1.0, 0.0]
    vectors["closely matching"] = np.array([1.0, 0.1])
    vectors["unrelated"] = np.array([0.0, 1.0])
    vectors["exact match"] = np.array([1.0, 0.0])
    pairs = [
        _pair(1, 1, "Low Match", "unrelated"),
        _pair(2, 2, "High Match", "exact match"),
        _pair(3, 3, "Mid Match", "closely matching"),
    ]

    result = rank_resumes_against_job(_job(), pairs)

    assert [c.candidate_name for c in result] == ["High Match", "Mid Match", "Low Match"]
    assert result[0].semantic_score >= result[1].semantic_score >= result[2].semantic_score


def test_rank_identical_scores_do_not_raise(fake_embeddings):
    vectors, _ = fake_embeddings
    vectors["same text"] = np.array([1.0, 0.0])
    pairs = [
        _pair(1, 1, "Candidate A", "same text"),
        _pair(2, 2, "Candidate B", "same text"),
    ]

    result = rank_resumes_against_job(_job(), pairs)

    assert len(result) == 2
    assert result[0].semantic_score == result[1].semantic_score


def test_rank_maps_resume_and_candidate_fields_correctly(fake_embeddings):
    vectors, _ = fake_embeddings
    vectors["resume text"] = np.array([1.0, 0.0])
    pairs = [_pair(resume_id=42, candidate_id=7, candidate_name="Jane Doe", raw_text="resume text")]

    result = rank_resumes_against_job(_job(job_id=99), pairs)

    assert result[0].resume_id == 42
    assert result[0].candidate_id == 7
    assert result[0].candidate_name == "Jane Doe"


def test_rank_computes_real_skill_score_from_faked_skills(fake_embeddings):
    # build_resume_embedding()/build_resume_skills() are faked, but
    # compute_skill_score() itself runs for real against a real JD
    # description string, proving the wiring (not just the mock).
    vectors, skills = fake_embeddings
    vectors["resume text"] = np.array([1.0, 0.0])
    skills["resume text"] = ResumeSkills(skills=("Python", "SQL", "Java"))
    pairs = [_pair(1, 1, "Jane Doe", "resume text")]
    job = _job(description="Looking for a Python and SQL developer")

    result = rank_resumes_against_job(job, pairs)

    assert result[0].skill_score == pytest.approx(2 / 3)


def test_rank_skill_score_is_zero_when_no_skills_extracted(fake_embeddings):
    vectors, _ = fake_embeddings
    vectors["resume text"] = np.array([1.0, 0.0])
    pairs = [_pair(1, 1, "Jane Doe", "resume text")]

    result = rank_resumes_against_job(_job(), pairs)

    assert result[0].skill_score == 0.0
