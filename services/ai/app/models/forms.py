"""
Form data models for API endpoints.
"""

from datetime import date

from fastapi import Form
from pydantic import BaseModel, Field, HttpUrl


class ScreeningFormData(BaseModel):
    """Form data for adverse media screening request."""

    url: HttpUrl = Field(..., description="Article URL to screen")
    first_name: str = Field(..., min_length=1, description="Person's first name")
    last_name: str = Field(..., min_length=1, description="Person's last name")
    middle_names: str | None = Field(None, description="Optional middle name(s)")
    date_of_birth: date | None = Field(
        None, description="Date of birth in YYYY-MM-DD format"
    )

    @classmethod
    def as_form(
        cls,
        url: str = Form(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        middle_names: str | None = Form(None),
        date_of_birth: str | None = Form(None),
    ) -> "ScreeningFormData":
        """Parse form data into ScreeningFormData model."""
        return cls(
            url=url,
            first_name=first_name,
            last_name=last_name,
            middle_names=middle_names,
            date_of_birth=date_of_birth,
        )

    @property
    def full_name(self) -> str:
        """Construct full name from components."""
        parts = [self.first_name]
        if self.middle_names:
            parts.append(self.middle_names)
        parts.append(self.last_name)
        return " ".join(parts)

    @property
    def birth_year(self) -> int | None:
        """Extract birth year from date of birth."""
        return self.date_of_birth.year if self.date_of_birth else None

    @property
    def dob_string(self) -> str | None:
        """Date of birth as ISO string for QueryPerson."""
        return self.date_of_birth.isoformat() if self.date_of_birth else None
