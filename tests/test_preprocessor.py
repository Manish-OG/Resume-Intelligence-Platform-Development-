from src.models import ParsedResume, StructuredResume
from src.preprocess.preprocessor import preprocess


def test_preprocess_returns_structured_resume():
    resume = ParsedResume(
        filename="resume.pdf",
        raw_text="Hello World",
        page_count=1,
    )

    result = preprocess(resume)

    assert isinstance(result, StructuredResume)

def test_preprocess_preserves_metadata():
    resume = ParsedResume(
        filename="resume.pdf",
        raw_text="Hello",
        page_count=2,
    )

    result = preprocess(resume)

    assert result.filename == resume.filename
    assert result.page_count == resume.page_count

def test_preprocess_collapses_blank_lines():
    resume = ParsedResume(
        filename="resume.pdf",
        raw_text="A\n\n\n\nB",
        page_count=1,
    )

    result = preprocess(resume)

    assert result.normalized_text == "A\n\nB"

def test_preprocess_removes_trailing_whitespace():
    resume = ParsedResume(
        filename="resume.pdf",
        raw_text="Hello   \nWorld    ",
        page_count=1,
    )

    result = preprocess(resume)

    assert result.normalized_text == "Hello\nWorld"