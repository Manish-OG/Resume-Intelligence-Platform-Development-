import re

from src.models import ResumeSkills

# Deliberately NOT \b: verified empirically (see PROJECT_BIBLE.md
# Section 11) that re.escape("C++") + \b fails to match "C++" in real
# text, because \b requires a word/non-word transition and both
# characters on either side of a symbol-suffixed skill (e.g. the
# trailing "+" in "C++" followed by a space) can be non-word, so no
# transition exists. This lookaround only cares whether the
# characters immediately outside the match are alphanumeric, so it
# correctly handles "C++", "C#", ".NET" as well as "Node.js"/"Draw.io"
# (which \b already handled correctly, since those start/end with
# alphanumeric characters).
_SKILL_BOUNDARY = "(?<![A-Za-z0-9]){}(?![A-Za-z0-9])"


def matched_skills(resume_skills: ResumeSkills, job_description: str) -> tuple[str, ...]:
    """
    The subset of a candidate's declared skills that appear (as a
    case-insensitive, boundary-matched token) in a Job's description
    text — in the candidate's original declared order.

    Exposed separately from compute_skill_score() (Session 22, for
    Feedback generation) so both consumers share one matching
    implementation instead of two independently-maintained copies of
    the same regex logic — the "pipeline divergence" risk this
    project has hit and fixed before (Section 11).

    Exact token matching only, no alias/synonym awareness: "Git" does
    not match "GitHub" in a JD, "SQL" does not match "PostgreSQL".
    Documented limitation, not a bug (Section 11).

    Never raises. Returns () if the candidate has no extracted skills.
    """

    return tuple(
        skill
        for skill in resume_skills.skills
        if re.search(
            _SKILL_BOUNDARY.format(re.escape(skill)), job_description, re.IGNORECASE
        )
    )


def compute_skill_score(resume_skills: ResumeSkills, job_description: str) -> float:
    """
    Fraction of a candidate's declared skills that matched_skills()
    finds in a Job's description text.

    Answers "what fraction of this candidate's claimed skills are
    relevant to this JD" — NOT "what skills does the JD require that
    the candidate is missing". The latter needs an independently
    extracted JD skill list, which this project has no real JD data
    to validate a heuristic against (same constraint that blocked JD
    title extraction). Not attempted here — see
    src/feedback/generator.py's missing_skills=None (Session 22).

    Returns 0.0 if the candidate has no extracted skills (0/0, not a
    ZeroDivisionError). Never raises.
    """

    if not resume_skills.skills:
        return 0.0

    return len(matched_skills(resume_skills, job_description)) / len(resume_skills.skills)
