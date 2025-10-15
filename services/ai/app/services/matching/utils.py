"""
Helper utilities for person matching.

Provides name normalisation, nickname variations, and date parsing.
"""

import re
from datetime import datetime

from nicknames import NickNamer

# Singleton NickNamer instance
_nn = NickNamer()

# Common titles to strip from entity names (not needed for analyst input)
TITLES = [
    "dr",
    "mr",
    "mrs",
    "ms",
    "miss",
    "sir",
    "prof",
    "professor",
    "sen",
    "senator",
    "rep",
]


def get_name_variations(name: str) -> dict[str, list[str]]:
    """
    Get nickname variations using the nicknames library.

    Args:
        name: Full name or single name part

    Returns:
        Dict with "all_variations" key containing list of nickname variations

    Example:
        >>> get_name_variations("Robert Smith")
        {"all_variations": ["bob", "rob", "bobby", "robert"]}
    """
    parts = name.lower().split()
    all_variations = set()

    for part in parts:
        # Get nicknames for this part (e.g., "robert" -> {"bob", "rob", "bobby"})
        nicks = _nn.nicknames_of(part)
        # Get canonical names for this part (e.g., "bob" -> {"robert"})
        canonicals = _nn.canonicals_of(part)
        all_variations.update(nicks | canonicals)

    return {"all_variations": list(all_variations)}


def normalise_name(name: str) -> str:
    """
    Normalize name: trim whitespace, collapse multiple spaces, title-case.

    Example:
        >>> normalize_name("  john   SMITH  ")
        "John Smith"
    """
    return " ".join(name.split()).title()


def strip_titles(name: str) -> str:
    """
    Remove common titles from name (for entity normalization).

    Example:
        >>> strip_titles("Dr. Jane Doe")
        "Jane Doe"
    """
    words = name.lower().split()
    filtered = [w for w in words if w.rstrip(".") not in TITLES]
    return " ".join(filtered).title()


def extract_year_from_date_string(dob: str) -> int | None:
    """
    Extract birth year from various date formats.

    Example:
        >>> extract_year_from_date_string("1980-01-15")
        1980
        >>> extract_year_from_date_string("15 Jan 1980")
        1980
        >>> extract_year_from_date_string("1980")
        1980
    """
    # Try parsing common formats
    for fmt in ["%Y-%m-%d", "%d %b %Y", "%Y"]:
        try:
            return datetime.strptime(dob, fmt).year
        except ValueError:
            continue

    # Fallback: extract 4-digit year with regex
    match = re.search(r"\b(19|20)\d{2}\b", dob)
    return int(match.group()) if match else None
