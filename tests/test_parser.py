import pytest

from src.parser.pdf_parser import PDFParseError, extract_text


def test_extract_text_missing_file():
    with pytest.raises(PDFParseError):
        extract_text("does-not-exist.pdf")
