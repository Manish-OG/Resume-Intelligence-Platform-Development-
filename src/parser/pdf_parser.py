from pathlib import Path

import fitz  # PyMuPDF


class PDFParseError(Exception):
    pass


def extract_text(pdf_path: Path | str) -> str:
    pdf_path = Path(pdf_path)
    try:
        with fitz.open(pdf_path) as doc:
            pages = [page.get_text() for page in doc]
    except Exception as exc:
        raise PDFParseError(f"Failed to parse {pdf_path.name}: {exc}") from exc

    text = "\n".join(pages).strip()
    if not text:
        raise PDFParseError(f"{pdf_path.name} contains no extractable text (possibly scanned)")
    return text
