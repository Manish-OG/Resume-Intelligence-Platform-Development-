import fitz
import pytest

from src.models import Section, SectionedResume, SectionType
from src.parser.pdf_parser import PDFParseError
from src.pipeline import PipelineResult, prepare_resume_embedding_text, process_resume


@pytest.fixture
def sample_pdf(tmp_path):
    path = tmp_path / "resume.pdf"
    doc = fitz.open()
    page = doc.new_page()
    lines = [
        "Jane Doe",
        "jane@example.com | (555) 123-4567",
        "",
        "Experience",
        "Backend Engineer at Acme",
        "",
        "Education",
        "BSc Computer Science",
    ]
    y = 72
    for line in lines:
        page.insert_text((72, y), line)
        y += 18
    doc.save(path)
    doc.close()
    return path


def test_process_resume_returns_pipeline_result(sample_pdf):
    result = process_resume(sample_pdf)

    assert isinstance(result, PipelineResult)


def test_process_resume_produces_correct_sections(sample_pdf):
    result = process_resume(sample_pdf)

    section_types = [s.section_type for s in result.sections.sections]
    assert SectionType.HEADER in section_types
    assert SectionType.EXPERIENCE in section_types
    assert SectionType.EDUCATION in section_types


def test_process_resume_produces_correct_contact_info(sample_pdf):
    result = process_resume(sample_pdf)

    assert result.contact.email == "jane@example.com"
    assert result.contact.phone == "(555) 123-4567"


def test_process_resume_produces_correct_name(sample_pdf):
    result = process_resume(sample_pdf)

    assert result.name.name == "Jane Doe"


def test_process_resume_raw_text_matches_parser_output(sample_pdf):
    result = process_resume(sample_pdf)

    assert "Jane Doe" in result.raw_text
    assert "Backend Engineer at Acme" in result.raw_text


def test_process_resume_produces_fallback_education_experience_entries(sample_pdf):
    # Fixture has no date lines in EXPERIENCE/EDUCATION, so each
    # should fall back to one entry (see entry_extractor's zero-date
    # fallback), not raise or be empty.
    result = process_resume(sample_pdf)

    assert len(result.experience) == 1
    assert "Backend Engineer at Acme" in result.experience[0].details

    assert len(result.education) == 1
    assert "BSc Computer Science" in result.education[0].details


def test_process_resume_missing_file_raises_pdfparseerror():
    with pytest.raises(PDFParseError):
        process_resume("does-not-exist.pdf")


def test_pipeline_result_is_immutable(sample_pdf):
    result = process_resume(sample_pdf)

    with pytest.raises(AttributeError):
        result.contact = None


def _sectioned_resume(sections: list[Section]) -> SectionedResume:
    from datetime import datetime

    return SectionedResume(
        filename="resume.pdf",
        page_count=1,
        processed_at=datetime.utcnow(),
        sections=tuple(sections),
    )


def test_prepare_resume_embedding_text_excludes_header():
    sections = _sectioned_resume(
        [
            Section(SectionType.HEADER, "", "Jane Doe\njane@example.com"),
            Section(SectionType.EXPERIENCE, "Experience", "Backend Engineer at Acme"),
        ]
    )

    text = prepare_resume_embedding_text(sections)

    assert "jane@example.com" not in text
    assert "Jane Doe" not in text
    assert "Backend Engineer at Acme" in text


def test_prepare_resume_embedding_text_joins_sections_in_order():
    sections = _sectioned_resume(
        [
            Section(SectionType.HEADER, "", "Jane Doe"),
            Section(SectionType.EXPERIENCE, "Experience", "Backend Engineer"),
            Section(SectionType.EDUCATION, "Education", "BSc Computer Science"),
        ]
    )

    text = prepare_resume_embedding_text(sections)

    assert text.index("Backend Engineer") < text.index("BSc Computer Science")


def test_prepare_resume_embedding_text_header_only_returns_empty_string():
    sections = _sectioned_resume([Section(SectionType.HEADER, "", "Jane Doe")])

    text = prepare_resume_embedding_text(sections)

    assert text == ""


def test_prepare_resume_embedding_text_no_sections_returns_empty_string():
    text = prepare_resume_embedding_text(_sectioned_resume([]))

    assert text == ""


def test_prepare_resume_embedding_text_real_resume_end_to_end(sample_pdf):
    result = process_resume(sample_pdf)

    text = prepare_resume_embedding_text(result.sections)

    assert "Jane Doe" not in text
    assert "Backend Engineer at Acme" in text
    assert "BSc Computer Science" in text
