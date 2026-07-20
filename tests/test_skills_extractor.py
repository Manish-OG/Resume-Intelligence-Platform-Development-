from src.extraction.skills_extractor import extract_skills
from src.models import ResumeSkills, Section, SectionType


def _section(content: str) -> Section:
    return Section(SectionType.SKILLS, "Skills", content)


def test_extract_skills_real_sample_resume_layout():
    # Verbatim structure from samples/Manish_ResumeDA01.pdf's SKILLS
    # section (hand-traced during design).
    content = (
        "Languages: Python, SQL, C++, Verilog.\n"
        "Tools/Technologies: MS Excel, Github, Numpy, Notion, Power BI, Draw.io.\n"
        "Interpersonal Skills: Leadership, Team work, Critical thinking, Time management, Problem solving."
    )

    result = extract_skills(_section(content))

    assert result.skills == (
        "Python", "SQL", "C++", "Verilog",
        "MS Excel", "Github", "Numpy", "Notion", "Power BI", "Draw.io",
        "Leadership", "Team work", "Critical thinking", "Time management", "Problem solving",
    )


def test_extract_skills_flat_comma_list_no_category_prefix():
    result = extract_skills(_section("Python, SQL, Java, AWS"))

    assert result.skills == ("Python", "SQL", "Java", "AWS")


def test_extract_skills_strips_trailing_period_without_breaking_internal_ones():
    result = extract_skills(_section("Tools: Draw.io, Node.js."))

    assert result.skills == ("Draw.io", "Node.js")


def test_extract_skills_deduplicates_case_insensitively_keeping_first_casing():
    result = extract_skills(_section("Languages: Python, SQL\nTools: python, Excel"))

    assert result.skills == ("Python", "SQL", "Excel")


def test_extract_skills_empty_section_returns_empty_tuple():
    result = extract_skills(_section("   \n  "))

    assert result == ResumeSkills(skills=())


def test_extract_skills_whitespace_normalized():
    result = extract_skills(_section("Languages:   Python  ,   SQL  "))

    assert result.skills == ("Python", "SQL")


def test_resume_skills_is_immutable():
    result = ResumeSkills(skills=("Python",))

    try:
        result.skills = ("Changed",)
        assert False, "expected AttributeError"
    except AttributeError:
        pass
