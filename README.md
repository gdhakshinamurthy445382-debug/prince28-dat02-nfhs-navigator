
# NFHS Navigator

Answers public-health indicator questions for Tamil Nadu districts using NFHS-5 and NFHS-4 fact sheets and reports, with exact table citations.

**Status:** Day 1 foundation (FastAPI skeleton, quality gates). Live URL from Day 5.

## Who it's for

District health analyst in the Tamil Nadu health department preparing a review of anaemia and child nutrition across 38 districts.

## The problem

Health analysts need to study anaemia and child nutrition across all 38 districts of Tamil Nadu. However, NFHS data is spread across many fact sheets and reports, making it difficult to find the correct information quickly. The same health indicator may have different values for NFHS-4 and NFHS-5, as well as for urban and rural areas. This makes manual comparison difficult and can lead to mistakes when preparing district-level reports.

## Data sources

NFHS-5 national, state and district fact sheets and state reports, plus NFHS-4 fact sheets for comparison.

- http://rchiips.org/nfhs/
- Terms: Public survey reports. The site blocks bots: download the PDFs by hand and list each in DATASET.md.

## Hardest problem (my interview story)

Tables, rounds and definitions: one indicator name appears for NFHS-4 and NFHS-5 and for urban/rural/total. Answers must pull the right cell (district x indicator x round x area), compute changes in code, and flag indicators whose definition changed between rounds.

## Signature feature

District compare: pick 2-5 districts and an indicator to see NFHS-4 vs NFHS-5 bars with citations.

## Target metric

Cell-level accuracy of 95%+ on 60 indicator lookups.

## Run it locally

```bash
uv sync
cp .env.example .env
# Windows: copy .env.example .env
uv run uvicorn nfhs_navigator.api.main:create_app --factory --reload
```

Then open http://localhost:8000/docs

## Checks

```bash
uv run pytest
uv run ruff check .
```


## Run locally in one command

You need Docker Desktop running. From a fresh clone:

```bash
docker compose up --build
```

This starts Postgres (with pgvector), Redis, runs the migrations and loads the sample data once, then starts the API.

- API docs: http://localhost:8000/docs
- Liveness: http://localhost:8000/health
- Readiness (checks the database): http://localhost:8000/ready

Stop with `Ctrl+C`, then `docker compose down`. Add `-v` to also delete the database volume.

## Develop and test

| Task | Mac / Linux | Windows |
|---|---|---|
| Run the API with reload | `make dev` | `uv run poe dev` |
| Unit tests (no network) | `make test` | `uv run poe test` |
| Integration tests (needs `docker compose up`) | `make test-integration` | `uv run poe test-integration` |
| Coverage report | `make cov` | `uv run poe cov` |
| Lint and format check | `make lint` | `uv run poe lint` |


## Run locally in one command

You need Docker Desktop running. From a fresh clone:

```bash
docker compose up --build
