"""
LLM-based person matching for adverse media screening.

Matches query persons (from analysts) against extracted entities from articles,
with conservative bias to avoid false negatives.


WHAT WE MATCH ON:
✓ Name exact match
✓ Name fuzzy match (typos, spacing)
✓ Nickname variations (Bob/Robert, Bill/William)
✓ Partial name match (first or last only)
✓ Title-stripped match (Dr., Mr., etc.)
✓ DOB exact match
✓ Birth year match

WHAT WE DON'T MATCH ON:
✗ Entity age (unreliable without article date and even then it's unreliable)

CONSERVATIVE BIAS:
- Prefers false positives (manual review) over false negatives (missed matches)
- When uncertain → flags for manual review
- Detailed reasoning for every decision (regulatory compliance)
"""

import time
from datetime import datetime

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.config import LLMProviderType
from app.models.llm_metadata import AnalyserMetadata
from app.services.extraction.models import Entity, ExtractionResult
from app.utils.logger import get_logger

from .models import (
    MatchAnalysis,
    MatchDecision,
    MatchingResult,
    PersonMatch,
    QueryPerson,
)
from .prompt import MATCHING_PROMPT, PROMPT_VERSION


class PersonMatcher:
    """
    Match query person against article entities using LLM.

    Conservative bias: prioritizes recall over precision.
    Returns all potential matches with detailed reasoning for auditability.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        *,
        provider: LLMProviderType,
        model_name: str,
        logger=None,
    ):
        """
        Initialize matcher with LLM and metadata.

        Args:
            llm: Language model for matching
            provider: LLM provider type (for metadata)
            model_name: Model name (for metadata)
            logger: Optional logger instance
        """
        self.llm = llm
        self.provider = provider
        self.model_name = model_name
        self.logger = logger or get_logger(service="matching")
        self.output_parser = PydanticOutputParser(pydantic_object=MatchAnalysis)

        # Build prompt template
        self.prompt = ChatPromptTemplate.from_template(MATCHING_PROMPT)

        # Create chain
        self.chain = self.prompt | self.llm | self.output_parser

    def match(
        self, query_person: QueryPerson, extraction_result: ExtractionResult
    ) -> MatchingResult:
        """
        Match query person against all entities in article.

        Args:
            query_person: Person to search for (from analyst)
            extraction_result: Extracted entities from article

        Returns:
            MatchingResult with all potential matches, ranked by confidence

        Example:
            >>> matcher = PersonMatcher()
            >>> query = QueryPerson(name="Robert Smith", date_of_birth="1980-01-15")
            >>> result = matcher.match(query, extraction_result)
            >>> if result.has_definite_match:
            ...     print(f"Found: {result.primary_match.entity_name}")
        """
        # Normalise query person
        query_person.normalise()

        # Track entities analysed
        entities_analysed: list[str] = [
            entity.id for entity in extraction_result.entities
        ]

        # Track start time for metadata
        start_time: float = time.time()

        # Match against each entity (no article date needed)
        matches: list[PersonMatch] = []
        for entity in extraction_result.entities:
            try:
                match = self._match_entity(query_person, entity)

                # Only include non-NO_MATCH results
                if match.decision != MatchDecision.NO_MATCH:
                    matches.append(match)
            except Exception as e:
                self.logger.exception(f"Error matching entity {entity.name}: {e}")
                raise

        # Sort by confidence (highest first)
        matches.sort(key=lambda m: m.confidence, reverse=True)

        # Mark primary match (highest confidence)
        if matches:
            matches[0].is_primary_match = True

        # Determine summary flags
        has_definite: bool = any(
            m.decision == MatchDecision.DEFINITE_MATCH for m in matches
        )
        requires_review: bool = (not has_definite) and any(
            m.decision in [MatchDecision.UNCERTAIN, MatchDecision.POSSIBLE_MATCH]
            for m in matches
        )

        # Generate summary
        summary: str = MatchingResult.generate_summary(matches, query_person.name)

        # Build metadata
        processing_time: float = time.time() - start_time
        metadata: AnalyserMetadata = AnalyserMetadata(
            processed_at=datetime.now().isoformat(),
            processing_time_seconds=round(processing_time, 2),
            llm_provider=str(self.provider.value),
            llm_model=self.model_name,
            analyser_version="0.1.0",
            prompt_version=PROMPT_VERSION,
        )

        return MatchingResult(
            query_person=query_person,
            entities_analysed=entities_analysed,
            matches=matches,
            has_definite_match=has_definite,
            has_any_match=len(matches) > 0,
            requires_manual_review=requires_review,
            primary_match=matches[0] if matches else None,
            summary=summary,
            metadata=metadata,
        )

    def _match_entity(self, query: QueryPerson, entity: Entity) -> PersonMatch:
        """
        Match query against single entity using LLM.

        Args:
            query: Normalised query person
            entity: Entity from article

        Returns:
            PersonMatch with decision, confidence, signals, and reasoning
        """
        # Build prompt data from query and entity
        prompt_data: dict[str, str] = {
            **query.to_prompt_fields(),
            "entity_name": entity.name,
            "entity_aliases": ", ".join(entity.aliases) if entity.aliases else "None",
            "entity_birth_year": (
                str(entity.birth_year) if entity.birth_year else "Unknown"
            ),
            "entity_dob": entity.date_of_birth or "Unknown",
            "format_instructions": self.output_parser.get_format_instructions(),
        }

        # Invoke LLM chain - Pydantic parser returns MatchAnalysis
        analysis: MatchAnalysis = self.chain.invoke(prompt_data)

        # Parse LLM output into structured match
        return self._parse_match_analysis(analysis, entity)

    def _parse_match_analysis(
        self, analysis: MatchAnalysis, entity: Entity
    ) -> PersonMatch:
        """
        Convert validated LLM analysis into PersonMatch.

        Args:
            analysis: Validated MatchAnalysis from Pydantic parser
            entity: Entity being matched

        Returns:
            PersonMatch with typed fields and enum conversions
        """
        return PersonMatch(
            entity_id=entity.id,
            entity_name=entity.name,
            decision=MatchDecision.from_string(analysis.decision),
            confidence=analysis.confidence,
            signals=analysis.to_match_signals(),
            reasoning=analysis.reasoning,
            evidence_for_match=analysis.evidence_for_match,
            evidence_against_match=analysis.evidence_against_match,
        )
