from dataclasses import dataclass


@dataclass(frozen=True)
class ResumeEntry:
    """
    One structural entry within an EDUCATION or EXPERIENCE section,
    produced by date-anchored segmentation (see
    src/extraction/entry_extractor.py).

    title is the line the extractor found immediately preceding the
    recognized date line — an implementation rule, not an assumption
    that every resume places the institution/company there. None if
    no date anchor was found for this entry (see the extractor's
    zero-date fallback) or no non-blank line precedes the date.

    details holds everything else in the entry as raw, undecomposed
    text (degree, GPA, location, bullets, ...) — no reliable
    text-only delimiter exists to split those apart further.
    """

    title: str | None
    dates: str | None
    details: str
