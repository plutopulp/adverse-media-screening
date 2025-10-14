from fastapi import APIRouter, Depends, Query

from app.dependencies import get_app_logger, get_scraper, get_settings
from app.models.articles import Article
from app.schemas.utils import HealthResponse
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
