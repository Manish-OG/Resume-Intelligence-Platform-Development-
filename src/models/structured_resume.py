from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class StructuredResume:
    """
    Represents a cleaned and normalized resume produced by the
    preprocessing pipeline.

    This model serves as the contract between the preprocessing
    module and downstream AI components.
    """

    filename: str
    normalized_text: str
    page_count: int
    processed_at: datetime