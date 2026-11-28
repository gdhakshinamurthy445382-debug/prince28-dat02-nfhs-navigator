"""Generate docs/INGEST_REPORT.md from PostgreSQL without overwriting notes."""

import asyncio
import re
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import text

from nfhs_navigator.config import get_settings
from nfhs_navigator.db.session import make_engine

START = "<!-- ingest-report:start -->"
END = "<!-- ingest-report:end -->"
REPORT = Path("docs/INGEST_REPORT.md")
CAPACITY = Path("docs/CAPACITY.md")


async def collect() -> dict:
    engine = make_engine(get_settings())
    try:
        async with engine.connect() as conn:
            documents = await conn.scalar(text("SELECT COUNT(*) FROM documents")) or 0
            parsed = await conn.scalar(text("SELECT COUNT(DISTINCT document_id) FROM pages")) or 0
            page_result = await conn.execute(
                text("""
                SELECT COUNT(*) AS pages,
                       COALESCE(SUM(char_length(text)), 0) AS text_characters
                FROM pages
            """)
            )
            page_row = page_result.one()
            failures = await conn.scalar(text("SELECT COUNT(*) FROM parse_failures")) or 0
            usage_result = await conn.execute(
                text("""
                SELECT COALESCE(SUM(tokens_in), 0) AS tokens_in,
                       COALESCE(SUM(tokens_out), 0) AS tokens_out
                FROM llm_calls
            """)
            )
            usage = usage_result.one()
            status_result = await conn.execute(
                text("""
                SELECT status, COUNT(*) AS items
                FROM ingest_items GROUP BY status
            """)
            )
            statuses = {row.status: row.items for row in status_result}
    finally:
        await engine.dispose()

    capacity_text = CAPACITY.read_text(encoding="utf-8") if CAPACITY.exists() else ""
    match = re.search(r"Total PDF pages:\s*([\d,]+)", capacity_text)
    baseline = int(match.group(1).replace(",", "")) if match else None

    return {
        "documents": int(documents),
        "parsed": int(parsed),
        "pages": int(page_row.pages),
        "text_characters": int(page_row.text_characters),
        "approx_text_tokens": round(int(page_row.text_characters) / 4),
        "parse_failures": int(failures),
        "dead_letter": int(statuses.get("failed", 0)),
        "queued": int(statuses.get("queued", 0)),
        "running": int(statuses.get("running", 0)),
        "done": int(statuses.get("done", 0)),
        "skipped": int(statuses.get("skipped", 0)),
        "tokens_in": int(usage.tokens_in),
        "tokens_out": int(usage.tokens_out),
        "capacity_baseline": baseline,
    }


def update_report(data: dict) -> None:
    generated = datetime.now(UTC).isoformat(timespec="seconds")
    total_llm_tokens = data["tokens_in"] + data["tokens_out"]
    baseline = data["capacity_baseline"]

    if baseline:
        comparison = (
            f"{data['pages'] / baseline:.1f}x the historical page baseline. "
            "The corpus scopes differ, so this is not an apples-to-apples "
            "forecast-accuracy comparison."
        )
        baseline_line = f"{baseline:,} pages"
    else:
        comparison = "No historical page baseline was found in CAPACITY.md."
        baseline_line = "Not recorded"

    block = f"""{START}
## Latest database snapshot

- Generated (UTC): {generated}
- Documents in database: {data["documents"]}
- Documents with indexed pages: {data["parsed"]}
- Indexed pages: {data["pages"]}
- Stored page-text characters: {data["text_characters"]:,}
- Approximate document-text tokens (characters divided by 4): {data["approx_text_tokens"]:,}
- Ingestion items done: {data["done"]}
- Ingestion items skipped: {data["skipped"]}
- Ingestion items queued: {data["queued"]}
- Ingestion items running: {data["running"]}
- Dead-letter ingestion items: {data["dead_letter"]}
- Parse failures: {data["parse_failures"]}
- LLM input tokens recorded by the API: {data["tokens_in"]:,}
- LLM output tokens recorded by the API: {data["tokens_out"]:,}
- Total recorded LLM usage tokens: {total_llm_tokens:,}

## Capacity comparison

- Historical page baseline in CAPACITY.md: {baseline_line}
- Current indexed pages: {data["pages"]:,}
- Comparison: {comparison}
- Historical token estimate in CAPACITY.md: Not recorded.
- Note: document-text tokens above are a rough character-based estimate, not tokenizer measurements
  or LLM API usage tokens.
{END}"""

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    if REPORT.exists():
        old = REPORT.read_text(encoding="utf-8")
        if START in old and END in old:
            before, remainder = old.split(START, 1)
            _, after = remainder.split(END, 1)
            content = before + block + after
        elif START in old or END in old:
            raise RuntimeError("Incomplete report markers; refusing to overwrite.")
        else:
            content = old.rstrip() + "\n\n" + block + "\n"
    else:
        content = block + "\n\n### What I learnt\n- \n- \n- \n"

    REPORT.write_text(content, encoding="utf-8")
    print(
        f"documents={data['documents']} pages={data['pages']} "
        f"dead_letter={data['dead_letter']} -> {REPORT.as_posix()}"
    )
    print(
        f"text_characters={data['text_characters']} "
        f"approx_text_tokens={data['approx_text_tokens']} "
        f"llm_tokens={total_llm_tokens}"
    )


async def main() -> None:
    update_report(await collect())


if __name__ == "__main__":
    asyncio.run(main())
