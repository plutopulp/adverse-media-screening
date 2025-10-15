"""Person matching package."""

from .matcher import PersonMatcher
from .models import (
    MatchDecision,
    MatchingResult,
    MatchSignals,
    PersonMatch,
    QueryPerson,
    SignalValue,
)

__all__ = [
    "MatchDecision",
    "SignalValue",
    "QueryPerson",
    "MatchSignals",
    "PersonMatch",
    "MatchingResult",
    "PersonMatcher",
]
