from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ParsedResume:
    """
    Represents the output of the PDF parser.

    This object contains the raw extracted information from a resume
    before any preprocessing or NLP operations are performed. A failed
    parse raises PDFParseError rather than being represented here.
    """

    filename: str
    raw_text: str
    page_count: int
    parsed_at: datetime = field(default_factory=datetime.utcnow)