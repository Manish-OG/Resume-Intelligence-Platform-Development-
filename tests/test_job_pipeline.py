import fitz
import pytest

from src.job_pipeline import parse_job_description
from src.parser.pdf_parser import PDFParseError


@pytest.fixture
def sample_jd_pdf(tmp_path):
    path = tmp_path / "job.pdf"
    doc = fitz.open()
    page = doc.new_page()
    lines = [
        "Senior Backend Engineer",
        "",
        "Requirements",
        "Education",
        "Bachelor's degree in Computer Science or related field",
        "Experience",
        "3+ years of software development experience",
    ]
    y = 72
    for line in lines:
        page.insert_text((72, y), line)
        y += 18
    doc.save(path)
    doc.close()
    return path


def test_parse_job_description_returns_cleaned_text(sample_jd_pdf):
    text = parse_job_description(sample_jd_pdf)

    assert "Senior Backend Engineer" in text
    assert "3+ years of software development experience" in text


def test_parse_job_description_does_not_impose_resume_section_structure(sample_jd_pdf):
    # This is the exact collision case identified during design review:
    # a JD's own "Education"/"Experience" requirement subheadings must
    # NOT get resume-section semantics imposed on them — parse_job_description()
    # returns plain text, not a SectionedResume, so there's nothing to mislabel.
    text = parse_job_description(sample_jd_pdf)

    assert isinstance(text, str)
    assert "Education" in text
    assert "Experience" in text


def test_parse_job_description_missing_file_raises_pdfparseerror():
    with pytest.raises(PDFParseError):
        parse_job_description("does-not-exist.pdf")


def test_parse_job_description_normalizes_whitespace(tmp_path):
    path = tmp_path / "messy.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Title")
    page.insert_text((72, 90), "Body")
    doc.save(path)
    doc.close()

    text = parse_job_description(path)

    # clean_text() strips document boundaries; result shouldn't have
    # leading/trailing whitespace.
    assert text == text.strip()
