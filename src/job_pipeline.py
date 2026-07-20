from pathlib import Path

import numpy as np

from src.embeddings.encoder import encode
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


def build_job_embedding(description: str) -> np.ndarray:
    """
    The single, shared path from a Job's description to its semantic
    embedding.

    Unlike the resume side (see src/pipeline.py's build_resume_embedding()),
    no re-derivation is needed: Job.description is already the fully
    cleaned text (parse_job_description() already ran clean_text() at
    ingestion time), and no JD section structure exists to strip
    (deliberate design — see PROJECT_BIBLE.md Section 11). Encode
    directly.
    """

    return encode(description)
