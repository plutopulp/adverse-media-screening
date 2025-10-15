"""
Credibility analyser using LLM-based signal extraction.

Assesses article reliability by extracting journalistic quality signals
and aggregating them into an overall credibility score.
"""

import time
from datetime import datetime

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.models.articles import Article
from app.models.llm_metadata import AnalyserMetadata
from app.utils.logger import get_logger

from .models import CredibilityAssessment, CredibilityResult
from .prompt import CREDIBILITY_PROMPT, PROMPT_VERSION


class CredibilityAnalyser:
    """
    LLM-based credibility assessment for news articles.

    Analyses articles for journalistic quality signals before entity extraction
    to identify potentially unreliable sources.

    Example:
        analyser = CredibilityAnalyser()
        article = extract_article(url)
        credibility = analyser.assess(article)

        if credibility.recommendation == "unreliable":
            logger.warning("Low credibility source")
    """

    def __init__(
        self,
        llm: BaseChatModel,
        *,
        provider,
        model_name: str,
        logger=get_logger(service="credibility"),
    ):
        """
        Initialize credibility analyser with LLM.

        Args:
            llm: Language model to use
            logger: Logger instance

        NOTE: Consider using cheaper models for credibility assessment
        (gpt-4o-mini, claude-haiku) as this runs before extraction and may
        not need flagship model capabilities.
        """
        self.llm = llm
        self.logger = logger
        self.provider = provider
        self.model_name = model_name

    def assess(self, article: Article) -> CredibilityResult:
        """
        Assess article credibility via LLM signal extraction.

        Args:
            article: Article to assess

        Returns:
            CredibilityAssessment with signals, scores, and recommendations

        Raises:
            RuntimeError: If credibility assessment fails
        """
        self.logger.info("Assessing credibility for: {}", article.title)
        start_time = time.time()

        # Setup Pydantic parser for structured output
        parser = PydanticOutputParser(pydantic_object=CredibilityAssessment)

        # Create prompt template
        prompt = ChatPromptTemplate.from_template(CREDIBILITY_PROMPT)

        # Build chain with LCEL
        chain = prompt | self.llm | parser

        prompt_data = {
            **article.model_dump(),
            "format_instructions": parser.get_format_instructions(),
        }

        try:
            # Invoke chain with article data
            assessment: CredibilityAssessment = chain.invoke(prompt_data)

            # Build metadata
            processing_time = time.time() - start_time

            metadata = AnalyserMetadata(
                processed_at=datetime.now().isoformat(),
                processing_time_seconds=round(processing_time, 2),
                llm_provider=str(self.provider.value),
                llm_model=self.model_name,
                analyser_version="0.1.0",
                prompt_version=PROMPT_VERSION,
            )

            credibility_result = CredibilityResult(
                assessment=assessment,
                metadata=metadata,
            )

            return credibility_result

        except Exception as e:
            self.logger.exception("Credibility assessment failed: {}", e)
            raise
