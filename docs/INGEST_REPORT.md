<!-- ingest-report:start -->
## Latest database snapshot

- Generated (UTC): 2026-11-28T10:07:09+00:00
- Documents in database: 40
- Documents with indexed pages: 20
- Indexed pages: 4519
- Stored page-text characters: 10,746,095
- Approximate document-text tokens (characters divided by 4): 2,686,524
- Ingestion items done: 20
- Ingestion items skipped: 0
- Ingestion items queued: 0
- Ingestion items running: 0
- Dead-letter ingestion items: 0
- Parse failures: 0
- LLM input tokens recorded by the API: 9,671
- LLM output tokens recorded by the API: 4,132
- Total recorded LLM usage tokens: 13,803

## Capacity comparison

- Historical page baseline in CAPACITY.md: 204 pages
- Current indexed pages: 4,519
- Comparison: 22.2x the historical page baseline. The corpus scopes differ, so this is not an apples-to-apples forecast-accuracy comparison.
- Historical token estimate in CAPACITY.md: Not recorded.
- Note: document-text tokens above are a rough character-based estimate, not tokenizer measurements or LLM API usage tokens.
<!-- ingest-report:end -->

### What I learnt
- PostgreSQL stores the authoritative ingestion status, while Redis holds the ARQ jobs and in-progress locks.
- After the worker restarted, interrupted items 8 and 9 were processed again; both reached attempts=2 without creating duplicate documents.
- Separating the API and worker into Docker Compose services lets the API accept requests while the worker processes the background queue independently.
