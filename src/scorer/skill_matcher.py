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


def compute_skill_score(resume_skills: ResumeSkills, job_description: str) -> float:
    """
    Fraction of a candidate's declared skills that appear (as a
    case-insensitive, boundary-matched token) in a Job's description
    text.

    Answers "what fraction of this candidate's claimed skills are
    relevant to this JD" — NOT "what skills does the JD require that
    the candidate is missing". The latter needs an independently
    extracted JD skill list, which this project has no real JD data
    to validate a heuristic against (same constraint that blocked JD
    title extraction). Not attempted here; left to a future Feedback
    milestone if evidence ever supports it.

    Exact token matching only, no alias/synonym awareness: "Git" does
    not match "GitHub" in a JD, "SQL" does not match "PostgreSQL".
    Documented limitation, not a bug — an alias dictionary has the
    same unbounded-vocabulary problem this project already rejected
    for skill extraction itself (see Section 11).

    Returns 0.0 if the candidate has no extracted skills (0/0, not a
    ZeroDivisionError). Never raises.
    """

    if not resume_skills.skills:
        return 0.0

    matched = sum(
        1
        for skill in resume_skills.skills
        if re.search(
            _SKILL_BOUNDARY.format(re.escape(skill)), job_description, re.IGNORECASE
        )
    )

    return matched / len(resume_skills.skills)
