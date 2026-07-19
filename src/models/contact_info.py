from dataclasses import dataclass


@dataclass(frozen=True)
class ContactInfo:
    """
    Email and phone number extracted from a resume's HEADER section.

    Either field is None if no match was found.
    """

    email: str | None
    phone: str | None
