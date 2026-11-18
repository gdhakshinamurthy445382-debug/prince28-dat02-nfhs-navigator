"""Pydantic models for NFHS indicator observations."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from nfhs_navigator.models.districts import TAMIL_NADU_DISTRICTS
from nfhs_navigator.models.indicators import IndicatorCode


class SurveyRound(StrEnum):
    NFHS_4 = "NFHS-4"
    NFHS_5 = "NFHS-5"


class Area(StrEnum):
    TOTAL = "Total"
    RURAL = "Rural"
    URBAN = "Urban"


class IndicatorRecord(BaseModel):
    """A single sourced NFHS district-level indicator observation."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    id: str = Field(min_length=1)
    state: str = Field(default="Tamil Nadu", min_length=1)
    district: str = Field(min_length=1)
    survey_round: SurveyRound
    indicator: IndicatorCode
    area: Area
    population_group: str = Field(min_length=1)
    value: float = Field(ge=0, le=100)
    unit: str = Field(default="percent")
    source_document: str = Field(min_length=1)
    source_table: str = Field(min_length=1)
    source_page: str = Field(min_length=1)
    definition: str = Field(min_length=1)

    @field_validator("district")
    @classmethod
    def validate_district(cls, value: str) -> str:
        if value not in TAMIL_NADU_DISTRICTS:
            raise ValueError(f"'{value}' is not a recognised Tamil Nadu district")
        return value
