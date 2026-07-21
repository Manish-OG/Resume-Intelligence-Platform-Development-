import pytest

from src.models import ResumeEntry
from src.scorer.education_matcher import compute_education_score, describe_education_match


def _entry(title, details):
    return ResumeEntry(title=title, dates="2020 - 2024", details=details)


def test_compute_education_score_meets_requirement_exactly():
    entries = (_entry("State University", "Bachelor of Science in Computer Science"),)
    jd = "Bachelor's degree required"

    assert compute_education_score(entries, jd) == 1.0


def test_compute_education_score_exceeds_requirement():
    entries = (_entry("State University", "Master of Science in Computer Science"),)
    jd = "Bachelor's degree required"

    assert compute_education_score(entries, jd) == 1.0


def test_compute_education_score_below_requirement_partial_credit():
    entries = (_entry("State University", "Bachelor of Science in Computer Science"),)
    jd = "Master's degree required"

    assert compute_education_score(entries, jd) == pytest.approx(2 / 3)


def test_compute_education_score_real_resume_btech_format_recognized():
    # Exact heading/phrasing hand-traced from the real sample resume
    # during design: "B. Tech Electronics and Communication Engineering".
    entries = (
        ResumeEntry(
            title="Birla Institute of Technology, Mesra",
            dates="Sep 2023 - 2027",
            details="B. Tech Electronics and Communication Engineering : 7.45/10",
        ),
    )
    jd = "Bachelor's degree in Electronics required"

    assert compute_education_score(entries, jd) == 1.0


def test_compute_education_score_no_recognized_degree_in_resume_returns_zero():
    entries = (_entry("Central High School", "Senior Secondary (CBSE) : 77.6%"),)
    jd = "Bachelor's degree required"

    assert compute_education_score(entries, jd) == 0.0


def test_compute_education_score_no_jd_requirement_returns_zero():
    entries = (_entry("State University", "Bachelor of Science in Computer Science"),)
    jd = "Looking for a great engineer"

    assert compute_education_score(entries, jd) == 0.0


def test_compute_education_score_empty_entries_returns_zero():
    jd = "Bachelor's degree required"

    assert compute_education_score((), jd) == 0.0


def test_compute_education_score_case_insensitive():
    entries = (_entry("State University", "BACHELOR of science"),)
    jd = "bachelor's degree required"

    assert compute_education_score(entries, jd) == 1.0


def test_compute_education_score_bare_be_word_does_not_false_positive():
    # "be"/"me" are common English words; the abbreviation patterns
    # require literal dots (b.e./m.e.) specifically to avoid this,
    # verified empirically during design.
    entries = (_entry("State University", "Coursework will be evaluated by faculty"),)
    jd = "Candidates must be available to start immediately"

    assert compute_education_score(entries, jd) == 0.0


def test_compute_education_score_phd_recognized():
    entries = (_entry("State University", "Ph.D. in Computer Science"),)
    jd = "PhD required"

    assert compute_education_score(entries, jd) == 1.0


def test_describe_education_match_returns_candidate_and_required_levels():
    entries = (_entry("State University", "Bachelor of Science in Computer Science"),)
    jd = "Master's degree required"

    assert describe_education_match(entries, jd) == (2, 3)


def test_describe_education_match_zero_means_not_found_on_each_side():
    no_degree_entries = (_entry("Central High School", "Senior Secondary (CBSE)"),)
    assert describe_education_match(no_degree_entries, "Bachelor's degree required") == (0, 2)
    assert describe_education_match((), "Looking for a great engineer") == (0, 0)
