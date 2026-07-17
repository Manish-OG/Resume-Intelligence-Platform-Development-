from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ParsedResume:
    """
    Represents the output of the PDF parser.

    This object contains the raw extracted information from a resume
    before any preprocessing or NLP operations are performed.
    """

    filename: str
    raw_text: str
    page_count: int
    parsed_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "SUCCESS"
    errors: list[str] = field(default_factory=list)