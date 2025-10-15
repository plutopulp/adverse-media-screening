"""
Pydantic data models for person matching.

Defines models for matching query persons against article entities,
with conservative bias to avoid false negatives.
"""

from enum import Enum

from pydantic import BaseModel, Field

from app.models.llm_metadata import AnalyserMetadata

from .utils import extract_year_from_date_string, get_name_variations, normalise_name


class MatchDecision(str, Enum):
    """
    Match decision with conservative bias (prefer manual review).

    Prioritises recall over precision - better to flag uncertain matches
    for manual review than to miss a true match.
    """

    DEFINITE_MATCH = "definite_match"  # High confidence match
    PROBABLE_MATCH = "probable_match"  # Good match, minor discrepancies
    POSSIBLE_MATCH = "possible_match"  # Some signals match, needs review
    UNCERTAIN = "uncertain"  # Ambiguous, requires manual review
    NO_MATCH = "no_match"  # Clearly different person

    @classmethod
    def from_string(cls, value: str | None) -> "MatchDecision":
        """
        Convert string to MatchDecision enum, with fallback to UNCERTAIN.

        """
        if value is None:
            return cls.UNCERTAIN

        normalised = value.lower().replace(" ", "_")
        try:
            return cls(normalised)
        # Consider raising an error here to better understand what is being passed in
        except ValueError:
            return cls.UNCERTAIN


class SignalValue(str, Enum):
    """
    Three-state value for matching signals.

    Prevents bugs from bool | None where None is treated as False.
    Forces explicit handling of unknown/missing data.

    """

    MATCH = "match"
    NO_MATCH = "no_match"
    UNKNOWN = "unknown"  # Not enough data to determine

    @classmethod
    def from_string(cls, value: str | None) -> "SignalValue":
        """
        Convert string to SignalValue enum, with fallback to UNKNOWN.
        """
        if value is None:
            return cls.UNKNOWN

        normalised = value.lower().replace(" ", "_")
        try:
            return cls(normalised)
        # Consider raising an error here to better understand what is being passed in
        except ValueError:
            return cls.UNKNOWN


class QueryPerson(BaseModel):
    """
    Person to search for in articles (from analyst).

    Input: name + optional DOB only
    No role, location, or employment data is provided.

    Name is required, DOB is optional but strengthens matching.
    """

    model_config = {"validate_assignment": True}

    name: str  # Can be full name, partial, with titles, etc.
    date_of_birth: str | None = None  # Optional: "1980-01-15", "15 Jan 1980", "1980"

    # Derived/normalised fields (populated by normalise())
    normalised_name: str | None = None
    possible_nicknames: list[str] = []
    birth_year: int | None = None

    def normalise(self) -> None:
        """
        Normalise query person: normalise name, generate nicknames, parse DOB.

        Modifies self in-place. Call this before matching.

        """

        # Normalise name (analyst input has no titles)
        self.normalised_name = normalise_name(self.name)

        # Generate possible nicknames
        variations = get_name_variations(self.normalised_name)
        self.possible_nicknames = variations.get("all_variations", [])

        # Extract birth year from DOB
        if self.date_of_birth:
            self.birth_year = extract_year_from_date_string(self.date_of_birth)

    def to_prompt_fields(self) -> dict[str, str]:
        """
        Convert query person to prompt-ready string fields.

        """
        return {
            "query_name": self.name,
            "query_normalised_name": self.normalised_name or self.name,
            "query_nicknames": (
                ", ".join(self.possible_nicknames)
                if self.possible_nicknames
                else "None"
            ),
            "query_dob": self.date_of_birth or "Unknown",
            "query_birth_year": str(self.birth_year) if self.birth_year else "Unknown",
        }


class NameSignals(BaseModel):
    """Name matching signals."""

    exact_match: SignalValue
    fuzzy_similarity: float = Field(ge=0, le=1, description="0-1 similarity score")
    nickname_match: SignalValue = SignalValue.UNKNOWN
    partial_match: SignalValue = SignalValue.UNKNOWN
    title_stripped_match: SignalValue = SignalValue.UNKNOWN


class DemographicSignals(BaseModel):
    """Demographic matching signals (strongest identifiers)."""

    dob_exact_match: SignalValue = SignalValue.UNKNOWN
    birth_year_match: SignalValue = SignalValue.UNKNOWN
    age_discrepancy_years: int | None = None


class MatchSignals(BaseModel):
    """
    Individual matching signals evaluated.

    Query input: name + optional DOB only
    Matching signals: name variations + demographics
    Each signal is explicitly MATCH, NO_MATCH, or UNKNOWN.
    """

    name: NameSignals
    demographics: DemographicSignals

    @property
    def has_strong_signal(self) -> bool:
        """
        Computed property: True if name matches AND demographics match.

        Strong signal = exact name match + (DOB match OR birth year match)
        """
        return self.name.exact_match == SignalValue.MATCH and (
            self.demographics.dob_exact_match == SignalValue.MATCH
            or self.demographics.birth_year_match == SignalValue.MATCH
        )

    @property
    def has_contradiction(self) -> bool:
        """
        Computed property: True if signals contradict each other.

        Contradiction = name mismatch OR significant age discrepancy (>5 years)
        """
        name_mismatch = self.name.exact_match == SignalValue.NO_MATCH
        age_mismatch = (
            self.demographics.age_discrepancy_years is not None
            and self.demographics.age_discrepancy_years > 5
        )
        return name_mismatch or age_mismatch


class PersonMatch(BaseModel):
    """Result of matching query person against one entity."""

    # Entity reference (slim - just ID + name)
    entity_id: str
    entity_name: str

    # Match assessment
    decision: MatchDecision
    confidence: float = Field(ge=0, le=1)
    signals: MatchSignals

    # Audit trail
    reasoning: str
    evidence_for_match: list[str] = []
    evidence_against_match: list[str] = []
    is_primary_match: bool = False


# LLM output schema for structured parsing
class MatchAnalysisNameSignals(BaseModel):
    """Name signals from LLM output, with automatic enum conversion."""

    exact_match: str
    fuzzy_similarity: float = Field(ge=0, le=1)
    nickname_match: str
    partial_match: str
    title_stripped_match: str

    def to_name_signals(self) -> NameSignals:
        """Convert to NameSignals with proper enums."""
        return NameSignals(
            exact_match=SignalValue.from_string(self.exact_match),
            fuzzy_similarity=self.fuzzy_similarity,
            nickname_match=SignalValue.from_string(self.nickname_match),
            partial_match=SignalValue.from_string(self.partial_match),
            title_stripped_match=SignalValue.from_string(self.title_stripped_match),
        )


class MatchAnalysisDemographicSignals(BaseModel):
    """Demographic signals from LLM output, with automatic enum conversion."""

    dob_exact_match: str
    birth_year_match: str
    age_discrepancy_years: int | None = None

    def to_demographic_signals(self) -> DemographicSignals:
        """Convert to DemographicSignals with proper enums."""
        return DemographicSignals(
            dob_exact_match=SignalValue.from_string(self.dob_exact_match),
            birth_year_match=SignalValue.from_string(self.birth_year_match),
            age_discrepancy_years=self.age_discrepancy_years,
        )


class MatchAnalysis(BaseModel):
    """
    Structured output from LLM matching analysis.

    This is the raw LLM output schema. Use to_match_signals() to convert
    string signals to typed enums.
    """

    decision: str  # Will be converted to MatchDecision enum
    confidence: float = Field(ge=0, le=1)

    # Nested signal groups
    name: MatchAnalysisNameSignals
    demographics: MatchAnalysisDemographicSignals

    # Explanations
    reasoning: str
    evidence_for_match: list[str] = Field(default_factory=list)
    evidence_against_match: list[str] = Field(default_factory=list)

    def to_match_signals(self) -> MatchSignals:
        """Convert raw LLM signals to typed MatchSignals with enums."""
        return MatchSignals(
            name=self.name.to_name_signals(),
            demographics=self.demographics.to_demographic_signals(),
        )


class MatchingResult(BaseModel):
    """Overall matching result for article."""

    query_person: QueryPerson
    # Entity tracking
    entities_analysed: list[str] = []  # Entity IDs checked

    # Match results
    matches: list[PersonMatch]
    has_definite_match: bool
    has_any_match: bool
    requires_manual_review: bool
    primary_match: PersonMatch | None = None
    summary: str
    metadata: AnalyserMetadata

    def get_sentiment_targets(self) -> list[str]:
        """
        Get entity IDs that should undergo sentiment analysis.

        Returns definite matches if any exist, otherwise probable and possible matches.
        Skips uncertain and no_match results.
        """
        if self.has_definite_match:
            return [
                m.entity_id
                for m in self.matches
                if m.decision == MatchDecision.DEFINITE_MATCH
            ]
        return [
            m.entity_id
            for m in self.matches
            if m.decision
            in (MatchDecision.PROBABLE_MATCH, MatchDecision.POSSIBLE_MATCH)
        ]

    @staticmethod
    def generate_summary(matches: list[PersonMatch], query_name: str) -> str:
        """
        Generate human-readable summary of matching results.

        """
        if not matches:
            return f"No matches found for '{query_name}' in this article."

        if len(matches) == 1:
            m = matches[0]
            match m.decision:
                case MatchDecision.DEFINITE_MATCH:
                    return (
                        f"Definite match: '{query_name}' matches '{m.entity_name}' "
                        f"(confidence: {m.confidence:.0%})"
                    )
                case MatchDecision.PROBABLE_MATCH:
                    return (
                        f"Probable match: '{query_name}' likely matches '{m.entity_name}' "
                        f"(confidence: {m.confidence:.0%}) - Review recommended"
                    )
                case MatchDecision.POSSIBLE_MATCH:
                    return (
                        f"Possible match: '{query_name}' may match '{m.entity_name}' "
                        f"(confidence: {m.confidence:.0%}) - Manual review required"
                    )
                case MatchDecision.UNCERTAIN | MatchDecision.NO_MATCH:
                    return (
                        f"Uncertain: '{query_name}' and '{m.entity_name}' have conflicting "
                        f"signals (confidence: {m.confidence:.0%}) - Manual review required"
                    )

        # Multiple matches
        top_match = matches[0]
        return (
            f"Found {len(matches)} potential matches for '{query_name}'. "
            f"Top match: '{top_match.entity_name}' ({top_match.decision.value}, {top_match.confidence:.0%}). "
            f"Manual review recommended for disambiguation."
        )
