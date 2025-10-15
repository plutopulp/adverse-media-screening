"""
Screening service for adverse media analysis.

Orchestrates the complete screening workflow: scraping, entity extraction,
person matching, and sentiment analysis.
"""

from .models import ScreeningResult

__all__ = ["ScreeningResult"]
