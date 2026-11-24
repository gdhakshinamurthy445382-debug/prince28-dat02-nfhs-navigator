"""Compare two parsers on your hardest files and write a table into NOTES.md.

  uv run python scripts/compare_parsers.py
  uv run python scripts/compare_parsers.py data/raw/a.pdf data/raw/b.pdf

PDF: PyMuPDF against pypdf. HTML: trafilatura against simply stripping the tags.
Text files (Markdown, reStructuredText, YAML ...) have one parser, so you check headings by eye.
"""

import json
import re
import sys
import time
from pathlib import Path

from nfhs_navigator.ingest.parse import (
    ParsedDoc,
    ParseError,
    finish,
    headings_in,
    parse_file,
    split_pages,
)

MANIFEST = Path("data/manifest.jsonl")
NOTES = Path("NOTES.md")
START, END = "<!-- parsers:start -->", "<!-- parsers:end -->"


def strip_tags(path: Path) -> ParsedDoc:
    """The naive HTML 'parser': delete every tag and keep whatever text is left."""
    html = path.read_text(encoding="utf-8", errors="replace")
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    return finish("strip-tags", "html", "", split_pages(text))


def measure(parser, path: Path) -> dict:
    started = time.perf_counter()
    try:
        doc = parser(path)
    except ParseError as error:
        return {
            "ok": False,
            "note": error.reason,
            "seconds": time.perf_counter() - started,
        }

    text = "\n".join(page.text for page in doc.pages)
    return {
        "ok": True,
        "pages": len(doc.pages),
        "chars": len(text),
        "headings": len(headings_in(text)[0]),
        "tables": sum(page.tables for page in doc.pages),
        "seconds": time.perf_counter() - started,
    }


def pick_files() -> list[Path]:
    """Pick the 10 largest downloaded PDF/HTML files, resolving paths under data/."""
    records = [
        json.loads(line)
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    candidates = []
    for record in records:
        if record.get("status") != "downloaded" or not record.get("path"):
            continue

        manifest_path = Path(record["path"])
        path = manifest_path if manifest_path.is_absolute() else MANIFEST.parent / manifest_path

        if path.is_file():
            candidates.append((path, record.get("bytes", 0)))

    candidates.sort(key=lambda item: -item[1])

    rich = [path for path, _ in candidates if path.suffix.lower() in {".pdf", ".html", ".htm"}]

    selected = (rich or [path for path, _ in candidates])[:10]
    return selected


def cells(result: dict | None) -> str:
    if result is None:
        return "-"
    if not result["ok"]:
        return f"FAILED: {result['note']}"
    return f"{result['chars']:,} chars, {result['headings']} headings, {result['tables']} tables"


def main() -> int:
    sys.stdout.reconfigure(errors="replace")

    files = [Path(arg) for arg in sys.argv[1:]] or pick_files()

    if not files:
        print("No downloaded files found in the manifest.")
        return 1

    rows = []

    for path in files:
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            a = measure(parse_file, path)
            b = measure(lambda p: parse_file(p, pdf_parser="pypdf"), path)
            names = "PyMuPDF / pypdf"

        elif suffix in {".html", ".htm"}:
            a = measure(parse_file, path)
            b = measure(strip_tags, path)
            names = "trafilatura / strip tags"

        else:
            a = measure(parse_file, path)
            b = None
            names = "plain (check headings by eye)"

        pages = a.get("pages", "-")

        speed = f"{a['seconds']:.2f} s"
        if b is not None:
            speed += f" / {b['seconds']:.2f} s"

        row = f"| {path.name[:48]} | {names} | {pages} | {cells(a)} | {cells(b)} | {speed} | |"

        rows.append(row)
        print(row)

    table = "\n".join(
        [
            START,
            "| File | Parsers (A / B) | Pages | A found | B found | Time (A / B) | Better, why |",
            "|---|---|---|---|---|---|---|",
            *rows,
            END,
        ]
    )

    text = NOTES.read_text(encoding="utf-8") if NOTES.exists() else "# Notes\n"

    if START in text and END in text:
        start_index = text.index(START)
        end_index = text.index(END) + len(END)
        text = text[:start_index] + table + text[end_index:]
    else:
        text = text.rstrip() + "\n\n## D07 - Parser comparison\n\n" + table + "\n"

    NOTES.write_text(text, encoding="utf-8")

    print(f"compared {len(rows)} files -> table written to NOTES.md (fill in the last column)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
