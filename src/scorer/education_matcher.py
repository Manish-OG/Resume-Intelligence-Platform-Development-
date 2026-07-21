import re

from src.models import ResumeEntry

# Ordered lowest -> highest. A small, evidence-based vocabulary, not
# an attempt at a complete degree taxonomy — same unbounded-vocabulary
# problem already accepted for skill matching (PROJECT_BIBLE.md
# Section 11). Two-letter forms with no required punctuation (bare
# "BE"/"ME"/"BA"/"MS" ...) are deliberately excluded: empirically,
# "be"/"me" collide with common English words ("will be considered",
# "contact me") even with \b word-boundary anchoring, since those are
# real standalone words. "B.E."/"M.E." require both literal dots to
# avoid that collision; "tech"/"sc" are not real English words so
# their dots stay optional.
_DEGREE_LEVELS: tuple[tuple[int, re.Pattern], ...] = (
    (1, re.compile(r"\bdiploma\b|\bassociate(?:'s)?\s+degree\b", re.IGNORECASE)),
    (
        2,
        re.compile(
            r"\bbachelor(?:'s)?\b|\bb\.?\s*tech\b|\bb\.e\.|\bb\.?\s*sc\.?\b",
            re.IGNORECASE,
        ),
    ),
    (
        3,
        re.compile(
            r"\bmaster(?:'s)?\b|\bm\.?\s*tech\b|\bm\.e\.|\bm\.?\s*sc\.?\b|\bmba\b",
            re.IGNORECASE,
        ),
    ),
    (4, re.compile(r"\bph\.?\s*d\.?\b|\bdoctorate\b|\bdoctoral\b", re.IGNORECASE)),
)


def _highest_level(text: str) -> int:
    """Highest recognized degree level mentioned in text, 0 if none."""

    found = [level for level, pattern in _DEGREE_LEVELS if pattern.search(text)]
    return max(found, default=0)


def describe_education_match(
    education_entries: tuple[ResumeEntry, ...], job_description: str
) -> tuple[int, int]:
    """
    (candidate_level, required_level) — the two intermediate values
    compute_education_score() derives before collapsing them to a
    single float. 0 means "no recognized level found" on that side
    (candidate: no recognized degree; JD: no stated requirement) — not
    that a level of 0 exists in the vocabulary.

    Exposed separately from compute_education_score() (Session 22,
    for Feedback generation): a candidate_level of 0 and a
    required_level of 0 both collapse to the same 0.0 score, but they
    mean different things ("this candidate has no recognized degree"
    vs. "this JD stated no degree requirement") — Feedback needs to
    tell those apart to stay honest; a bare float can't.

    Candidate side: the highest degree level recognized anywhere
    across every EDUCATION entry's title + details text (an ongoing,
    not-yet-completed degree still counts — hand-traced against the
    real sample resume, whose in-progress "B. Tech" entry should
    count as bachelor-level even though it lists an end date of
    2027). Sub-degree qualifications the curated vocabulary doesn't
    recognize (e.g. secondary-school certificates) simply don't
    contribute a level, honestly.

    JD side: same sidestep already used for skill matching and
    experience matching (Section 11) — no independent JD structure is
    extracted. Instead, search job_description text directly for the
    same degree-level vocabulary and take the highest level mentioned
    as the requirement.

    Never raises.
    """

    candidate_text = "\n".join(f"{e.title or ''} {e.details}" for e in education_entries)
    return _highest_level(candidate_text), _highest_level(job_description)


def compute_education_score(
    education_entries: tuple[ResumeEntry, ...], job_description: str
) -> float:
    """
    How well a candidate's highest attained degree level meets a JD's
    stated degree-level requirement — derived from
    describe_education_match()'s (candidate_level, required_level).

    Returns 0.0 if the candidate has no recognized degree level (0/N
    is an honest "no signal", not a guess), and 0.0 if the JD states
    no recognizable requirement (nothing to compare against —
    consistent with compute_skill_score's/compute_experience_score's
    "no comparable data -> 0.0" convention). 1.0 if the candidate
    meets or exceeds the required level; otherwise a partial
    candidate_level / required_level ratio. Never raises.
    """

    candidate_level, required_level = describe_education_match(
        education_entries, job_description
    )
    if candidate_level == 0 or required_level == 0:
        return 0.0

    if candidate_level >= required_level:
        return 1.0

    return candidate_level / required_level
