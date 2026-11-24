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



## D05 · CI/CD and going live

- Live URL: https://prince28-dat02-nfhs-navigator.onrender.com
- CI run for pull request 1: https://github.com/gdhakshinamurthy445382-debug/prince28-dat02-nfhs-navigator/actions (PR #6 — docs/day-05-live)
- First deploy that ran by itself: GitHub Actions CD workflow (exact run link not recorded)
- Merge clicked at [time not recorded] → "Smoke test passed" at [time not recorded] → lead time: [not recorded]

### Smoke test output from that CD run

```text
[Exact last 4 lines of the CD smoke-test log not recorded]
```

### Rollback drill

- Rolled back to sha a74f43eed680f0cdb4473df5593adea6fab3440c : started [time not recorded], smoke passed [time not recorded] (duration not recorded)
- Rolled forward to sha 2a35fbe5440465d02d66d8d9ca19557189dd9e69 : 1m 50s
- During the rollback, the database stayed on the newer schema. Why is that safe here?
  The rollback deploys an older application commit without downgrading the database.
  The database schema remains newer, avoiding destructive migrations and preserving data.

### Where my secrets live

- Neon string: GitHub Secret DATABASE_URL + Render environment. Not in Git, not in the image.
- Render deploy hook: GitHub Secret RENDER_DEPLOY_HOOK only.

### Monitoring

- UptimeRobot checks /health every 5 minutes; alerts go to my email.
- One thing that would make my live app faster on its first request: Keeping the Render service warm with an always-on instance avoids cold-start delays.
- Fixed UptimeRobot HEAD check: added explicit HEAD support to /health; production HEAD returns 200 OK.
- Monitoring status: UP
- HEAD health fix commit: c91cc0c



## D06 - Corpus Collection

### Initial corpus target

- NFHS-5 Tamil Nadu state fact sheet.
- 32 district fact sheets (survey-era coverage).
- Target: 33 fact sheets.

### Downloader

- Implemented URL downloader and manual registration CLI.
- Robots.txt compliance using Protego.
- Per-host delay and concurrency controls.
- Retry and timeout handling.
- SHA-256 file integrity tracking.
- Manifest tracking.
- Temporary `.part` files and atomic file completion.

### Validation

- Full test suite: 51 passed.
- Ruff checks: passed.
- Ruff format check: passed.
- Pre-commit hooks: passed.
- `uv lock --check`: passed.
- CLI help: verified for `urls` and `manual`.

### Documentation

- `DATASET.md` created and updated to reflect current collection status.
- `docs/CAPACITY.md` created.
- Historical Tamil Nadu compendium metadata retained in `data/sources/source_manifest.json`.

### Current collection run

- NFHS-5 India Report downloaded successfully.
- NFHS-6 India and State Fact Sheets downloaded successfully.
- NFHS-5 Himachal Pradesh download blocked by `robots.txt`.
- Successful downloads: 2 PDFs.
- Blocked downloads: 1 source.
- Current local corpus: 2 PDFs in `data/raw/`.
- Raw PDFs are excluded from version control.
- Reuse/licensing terms for downloaded documents remain unverified.

### Historical Tamil Nadu compendium record

- Previously recorded as manually acquired from OpenCity.
- Historical raw filename: `994c9ee4-803c-4891-8897-ab4db4a445ff.pdf`.
- Historical file size: 6,779,076 bytes.
- Historical SHA-256: `40cf5c83ddbb053fc8352911fa428101b50c423abc96254989cbd9529ffa398a`.
- Historical PDF page count: 204.
- Historical fact sheets identified: 33 (1 state + 32 districts).
- Fact-sheet section: PDF pages 5–202 (198 pages).
- Front matter: PDF pages 1–4.
- Closing pages: PDF pages 203–204.
- The PDF is currently missing from the local repository.
- Historical metadata is retained; current status is `missing_local_file`.
- License/reuse terms remain unverified.

### Remaining work

- Verify document reuse/licensing terms.
- Recover the original Tamil Nadu compendium or document its recovery gap.
- Acquire additional permitted NFHS source documents as available.
- Refine expanded corpus capacity estimates as more documents are collected.
- Individual fact-sheet PDF sizes have not yet been measured separately.
