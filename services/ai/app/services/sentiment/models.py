"""
Pydantic data models for adverse media sentiment analysis.
"""

from pydantic import BaseModel, Field

from app.models.llm_metadata import AnalyserMetadata


class EvidenceSpan(BaseModel):
    """Sentence-level evidence with indices for auditability."""

    quote: str
    start_index: int | None = None
    end_index: int | None = None


class Allegation(BaseModel):
    """
    Individual allegation extracted from article.

    Each allegation represents a distinct adverse claim about the entity.
    """

    category: str  # criminal, money_laundering, corruption, fraud, etc.
    description: str  # What specifically they allegedly did
    status: str  # alleged, investigated, charged, convicted, acquitted, dismissed
    severity: str  # low, medium, high, critical
    monetary_amount: str | None = None
    timeframe: str | None = None
    jurisdiction: str | None = None
    evidence_spans: list[EvidenceSpan] = Field(default_factory=list)
    subject_response: str | None = None  # Entity's response to this allegation


class ToneSignals(BaseModel):
    """
    Tone and certainty signals from language analysis.

    Helps distinguish allegations from proven facts and assess reliability.
    """

    certainty_level: str  # definite, probable, alleged, speculative
    hedging_language: bool  # Presence of "allegedly", "reportedly", modal verbs
    attribution_quality: str  # named_sources, anonymous_sources, no_attribution
    temporal_context: str | None = None  # recent, ongoing, historical
    subject_denial: bool  # Did entity deny the allegations?
    contradictory_evidence: bool  # Are there conflicting claims in the article?


class SentimentAssessment(BaseModel):
    """
    Overall sentiment assessment for a matched entity.

    Combines per-allegation analysis with tone signals and risk scoring.
    """

    entity_id: str
    entity_name: str

    # Per-allegation breakdown
    allegations: list[Allegation] = Field(default_factory=list)

    # Tone/certainty analysis
    tone_signals: ToneSignals

    # Overall risk assessment
    overall_polarity: str  # adverse, neutral, positive
    risk_score: float = Field(
        ge=0, le=1, description="0.0 = no risk, 1.0 = critical risk"
    )
    risk_category: str  # high_risk, medium_risk, low_risk, no_adverse_content

    # Relationship context (network risk)
    related_entities_mentioned: list[str] = Field(
        default_factory=list,
        description="Names of related entities mentioned in adverse context",
    )

    # Audit trail
    rationale: str  # Why this risk score/category
    requires_manual_review: bool


class SentimentResult(BaseModel):
    """Result of sentiment analysis for one or more entities."""

    assessments: list[SentimentAssessment]
    metadata: AnalyserMetadata
