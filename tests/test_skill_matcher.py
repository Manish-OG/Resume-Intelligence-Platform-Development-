import pytest

from src.models import ResumeSkills
from src.scorer.skill_matcher import compute_skill_score, matched_skills


def test_compute_skill_score_all_matched():
    skills = ResumeSkills(skills=("Python", "SQL"))
    jd = "Looking for a developer skilled in Python and SQL"

    assert compute_skill_score(skills, jd) == 1.0


def test_compute_skill_score_none_matched():
    skills = ResumeSkills(skills=("COBOL", "Fortran"))
    jd = "Looking for a Python developer"

    assert compute_skill_score(skills, jd) == 0.0


def test_compute_skill_score_partial_match():
    skills = ResumeSkills(skills=("Python", "SQL", "Java"))
    jd = "Looking for a Python and SQL developer"

    assert compute_skill_score(skills, jd) == pytest.approx(2 / 3)


def test_compute_skill_score_case_insensitive():
    skills = ResumeSkills(skills=("python",))
    jd = "Experience with PYTHON required"

    assert compute_skill_score(skills, jd) == 1.0


def test_compute_skill_score_empty_skills_returns_zero():
    assert compute_skill_score(ResumeSkills(skills=()), "anything") == 0.0


def test_compute_skill_score_java_does_not_match_javascript():
    skills = ResumeSkills(skills=("Java",))
    jd = "Experience with JavaScript frameworks required"

    assert compute_skill_score(skills, jd) == 0.0


def test_compute_skill_score_sql_does_not_match_postgresql():
    skills = ResumeSkills(skills=("SQL",))
    jd = "Experience with PostgreSQL required"

    assert compute_skill_score(skills, jd) == 0.0


def test_compute_skill_score_handles_regex_special_characters():
    # C++ contains regex metacharacters; must be escaped, not treated
    # as a regex quantifier.
    skills = ResumeSkills(skills=("C++", "C#", ".NET"))
    jd = "Experience with C++, C#, and .NET required"

    assert compute_skill_score(skills, jd) == 1.0


def test_compute_skill_score_symbol_suffixed_skill_matches_naive_boundary_would_miss():
    # Empirically verified during design: naive \bC\+\+\b fails to
    # match "C++ " because \b requires a word/non-word transition,
    # and both the trailing "+" and the following space are non-word.
    skills = ResumeSkills(skills=("C++",))
    jd = "Familiar with C++ and Java"

    assert compute_skill_score(skills, jd) == 1.0


def test_compute_skill_score_dotted_skill_matches():
    skills = ResumeSkills(skills=("Node.js", "Draw.io"))
    jd = "Experience with Node.js development. Diagrams made with Draw.io."

    assert compute_skill_score(skills, jd) == 1.0


def test_compute_skill_score_duplicate_jd_mentions_count_once_per_skill():
    skills = ResumeSkills(skills=("Python",))
    jd = "Python, Python, and more Python required"

    assert compute_skill_score(skills, jd) == 1.0


def test_matched_skills_returns_only_matched_in_original_order():
    skills = ResumeSkills(skills=("Python", "COBOL", "SQL"))
    jd = "Looking for a Python and SQL developer"

    assert matched_skills(skills, jd) == ("Python", "SQL")


def test_matched_skills_empty_when_none_match():
    skills = ResumeSkills(skills=("COBOL",))
    jd = "Looking for a Python developer"

    assert matched_skills(skills, jd) == ()


def test_matched_skills_empty_for_empty_resume_skills():
    assert matched_skills(ResumeSkills(skills=()), "anything") == ()


def test_compute_skill_score_matches_len_matched_skills_ratio():
    skills = ResumeSkills(skills=("Python", "SQL", "Java"))
    jd = "Looking for a Python and SQL developer"

    assert compute_skill_score(skills, jd) == len(matched_skills(skills, jd)) / len(
        skills.skills
    )
