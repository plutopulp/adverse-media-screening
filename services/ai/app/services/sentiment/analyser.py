"""
LLM-based adverse media sentiment analyser for matched persons.
"""

import time
from datetime import datetime

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.models.articles import Article
from app.models.llm_metadata import AnalyserMetadata
from app.services.extraction.models import Entity, ExtractionResult
from app.utils.logger import get_logger

from .models import SentimentAssessment, SentimentResult
from .prompt import PROMPT_VERSION, SENTIMENT_PROMPT


class SentimentAnalyser:
    """
    LLM-based sentiment analyser for adverse media screening.

    Analyses articles for adverse signals about matched entities,
    with conservative bias to avoid false negatives.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        *,
        provider,
        model_name: str,
        logger=get_logger(service="sentiment"),
    ):
        """
        Initialise sentiment analyser with LLM.
        """
        self.llm = llm
        self.provider = provider
        self.model_name = model_name
        self.logger = logger

        # Setup parser and prompt template
        self.parser = PydanticOutputParser(pydantic_object=SentimentAssessment)
        self.prompt_template = ChatPromptTemplate.from_template(SENTIMENT_PROMPT)
        self.chain = self.prompt_template | self.llm | self.parser

    def preprocess(self, entity: Entity, article: Article) -> dict:
        """
        Build context for sentiment analysis.

        """
        entity_data = entity.model_dump(
            include={
                "name",
                "aliases",
                "employments",
                "relationships",
                "mention_sentences",
            }
        )

        # Provide both mention sentences and full article for context
        mention_text = (
            "\n".join(entity.mention_sentences)
            if entity.mention_sentences
            else "No specific mentions extracted"
        )

        return {
            **entity_data,
            "mention_sentences_text": mention_text,
            "full_article": article.content,
        }

    def compose_prompt(self, context: dict) -> dict:
        """
        Add format instructions to context.

        """
        return {
            **context,
            "format_instructions": self.parser.get_format_instructions(),
        }

    def invoke_model(self, prompt_data: dict) -> SentimentAssessment:
        """
        Invoke LLM chain and return parsed assessment.
        """
        return self.chain.invoke(prompt_data)

    def postprocess(
        self, assessment: SentimentAssessment, entity: Entity
    ) -> SentimentAssessment:
        """
        Post-process assessment and ensure entity IDs are set.

        """
        # Ensure entity identification is set
        assessment.entity_id = entity.id
        assessment.entity_name = entity.name
        return assessment

    def analyse(self, entity: Entity, article: Article) -> SentimentAssessment:
        """
        Analyse adverse media sentiment for a matched entity.

        Args:
            entity: Entity to analyse
            article: Article being screened

        Returns:
            SentimentAssessment with allegations, tone signals, and risk scoring
        """
        self.logger.info("Analysing sentiment for entity: {}", entity.name)
        start_time = time.time()

        try:
            # Standard 4-phase lifecycle
            context = self.preprocess(entity, article)
            prompt_data = self.compose_prompt(context)
            assessment = self.invoke_model(prompt_data)
            processing_time = time.time() - start_time
            final_assessment = self.postprocess(assessment, entity, processing_time)

            self.logger.info(
                "Sentiment analysed in {:.2f}s: {} allegations, risk={}",
                processing_time,
                len(final_assessment.allegations),
                final_assessment.risk_category,
            )
            return final_assessment

        except Exception as e:
            self.logger.exception(
                "Sentiment analysis failed for {}: {}", entity.name, e
            )
            raise RuntimeError(f"Failed to analyse sentiment: {e}")

    def build_result(
        self, assessments: list[SentimentAssessment], processing_time: float
    ) -> SentimentResult:
        """
        Build final sentiment result with metadata.
        """
        metadata = AnalyserMetadata(
            processed_at=datetime.now().isoformat(),
            processing_time_seconds=round(processing_time, 2),
            llm_provider=str(self.provider.value),
            llm_model=self.model_name,
            analyser_version="0.1.0",
            prompt_version=PROMPT_VERSION,
        )
        return SentimentResult(assessments=assessments, metadata=metadata)

    def analyse_batch(
        self,
        entity_ids: list[str],
        extraction_result: ExtractionResult,
        article: Article,
    ) -> SentimentResult | None:
        """
        Analyse sentiment for multiple entities in batch.
        """
        if not entity_ids:
            return None

        start_time = time.time()
        assessments: list[SentimentAssessment] = []

        for entity_id in entity_ids:
            entity = extraction_result.get_entity_by_id(entity_id)
            if not entity:
                self.logger.warning("Entity not found: {}", entity_id)
                continue
            try:
                assessment = self.analyse(entity, article)
                assessments.append(assessment)
            except Exception as e:
                self.logger.exception(
                    "Failed to analyse sentiment for entity {}: {}",
                    entity.name,
                    e,
                )
                # Continue with other entities

        if not assessments:
            return None

        processing_time = time.time() - start_time
        return self.build_result(assessments, processing_time)
