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



## D07 - Parsing and corpus ingestion

### First parsing run

- Fixed manifest path resolution in scripts/parse_corpus.py.
- Manifest paths are relative to data/, while downloaded files exist under data/raw/.
- Added corpus_path() to resolve actual file paths without changing stored manifest paths.
- Verified downloaded files discovered: 2.
- First parsing run: 2 files parsed, 897 pages stored.
- Parsing runtime: 168.0 seconds.
- PyMuPDF emitted an optional pymupdf_layout suggestion; no installation required.

### Content quality inspection

- Document title extraction verified: National Family Health Survey.
- Page text and heading paths were successfully stored.
- Some table content was readable.
- Continuation headings such as Continued... appear in heading paths.
- Some pages contain footer/contact information and unwanted text.
- Garbled characters were observed in extracted text, likely related to font encoding.
- Legacy Tamil fonts may require OCR or a Unicode source for better text extraction.

### Corpus status after first parse

- Downloaded files available locally: 2 PDFs.
- Parsed documents: 2.
- Pages extracted: 897.
- Parse failures observed in the first run: none.
- Parser works for the initial corpus; text cleanup and heading refinement remain future work.

### Parse failures and repeat-run verification

- Ran the parser twice against the current corpus.
- Second run skipped both previously parsed files.
- Second run inserted 0 new pages.
- Verified parse_failures table: 0 failure records.
- Current corpus parse failures: 0 out of 2 files.
- No retry-failed run was necessary.

## D07 - Expanded NFHS corpus ingestion

### Corpus expansion

- Expanded the local PDF corpus from 2 to 10 documents.
- Added 8 NFHS-5 state reports: Arunachal Pradesh, Assam, Delhi, Goa, Gujarat, Madhya Pradesh, Maharashtra, and Manipur.
- Verified PDF signatures, readability, manifest hashes, and file sizes for all 10 documents.
- Total corpus size: 49,730,324 bytes (approximately 47.4 MiB).
- Total pages across the 10 PDFs: 2,503.

### Expanded parsing verification

- First expanded parsing run: 2 files already parsed, 8 newly parsed.
- Newly extracted pages: 1,606.
- Parsing runtime: 218.2 seconds.
- Repeat run: all 10 files already parsed; 0 new pages.
- Repeat-run runtime: 1.1 seconds.
- No parsing errors were reported in either run.
- Corpus parsing is repeatable and skips previously parsed documents.


### Final failure audit

- Queried PostgreSQL \parse_failures\ directly after the expanded corpus run.
- Result: 0 parsing failures out of 10 documents.
- No \--retry-failed\ run was necessary.
- Day 4 parsing and failure-audit checklist completed.

## D07 · Parser comparison

<!-- parsers:start -->
| File | Parsers (A / B) | Pages | A found | B found | Time (A / B) | Better, why |
|---|---|---|---|---|---|---|
| national-family-health-survey-nfhs-6-2023-2024-f | PyMuPDF / pypdf | 182 | 1,744,457 chars, 349 headings, 183 tables | 543,767 chars, 0 headings, 0 tables | 70.74 s / 21.43 s | PyMuPDF detected headings/tables; pypdf detected none |
| fr375-a059d415.pdf | PyMuPDF / pypdf | 715 | 1,510,511 chars, 1659 headings, 165 tables | 2,763,016 chars, 0 headings, 0 tables | 68.12 s / 100.45 s | PyMuPDF detected headings/tables; pypdf detected none |
| fr374-arunachalpradesh-7bd9dee4.pdf | PyMuPDF / pypdf | 200 | 427,709 chars, 404 headings, 14 tables | 839,517 chars, 0 headings, 0 tables | 19.14 s / 25.79 s | PyMuPDF detected headings/tables; pypdf detected none |
| fr374-manipur-1337b41f.pdf | PyMuPDF / pypdf | 198 | 408,216 chars, 344 headings, 17 tables | 790,552 chars, 0 headings, 0 tables | 18.06 s / 22.76 s | PyMuPDF detected headings/tables; pypdf detected none |
| fr374-assam-e9606422.pdf | PyMuPDF / pypdf | 200 | 432,184 chars, 425 headings, 25 tables | 816,894 chars, 0 headings, 0 tables | 19.27 s / 25.09 s | PyMuPDF detected headings/tables; pypdf detected none |
| fr374-madhyapradesh-1d9acdff.pdf | PyMuPDF / pypdf | 206 | 447,095 chars, 525 headings, 19 tables | 829,656 chars, 0 headings, 0 tables | 22.13 s / 23.03 s | PyMuPDF detected headings/tables; pypdf detected none |
| fr374-delhi-f1b5988e.pdf | PyMuPDF / pypdf | 206 | 411,541 chars, 367 headings, 14 tables | 804,785 chars, 0 headings, 0 tables | 17.66 s / 24.40 s | PyMuPDF detected headings/tables; pypdf detected none |
| fr374-maharashtra-5f247407.pdf | PyMuPDF / pypdf | 204 | 437,097 chars, 481 headings, 15 tables | 438,012 chars, 0 headings, 0 tables | 19.32 s / 6.82 s | PyMuPDF detected headings/tables; pypdf detected none |
| fr374-gujarat-0a0b1d93.pdf | PyMuPDF / pypdf | 210 | 436,917 chars, 435 headings, 22 tables | 439,096 chars, 0 headings, 0 tables | 18.91 s / 6.37 s | PyMuPDF detected headings/tables; pypdf detected none |
| fr374-goa-3c688307.pdf | PyMuPDF / pypdf | 182 | 345,332 chars, 320 headings, 12 tables | 347,855 chars, 0 headings, 0 tables | 15.10 s / 5.74 s | PyMuPDF detected headings/tables; pypdf detected none |
<!-- parsers:end -->

## D07 · Parsing my corpus

- Files in manifest: 11 · downloaded: 10 · blocked: 1 · parsed: 10 · failed: 0 · pages in PostgreSQL: 2,503
- Parsing coverage: 100% of downloaded files (10/10). The blocked manifest entry is excluded.

### Failures by reason

| Reason | Files | What I did |
|---|---:|---|
| None | 0 | No parsing failures; no retry required |

- The one I fixed: manifest paths were not resolved correctly; fixed with `corpus_path()` in `scripts/parse_corpus.py`, resolving paths relative to `data/`.

### What I saw when I read my parsed pages

- A page where the heading path is right: Gujarat report, page 17 — `FERTILITY` → `Age at first marriage` → `Fertility levels`.
- Something that came out wrong: Madhya Pradesh report, page 65 — heading metadata refers to domestic/sexual violence, but the page text is a fertility table.
- A table: Madhya Pradesh report, page 66 — Table 19 was extracted as loose text rather than a Markdown grid.

### My parser choice

- For PDFs I use PyMuPDF because the comparison detected headings and tables in all 10 PDFs (2,503 pages); pypdf detected 0 headings and 0 tables across the same files.
- Chart-heavy pages, formula-heavy content, and some poorly encoded PDF text remain difficult for both parsers.

### One thing that went wrong today, and how I fixed it

- The manifest had 11 entries, which initially made parsing coverage appear to be 90.9%. One entry was blocked, not a downloadable PDF. I corrected the audit to measure coverage against the 10 downloaded files, giving 100% (10/10).


## D08 · LLM gateway

### Gateway and configuration
- Primary provider: Gemini, model `gemini-3.5-flash-lite`.
- Fallback provider: Groq, model `openai/gpt-oss-20b`.
- Provider mode: `auto`; Groq-only mode is also configurable.
- Added `/v1/chat` streaming endpoint and LLM usage logging in `llm_calls`.
- Added `scripts/ask.py` and `scripts/llm_ping.py`.
- System prompt stored at `prompts/chat_system_v1.md`.
- Dockerfile copies prompts into `/app/prompts`.
- API keys configured in local `.env` and Render environment; `.env` is Git-ignored.

### Validation
- Unit and integration tests: 94 passed.
- Alembic: one head, `aa046f38c1e5`.
- Docker image `nfhs-navigator:day08` built successfully.
- Verified `/app/prompts/chat_system_v1.md` inside the Docker image.
- Docker warning: duplicate `builder` stage name; build succeeded, warning not fixed.

### Tokens: English against Tamil
| Message | tokens in |
|---|---:|
| "Hi" (baseline, mostly system prompt) | 170 |
| English refund question | 178 (8 message tokens) |
| Same refund question in Tamil | 186 (16 message tokens) |

- Tamil message used approximately 2x the message tokens of English.

### What the model does without my documents
- NFHS-6 future question: acknowledged uncertainty.
- Off-topic Cricket World Cup question: rejected as off-topic.
- Tamil Nadu stunting under 5, NFHS-5: answered 25.0%, matching the verified figure.
- Tamil Nadu anemia among women 15–49: answered 57%; verified figure 53.4%, a difference of 3.6 percentage points. Possible confusion with child anemia; answer needs correction.

### Fallback and circuit breaker
- With Gemini intentionally broken, requests successfully fell back to Groq.
- Database showed Gemini 404 failures and successful Groq fallback calls.
- Circuit-breaker skip and half-open recovery behavior were not fully verified from logs.

### The bill
- Observed 15 usage rows: 11 Gemini calls and 4 Groq calls.
- Combined estimated cost: Rs 0.206534.
- Groq fallback cost for 4 calls: Rs 0.031635.
- Final live `/v1/usage` bill: pending.

### Docker and deployment
- Docker build succeeded after starting Docker Desktop.
- Prompt file verified inside image.
- Render API keys configured.
- Live deployment test, streaming latency and live usage verification: pending.

### One thing that went wrong today, and how I fixed it
- Docker initially failed because the Docker engine was not running. Started Docker Desktop, verified the engine, and rebuilt successfully.
- Duplicate Docker build stages produce a warning; deferred cleanup.

## D09 · Prompt versions compared

<!-- prompts:start -->

| Prompt version | Correct | Accuracy | Invalid replies | Avg tokens in |

|---|---|---|---|---|

| classify_v1 | 12/20 | 60% | 0 | 116 |

| classify_v2 | 20/20 | 100% | 0 | 279 |

| classify_v3 | 20/20 | 100% | 0 | 414 |

| classify_v4 | 20/20 | 100% | 0 | 432 |

<!-- prompts:end -->

### D09 · Prompts and structured output
- My best router prompt: classify_v4 with 20 / 20 (100%)
- What I changed in v4, and what happened to the score: Tightened the definition of personal; score stayed 20/20 (100%).
- The question my best version still gets wrong (line, wanted, got), and why I think so: None for v2, v3, or v4 on this 20-question test set.
- A label in my test set that I changed after seeing the results (or "none"): None.
- Input tokens per question: v1 116, best version (v4) 432. Is the extra accuracy worth it? Both v2 and v4 score 100%, so v4 shows no measured accuracy gain on this test set while using more input tokens.
### My contract (DocMeta)
- Fields I kept from my project card: [confirm final DocMeta fields].
- Fields I deleted, and why they make no sense per document: [confirm fields deleted].
- The field I tightened, and how: [confirm field and constraint].
### Extraction run
- Prompt version: extract_v2 · documents: 10 ok, 0 repaired, 0 failed (of 10 parsed).
- Not finished? Why, and how many are left: Finished; 0 left.
- Most common failure reason, and what I did about it: None; no failures were recorded, so no retry was needed.
- A record that was valid but wrong (document, field, what it said, what is true): [fill from the record you manually checked; not yet confirmed].
- Cost at list price: Rs 0.2454 in total, Rs 0.02454 per document (approximately Rs 0.0245).
### One thing that went wrong today, and how I fixed it
- Router v1 missed 8 questions; adding clearer prompt definitions/examples in v2/v3 brought the test score to 20/20, and tightening the personal definition in v4 kept it at 20/20.
