from pathlib import Path

from src.parser.pdf_parser import extract_text
from src.preprocess.preprocessor import clean_text


def parse_job_description(pdf_path: Path | str) -> str:
    """
    Parse a Job Description PDF into cleaned text.

    Reuses extract_text() (generic PDF parsing) and clean_text()
    (generic text hygiene) from the resume pipeline — neither is
    resume-specific. Deliberately does NOT reuse detect_sections() or
    any resume extraction stage: those depend on a curated
    resume-section-heading vocabulary that collides with ordinary JD
    phrasing (a JD's own "Education"/"Experience" requirement
    subheadings would be mislabeled as resume sections by the exact
    same exact-match logic that works correctly for actual resumes).

    Raises PDFParseError if the PDF cannot be parsed (see
    src/parser/pdf_parser.py) — same failure mode as process_resume().
    """

    parsed = extract_text(pdf_path)
    return clean_text(parsed.raw_text)
