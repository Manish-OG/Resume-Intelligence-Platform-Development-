from dataclasses import dataclass


@dataclass(frozen=True)
class ResumeSkills:
    """
    Skills listed in a resume's SKILLS section, produced by heuristic
    comma-separated list extraction (see
    src/extraction/skills_extractor.py).

    Case-insensitively deduplicated, order-preserving (first-seen
    casing kept). Empty tuple if no SKILLS section exists or it has
    no recognizable comma-separated items.
    """

    skills: tuple[str, ...]
