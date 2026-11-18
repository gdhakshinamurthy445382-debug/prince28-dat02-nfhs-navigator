"""Tests for NFHS indicator data storage and search."""

import json

import pytest

from nfhs_navigator.indicator_store import IndicatorStore
from nfhs_navigator.models.indicator import Area, SurveyRound


@pytest.fixture
def sample_data() -> list[dict]:
    return [
        {
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
        },
        {
            "id": "TEST-002",
            "district": "Coimbatore",
            "survey_round": "NFHS-5",
            "indicator": "child_stunting",
            "area": "Urban",
            "population_group": "Children under 5",
            "value": 20.0,
            "source_document": "NFHS-5 Sample",
            "source_table": "Table 10.1",
            "source_page": "201",
            "definition": "Children under five who are stunted",
        },
        {
            "id": "TEST-003",
            "district": "Chennai",
            "survey_round": "NFHS-4",
            "indicator": "women_anaemia",
            "area": "Total",
            "population_group": "Women aged 15–49 years",
            "value": 55.0,
            "source_document": "NFHS-4 Sample",
            "source_table": "Table 11.1",
            "source_page": "180",
            "definition": "Women aged 15–49 years with anaemia",
        },
    ]


@pytest.fixture
def store(tmp_path, sample_data) -> IndicatorStore:
    path = tmp_path / "indicators.json"
    path.write_text(json.dumps(sample_data), encoding="utf-8")

    indicator_store = IndicatorStore(path)
    indicator_store.load()
    return indicator_store


def test_load_records(tmp_path, sample_data) -> None:
    path = tmp_path / "indicators.json"
    path.write_text(json.dumps(sample_data), encoding="utf-8")

    indicator_store = IndicatorStore(path)

    assert indicator_store.load() == 3
    assert indicator_store.ready is True


def test_search_by_district(store) -> None:
    results = store.search(district="Chennai")

    assert len(results) == 2
    assert all(record.district == "Chennai" for record in results)


def test_search_is_case_insensitive_for_district(store) -> None:
    results = store.search(district="chennai")

    assert len(results) == 2


def test_search_by_indicator(store) -> None:
    results = store.search(indicator="child_stunting")

    assert len(results) == 2


def test_search_by_survey_round(store) -> None:
    results = store.search(survey_round=SurveyRound.NFHS_4)

    assert len(results) == 1
    assert results[0].id == "TEST-003"


def test_search_by_area(store) -> None:
    results = store.search(area=Area.URBAN)

    assert len(results) == 1
    assert results[0].district == "Coimbatore"


def test_search_with_multiple_filters(store) -> None:
    results = store.search(
        district="Chennai",
        indicator="women_anaemia",
        survey_round=SurveyRound.NFHS_4,
    )

    assert len(results) == 1
    assert results[0].id == "TEST-003"


def test_get_existing_record(store) -> None:
    record = store.get("TEST-001")

    assert record is not None
    assert record.district == "Chennai"


def test_get_missing_record(store) -> None:
    assert store.get("UNKNOWN-ID") is None


def test_reject_duplicate_record_ids(tmp_path, sample_data) -> None:
    sample_data.append(sample_data[0])

    path = tmp_path / "indicators.json"
    path.write_text(json.dumps(sample_data), encoding="utf-8")

    indicator_store = IndicatorStore(path)

    with pytest.raises(ValueError, match="Duplicate indicator record ID"):
        indicator_store.load()


def test_reject_non_list_json(tmp_path) -> None:
    path = tmp_path / "indicators.json"
    path.write_text('{"id": "TEST-001"}', encoding="utf-8")

    indicator_store = IndicatorStore(path)

    with pytest.raises(ValueError, match="JSON list"):
        indicator_store.load()
