import re

from src.models import ContactInfo, SectionedResume, SectionType

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

PHONE_PATTERN = re.compile(
    r"(?:\+?1[-.\s]?)?"      # optional country code (+1 or 1)
    r"(?:\(\d{3}\)|\d{3})"   # area code: (123) or 123
    r"[-.\s]?\d{3}[-.\s]?\d{4}"
)


def extract_contact_info(resume: SectionedResume) -> ContactInfo:
    """
    Extract email and phone number from a SectionedResume's HEADER
    section only. Never raises: no HEADER section, or no match,
    yields None for that field.

    If multiple emails or phones appear in the header, the first
    (leftmost) match is returned; no attempt is made to disambiguate
    a personal number/address from a secondary one, or from
    phone-shaped digits embedded in a URL (e.g. a LinkedIn profile
    ID). Phone matching covers common NANP formats only (with/without
    "+1", with parens/dashes/dots/spaces as separators); non-NANP
    international formats and extensions are not recognized.
    """

    header = next(
        (s for s in resume.sections if s.section_type == SectionType.HEADER),
        None,
    )
    if header is None:
        return ContactInfo(email=None, phone=None)

    email_match = EMAIL_PATTERN.search(header.content)
    phone_match = PHONE_PATTERN.search(header.content)

    return ContactInfo(
        email=email_match.group(0) if email_match else None,
        phone=phone_match.group(0) if phone_match else None,
    )
