import httpx
from fastapi import Depends

from app.config import Settings
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
