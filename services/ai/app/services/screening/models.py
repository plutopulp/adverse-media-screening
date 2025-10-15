"""
Data models for screening results.

Defines the top-level ScreeningResult that aggregates article, entities,
and matching data without duplication.
"""

from pydantic import BaseModel

from app.models.articles import Article
from app.services.credibility.models import CredibilityResult
from app.services.extraction.models import Entity
from app.services.matching.models import MatchingResult, QueryPerson


class ScreeningResult(BaseModel):
    """
    Complete screening result for adverse media analysis.

    Top-level model containing query context, article, extracted entities,
    and matching results. Future versions will include sentiment analysis.

    Attributes:
        query_person: The person being screened (with normalised fields)
        article: Full article content (single source of truth, not duplicated)
        entities: All extracted entities (needed for allegations/sentiment later)
        matching: Match decisions, signals, and evidence

    Data Flow:
        1. Scrape article → article field
        2. Extract entities → entities field
        3. Match person → matching field
        4. (Future) Analyse sentiment → sentiment field

    """

    article: Article  # Full article at top level (url, title, content)
    article_credibility: CredibilityResult | None = None
    query_person: QueryPerson
    entities: list[Entity]  # All extracted entities with allegations
    matching: MatchingResult  # Match decisions and signals

    # Future expansion
    # sentiment: SentimentResult | None = None
