from datetime import datetime

import pytest

from src.extraction.contact_extractor import extract_contact_info
from src.models import ContactInfo, Section, SectionedResume, SectionType


def make_sectioned_resume(
    sections: tuple[Section, ...], filename: str = "resume.pdf", page_count: int = 1
) -> SectionedResume:
    return SectionedResume(
        filename=filename,
        page_count=page_count,
        processed_at=datetime.utcnow(),
        sections=sections,
    )


def make_header_section(content: str) -> Section:
    return Section(section_type=SectionType.HEADER, heading="", content=content)


def test_extracts_email_from_header():
    resume = make_sectioned_resume((make_header_section("Jane Doe\njane@example.com"),))

    result = extract_contact_info(resume)

    assert result.email == "jane@example.com"
    assert result.phone is None


def test_extracts_phone_dashes_format():
    resume = make_sectioned_resume((make_header_section("Jane Doe\n555-123-4567"),))

    result = extract_contact_info(resume)

    assert result.phone == "555-123-4567"


def test_extracts_phone_parens_format():
    resume = make_sectioned_resume((make_header_section("Jane Doe\n(555) 123-4567"),))

    result = extract_contact_info(resume)

    assert result.phone == "(555) 123-4567"


def test_extracts_phone_dots_format():
    resume = make_sectioned_resume((make_header_section("Jane Doe\n555.123.4567"),))

    result = extract_contact_info(resume)

    assert result.phone == "555.123.4567"


def test_extracts_phone_with_country_code():
    resume = make_sectioned_resume((make_header_section("Jane Doe\n+1 555-123-4567"),))

    result = extract_contact_info(resume)

    assert result.phone == "+1 555-123-4567"


def test_extracts_both_email_and_phone():
    resume = make_sectioned_resume(
        (make_header_section("Jane Doe\njane@example.com | 555-123-4567"),)
    )

    result = extract_contact_info(resume)

    assert result.email == "jane@example.com"
    assert result.phone == "555-123-4567"


def test_no_header_section_returns_none_for_both():
    experience = Section(
        section_type=SectionType.EXPERIENCE, heading="Experience", content="Did stuff."
    )
    resume = make_sectioned_resume((experience,))

    result = extract_contact_info(resume)

    assert result == ContactInfo(email=None, phone=None)


def test_empty_sections_returns_none_for_both():
    resume = make_sectioned_resume(())

    result = extract_contact_info(resume)

    assert result == ContactInfo(email=None, phone=None)


def test_header_with_no_contact_info_returns_none_for_both():
    resume = make_sectioned_resume((make_header_section("Jane Doe"),))

    result = extract_contact_info(resume)

    assert result.email is None
    assert result.phone is None


def test_multiple_emails_first_wins():
    resume = make_sectioned_resume(
        (make_header_section("jane@example.com, jane.doe@work.com"),)
    )

    result = extract_contact_info(resume)

    assert result.email == "jane@example.com"


def test_multiple_phones_first_wins():
    resume = make_sectioned_resume(
        (make_header_section("555-123-4567 or 555-987-6543"),)
    )

    result = extract_contact_info(resume)

    assert result.phone == "555-123-4567"


def test_email_case_preserved():
    resume = make_sectioned_resume((make_header_section("Jane.Doe@Example.COM"),))

    result = extract_contact_info(resume)

    assert result.email == "Jane.Doe@Example.COM"


def test_contact_info_is_immutable():
    resume = make_sectioned_resume((make_header_section("jane@example.com"),))
    result = extract_contact_info(resume)

    with pytest.raises(AttributeError):
        result.email = "changed@example.com"


def test_phone_like_digits_in_non_header_section_ignored():
    experience = Section(
        section_type=SectionType.EXPERIENCE,
        heading="Experience",
        content="Called 555-123-4567 references available.",
    )
    resume = make_sectioned_resume((experience,))

    result = extract_contact_info(resume)

    assert result.phone is None
