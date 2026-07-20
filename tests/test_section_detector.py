from datetime import datetime

import pytest

from src.models import SectionedResume, SectionType, StructuredResume
from src.preprocess.section_detector import detect_sections


def make_structured_resume(text: str, filename: str = "resume.pdf", page_count: int = 1) -> StructuredResume:
    return StructuredResume(
        filename=filename,
        normalized_text=text,
        page_count=page_count,
        processed_at=datetime.utcnow(),
    )


def test_detect_sections_returns_sectioned_resume():
    resume = make_structured_resume("Experience\nDid stuff.")

    result = detect_sections(resume)

    assert isinstance(result, SectionedResume)


def test_detect_sections_preserves_metadata():
    resume = make_structured_resume("Experience\nDid stuff.", filename="jane.pdf", page_count=2)

    result = detect_sections(resume)

    assert result.filename == "jane.pdf"
    assert result.page_count == 2


def test_detect_single_known_heading():
    resume = make_structured_resume("Education\nBSc Computer Science")

    result = detect_sections(resume)

    assert len(result.sections) == 1
    section = result.sections[0]
    assert section.section_type == SectionType.EDUCATION
    assert section.heading == "Education"
    assert section.content == "BSc Computer Science"


def test_detect_multiple_headings_in_order():
    text = (
        "Experience\n"
        "Backend Engineer at Acme\n"
        "\n"
        "Education\n"
        "BSc Computer Science\n"
        "\n"
        "Skills\n"
        "Python, FastAPI"
    )
    resume = make_structured_resume(text)

    result = detect_sections(resume)

    assert [s.section_type for s in result.sections] == [
        SectionType.EXPERIENCE,
        SectionType.EDUCATION,
        SectionType.SKILLS,
    ]
    assert result.sections[0].content == "Backend Engineer at Acme"
    assert result.sections[1].content == "BSc Computer Science"
    assert result.sections[2].content == "Python, FastAPI"


def test_heading_case_insensitivity():
    for heading in ("education", "Education", "EDUCATION"):
        resume = make_structured_resume(f"{heading}\nBSc Computer Science")
        result = detect_sections(resume)
        assert result.sections[0].section_type == SectionType.EDUCATION


def test_heading_trailing_colon_stripped():
    resume = make_structured_resume("Work Experience:\nBackend Engineer at Acme")

    result = detect_sections(resume)

    assert result.sections[0].section_type == SectionType.EXPERIENCE
    assert result.sections[0].heading == "Work Experience"


def test_content_line_containing_keyword_not_treated_as_heading():
    resume = make_structured_resume(
        "Experience\n5 years of experience in Python and Django"
    )

    result = detect_sections(resume)

    assert len(result.sections) == 1
    assert result.sections[0].content == "5 years of experience in Python and Django"


def test_header_block_before_first_heading():
    text = "Jane Doe\njane@example.com\n\nExperience\nBackend Engineer at Acme"
    resume = make_structured_resume(text)

    result = detect_sections(resume)

    assert result.sections[0].section_type == SectionType.HEADER
    assert result.sections[0].heading == ""
    assert result.sections[0].content == "Jane Doe\njane@example.com"
    assert result.sections[1].section_type == SectionType.EXPERIENCE


def test_no_header_section_when_document_starts_with_heading():
    resume = make_structured_resume("Experience\nBackend Engineer at Acme")

    result = detect_sections(resume)

    assert all(s.section_type != SectionType.HEADER for s in result.sections)


def test_zero_recognized_headings_falls_back_to_single_section():
    resume = make_structured_resume("Just a plain paragraph.\nMore text here.")

    result = detect_sections(resume)

    assert len(result.sections) == 1
    assert result.sections[0].section_type == SectionType.OTHER
    assert result.sections[0].content == "Just a plain paragraph.\nMore text here."


def test_empty_normalized_text_returns_no_sections():
    resume = make_structured_resume("")

    result = detect_sections(resume)

    assert result.sections == ()


def test_known_secondary_heading_gets_own_other_section():
    text = "Experience\nBackend Engineer at Acme\n\nAwards\nEmployee of the Month 2022\n\nEducation\nBSc CS"
    resume = make_structured_resume(text)

    result = detect_sections(resume)

    assert [s.section_type for s in result.sections] == [
        SectionType.EXPERIENCE,
        SectionType.OTHER,
        SectionType.EDUCATION,
    ]
    assert result.sections[1].heading == "Awards"
    assert result.sections[1].content == "Employee of the Month 2022"
    # The Awards content must not leak into the preceding Experience section.
    assert "Employee of the Month" not in result.sections[0].content


def test_other_alias_types_all_recognized():
    for heading in ("Publications", "Languages", "Volunteer Work", "Positions of Responsibility"):
        resume = make_structured_resume(f"Experience\nDid stuff.\n\n{heading}\nSome content.")
        result = detect_sections(resume)
        assert result.sections[-1].section_type == SectionType.OTHER
        assert result.sections[-1].heading == heading


def test_positions_of_responsibility_does_not_leak_into_preceding_skills_section():
    # Regression test: found via real-data verification of skills
    # extraction (Session 16) — "Positions of Responsibility" wasn't
    # in ALIASES, so it and everything after it (job titles, club
    # descriptions) bled into the preceding SKILLS section and got
    # misparsed as skill items. Real resume layout, not synthetic.
    text = (
        "Skills\n"
        "Languages: Python, SQL.\n\n"
        "Positions of Responsibility\n"
        "General Secretary, Sports Club\n"
        "Organized events for the club."
    )
    resume = make_structured_resume(text)

    result = detect_sections(resume)

    assert [s.section_type for s in result.sections] == [SectionType.SKILLS, SectionType.OTHER]
    assert result.sections[0].content == "Languages: Python, SQL."
    assert "General Secretary" not in result.sections[0].content


def test_truly_unknown_heading_still_treated_as_content():
    # Not in the curated OTHER alias list: absorbed into the open
    # section rather than mistakenly split off, since there is no
    # reliable way to tell a genuinely novel heading apart from a
    # short content line (e.g. a job title) without formatting cues
    # that plain extracted text does not carry.
    text = "Experience\nBackend Engineer\n\nPineapple Committee\nSome content"
    resume = make_structured_resume(text)

    result = detect_sections(resume)

    assert len(result.sections) == 1
    assert result.sections[0].section_type == SectionType.EXPERIENCE
    assert "Pineapple Committee" in result.sections[0].content


def test_sectioned_resume_is_immutable():
    resume = make_structured_resume("Experience\nDid stuff.")
    result = detect_sections(resume)

    with pytest.raises(AttributeError):
        result.filename = "changed.pdf"


def test_content_excludes_heading_line():
    resume = make_structured_resume("Education\nBSc Computer Science")

    result = detect_sections(resume)

    assert "Education" not in result.sections[0].content


def test_processed_at_is_set():
    resume = make_structured_resume("Experience\nDid stuff.")

    result = detect_sections(resume)

    assert isinstance(result.processed_at, datetime)
