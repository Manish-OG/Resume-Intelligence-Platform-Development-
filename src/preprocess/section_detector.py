import re
from datetime import datetime

from src.models import Section, SectionedResume, SectionType, StructuredResume

ALIASES: dict[SectionType, set[str]] = {
    SectionType.SUMMARY: {
        "summary",
        "professional summary",
        "objective",
        "career objective",
        "profile",
    },
    SectionType.EXPERIENCE: {
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
    },
    SectionType.EDUCATION: {
        "education",
        "academic background",
    },
    SectionType.SKILLS: {
        "skills",
        "technical skills",
        "core competencies",
        "key skills",
    },
    SectionType.PROJECTS: {
        "projects",
        "personal projects",
        "academic projects",
    },
    SectionType.CERTIFICATIONS: {
        "certifications",
        "certificates",
        "licenses and certifications",
    },
    SectionType.OTHER: {
        "awards",
        "awards and honors",
        "honors",
        "honors and awards",
        "publications",
        "languages",
        "volunteer work",
        "volunteering",
        "interests",
        "hobbies",
        "references",
        "activities",
        "leadership",
        "affiliations",
    },
}


def _normalize_for_matching(line: str) -> str:
    normalized = line.strip()
    if normalized.endswith(":"):
        normalized = normalized[:-1].strip()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.lower()


def _strip_heading_text(line: str) -> str:
    heading = line.strip()
    if heading.endswith(":"):
        heading = heading[:-1].strip()
    return re.sub(r"\s+", " ", heading)


def _match_heading(line: str) -> SectionType | None:
    normalized = _normalize_for_matching(line)
    if not normalized:
        return None
    for section_type, aliases in ALIASES.items():
        if normalized in aliases:
            return section_type
    return None


def detect_sections(resume: StructuredResume) -> SectionedResume:
    """
    Detect common resume sections (Experience, Education, Skills, etc.)
    from a StructuredResume's normalized text.

    Detection is heuristic (exact-match against curated heading
    keywords) and never raises. OTHER covers two distinct cases:
    common secondary headings (Awards, Publications, Languages, etc.)
    get their own OTHER-typed section with a real heading; a resume
    with no recognized headings at all falls back to a single
    OTHER section with an empty heading. Empty text produces no
    sections.
    """

    lines = resume.normalized_text.split("\n")

    sections: list[Section] = []
    current_type: SectionType | None = None
    current_heading = ""
    buffer: list[str] = []
    any_heading_matched = False

    def flush() -> None:
        content = "\n".join(buffer).strip()
        if current_type is not None and content:
            sections.append(
                Section(
                    section_type=current_type,
                    heading=current_heading,
                    content=content,
                )
            )

    for line in lines:
        matched_type = _match_heading(line)
        if matched_type is not None:
            flush()
            any_heading_matched = True
            current_type = matched_type
            current_heading = _strip_heading_text(line)
            buffer = []
        else:
            if current_type is None:
                current_type = SectionType.HEADER
            buffer.append(line)

    if not any_heading_matched:
        # Nothing recognized in the whole document: the trailing buffer
        # is un-sectioned content, not a contact/header block.
        current_type = SectionType.OTHER
        current_heading = ""
    flush()

    return SectionedResume(
        filename=resume.filename,
        page_count=resume.page_count,
        processed_at=datetime.utcnow(),
        sections=tuple(sections),
    )
