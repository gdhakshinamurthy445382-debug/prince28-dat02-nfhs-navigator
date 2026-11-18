"""Endpoints for searching NFHS indicator observations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from nfhs_navigator.api.deps import get_indicator_store
from nfhs_navigator.indicator_store import IndicatorStore
from nfhs_navigator.models.indicator import (
    Area,
    IndicatorRecord,
    SurveyRound,
)
from nfhs_navigator.models.indicators import IndicatorCode

router = APIRouter(prefix="/indicators", tags=["indicators"])


@router.get("", response_model=list[IndicatorRecord])
def search_indicators(
    store: Annotated[IndicatorStore, Depends(get_indicator_store)],
    district: Annotated[str | None, Query()] = None,
    indicator: Annotated[IndicatorCode | None, Query()] = None,
    survey_round: Annotated[SurveyRound | None, Query()] = None,
    area: Annotated[Area | None, Query()] = None,
) -> list[IndicatorRecord]:
    """Search NFHS observations by district, indicator, round and area."""

    return store.search(
        district=district,
        indicator=indicator.value if indicator else None,
        survey_round=survey_round,
        area=area,
    )
