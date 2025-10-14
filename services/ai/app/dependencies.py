import httpx
from fastapi import Depends

from app.config import Settings
from app.services.extraction.llm import LLMExtractor
from app.services.llm_factory import create_llm, select_llm_config
from app.services.pipeline import ArticleExtractionPipeline
from app.utils.logger import get_logger
from app.utils.scraping import ArticleScraper


def get_app_logger():
    return get_logger(service="api")


def get_http_client():
    return httpx.Client(follow_redirects=True)


def get_scraper(logger=Depends(get_app_logger), client=Depends(get_http_client)):
    return ArticleScraper(logger=logger, http_client=client)


def get_settings() -> Settings:
    return Settings()


def get_extractor(settings=Depends(get_settings), logger=Depends(get_app_logger)):
    provider, cfg = select_llm_config(settings)
    llm = create_llm(provider, cfg.model, cfg.api_key, cfg.temperature)
    return LLMExtractor(llm=llm, logger=logger, provider=provider, model_name=cfg.model)


def get_pipeline(
    scraper=Depends(get_scraper), extractor=Depends(get_extractor)
) -> ArticleExtractionPipeline:
    return ArticleExtractionPipeline(scraper, extractor)
