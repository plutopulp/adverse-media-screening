"""
Data models for screening results persistence.

Defines metadata and index models for tracking saved screening results.
"""

from pydantic import BaseModel


class ResultMetadata(BaseModel):
    """
    Metadata for a saved screening result.

    Used in the index to provide quick access to result information
    without loading the full result data.
    """

    id: str
    display_name: str
    person_name: str
    article_url: str
    article_title: str
    created_at: str  # ISO format timestamp
    schema_version: str


class ResultIndex(BaseModel):
    """
    Index of all saved screening results.

    Stored as index.json in the results directory.
    """

    version: str  # Index file format version
    results: list[ResultMetadata]
