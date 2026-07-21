from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np

from src.embeddings.encoder import encode
from src.extraction.contact_extractor import extract_contact_info
from src.extraction.entry_extractor import extract_entries
from src.extraction.name_extractor import extract_name
from src.extraction.skills_extractor import extract_skills
from src.models import (
    CandidateName,
    ContactInfo,
    ResumeEntry,
    ResumeSkills,
    SectionedResume,
    SectionType,
    StructuredResume,
)
from src.parser.pdf_parser import extract_text
from src.preprocess.preprocessor import clean_text, preprocess
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


def prepare_resume_embedding_text(sections: SectionedResume) -> str:
    """
    Build the text representation of a resume that should be embedded
    for semantic matching against a Job Description.

    Deliberately excludes the HEADER section (name/email/phone/URLs) —
    contact information carries no semantic signal for matching
    against a JD's skills/responsibilities, and including it would
    dilute a short document's embedding with irrelevant proper nouns
    and numbers. All other sections are joined in document order.

    Not called from process_resume() — embeddings are computed on
    demand by a future consumer (e.g. /rank), not eagerly at ingestion
    time, since no storage/consumer exists yet (see PROJECT_BIBLE.md
    Section 11). Kept in src/pipeline.py rather than src/embeddings/
    so the Embeddings module itself stays a domain-agnostic
    text-to-vector encoder, per Section 7's "Embeddings - Generate
    vectors only."

    Never raises. Returns "" if the resume has no non-HEADER sections
    (e.g. a near-empty resume) — encode("") is a valid, if unhelpful,
    embedding, same as every other extractor's honest-empty-result
    convention in this codebase.
    """

    non_header = (s for s in sections.sections if s.section_type != SectionType.HEADER)
    return "\n\n".join(s.content for s in non_header)


def _reconstruct_sections(raw_text: str, filename: str = "") -> SectionedResume:
    """
    Shared re-derivation from a persisted Resume.raw_text back to
    SectionedResume: clean_text -> detect_sections.

    Factored out so every rank-time consumer (build_resume_embedding,
    build_resume_skills, and any future one) goes through the exact
    same reconstruction instead of each re-implementing it — the
    "pipeline divergence" risk ChatGPT cross-review flagged applies
    just as much to two *rank-time* helpers diverging from each other
    as it does to upload-time vs. rank-time diverging.

    filename/page_count are decorative metadata only (detect_sections()
    reads solely .normalized_text); page_count is not tracked for
    persisted resumes and defaults to 0 rather than a guessed value.
    """

    structured = StructuredResume(
        filename=filename,
        normalized_text=clean_text(raw_text),
        page_count=0,
        processed_at=datetime.utcnow(),
    )
    return detect_sections(structured)


def build_resume_embedding(raw_text: str, filename: str = "") -> np.ndarray:
    """
    The single, shared path from a resume's raw text to its semantic
    embedding: _reconstruct_sections -> prepare_resume_embedding_text
    -> encode.

    Exists so /rank (src/ranking.py) and any future caller reconstruct
    a resume's embedding identically, rather than each re-implementing
    this sequence — added per ChatGPT cross-review's "pipeline
    divergence" concern: two independently-maintained paths preparing
    resume text for embedding would risk silently drifting apart.
    """

    sectioned = _reconstruct_sections(raw_text, filename)
    text = prepare_resume_embedding_text(sectioned)
    return encode(text)


def build_resume_skills(raw_text: str, filename: str = "") -> ResumeSkills:
    """
    The single, shared path from a resume's raw text to its extracted
    skills list: _reconstruct_sections -> find SKILLS section ->
    extract_skills.

    Mirrors build_resume_embedding()'s shape for the same "shared
    orchestration, not duplicated" reason. Returns
    ResumeSkills(skills=()) if the resume has no SKILLS section at
    all — never raises.
    """

    sectioned = _reconstruct_sections(raw_text, filename)
    skills_section = next(
        (s for s in sectioned.sections if s.section_type == SectionType.SKILLS), None
    )
    return extract_skills(skills_section) if skills_section else ResumeSkills(skills=())


def build_resume_education(raw_text: str, filename: str = "") -> tuple[ResumeEntry, ...]:
    """
    The single, shared path from a resume's raw text to its extracted
    EDUCATION entries: _reconstruct_sections -> find EDUCATION section
    -> extract_entries.

    Mirrors build_resume_skills()'s shape. Returns () if the resume
    has no EDUCATION section at all — never raises.
    """

    sectioned = _reconstruct_sections(raw_text, filename)
    education_section = next(
        (s for s in sectioned.sections if s.section_type == SectionType.EDUCATION), None
    )
    return extract_entries(education_section) if education_section else ()


def build_resume_experience(raw_text: str, filename: str = "") -> tuple[ResumeEntry, ...]:
    """
    The single, shared path from a resume's raw text to its extracted
    EXPERIENCE entries: _reconstruct_sections -> find EXPERIENCE
    section -> extract_entries.

    Mirrors build_resume_skills()'s shape. Returns () if the resume
    has no EXPERIENCE section at all — never raises.
    """

    sectioned = _reconstruct_sections(raw_text, filename)
    experience_section = next(
        (s for s in sectioned.sections if s.section_type == SectionType.EXPERIENCE), None
    )
    return extract_entries(experience_section) if experience_section else ()
