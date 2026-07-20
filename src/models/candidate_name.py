from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateName:
    """
    Candidate name extracted from a resume's HEADER section.

    None if no HEADER section exists, or the first HEADER line looks
    like contact info rather than a name.
    """

    name: str | None
