from datetime import date

import pytest

from src.models import ResumeEntry
from src.scorer.experience_matcher import compute_experience_score, describe_experience_match


def _entry(dates):
    return ResumeEntry(title="Company", dates=dates, details="did stuff")


def test_compute_experience_score_meets_requirement_exactly():
    entries = (_entry("2020 - 2023"),)
    jd = "3+ years of experience required"

    assert compute_experience_score(entries, jd) == 1.0


def test_compute_experience_score_exceeds_requirement_caps_at_one():
    entries = (_entry("2015 - 2023"),)
    jd = "3 years of experience required"

    assert compute_experience_score(entries, jd) == 1.0


def test_compute_experience_score_partial_match():
    entries = (_entry("2021 - 2023"),)
    jd = "4 years of experience required"

    assert compute_experience_score(entries, jd) == pytest.approx(2 / 4)


def test_compute_experience_score_sums_multiple_entries():
    entries = (_entry("2018 - 2020"), _entry("2021 - 2023"))
    jd = "4 years of experience required"

    assert compute_experience_score(entries, jd) == 1.0


def test_compute_experience_score_present_uses_today():
    entries = (_entry("2020 - Present"),)
    jd = "5 years of experience required"

    assert compute_experience_score(entries, jd, today=date(2025, 1, 1)) == 1.0


def test_compute_experience_score_no_dates_returns_zero():
    entries = (ResumeEntry(title=None, dates=None, details="did stuff"),)
    jd = "3+ years of experience required"

    assert compute_experience_score(entries, jd) == 0.0


def test_compute_experience_score_single_date_not_a_range_returns_zero():
    # A single date (e.g. a completion date) has no end point to
    # measure duration against — same shape as the real sample
    # resume's EDUCATION dates, hand-traced during design.
    entries = (_entry("February 2022"),)
    jd = "3+ years of experience required"

    assert compute_experience_score(entries, jd) == 0.0


def test_compute_experience_score_no_jd_requirement_returns_zero():
    entries = (_entry("2015 - 2023"),)
    jd = "Looking for a great engineer"

    assert compute_experience_score(entries, jd) == 0.0


def test_compute_experience_score_empty_entries_returns_zero():
    jd = "3+ years of experience required"

    assert compute_experience_score((), jd) == 0.0


def test_compute_experience_score_never_negative_for_reversed_range():
    entries = (_entry("2023 - 2020"),)
    jd = "3+ years of experience required"

    assert compute_experience_score(entries, jd) == 0.0


def test_describe_experience_match_returns_years_and_parseable_flag():
    entries = (_entry("2020 - 2023"),)
    jd = "4 years of experience required"

    assert describe_experience_match(entries, jd) == (3.0, 4, True)


def test_describe_experience_match_no_parseable_dates_at_all():
    # The real sample resume's actual EXPERIENCE case, hand-traced
    # during design (Session 18): zero standalone date lines anywhere.
    entries = (ResumeEntry(title=None, dates=None, details="did stuff"),)
    jd = "3+ years of experience required"

    assert describe_experience_match(entries, jd) == (0.0, 3, False)


def test_describe_experience_match_no_jd_requirement_returns_zero_required_years():
    entries = (_entry("2020 - 2023"),)
    jd = "Looking for a great engineer"

    assert describe_experience_match(entries, jd) == (3.0, 0, True)
