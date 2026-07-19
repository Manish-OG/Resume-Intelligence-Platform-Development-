import re
from datetime import datetime

from src.models import ParsedResume, StructuredResume


def preprocess(resume: ParsedResume) -> StructuredResume:
    """
    Convert a ParsedResume into a StructuredResume by applying
    the preprocessing pipeline.
    """

    text = clean_text(resume.raw_text)

    return StructuredResume(
        filename=resume.filename,
        normalized_text=text,
        page_count=resume.page_count,
        processed_at=datetime.utcnow(),
    )


def clean_text(text: str) -> str:
    """
    Apply safe, non-destructive text normalization.

    The goal is to normalize formatting without changing the
    semantic meaning of the resume.
    """

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Remove trailing whitespace from each line
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Trim document
    return text.strip() 