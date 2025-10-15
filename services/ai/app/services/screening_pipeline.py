"""
Screening pipeline for adverse media analysis.

Orchestrates the complete workflow: scrape → extract → match → (future: sentiment).
"""

from app.config import Settings
from app.models.articles import Article
from app.services.extraction.llm import LLMExtractor
from app.services.extraction.models import ExtractionResult
from app.services.matching.matcher import PersonMatcher
from app.services.matching.models import MatchingResult, QueryPerson
from app.services.screening.models import ScreeningResult
from app.utils.scraping import ArticleScraper


class ScreeningPipeline:
    """
    Complete adverse media screening pipeline.

    Coordinates scraping, entity extraction, and person matching to produce
    comprehensive screening results.
    """

    def __init__(
        self,
        scraper: ArticleScraper,
        extractor: LLMExtractor,
        matcher: PersonMatcher,
        settings: Settings,
    ):
        """
        Initialize screening pipeline with required services.

        Args:
            scraper: Article scraper for fetching content
            extractor: LLM-based entity extractor
            matcher: LLM-based person matcher
            settings: Application settings
        """
        self.scraper = scraper
        self.extractor = extractor
        self.matcher = matcher
        self.settings = settings

    def screen(self, url: str, query_person: QueryPerson) -> ScreeningResult:
        """
        Execute complete screening workflow.

        Args:
            url: Article URL to screen
            query_person: Person to match against article entities

        Returns:
            ScreeningResult with article, entities, and matching data

        Workflow:
            1. Scrape article content
            2. Extract person entities with LLM
            3. Match query person against entities
            4. (Future) Analyze sentiment of matched entities

        Example:
            >>> pipeline = ScreeningPipeline(...)
            >>> query = QueryPerson(name="John Doe", date_of_birth="1980-01-15")
            >>> result = pipeline.screen("https://example.com/article", query)
            >>> if result.matching.has_definite_match:
            ...     print(f"Match found: {result.matching.summary}")
        """
        # Step 1: Scrape article
        article: Article = self.scraper.extract_article(url)

        # Step 2: Extract entities
        extraction_result: ExtractionResult = self.extractor.extract(article)

        # Step 3: Match query person against entities
        matching_result: MatchingResult = self.matcher.match(
            query_person, extraction_result
        )

        # Build comprehensive result (article at top level, no duplication)
        return ScreeningResult(
            query_person=query_person,
            article=article,
            entities=extraction_result.entities,
            matching=matching_result,
        )
