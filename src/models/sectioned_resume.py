from dataclasses import dataclass
from datetime import datetime

from src.models.section import Section


@dataclass(frozen=True)
class SectionedResume:
    """
    Represents a resume broken into detected sections, produced by
    the section detection stage.

    This model serves as the contract between section detection and
    downstream AI components that need section-aware content.
    """

    filename: str
    page_count: int
    processed_at: datetime
    sections: tuple[Section, ...]
