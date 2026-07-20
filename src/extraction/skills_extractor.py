from src.models import ResumeSkills, Section


def extract_skills(section: Section) -> ResumeSkills:
    """
    Extract a flat skills list from a resume's SKILLS section.

    Handles two real-world layouts with one rule: for each line, take
    the text after the first colon (category-prefixed, e.g.
    "Languages: Python, SQL, C++.") or the whole line if there's no
    colon (a flat list, e.g. "Python, SQL, Java, AWS"). Splits that
    segment on commas, stripping whitespace and a single trailing
    period per item (so "Draw.io." correctly becomes "Draw.io", not
    "Draw.io" missing its internal period — rstrip(".") only removes
    the single trailing sentence-ending period, not internal ones).

    Case-insensitively deduplicated (first-seen casing kept) so a
    skill listed twice doesn't distort downstream matching ratios.

    Never raises. Returns ResumeSkills(skills=()) for empty content.

    Accepted gap, no real data to validate against: a bullet-per-line
    layout ("• Python\\n• SQL") is not handled — each bulleted line
    would be treated as one comma-free item, including the bullet
    character, rather than split into individual skills.
    """

    seen: dict[str, str] = {}

    for line in section.content.splitlines():
        line = line.strip()
        if not line:
            continue

        before, sep, after = line.partition(":")
        segment = after if sep else line

        for raw_item in segment.split(","):
            cleaned = raw_item.strip().rstrip(".").strip()
            if not cleaned:
                continue
            key = cleaned.lower()
            if key not in seen:
                seen[key] = cleaned

    return ResumeSkills(skills=tuple(seen.values()))
