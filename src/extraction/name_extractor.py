from src.extraction.contact_extractor import EMAIL_PATTERN, PHONE_PATTERN
from src.models import CandidateName, SectionedResume, SectionType


def extract_name(resume: SectionedResume) -> CandidateName:
    """
    Extract the candidate's name from a SectionedResume's HEADER
    section only. Never raises: no HEADER section, an empty HEADER,
    or a first line that looks like an email/phone (rather than a
    name) yields None.

    Heuristic: the first non-empty line of the HEADER section is the
    name. Holds for every resume seen so far (name is conventionally
    the first thing on a resume), but is not verified against any
    formatting/positional signal, since plain extracted text carries
    none. A HEADER that opens with something other than a name (e.g.
    an address or objective statement) will misextract; no NLP
    dependency is used to guard against that, consistent with every
    other extraction/detection decision in this project.
    """

    header = next(
        (s for s in resume.sections if s.section_type == SectionType.HEADER),
        None,
    )
    if header is None:
        return CandidateName(name=None)

    first_line = next(
        (line.strip() for line in header.content.splitlines() if line.strip()),
        None,
    )
    if first_line is None:
        return CandidateName(name=None)

    if EMAIL_PATTERN.search(first_line) or PHONE_PATTERN.search(first_line):
        return CandidateName(name=None)

    return CandidateName(name=first_line)
