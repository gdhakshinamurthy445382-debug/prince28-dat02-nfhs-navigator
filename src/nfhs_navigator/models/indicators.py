"""Canonical health indicator definitions for NFHS Navigator."""

from enum import StrEnum


class IndicatorCode(StrEnum):
    CHILD_STUNTING = "child_stunting"
    CHILD_WASTING = "child_wasting"
    CHILD_UNDERWEIGHT = "child_underweight"
    CHILD_ANAEMIA = "child_anaemia"
    WOMEN_ANAEMIA = "women_anaemia"
    PREGNANT_WOMEN_ANAEMIA = "pregnant_women_anaemia"


INDICATOR_CATALOG: dict[IndicatorCode, dict[str, str]] = {
    IndicatorCode.CHILD_STUNTING: {
        "label": "Children under five who are stunted",
        "population_group": "Children under 5",
    },
    IndicatorCode.CHILD_WASTING: {
        "label": "Children under five who are wasted",
        "population_group": "Children under 5",
    },
    IndicatorCode.CHILD_UNDERWEIGHT: {
        "label": "Children under five who are underweight",
        "population_group": "Children under 5",
    },
    IndicatorCode.CHILD_ANAEMIA: {
        "label": "Children aged 6–59 months with anaemia",
        "population_group": "Children aged 6–59 months",
    },
    IndicatorCode.WOMEN_ANAEMIA: {
        "label": "Women aged 15–49 years with anaemia",
        "population_group": "Women aged 15–49 years",
    },
    IndicatorCode.PREGNANT_WOMEN_ANAEMIA: {
        "label": "Pregnant women aged 15–49 years with anaemia",
        "population_group": "Pregnant women aged 15–49 years",
    },
}
