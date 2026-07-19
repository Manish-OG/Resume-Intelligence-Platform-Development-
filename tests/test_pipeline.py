import fitz
import pytest

from src.models import SectionType
from src.parser.pdf_parser import PDFParseError
from src.pipeline import PipelineResult, process_resume


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


def test_process_resume_missing_file_raises_pdfparseerror():
    with pytest.raises(PDFParseError):
        process_resume("does-not-exist.pdf")


def test_pipeline_result_is_immutable(sample_pdf):
    result = process_resume(sample_pdf)

    with pytest.raises(AttributeError):
        result.contact = None
