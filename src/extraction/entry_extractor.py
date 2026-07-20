import re

from src.models import ResumeEntry, Section

MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
YEAR = r"\d{4}"
SINGLE_DATE = rf"(?:{MONTH}\s+)?{YEAR}"

DATE_LINE_PATTERN = re.compile(
    rf"(?:{SINGLE_DATE}\s*(?:[-–—]|to)\s*(?:{SINGLE_DATE}|Present|Current))"
    rf"|{SINGLE_DATE}",
    re.IGNORECASE,
)


def extract_entries(section: Section) -> tuple[ResumeEntry, ...]:
    """
    Split a section's content into entries anchored on standalone date
    lines (re.fullmatch, not .search — a bullet that merely mentions a
    year should not trigger a false boundary).

    For each date line found, the nearest preceding non-blank line
    becomes that entry's title (an implementation rule, not an
    assumption that every resume places the institution/company
    there); everything between one entry's date and the next entry's
    title line becomes that entry's details, kept as raw undecomposed
    text.

    If no line in the section fullmatches a date, the whole section
    becomes a single entry with title=None, dates=None — an honest
    "couldn't segment this" result rather than a guess. An
    all-whitespace section yields zero entries. Never raises.

    Known limitation: assumes one date anchor per logical entry. An
    entry containing more than one standalone date-shaped line (e.g.
    a sub-timeline within a single job) will be over-segmented into
    multiple entries.
    """

    lines = [line.strip() for line in section.content.splitlines()]
    date_indices = [
        i for i, line in enumerate(lines) if line and DATE_LINE_PATTERN.fullmatch(line)
    ]

    if not date_indices:
        content = section.content.strip()
        if not content:
            return ()
        return (ResumeEntry(title=None, dates=None, details=content),)

    entries = []
    for n, date_idx in enumerate(date_indices):
        lower_bound = date_indices[n - 1] if n > 0 else -1
        title = None
        i = date_idx - 1
        while i > lower_bound:
            if lines[i]:
                title = lines[i]
                break
            i -= 1

        dates = lines[date_idx]

        detail_start = date_idx + 1
        detail_end = (
            date_indices[n + 1] - 1 if n + 1 < len(date_indices) else len(lines)
        )
        details = "\n".join(line for line in lines[detail_start:detail_end] if line)

        entries.append(ResumeEntry(title=title, dates=dates, details=details))

    return tuple(entries)
