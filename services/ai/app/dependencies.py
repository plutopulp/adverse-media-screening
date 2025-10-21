import httpx
from fastapi import Depends

from app.config import APP_VERSION, Settings
from app.services.credibility.analyser import CredibilityAnalyser
from app.services.extraction.llm import EntityExtractor
from app.services.llm_factory import create_llm, select_llm_config
from app.services.matching.matcher import PersonMatcher
from app.services.pipeline import ArticleExtractionPipeline
from app.services.results.storage import ResultsStorage
from app.services.screening_pipeline import ScreeningPipeline
from app.services.sentiment.analyser import SentimentAnalyser
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
    return EntityExtractor(
        llm=llm, logger=logger, provider=provider, model_name=cfg.model
    )


def get_credibility_analyser(
    settings=Depends(get_settings), logger=Depends(get_app_logger)
) -> CredibilityAnalyser:
    """Create CredibilityAnalyser with configured LLM (reuse default)."""
    provider, cfg = select_llm_config(settings)
    llm = create_llm(provider, cfg.model, cfg.api_key, cfg.temperature)
    return CredibilityAnalyser(
        llm=llm, provider=provider, model_name=cfg.model, logger=logger
    )


def get_pipeline(
    scraper=Depends(get_scraper),
    extractor=Depends(get_extractor),
) -> ArticleExtractionPipeline:
    return ArticleExtractionPipeline(scraper, extractor)


def get_matcher(
    settings=Depends(get_settings), logger=Depends(get_app_logger)
) -> PersonMatcher:
    """Create PersonMatcher with configured LLM."""
    provider, cfg = select_llm_config(settings)
    llm = create_llm(provider, cfg.model, cfg.api_key, cfg.temperature)
    return PersonMatcher(
        llm=llm, provider=provider, model_name=cfg.model, logger=logger
    )


def get_sentiment_analyser(
    settings=Depends(get_settings), logger=Depends(get_app_logger)
) -> SentimentAnalyser:
    """Create SentimentAnalyser with configured LLM."""
    provider, cfg = select_llm_config(settings)
    llm = create_llm(provider, cfg.model, cfg.api_key, cfg.temperature)
    return SentimentAnalyser(
        llm=llm, provider=provider, model_name=cfg.model, logger=logger
    )


def get_results_storage(
    settings: Settings = Depends(get_settings), logger=Depends(get_app_logger)
) -> ResultsStorage:
    """Create ResultsStorage for persisting screening results."""
    storage = ResultsStorage(
        results_dir=settings.project_root / "results",
        schema_version=APP_VERSION,
        logger=logger,
    )

    # Load example results if no results exist yet
    storage.load_examples(settings.project_root / settings.output_dir)

    return storage


def get_screening_pipeline(
    scraper=Depends(get_scraper),
    extractor=Depends(get_extractor),
    matcher=Depends(get_matcher),
    analyser=Depends(get_credibility_analyser),
    sentiment_analyser=Depends(get_sentiment_analyser),
    storage=Depends(get_results_storage),
    settings=Depends(get_settings),
) -> ScreeningPipeline:
    """Create ScreeningPipeline with all required services."""
    return ScreeningPipeline(
        scraper, extractor, matcher, settings, analyser, sentiment_analyser, storage
    )
