"""
Test routes for development with mock data.
"""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends

from app.services.screening.models import ScreeningResult
from app.config import Settings
from app.dependencies import get_settings

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/mock-result", response_model=ScreeningResult)
def get_mock_result(example: str = "roman-typo-2", settings: Settings = Depends(get_settings)):
    """
    Return a mock screening result for UI development.
    
    Available examples:
    - roman-typo-2: Roman Abramovich with adverse media
    - hasan: Turkish mayor with corruption allegations
    - rachel-smith-reeves-2: Policy criticism (neutral sentiment)
    - no_match: Article with no matching person
    """
    downloads_dir = Path(settings.project_root) / "downloads"
    
    example_file = downloads_dir / f"{example}.json"
    
    if not example_file.exists():
        available = [f.stem for f in downloads_dir.glob("*.json")]
        raise HTTPException(
            status_code=404,
            detail=f"Example '{example}' not found. Available: {', '.join(available)}"
        )
    
    try:
        with open(example_file, "r") as f:
            data = json.load(f)
        return ScreeningResult(**data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load example: {str(e)}"
        )

