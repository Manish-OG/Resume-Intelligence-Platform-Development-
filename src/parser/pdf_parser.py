from pathlib import Path
import logging
import time

import fitz  # PyMuPDF

from src.models.parsed_resume import ParsedResume

logger = logging.getLogger(__name__)


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

    if not pdf_path.exists():
        logger.error("PDF '%s' does not exist.", pdf_path)
        raise PDFParseError(f"'{pdf_path}' does not exist.")

    if not pdf_path.is_file():
        logger.error("'%s' is not a file.", pdf_path)
        raise PDFParseError(f"'{pdf_path}' is not a file.")

    start_time = time.perf_counter()

    logger.info("Started parsing '%s'.", pdf_path.name)

    try:
        with fitz.open(pdf_path) as doc:
            if doc.needs_pass:
                logger.error(
                    "PDF '%s' is password protected.",
                    pdf_path.name,
                )
                raise PDFParseError(
                    f"'{pdf_path.name}' is password protected."
                )
            page_count = len(doc)

            logger.info(
                "Opened PDF '%s' (%d pages).",
                pdf_path.name,
                page_count,
            )

            pages = [page.get_text() for page in doc]

    except Exception as exc:
        logger.exception(
            "Failed to parse PDF '%s'.",
            pdf_path.name,
        )
        raise PDFParseError(
            f"Failed to parse '{pdf_path.name}': {exc}"
        ) from exc

    text = "\n".join(pages).strip()

    if not text:
        logger.warning(
            "PDF '%s' contains no extractable text (possibly scanned).",
            pdf_path.name,
        )
        raise PDFParseError(
            f"'{pdf_path.name}' contains no extractable text (possibly scanned)."
        )

    logger.info(
        "Successfully extracted text from '%s'.",
        pdf_path.name,
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "Completed parsing '%s' in %.2f ms.",
        pdf_path.name,
        elapsed_ms,
    )

    return ParsedResume(
        filename=pdf_path.name,
        raw_text=text,
        page_count=page_count,
    )