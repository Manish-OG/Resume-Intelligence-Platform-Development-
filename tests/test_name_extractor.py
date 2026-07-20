from datetime import datetime

from src.extraction.name_extractor import extract_name
from src.models import CandidateName, Section, SectionedResume, SectionType


def _resume(sections: list[Section]) -> SectionedResume:
    return SectionedResume(
        filename="resume.pdf",
        page_count=1,
        processed_at=datetime.utcnow(),
        sections=tuple(sections),
    )


def test_extract_name_from_first_header_line():
    resume = _resume(
        [
            Section(
                section_type=SectionType.HEADER,
                heading="",
                content="Jane Doe\njane@example.com | (555) 123-4567",
            )
        ]
    )

    result = extract_name(resume)

    assert result == CandidateName(name="Jane Doe")


def test_extract_name_no_header_section_returns_none():
    resume = _resume(
        [Section(section_type=SectionType.EXPERIENCE, heading="Experience", content="...")]
    )

    result = extract_name(resume)

    assert result.name is None


def test_extract_name_empty_header_content_returns_none():
    resume = _resume([Section(section_type=SectionType.HEADER, heading="", content="   \n  ")])

    result = extract_name(resume)

    assert result.name is None


def test_extract_name_header_starting_with_email_returns_none():
    resume = _resume(
        [
            Section(
                section_type=SectionType.HEADER,
                heading="",
                content="jane@example.com\nJane Doe",
            )
        ]
    )

    result = extract_name(resume)

    assert result.name is None


def test_extract_name_header_starting_with_phone_returns_none():
    resume = _resume(
        [
            Section(
                section_type=SectionType.HEADER,
                heading="",
                content="(555) 123-4567\nJane Doe",
            )
        ]
    )

    result = extract_name(resume)

    assert result.name is None


def test_extract_name_skips_leading_blank_lines():
    resume = _resume(
        [
            Section(
                section_type=SectionType.HEADER,
                heading="",
                content="\n\nJane Doe\njane@example.com",
            )
        ]
    )

    result = extract_name(resume)

    assert result.name == "Jane Doe"


def test_candidate_name_is_immutable():
    result = CandidateName(name="Jane Doe")

    try:
        result.name = "Changed"
        assert False, "expected AttributeError"
    except AttributeError:
        pass
