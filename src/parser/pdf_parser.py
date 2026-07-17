from pathlib import Path

import fitz  # PyMuPDF

from src.models.resume_models import ParsedResume


class PDFParseError(Exception):
    """Raised when a PDF cannot be parsed."""
    pass


def extract_text(pdf_path: Path | str) -> ParsedResume:
    """
    Extract raw text from a PDF resume and return a ParsedResume object.

    Parameters
    ----------
    pdf_path : Path | str
        Path to the PDF file.

    Returns
    -------
    ParsedResume
        Structured object containing the extracted resume information.

    Raises
    ------
    PDFParseError
        If the PDF cannot be opened or contains no extractable text.
    """

    pdf_path = Path(pdf_path)

    try:
        with fitz.open(pdf_path) as doc:
            page_count = len(doc)
            pages = [page.get_text() for page in doc]

    except Exception as exc:
        raise PDFParseError(
            f"Failed to parse '{pdf_path.name}': {exc}"
        ) from exc

    text = "\n".join(pages).strip()

    if not text:
        raise PDFParseError(
            f"'{pdf_path.name}' contains no extractable text (possibly scanned)."
        )

    return ParsedResume(
        filename=pdf_path.name,
        raw_text=text,
        page_count=page_count,
    )
