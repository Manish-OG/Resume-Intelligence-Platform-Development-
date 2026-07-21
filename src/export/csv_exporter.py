import csv
import io
from dataclasses import asdict, fields

from src.ranking import RankedCandidate


def export_ranked_candidates_to_csv(
    candidates: list[RankedCandidate], extra_columns: dict[str, object] | None = None
) -> str:
    """
    Format a list of RankedCandidate as CSV text.

    Pure formatting: rows in, CSV text out. No FastAPI/SQLAlchemy
    dependency, and deliberately no awareness of what extra_columns'
    keys mean (e.g. "job_id") — that's the caller's concern, keeping
    this reusable if a future export ever wants different context
    columns instead (cross-reviewed with ChatGPT — see
    PROJECT_BIBLE.md Section 11).

    extra_columns is applied identically to every row, with its keys
    placed before RankedCandidate's own fields.

    Empty candidates -> header-only CSV (still valid, parseable
    output), not an empty string. Never raises.
    """

    extra_columns = extra_columns or {}
    fieldnames = list(extra_columns.keys()) + [f.name for f in fields(RankedCandidate)]

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for candidate in candidates:
        writer.writerow({**extra_columns, **asdict(candidate)})

    return buffer.getvalue()
