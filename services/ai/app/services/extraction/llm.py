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
from app.models.llm_metadata import AnalyserMetadata
from app.utils.logger import get_logger

from .models import EntitiesOutput, ExtractionResult
from .prompt import EXTRACTION_PROMPT, PROMPT_VERSION


class EntityExtractor:
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
        Initialise extractor with an LLM.

        """
        self.llm = llm
        self.logger = logger
        self.provider = provider
        self.model_name = model_name
        self.logger.info(
            "Initialised EntityExtractor provider={} model={}",
            self.provider,
            self.model_name,
        )

        # Setup parser and prompt template
        self.parser = PydanticOutputParser(pydantic_object=EntitiesOutput)
        self.prompt_template = ChatPromptTemplate.from_template(EXTRACTION_PROMPT)
        self.chain = self.prompt_template | self.llm | self.parser

    def preprocess(self, article: Article) -> dict:
        """Prepare input for the model."""
        return {
            "article_text": article.content,
            "format_instructions": self.parser.get_format_instructions(),
        }

    def compose_prompt(self, preprocessed_input: dict) -> dict:
        """Compose prompt data (already done in preprocess for this analyser)."""
        return preprocessed_input

    def invoke_model(self, prompt_data: dict) -> EntitiesOutput:
        """Invoke LLM chain and return parsed output."""
        return self.chain.invoke(prompt_data)

    def postprocess(
        self, output: EntitiesOutput, article: Article, processing_time: float
    ) -> ExtractionResult:
        """Assign IDs, build metadata, construct result."""
        # Assign unique IDs to each entity
        for entity in output.entities:
            entity.id = str(uuid.uuid4())

        metadata = AnalyserMetadata(
            processed_at=datetime.now(timezone.utc).isoformat(),
            processing_time_seconds=round(processing_time, 2),
            llm_provider=str(self.provider.value),
            llm_model=self.model_name,
            analyser_version="0.2.0",
            prompt_version=PROMPT_VERSION,
        )

        return ExtractionResult(entities=output.entities, metadata=metadata)

    def extract(self, article: Article) -> ExtractionResult:
        """
        Extract person entities from article using LLM with comprehensive metadata
        tracking.
        """
        self.logger.info("Extracting entities from article: {}", article.title)
        start_time = time.time()

        try:
            # Standard 4-phase lifecycle
            preprocessed = self.preprocess(article)
            prompt_data = self.compose_prompt(preprocessed)
            output = self.invoke_model(prompt_data)
            processing_time = time.time() - start_time
            extraction_result = self.postprocess(output, article, processing_time)

            self.logger.info(
                "Successfully extracted {} entities in {:.2f}s",
                len(extraction_result.entities),
                processing_time,
            )
            return extraction_result

        except Exception as e:
            self.logger.exception("Entity extraction failed: {}", e)
            raise RuntimeError(f"Failed to extract entities: {e}")
