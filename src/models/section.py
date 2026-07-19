from dataclasses import dataclass
from enum import Enum


class SectionType(str, Enum):
    """
    Canonical resume section categories recognized by section detection.

    A str Enum keeps the taxonomy closed (typo-proof) while still
    comparing and serializing like a plain string.
    """

    HEADER = "header"
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    OTHER = "other"


@dataclass(frozen=True)
class Section:
    """
    A single detected section of a resume.

    heading is "" for HEADER (contact/name block before the first
    recognized heading) and OTHER (whole document when nothing was
    recognized).
    """

    section_type: SectionType
    heading: str
    content: str
