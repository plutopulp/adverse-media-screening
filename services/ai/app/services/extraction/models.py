from pydantic import BaseModel, Field

from app.models.llm_metadata import AnalyserMetadata


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


# Allegation extraction has been moved to the sentiment step.


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

    # Additional identity details (explicit only)
    nationalities: list[str] = []  # e.g., British, French
    place_of_birth: str | None = None
    identifiers: list[str] = []  # e.g., passport numbers if explicitly stated

    # Relationships
    relationships: list[EntityRelationship] = []

    # Audit trail & confidence
    mention_sentences: list[str] = []
    mention_count: int = 0
    extraction_confidence: float = Field(ge=0, le=1, default=1.0)


# Pydantic model for LLM output validation
class EntitiesOutput(BaseModel):
    """Schema for LLM entity extraction output."""

    entities: list[Entity]


class ExtractionResult(BaseModel):
    """
    Result of entity extraction from an article with comprehensive metadata.

    Attributes:
        entities: List of extracted person entities
        metadata: Extraction metadata
    """

    entities: list[Entity]
    metadata: AnalyserMetadata

    def get_entity_by_id(self, entity_id: str) -> Entity | None:
        """
        Look up entity by ID.

        Returns:
            Entity if found, None otherwise
        """
        return next((e for e in self.entities if e.id == entity_id), None)
