from src.extraction.entry_extractor import extract_entries
from src.models import ResumeEntry, Section, SectionType


def _section(content: str, section_type: SectionType = SectionType.EDUCATION) -> Section:
    return Section(section_type=section_type, heading="Education", content=content)


def test_extract_entries_real_multi_entry_education_layout():
    # Verbatim structure from samples/Manish_ResumeDA01.pdf's EDUCATION
    # section (hand-traced during design) — no blank lines between
    # entries, three entries anchored on standalone date lines.
    content = "\n".join(
        [
            "Birla Institute of Technology, Mesra",
            "Sep 2023 - 2027",
            "B. Tech Electronics and Communication Engineering : 7.45/10",
            "Ranchi, Jharkhand",
            "AISSCE",
            "February 2022",
            "Senior Secondary(CBSE) : 77.6%",
            "Jamshedpur, Jharkhand",
            "CISCE",
            "February 2020",
            "Secondary(ICSE) : 90.4%",
            "Chakradharpur, Jharkhand",
        ]
    )

    entries = extract_entries(_section(content))

    assert len(entries) == 3

    assert entries[0].title == "Birla Institute of Technology, Mesra"
    assert entries[0].dates == "Sep 2023 - 2027"
    assert "Ranchi, Jharkhand" in entries[0].details
    assert "AISSCE" not in entries[0].details

    assert entries[1].title == "AISSCE"
    assert entries[1].dates == "February 2022"
    assert "Jamshedpur, Jharkhand" in entries[1].details
    assert "CISCE" not in entries[1].details

    assert entries[2].title == "CISCE"
    assert entries[2].dates == "February 2020"
    assert "Chakradharpur, Jharkhand" in entries[2].details


def test_extract_entries_zero_dates_returns_single_fallback_entry():
    # Verbatim structure from the same resume's EXPERIENCE section: no
    # standalone date line anywhere.
    content = "\n".join(
        [
            "Electric Loco Shed, S.E.Railway, Tatanagar, Indian Railways",
            "Gained hands-on exposure to the internal working of electric locomotives.",
            "Studied the functionality of key components.",
        ]
    )

    entries = extract_entries(_section(content, SectionType.EXPERIENCE))

    assert len(entries) == 1
    assert entries[0].title is None
    assert entries[0].dates is None
    assert "Electric Loco Shed" in entries[0].details


def test_extract_entries_bullet_mentioning_a_year_does_not_create_a_boundary():
    content = "\n".join(
        [
            "Acme Corp",
            "Jan 2020 - Present",
            "Built a forecasting model using 2024 sales data",
        ]
    )

    entries = extract_entries(_section(content, SectionType.EXPERIENCE))

    assert len(entries) == 1
    assert entries[0].dates == "Jan 2020 - Present"
    assert "2024 sales data" in entries[0].details


def test_extract_entries_skips_blank_line_when_finding_title():
    content = "\n".join(["Google", "", "Jan 2020 - Present", "Software Engineer"])

    entries = extract_entries(_section(content, SectionType.EXPERIENCE))

    assert len(entries) == 1
    assert entries[0].title == "Google"
    assert entries[0].dates == "Jan 2020 - Present"


def test_extract_entries_date_as_first_line_has_no_title():
    content = "\n".join(["Jan 2020 - Present", "Google", "Software Engineer"])

    entries = extract_entries(_section(content, SectionType.EXPERIENCE))

    assert len(entries) == 1
    assert entries[0].title is None
    assert entries[0].dates == "Jan 2020 - Present"


def test_extract_entries_empty_section_returns_no_entries():
    entries = extract_entries(_section("   \n  "))

    assert entries == ()


def test_extract_entries_single_standalone_year():
    content = "\n".join(["Some Certification", "2022"])

    entries = extract_entries(_section(content, SectionType.CERTIFICATIONS))

    assert len(entries) == 1
    assert entries[0].title == "Some Certification"
    assert entries[0].dates == "2022"


def test_resume_entry_is_immutable():
    entry = ResumeEntry(title="Acme", dates="2020", details="")

    try:
        entry.title = "Changed"
        assert False, "expected AttributeError"
    except AttributeError:
        pass
