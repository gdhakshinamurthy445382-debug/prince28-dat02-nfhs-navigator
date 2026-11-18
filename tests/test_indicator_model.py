"""Tests for NFHS indicator data validation."""

import pytest
from pydantic import ValidationError

from nfhs_navigator.models.indicator import IndicatorRecord


@pytest.fixture
def valid_record_data() -> dict:
    return {
        "id": "TEST-001",
        "district": "Chennai",
        "survey_round": "NFHS-5",
        "indicator": "child_stunting",
        "area": "Total",
        "population_group": "Children under 5",
        "value": 25.5,
        "source_document": "NFHS-5 Sample",
        "source_table": "Table 10.1",
        "source_page": "200",
        "definition": "Children under five who are stunted",
    }


def test_valid_indicator_record(valid_record_data: dict) -> None:
    record = IndicatorRecord(**valid_record_data)

    assert record.district == "Chennai"
    assert record.survey_round == "NFHS-5"
    assert record.value == 25.5
    assert record.state == "Tamil Nadu"


def test_reject_percentage_above_100(valid_record_data: dict) -> None:
    valid_record_data["value"] = 105

    with pytest.raises(ValidationError):
        IndicatorRecord(**valid_record_data)


def test_reject_negative_percentage(valid_record_data: dict) -> None:
    valid_record_data["value"] = -1

    with pytest.raises(ValidationError):
        IndicatorRecord(**valid_record_data)


def test_reject_invalid_district(valid_record_data: dict) -> None:
    valid_record_data["district"] = "Invalid District"

    with pytest.raises(ValidationError):
        IndicatorRecord(**valid_record_data)


def test_reject_invalid_survey_round(valid_record_data: dict) -> None:
    valid_record_data["survey_round"] = "NFHS-6"

    with pytest.raises(ValidationError):
        IndicatorRecord(**valid_record_data)


def test_reject_missing_source_document(valid_record_data: dict) -> None:
    del valid_record_data["source_document"]

    with pytest.raises(ValidationError):
        IndicatorRecord(**valid_record_data)
