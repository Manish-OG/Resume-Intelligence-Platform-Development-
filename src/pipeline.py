from dataclasses import dataclass
from pathlib import Path

from src.extraction.contact_extractor import extract_contact_info
from src.extraction.entry_extractor import extract_entries
from src.extraction.name_extractor import extract_name
from src.models import CandidateName, ContactInfo, ResumeEntry, SectionedResume, SectionType
from src.parser.pdf_parser import extract_text
from src.preprocess.preprocessor import preprocess
from src.preprocess.section_detector import detect_sections


@dataclass(frozen=True)
class PipelineResult:
    """
    Terminal output of running a resume through parsing,
    preprocessing, section detection, and extraction.

    Not a per-stage domain model (see src/models/) since nothing
    downstream consumes it as input — it's a caller-convenience
    bundle of the pipeline's final outputs.

    raw_text is the canonical (unnormalized) parser output — the same
    value as ParsedResume.raw_text. It exists here purely so a caller
    persisting a Resume row can reach it without re-parsing the PDF;
    intentionally excluded from the API response (see
    app/backend/api/schemas.py's UploadResumeResponse).

    education/experience are empty tuples if the resume has no
    EDUCATION/EXPERIENCE section at all; see
    src/extraction/entry_extractor.py for how entries within a
    present section are segmented.
    """

    sections: SectionedResume
    contact: ContactInfo
    name: CandidateName
    raw_text: str
    education: tuple[ResumeEntry, ...]
    experience: tuple[ResumeEntry, ...]


def process_resume(pdf_path: Path | str) -> PipelineResult:
    """
    Run a resume PDF through the full pipeline: parse, preprocess,
    detect sections, extract contact info, extract name, extract
    education/experience entries.

    Raises PDFParseError if the PDF cannot be parsed (see
    src/parser/pdf_parser.py); every later stage is guaranteed not
    to raise.
    """

    parsed = extract_text(pdf_path)
    structured = preprocess(parsed)
    sectioned = detect_sections(structured)
    contact = extract_contact_info(sectioned)
    name = extract_name(sectioned)

    education_section = next(
        (s for s in sectioned.sections if s.section_type == SectionType.EDUCATION), None
    )
    experience_section = next(
        (s for s in sectioned.sections if s.section_type == SectionType.EXPERIENCE), None
    )
    education = extract_entries(education_section) if education_section else ()
    experience = extract_entries(experience_section) if experience_section else ()

    return PipelineResult(
        sections=sectioned,
        contact=contact,
        name=name,
        raw_text=parsed.raw_text,
        education=education,
        experience=experience,
    )
