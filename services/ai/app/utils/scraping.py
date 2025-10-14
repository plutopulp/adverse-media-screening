"""
Article extraction from web URLs.

Fetch and extract main content using httpx + readabilipy.
Minimal, basic setup with optional logger injection.
"""

import json
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from readabilipy import simple_json_from_html_string

from app.models.articles import Article

from ..utils.logger import get_logger


class ArticleScraper:
    """Minimal article scraper with optional logger and httpx client injection."""

    def __init__(self, logger=None, http_client: httpx.Client | None = None) -> None:
        self._logger = logger or get_logger(service="scraper")
        self._client = http_client or httpx.Client(follow_redirects=True)
        self._owns_client = http_client is None

    def close(self) -> None:
        if self._owns_client:
            try:
                self._client.close()
            except Exception:
                self._logger.exception("Failed to close HTTP client")

    def extract_article(self, url: str) -> Article:
        self._logger.info(f"Extracting article from {url}")
        html = self._fetch_html(url)
        title, content_text = self._extract_and_convert(html)
        return Article(url=url, title=title, content=content_text)

    def save_article_json(self, article: Article, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / self._generate_filename(url=article.url, suffix=".json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(article.model_dump(), f, ensure_ascii=False, indent=2)
        self._logger.info(f"Saved article JSON to {filepath}")
        return filepath

    def _fetch_html(self, url: str) -> str:
        try:
            resp = self._client.get(url)
            resp.raise_for_status()
            return resp.text
        except Exception as exc:
            self._logger.exception(f"Failed to fetch HTML from {url}: {exc}")
            raise

    def _extract_and_convert(self, html: str) -> tuple[str, str]:
        title = ""
        content_html = ""
        try:
            obj = simple_json_from_html_string(html)
            title = (obj or {}).get("title") or ""
            content_html = (obj or {}).get("content") or ""
        except Exception as exc:
            self._logger.exception(f"Readability extraction failed: {exc}")
        text = self._html_to_text(content_html) if content_html else ""
        return title, text

    def _html_to_text(self, html_fragment: str) -> str:
        soup = BeautifulSoup(html_fragment, "html.parser")
        paragraphs = [p.get_text().strip() for p in soup.find_all("p")]
        return "\n\n".join([p for p in paragraphs if p])

    def _generate_filename(self, url: str, suffix: str = ".txt") -> str:
        parsed = urlparse(url)
        parts = [p for p in parsed.path.split("/") if p]
        name = parts[-1] if parts else parsed.netloc.replace(".", "_")
        name = re.sub(r"[^\w\-]", "_", name)[:100]
        return f"{name}{suffix}"
