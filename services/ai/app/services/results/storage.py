"""
Storage service for persisting screening results to the file system.

Manages saving, loading, and indexing of screening results with version control.
"""

import json
import uuid
from datetime import datetime, timezone
from logging import Logger
from pathlib import Path

from app.services.results.models import ResultIndex, ResultMetadata
from app.services.screening.models import ScreeningResult


class ResultsStorage:
    """
    File-based storage for screening results.

    Stores individual results as JSON files in a data directory and maintains
    an index for efficient listing and filtering by schema version.
    """

    def __init__(self, results_dir: Path, schema_version: str, logger: Logger) -> None:
        """
        Initialize results storage.

        Args:
            results_dir: Root directory for storing results
            schema_version: Current application version for filtering
            logger: Logger instance
        """
        self.results_dir = results_dir
        self.data_dir = results_dir / "data"
        self.index_file = results_dir / "index.json"
        self.schema_version = schema_version
        self.logger = logger

        # Create directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize index if it doesn't exist
        if not self.index_file.exists():
            self._save_index(ResultIndex(version="1.0.0", results=[]))

    def save_result(self, result: ScreeningResult) -> str:
        """
        Save a screening result to storage and update the index.

        Args:
            result: Screening result to save

        Returns:
            UUID of the saved result
        """
        # Generate UUID for this result
        result_id = str(uuid.uuid4())

        # Save result data
        result_file = self.data_dir / f"{result_id}.json"
        result_file.write_text(result.model_dump_json(indent=2))

        # Create metadata
        metadata = ResultMetadata(
            id=result_id,
            display_name=self._build_display_name(
                result.query_person.name, result.article.title
            ),
            person_name=result.query_person.name,
            article_url=result.article.url,
            article_title=result.article.title,
            created_at=datetime.now(timezone.utc).isoformat(),
            schema_version=self.schema_version,
        )

        # Update index
        index = self._load_index()
        index.results.append(metadata)
        self._save_index(index)

        self.logger.info(f"Saved screening result with ID: {result_id}")
        return result_id

    def get_result(self, result_id: str) -> ScreeningResult:
        """
        Load a screening result by ID.

        Args:
            result_id: UUID of the result to load

        Returns:
            Screening result

        Raises:
            FileNotFoundError: If result doesn't exist
        """
        result_file = self.data_dir / f"{result_id}.json"
        if not result_file.exists():
            raise FileNotFoundError(f"Result not found: {result_id}")

        result_data = json.loads(result_file.read_text())
        return ScreeningResult(**result_data)

    def list_results(self) -> list[ResultMetadata]:
        """
        List all saved results filtered by current schema version.

        Returns:
            List of result metadata, newest first
        """
        index = self._load_index()

        # Filter by schema version and sort by created_at desc
        filtered = [r for r in index.results if r.schema_version == self.schema_version]
        filtered.sort(key=lambda r: r.created_at, reverse=True)

        return filtered

    def _build_display_name(self, person_name: str, article_title: str) -> str:
        """
        Build a human-friendly display name.

        Args:
            person_name: Full name of the person
            article_title: Article title

        Returns:
            Display name in format "Person Name - Article Title"
        """
        truncated_title = self._truncate_title(article_title)
        return f"{person_name} - {truncated_title}"

    def _truncate_title(self, title: str, max_len: int = 50) -> str:
        """
        Truncate long titles with ellipsis.

        Args:
            title: Title to truncate
            max_len: Maximum length before truncation

        Returns:
            Truncated title
        """
        if len(title) <= max_len:
            return title
        return title[: max_len - 3] + "..."

    def _load_index(self) -> ResultIndex:
        """Load the index file."""
        if not self.index_file.exists():
            return ResultIndex(version="1.0.0", results=[])

        index_data = json.loads(self.index_file.read_text())
        return ResultIndex(**index_data)

    def _save_index(self, index: ResultIndex) -> None:
        """Save the index file."""
        self.index_file.write_text(index.model_dump_json(indent=2))
