from pydantic import BaseModel, Field

from app.models.articles import Article
from app.models.llm_metadata import LLMMetadata


class EntityRelationship(BaseModel):
    """
    Relationship to another entity in the article.

    Captures network connections for context and disambiguation.
    """

    related_entity_name: str  # Name of the other person
    relationship_type: str  # worked_for, associate_of, investigated_by, sued_by
    description: str  # Human-readable description
    evidence_quote: str  # Sentence describing relationship


class EmploymentRecord(BaseModel):
    """
    Professional role linked to organization and location.

    Solves the ambiguity of which role belongs to which organization.
    """

    role: str  # "CEO", "organisational secretary"
    organization: str | None = None  # Which organization
    location: str | None = None  # Where they held this role
    timeframe: str | None = None  # "current", "former", "2018-2020"
    evidence_quote: str  # Sentence stating this employment


class Allegation(BaseModel):
    """
    Structured allegation or criminal charge.

    Captures allegations with full context including financial amounts,
    timeframes, and jurisdiction for adverse media screening.
    """

    category: str  # corruption, fraud, money_laundering, sanctions, violence, etc.
    description: str  # What they allegedly did
    status: str  # alleged, charged, under_investigation, convicted, dismissed, denied
    amount: str | None = None  # Financial amount specific to this allegation
    timeframe: str | None = None  # When this allegation occurred
    jurisdiction: str | None = None  # Where: "Jersey", "Spain", etc.
    evidence_quote: str  # Exact sentence from article
    subject_response: str | None = None  # Rare: response to this specific allegation


class Entity(BaseModel):
    """
    Enhanced entity model for adverse media screening.

    Captures person entities with structured allegations, employments, and relationships
    to enable proper matching and sentiment analysis.
    """

    # Unique identifier
    id: str  # UUID (assigned at extraction)

    # Core identification
    name: str
    aliases: list[str] = []

    # Demographics (for matching)
    age: str | None = None
    birth_year: str | None = None
    date_of_birth: str | None = None  # Strengthens matching if available

    # Professional context (STRUCTURED - solves role-org linkage)
    employments: list[EmploymentRecord] = []
    locations: list[str] = []  # General location associations

    # Adverse media data
    allegations: list[Allegation] = []
    overall_response: str | None = None  # General response to allegations

    # Relationships
    relationships: list[EntityRelationship] = []

    # Audit trail & confidence
    mention_sentences: list[str] = []
    mention_count: int = 0
    extraction_confidence: float = Field(ge=0, le=1, default=1.0)

    # LLM will populate both structured employments AND these simple lists
    roles: list[str] = []
    organization: list[str] = []


class ExtractionMetadata(LLMMetadata):
    """Extraction-specific metadata."""

    # Article context
    url: str
    title: str
    article_length_chars: int


# Pydantic model for LLM output validation
class EntitiesOutput(BaseModel):
    """Schema for LLM entity extraction output."""

    entities: list[Entity]


class ExtractionResult(BaseModel):
    """
    Result of entity extraction from an article with comprehensive metadata.

    Attributes:
        entities: List of extracted person entities
        metadata: Extraction metadata (includes url, title, article_length_chars)

    Note:
        Article is not included to avoid duplication in ScreeningResult.
        Article metadata (url, title, length) is available in metadata field.
    """

    entities: list[Entity]
    metadata: ExtractionMetadata
