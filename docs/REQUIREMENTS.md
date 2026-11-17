
# NFHS Navigator — Project Requirements

## 1. Functional Requirements

**FR-01: Indicator Lookup**

The system shall allow users to search for public-health indicators such as child stunting, wasting, underweight and anaemia for any of the 38 districts of Tamil Nadu.

**FR-02: NFHS Round Selection**

The system shall support both NFHS-4 and NFHS-5 data and allow users to select the required survey round.

**FR-03: District Comparison**

The system shall allow users to compare data for 2 to 5 Tamil Nadu districts for a selected health indicator.

**FR-04: Change Calculation**

The system shall calculate the difference between NFHS-4 and NFHS-5 values in percentage points whenever the indicator definitions are comparable.

**FR-05: Source Citation**

Every displayed indicator value shall include its survey round, district, area, source document, table number and page number. The system shall flag indicators with changed definitions between survey rounds.

## 2. Non-Functional Requirements

**NFR-01: Accuracy**

The system shall achieve at least 95% cell-level accuracy across a test set of 60 indicator lookups (at least 57 correct answers).

**NFR-02: Performance**

The system shall return an answer within 3 seconds for at least 95% of queries using the prepared local dataset.

**NFR-03: Reliability**

The system shall handle missing or unavailable indicator values without crashing or generating guessed values.

**NFR-04: Security**

The system shall store configuration secrets in environment variables and shall not commit `.env` files or credentials to the public GitHub repository.

**NFR-05: Maintainability**

The project shall use Python 3.12, a `src` package layout, automated tests with pytest and code-quality checks with Ruff.
