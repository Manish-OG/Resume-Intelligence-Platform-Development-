from dataclasses import dataclass
from pathlib import Path

from src.extraction.contact_extractor import extract_contact_info
from src.models import ContactInfo, SectionedResume
from src.parser.pdf_parser import extract_text
from src.preprocess.preprocessor import preprocess
from src.preprocess.section_detector import detect_sections


@dataclass(frozen=True)
class PipelineResult:
    """
    Terminal output of running a resume through parsing,
    preprocessing, section detection, and contact extraction.

    Not a per-stage domain model (see src/models/) since nothing
    downstream consumes it as input — it's a caller-convenience
    bundle of the pipeline's final outputs.
    """

    sections: SectionedResume
    contact: ContactInfo


def process_resume(pdf_path: Path | str) -> PipelineResult:
    """
    Run a resume PDF through the full pipeline: parse, preprocess,
    detect sections, extract contact info.

    Raises PDFParseError if the PDF cannot be parsed (see
    src/parser/pdf_parser.py); every later stage is guaranteed not
    to raise.
    """

    parsed = extract_text(pdf_path)
    structured = preprocess(parsed)
    sectioned = detect_sections(structured)
    contact = extract_contact_info(sectioned)

    return PipelineResult(sections=sectioned, contact=contact)
