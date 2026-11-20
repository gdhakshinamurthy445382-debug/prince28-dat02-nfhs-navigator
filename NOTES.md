# Engineering notes: NFHS Navigator

## D03 · PostgreSQL

### Migrations (upgrade, downgrade, upgrade)

```text
paste the output of:
uv run alembic downgrade -1
uv run alembic current
uv run alembic upgrade head
uv run alembic history
```

### The loader is idempotent

```text
run 1: paste here
run 2: paste here
run 3 (after editing one record): paste here
```

### EXPLAIN for ?round=VALUE

```text
paste the output of: uv run python scripts/explain.py round VALUE
```

Why did the planner choose a Seq Scan on my table? (2 lines, your own words)

When would it switch to the GIN index? (1 line)



## D04 · Docker, Compose and tests

### The image

```text
paste the output of: docker images nfhs_navigator:dev
paste the output of: docker run --rm nfhs_navigator:dev id
```

- Size: ___ MB (target: under 400 MB)
- First build: ___ s. After changing one line of code: ___ s.
- Which step said CACHED, and why? (1 line, your own words)

### The stack

```text
paste the output of: docker compose ps -a
paste the last line of: docker compose logs migrate   (first up, then after down + up)
```

### Breaking the database on purpose

```text
db stopped:  /health → paste
db stopped:  /ready  → paste
db started:  /ready  → paste
```

Why should a load balancer stop sending traffic here but not restart the app? (2 lines)

### Tests and coverage

```text
uv run poe test              → paste the last line
uv run poe test-integration  → paste the last line
coverage TOTAL, unit only    → paste
coverage TOTAL, with integration tests → paste
```

Two files or lines my coverage report says are never run, and whether they matter: (2 lines)

The largest application-specific Docker layer is 96.3 MB, created by COPY --chown=app:app /app/.venv /app/.venv, because it copies the Python virtual environment and all installed dependencies into the final image.

### Indicator API and test coverage

- Added the `/v1/indicators` endpoint with district, indicator,
  survey-round, and area filters.
- Verified the endpoint using the FastAPI test client and HTTP requests.
- Added a test for invalid non-object indicator records.
- Test suite: 42 passed.
- HTML coverage report generated in `htmlcov/`.
