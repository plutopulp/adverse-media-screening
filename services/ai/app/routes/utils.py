from fastapi import APIRouter, Depends, Query

from app.dependencies import (
    get_app_logger,
    get_credibility_analyser,
    get_pipeline,
    get_scraper,
    get_screening_pipeline,
    get_settings,
)
from app.models.articles import Article
from app.schemas.utils import HealthResponse
from app.services.credibility.models import CredibilityResult
from app.services.extraction.models import ExtractionResult
from app.services.matching.models import QueryPerson
from app.services.screening.models import ScreeningResult
from app.utils.scraping import ArticleScraper

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(message="OK")


@router.get("/utils/extract", response_model=Article)
def extract(
    url: str = Query(..., description="Article URL"),
    logger=Depends(get_app_logger),
    scraper: ArticleScraper = Depends(get_scraper),
    settings=Depends(get_settings),
):
    article = scraper.extract_article(url)
    # Optional: persist to a temp folder for now
    try:
        download_dir = settings.project_root / settings.output_dir
        scraper.save_article_json(article, download_dir)
    except Exception:
        logger.exception("Failed to save article")
    finally:
        scraper.close()
    return article


# See if LLM Async interface is possible to make these async handlers
@router.get("/utils/extract_entities", response_model=ExtractionResult)
def extract_entities(
    url: str = Query(..., description="Article URL"), pipeline=Depends(get_pipeline)
):
    return pipeline.run(url)


@router.get("/utils/screen", response_model=ScreeningResult)
def screen_article(
    url: str = Query(..., description="Article URL to screen"),
    name: str = Query(..., description="Person's full name (first, middle, last)"),
    date_of_birth: str | None = Query(
        None,
        description="Date of birth (optional, strengthens matching)",
        example="1980-01-15",
    ),
    pipeline=Depends(get_screening_pipeline),
):
    """
    Complete adverse media screening workflow.

    Performs:
    1. Article scraping
    2. Credibility assessment
    3. Entity extraction
    4. Person matching
    5. Sentiment analysis

    Returns comprehensive screening results with article, entities, match data, and sentiment.
    """
    query_person = QueryPerson(name=name, date_of_birth=date_of_birth)
    return pipeline.screen(url, query_person)


@router.get("/utils/credibility", response_model=CredibilityResult)
def assess_credibility(
    url: str = Query(..., description="Article URL"),
    scraper: ArticleScraper = Depends(get_scraper),
    analyser=Depends(get_credibility_analyser),
):
    """Assess article credibility in isolation."""
    article = scraper.extract_article(url)
    try:
        return analyser.assess(article)
    finally:
        scraper.close()
