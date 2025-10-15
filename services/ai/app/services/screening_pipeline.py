"""
Screening pipeline for adverse media analysis.

Orchestrates the complete workflow: scrape → extract → match → (future: sentiment).
"""

from app.config import Settings
from app.models.articles import Article
from app.services.credibility.analyser import CredibilityAnalyser
from app.services.credibility.models import CredibilityResult
from app.services.extraction.llm import EntityExtractor
from app.services.extraction.models import ExtractionResult
from app.services.matching.matcher import PersonMatcher
from app.services.matching.models import MatchingResult, QueryPerson
from app.services.screening.models import ScreeningResult
from app.services.sentiment.analyser import SentimentAnalyser
from app.services.sentiment.models import SentimentResult
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
        extractor: EntityExtractor,
        matcher: PersonMatcher,
        settings: Settings,
        analyser: CredibilityAnalyser | None = None,
        sentiment_analyser: SentimentAnalyser | None = None,
    ):
        """
        Initialize screening pipeline with required services.

        Args:
            scraper: Article scraper for fetching content
            extractor: LLM-based entity extractor
            matcher: LLM-based person matcher
            settings: Application settings
            analyser: Credibility analyser (optional)
            sentiment_analyser: Sentiment analyser (optional)
        """
        self.scraper = scraper
        self.extractor = extractor
        self.matcher = matcher
        self.settings = settings
        self.analyser = analyser
        self.sentiment_analyser = sentiment_analyser

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
            4. (Future) Analyse sentiment of matched entities

        Example:
            >>> pipeline = ScreeningPipeline(...)
            >>> query = QueryPerson(name="John Doe", date_of_birth="1980-01-15")
            >>> result = pipeline.screen("https://example.com/article", query)
            >>> if result.matching.has_definite_match:
            ...     print(f"Match found: {result.matching.summary}")
        """
        # Step 1: Scrape article
        article: Article = self.scraper.extract_article(url)

        # Optional step: Credibility assessment first
        credibility: CredibilityResult | None = None
        if self.analyser is not None:
            credibility = self.analyser.assess(article)

        # Step 2: Extract entities
        extraction_result: ExtractionResult = self.extractor.extract(article)

        # Step 3: Match query person against entities
        matching_result: MatchingResult = self.matcher.match(
            query_person, extraction_result
        )

        # Step 4: Sentiment analysis on selected targets
        sentiment_result: SentimentResult | None = None
        if self.sentiment_analyser is not None:
            targets = matching_result.get_sentiment_targets()
            sentiment_result = self.sentiment_analyser.analyse_batch(
                targets, extraction_result, article
            )

        # Build comprehensive result
        return ScreeningResult(
            article=article,
            article_credibility=credibility,
            query_person=query_person,
            entities=extraction_result.entities,
            matching=matching_result,
            sentiment=sentiment_result,
        )
