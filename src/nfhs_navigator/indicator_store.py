"""Storage and search operations for NFHS indicator observations."""

import json
from pathlib import Path

from nfhs_navigator.models.indicator import (
    Area,
    IndicatorRecord,
    SurveyRound,
)


class IndicatorStore:
    """Loads, validates and searches NFHS indicator records."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._records: dict[str, IndicatorRecord] = {}

    def load(self) -> int:
        """Load and validate all indicator records from a JSON file."""

        data = json.loads(self.path.read_text(encoding="utf-8"))

        if not isinstance(data, list):
            raise ValueError(f"{self.path} must contain a JSON list of indicator records")

        records: dict[str, IndicatorRecord] = {}

        for row in data:
            if not isinstance(row, dict):
                raise ValueError("Every indicator record must be a JSON object")

            record = IndicatorRecord.model_validate(row)

            if record.id in records:
                raise ValueError(f"Duplicate indicator record ID: {record.id}")

            records[record.id] = record

        self._records = records
        return len(records)

    @property
    def ready(self) -> bool:
        """Return whether indicator records have been loaded."""

        return bool(self._records)

    def search(
        self,
        district: str | None = None,
        indicator: str | None = None,
        survey_round: SurveyRound | None = None,
        area: Area | None = None,
    ) -> list[IndicatorRecord]:
        """Search records using optional filters."""

        results = list(self._records.values())

        if district:
            results = [
                record for record in results if record.district.casefold() == district.casefold()
            ]

        if indicator:
            results = [record for record in results if record.indicator.value == indicator]

        if survey_round:
            results = [record for record in results if record.survey_round == survey_round]

        if area:
            results = [record for record in results if record.area == area]

        return results

    def get(self, record_id: str) -> IndicatorRecord | None:
        """Retrieve one indicator record by its ID."""

        return self._records.get(record_id)
