"""
Pydantic data models for credibility assessment.

Defines credibility signals and overall assessment structure
for evaluating article reliability.
"""

from enum import Enum

from pydantic import BaseModel, Field

from app.models.llm_metadata import AnalyserMetadata


class SignalValue(str, Enum):
    """Three-state signal value for credibility indicators."""

    YES = "yes"
    NO = "no"
    UNSURE = "unsure"


class CredibilitySignals(BaseModel):
    """
    Individual credibility signals extracted from article.

    Based on journalistic quality indicators from credibility research.
    Each signal is assessed as YES, NO, or UNSURE.
    """

    # Positive signals (indicators of good journalism)
    has_attribution: (
        SignalValue  # Named sources (court docs, regulatory bodies, officials)
    )
    has_multiple_sources: SignalValue  # Multiple independent sources for serious claims
    distinguishes_fact_allegation: (
        SignalValue  # Clearly marks allegations vs. presenting as fact
    )
    has_named_quotes: SignalValue  # Direct quotes from named persons/institutions
    has_balanced_coverage: SignalValue  # Includes subject responses or counterpoints
    is_internally_consistent: (
        SignalValue  # No contradictions, timeline errors, logical gaps
    )
    has_technical_detail: (
        SignalValue  # Specific dates, amounts, jurisdictions, legal references
    )
    uses_hedging_language: (
        SignalValue  # Appropriate "allegedly", "reportedly" when uncertain
    )

    # Negative signals (red flags indicating potential unreliability)
    has_sensational_language: (
        SignalValue  # "SHOCKING", excessive exclamation, hyperbole
    )
    has_excessive_anonymous_sources: SignalValue  # Heavy reliance on unnamed sources
    lacks_substantiating_detail: SignalValue  # Vague claims without supporting evidence
    has_poor_grammar: SignalValue  # Frequent typos, odd wording, poor editing
    has_conspiratorial_framing: (
        SignalValue  # Hidden motives or conspiracies without evidence
    )
    has_vague_institutions: SignalValue  # References to unnamed "watchdog groups", etc.
    has_meta_claims: SignalValue  # "widely believed", "rumor says" without evidence
    has_emotional_tone: (
        SignalValue  # Tries to persuade/evoke emotion rather than inform
    )


# Pydantic model of the chain output
class CredibilityAssessment(BaseModel):
    """
    Overall credibility assessment of a news article.

    Combines individual signals into an aggregated score with explanation.
    Used to flag low-credibility sources for manual verification.
    """

    # Individual signals
    signals: CredibilitySignals

    # Aggregated scores
    credibility_score: float = Field(
        ge=0, le=1, description="0.0 = unreliable, 1.0 = highly credible"
    )

    # Recommendation for action
    recommendation: str  # "reliable", "requires_verification", "unreliable"

    # Explanation and rationale
    rationale: str  # Why this rating (which signals tipped the balance)
    key_strengths: list[str] = []  # What makes it credible
    key_weaknesses: list[str] = []  # What raises concerns
    hard_red_flags: list[str] = []  # Critical issues forcing manual review


class CredibilityResult(BaseModel):
    """Result of credibility assessment."""

    assessment: CredibilityAssessment
    metadata: AnalyserMetadata
