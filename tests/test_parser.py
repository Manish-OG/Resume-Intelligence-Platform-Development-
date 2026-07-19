from unittest.mock import MagicMock, patch
import fitz
import pytest

from src.models.parsed_resume import ParsedResume
from src.parser.pdf_parser import PDFParseError, extract_text


@pytest.fixture
def sample_pdf(tmp_path):
    path = tmp_path / "sample_resume.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Jane Doe - Backend Engineer")
    page.insert_text((72, 90), "Skills: Python, FastAPI")
    doc.save(path)
    doc.close()
    return path


def test_extract_text_missing_file():
    with pytest.raises(PDFParseError):
        extract_text("does-not-exist.pdf")

def test_extract_text_directory_raises(tmp_path):
    with pytest.raises(PDFParseError):
        extract_text(tmp_path)


def test_extract_text_empty_pdf_raises(tmp_path):
    path = tmp_path / "empty.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(path)
    doc.close()

    with pytest.raises(PDFParseError):
        extract_text(path)


def test_extract_text_returns_parsed_resume(sample_pdf):
    result = extract_text(sample_pdf)
    assert isinstance(result, ParsedResume)


def test_extract_text_filename(sample_pdf):
    result = extract_text(sample_pdf)
    assert result.filename == sample_pdf.name


def test_extract_text_page_count(sample_pdf):
    result = extract_text(sample_pdf)
    assert result.page_count == 1


def test_extract_text_raw_text_content(sample_pdf):
    result = extract_text(sample_pdf)
    assert "Jane Doe" in result.raw_text
    assert "FastAPI" in result.raw_text


def test_parsed_resume_is_immutable(sample_pdf):
    result = extract_text(sample_pdf)
    with pytest.raises(AttributeError):
        result.filename = "changed.pdf"

def test_extract_text_password_protected_pdf():
    mock_doc = MagicMock()
    mock_doc.__enter__.return_value = mock_doc
    mock_doc.__exit__.return_value = None
    mock_doc.needs_pass = True

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.is_file", return_value=True),
        patch("fitz.open", return_value=mock_doc),
    ):
        with pytest.raises(PDFParseError, match="password protected"):
            extract_text("protected.pdf")