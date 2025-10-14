"""
Entity extraction from articles using LLM-based approach.
"""

import time
import uuid
from datetime import datetime, timezone

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.config import LLMProviderType
from app.models.articles import Article
from app.utils.logger import get_logger

from .models import EntitiesOutput, ExtractionMetadata, ExtractionResult
from .prompt import EXTRACTION_PROMPT


class LLMExtractor:
    """
    LLM-based entity extractor with Pydantic validation.

    Uses dependency injection for the LLM to allow easy swapping
    of providers and models.

    Example:
        # Use default LLM from settings
        extractor = LLMExtractor()

        # Use specific provider
        from app.services.llm_factory import create_llm, LLMProviderType
        llm = create_llm(LLMProviderType.ANTHROPIC)
        extractor = LLMExtractor(llm)

        # Extract entities
        result = extractor.extract(article)
    """

    def __init__(
        self,
        llm: BaseChatModel,
        provider: LLMProviderType,
        model_name: str,
        logger=get_logger(service="extraction"),
    ):
        """
        Initialize extractor with an LLM.

        """
        self.llm = llm
        self.logger = logger
        self.provider = provider
        self.model_name = model_name
        self.logger.info(
            f"Initialized LLMExtractor provider={self.provider} model={self.model_name}"
        )

    def extract(self, article: Article) -> ExtractionResult:
        """
        Extract person entities from article using LLM with comprehensive metadata tracking.

        Args:
            article: Article to process

        Returns:
            ExtractionResult with validated entities and performance metadata

        Raises:
            RuntimeError: If LLM extraction or validation fails
        """
        self.logger.info(f"Extracting entities from article: {article.title}")
        start_time = time.time()

        # Setup Pydantic parser for structured output
        parser = PydanticOutputParser(pydantic_object=EntitiesOutput)

        # Create prompt template
        prompt = ChatPromptTemplate.from_template(EXTRACTION_PROMPT)

        # Build chain with LCEL
        chain = prompt | self.llm | parser

        try:
            # Invoke chain with article text and format instructions
            result = chain.invoke(
                {
                    "article_text": article.content,
                    "format_instructions": parser.get_format_instructions(),
                }
            )

            # Assign unique IDs to each entity
            for entity in result.entities:
                entity.id = str(uuid.uuid4())

            # Calculate processing time
            processing_time = time.time() - start_time

            # Build comprehensive metadata
            metadata = ExtractionMetadata(
                url=article.url,
                title=article.title,
                processed_at=datetime.now(timezone.utc).isoformat(),
                processing_time_seconds=round(processing_time, 2),
                article_length_chars=len(article.content),
                llm_provider=str(self.provider.value),
                llm_model=self.model_name,
            )

            extraction_result = ExtractionResult(
                entities=result.entities, article=article, metadata=metadata
            )

            self.logger.info(
                f"Successfully extracted {len(result.entities)} entities in {processing_time:.2f}s"
            )
            return extraction_result

        except Exception as e:
            self.logger.error(f"Entity extraction failed: {e}")
            raise RuntimeError(f"Failed to extract entities: {e}")
