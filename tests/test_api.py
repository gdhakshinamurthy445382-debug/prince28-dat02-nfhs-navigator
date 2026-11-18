"""Tests for the NFHS Navigator API."""

import json

import pytest
from fastapi.testclient import TestClient

from nfhs_navigator.api.deps import get_indicator_store
from nfhs_navigator.api.main import create_app
from nfhs_navigator.indicator_store import IndicatorStore


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def test_liveness(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness(client):
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_list_documents(client):
    response = client.get("/documents")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 20
    assert len(body["items"]) == 20


def test_get_document(client):
    response = client.get("/documents/001")

    assert response.status_code == 200
    assert response.json()["id"] == "001"
    assert response.json()["district"] == "Chennai"


def test_search_documents(client):
    response = client.get("/documents", params={"q": "Coimbatore"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 4
    assert len(body["items"]) == 4
    assert all(record["district"] == "Coimbatore" for record in body["items"])


def test_document_not_found(client):
    response = client.get("/documents/INVALID-999")

    assert response.status_code == 404
    assert response.json()["title"] == "Not Found"
    assert response.json()["status"] == 404


def test_request_id_header(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers


@pytest.fixture
def indicator_client(tmp_path):
    records = [
        {
            "id": "TEST-001",
            "district": "Chennai",
            "survey_round": "NFHS-5",
            "indicator": "child_stunting",
            "area": "Total",
            "population_group": "Children under 5",
            "value": 25.5,
            "source_document": "Test NFHS-5",
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
            "source_document": "Test NFHS-5",
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
            "population_group": "Women aged 15-49 years",
            "value": 55.0,
            "source_document": "Test NFHS-4",
            "source_table": "Table 11.1",
            "source_page": "180",
            "definition": "Women aged 15-49 years with anaemia",
        },
    ]

    path = tmp_path / "indicators.json"
    path.write_text(json.dumps(records), encoding="utf-8")

    store = IndicatorStore(path)
    store.load()

    app = create_app()
    app.dependency_overrides[get_indicator_store] = lambda: store

    with TestClient(app) as test_client:
        yield test_client


def test_list_indicators(indicator_client):
    response = indicator_client.get("/indicators")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_filter_indicators_by_district(indicator_client):
    response = indicator_client.get(
        "/indicators",
        params={"district": "Chennai"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(record["district"] == "Chennai" for record in response.json())


def test_filter_indicators_by_indicator(indicator_client):
    response = indicator_client.get(
        "/indicators",
        params={"indicator": "women_anaemia"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "TEST-003"


def test_filter_indicators_by_survey_round(indicator_client):
    response = indicator_client.get(
        "/indicators",
        params={"survey_round": "NFHS-4"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "TEST-003"


def test_filter_indicators_by_area(indicator_client):
    response = indicator_client.get(
        "/indicators",
        params={"area": "Urban"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "TEST-002"


def test_filter_indicators_with_multiple_filters(indicator_client):
    response = indicator_client.get(
        "/indicators",
        params={
            "district": "Chennai",
            "indicator": "women_anaemia",
            "survey_round": "NFHS-4",
            "area": "Total",
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "TEST-003"


def test_indicator_search_returns_empty_list(indicator_client):
    response = indicator_client.get(
        "/indicators",
        params={"district": "Madurai"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_indicator_search_rejects_invalid_round(indicator_client):
    response = indicator_client.get(
        "/indicators",
        params={"survey_round": "NFHS-6"},
    )

    assert response.status_code == 422
