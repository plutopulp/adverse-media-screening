from app.services.extraction.llm import LLMExtractor
from app.services.extraction.models import ExtractionResult
from app.utils.scraping import ArticleScraper


class ArticleExtractionPipeline:
    def __init__(self, scraper: ArticleScraper, extractor: LLMExtractor) -> None:
        self.scraper = scraper
        self.extractor = extractor

    def run(self, url: str) -> ExtractionResult:
        article = self.scraper.extract_article(url)
        return self.extractor.extract(article)
