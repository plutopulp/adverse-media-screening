"""
Screening router for adverse media analysis.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_results_storage, get_screening_pipeline
from app.models.forms import ScreeningFormData
from app.services.matching.models import QueryPerson
from app.services.results.models import ResultMetadata
from app.services.results.storage import ResultsStorage
from app.services.screening.models import ScreeningResult
from app.services.screening_pipeline import ScreeningPipeline

router = APIRouter(prefix="/screening", tags=["screening"])


@router.post("/screen", response_model=ScreeningResult)
def screen_article(
    form_data: ScreeningFormData = Depends(ScreeningFormData.as_form),
    pipeline: ScreeningPipeline = Depends(get_screening_pipeline),
):
    """
    Screen an article for adverse media about a person.

    Performs complete workflow:
    1. Article scraping and credibility assessment
    2. Entity extraction
    3. Person matching
    4. Sentiment analysis (if match found)

    Accepts form data with:
    - url: Article URL (validated)
    - first_name, last_name: Required name components
    - middle_names: Optional middle name(s)
    - date_of_birth: Optional DOB in YYYY-MM-DD format

    Returns comprehensive screening results.
    """
    query_person = QueryPerson(
        name=form_data.full_name, date_of_birth=form_data.dob_string
    )
    return pipeline.screen(str(form_data.url), query_person)


@router.get("/results", response_model=list[ResultMetadata])
def list_results(storage: ResultsStorage = Depends(get_results_storage)):
    """
    List all saved screening results.

    Returns results filtered by current schema version,
    ordered by creation date (newest first).
    """
    return storage.list_results()


@router.get("/results/{result_id}", response_model=ScreeningResult)
def get_result(result_id: str, storage: ResultsStorage = Depends(get_results_storage)):
    """
    Get a specific screening result by ID.

    Args:
        result_id: UUID of the result to retrieve

    Returns:
        Complete screening result with all analysis data

    Raises:
        HTTPException: 404 if result not found
    """
    try:
        return storage.get_result(result_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Result not found")
