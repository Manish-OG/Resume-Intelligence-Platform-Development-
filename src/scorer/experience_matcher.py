import re
from datetime import date

from src.models import ResumeEntry

_RANGE_PATTERN = re.compile(
    r"(\d{4})\s*(?:[-–—]|to)\s*(\d{4}|present|current)", re.IGNORECASE
)

_REQUIRED_YEARS_PATTERN = re.compile(r"(\d+)\+?\s*years?", re.IGNORECASE)


def _entry_duration_years(dates: str | None, today: date) -> float:
    """
    Duration in years for one ResumeEntry.dates string, 0.0 if it
    isn't a parseable start-end range.

    Only a range ("2020 - 2023", "Sep 2023 - Present") yields a
    duration. A single date ("February 2022" — the shape a completion
    date or an EDUCATION entry typically takes, per the real sample
    resume hand-traced during design) has no end point to measure
    against, so it contributes 0.0 rather than guessing one.
    """

    if not dates:
        return 0.0

    match = _RANGE_PATTERN.search(dates)
    if not match:
        return 0.0

    start_year = int(match.group(1))
    end_token = match.group(2).lower()
    end_year = today.year if end_token in ("present", "current") else int(end_token)

    return max(0.0, float(end_year - start_year))


def _has_parseable_range(dates: str | None) -> bool:
    """Whether a ResumeEntry.dates string matched a start-end range at
    all, independent of the resulting duration — a genuine
    zero-length range ("2023 - 2023") is parseable but yields a 0.0
    duration, and must not be conflated with "no range found"."""

    return bool(dates) and _RANGE_PATTERN.search(dates) is not None


def describe_experience_match(
    experience_entries: tuple[ResumeEntry, ...],
    job_description: str,
    today: date | None = None,
) -> tuple[float, int, bool]:
    """
    (total_years, required_years, any_parseable_dates) — the
    intermediate values compute_experience_score() derives before
    collapsing them to a single float.

    Exposed separately from compute_experience_score() (Session 22,
    for Feedback generation): total_years == 0.0 means two different
    things depending on any_parseable_dates — "every EXPERIENCE entry
    had a genuinely zero-length or unparseable date range" (honest
    gap; e.g. no standalone date lines at all, the real sample
    resume's actual case) vs. a hypothetical future heuristic that
    could produce a true zero-length range. Feedback needs to tell
    these apart to stay honest ("we couldn't verify your experience
    duration" is a different claim than "you have zero years of
    experience"); a bare float can't. required_years == 0 means the
    JD stated no recognizable years requirement.

    Never raises.
    """

    today = today or date.today()

    total_years = sum(_entry_duration_years(e.dates, today) for e in experience_entries)
    any_parseable_dates = any(_has_parseable_range(e.dates) for e in experience_entries)

    required_match = _REQUIRED_YEARS_PATTERN.search(job_description)
    required_years = int(required_match.group(1)) if required_match else 0

    return total_years, required_years, any_parseable_dates


def compute_experience_score(
    experience_entries: tuple[ResumeEntry, ...],
    job_description: str,
    today: date | None = None,
) -> float:
    """
    How well a candidate's total years of experience meets a JD's
    stated years-of-experience requirement — derived from
    describe_experience_match()'s (total_years, required_years, ...).

    Hand-traced against the real sample resume during design: its
    EXPERIENCE section contains zero standalone date lines at all
    (see PROJECT_BIBLE.md Section 11), so this function will correctly
    and honestly return 0.0 for it — a real, documented limitation of
    the source data, not a defect here.

    Returns 0.0 if the JD states no recognizable years requirement
    (nothing to compare against — consistent with
    compute_skill_score's "no comparable data -> 0.0" convention,
    never a special sentinel). Score is total_years / required_years,
    capped at 1.0. Never raises.
    """

    total_years, required_years, _ = describe_experience_match(
        experience_entries, job_description, today
    )
    if required_years <= 0:
        return 0.0

    return min(1.0, total_years / required_years)
