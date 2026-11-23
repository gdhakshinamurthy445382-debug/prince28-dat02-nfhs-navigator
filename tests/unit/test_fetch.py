"""Unit tests for the polite corpus downloader."""

import asyncio
import hashlib
import json
from email.utils import formatdate

import httpx
import pytest

from nfhs_navigator.ingest.fetch import (
    MAX_BYTES,
    Downloader,
    Manifest,
    Source,
    backoff_delay,
    file_stem,
    pick_ext,
    read_sources,
    retry_after_seconds,
    slug,
)

# --------------------------------------------------
# Filename helpers
# --------------------------------------------------


def test_slug():
    assert slug("Tamil Nadu District #01") == "tamil-nadu-district-01"


def test_slug_empty():
    assert slug("") == "file"


def test_slug_limits_length():
    result = slug("a" * 100, limit=20)
    assert len(result) == 20


def test_file_stem_is_stable():
    url = "https://example.com/report.pdf"
    expected_hash = hashlib.sha256(url.encode()).hexdigest()[:8]

    assert file_stem(url) == f"report-{expected_hash}"
    assert file_stem(url) == file_stem(url)


def test_file_stem_for_url_without_filename():
    result = file_stem("https://example.com/")
    assert result.startswith("example-")


# --------------------------------------------------
# Extension detection
# --------------------------------------------------


def test_pick_ext_from_url():
    assert pick_ext("https://example.com/file.pdf", "") == ".pdf"


def test_pick_ext_from_content_type():
    assert (
        pick_ext(
            "https://example.com/download",
            "application/pdf",
        )
        == ".pdf"
    )


def test_pick_ext_from_content_type_with_charset():
    assert (
        pick_ext(
            "https://example.com/download",
            "text/html; charset=utf-8",
        )
        == ".html"
    )


def test_pick_ext_unknown_type():
    assert (
        pick_ext(
            "https://example.com/download",
            "application/unknown",
        )
        == ".bin"
    )


def test_url_extension_takes_precedence():
    assert (
        pick_ext(
            "https://example.com/file.csv",
            "application/pdf",
        )
        == ".csv"
    )


# --------------------------------------------------
# Retry and backoff
# --------------------------------------------------


def test_backoff_delay_range():
    delay = backoff_delay(2, base=1, cap=60)
    assert 0 <= delay <= 4


def test_backoff_delay_cap():
    delay = backoff_delay(20, base=1, cap=5)
    assert 0 <= delay <= 5


def test_retry_after_seconds():
    assert retry_after_seconds("15") == 15.0


def test_retry_after_invalid():
    assert retry_after_seconds("invalid-date") is None


def test_retry_after_empty():
    assert retry_after_seconds(None) is None


def test_retry_after_http_date():
    future_timestamp = 2_000_000_000
    http_date = formatdate(future_timestamp, usegmt=True)

    result = retry_after_seconds(http_date)

    assert result is not None
    assert result >= 0


# --------------------------------------------------
# Source CSV loading
# --------------------------------------------------


def test_read_sources(tmp_path):
    csv_file = tmp_path / "sources.csv"
    csv_file.write_text(
        "url,source,licence,title\n"
        "https://example.com/a.pdf,Example,Public domain,Report A\n"
        "https://example.com/b.pdf,Example,Public domain,Report B\n",
        encoding="utf-8",
    )

    sources = read_sources(csv_file)

    assert len(sources) == 2
    assert sources[0] == Source(
        "https://example.com/a.pdf",
        "Example",
        "Public domain",
        "Report A",
    )


def test_read_sources_skips_comments(tmp_path):
    csv_file = tmp_path / "sources.csv"
    csv_file.write_text(
        "# This is a comment\n"
        "\n"
        "url,source,licence,title\n"
        "https://example.com/a.pdf,Example,Terms,Report A\n",
        encoding="utf-8",
    )

    sources = read_sources(csv_file)

    assert len(sources) == 1
    assert sources[0].title == "Report A"


def test_read_sources_deduplicates_urls(tmp_path):
    csv_file = tmp_path / "sources.csv"
    csv_file.write_text(
        "url,source,licence,title\n"
        "https://example.com/a.pdf,Example,Terms,First\n"
        "https://example.com/a.pdf,Example,Terms,Duplicate\n",
        encoding="utf-8",
    )

    sources = read_sources(csv_file)

    assert len(sources) == 1
    assert sources[0].title == "First"


def test_read_sources_rejects_invalid_scheme(tmp_path):
    csv_file = tmp_path / "sources.csv"
    csv_file.write_text(
        "url,source,licence,title\nftp://example.com/a.pdf,Example,Terms,Report\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid URL"):
        read_sources(csv_file)


def test_read_sources_requires_source_and_licence(tmp_path):
    csv_file = tmp_path / "sources.csv"
    csv_file.write_text(
        "url,source,licence,title\nhttps://example.com/a.pdf,,,Report\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="required"):
        read_sources(csv_file)


def test_read_sources_empty_file(tmp_path):
    csv_file = tmp_path / "sources.csv"
    csv_file.write_text(
        "# No sources yet\nurl,source,licence,title\n",
        encoding="utf-8",
    )

    assert read_sources(csv_file) == []


# --------------------------------------------------
# Manifest
# --------------------------------------------------


def test_manifest_add_and_reload(tmp_path):
    manifest_file = tmp_path / "manifest.jsonl"

    manifest = Manifest(manifest_file)

    record = {
        "url": "https://example.com/a.pdf",
        "status": "downloaded",
        "path": "raw/a.pdf",
    }

    manifest.add(record)

    reloaded = Manifest(manifest_file)

    assert reloaded.records[record["url"]] == record


def test_manifest_done_when_file_exists(tmp_path):
    manifest_file = tmp_path / "manifest.jsonl"
    root = tmp_path / "data"

    downloaded_file = root / "raw" / "a.pdf"
    downloaded_file.parent.mkdir(parents=True)
    downloaded_file.write_bytes(b"PDF test content")

    manifest = Manifest(manifest_file)

    manifest.add(
        {
            "url": "https://example.com/a.pdf",
            "status": "downloaded",
            "path": "raw/a.pdf",
        }
    )

    assert manifest.done("https://example.com/a.pdf", root)


def test_manifest_not_done_when_file_missing(tmp_path):
    manifest_file = tmp_path / "manifest.jsonl"
    root = tmp_path / "data"

    manifest = Manifest(manifest_file)

    manifest.add(
        {
            "url": "https://example.com/a.pdf",
            " status": "downloaded",
            "path": "raw/missing.pdf",
        }
    )

    assert not manifest.done("https://example.com/a.pdf", root)


def test_manifest_not_done_for_blocked_url(tmp_path):
    manifest_file = tmp_path / "manifest.jsonl"
    root = tmp_path / "data"

    manifest = Manifest(manifest_file)

    manifest.add(
        {
            "url": "https://example.com/a.pdf",
            "status": "blocked",
            "reason": "robots.txt",
        }
    )

    assert not manifest.done("https://example.com/a.pdf", root)


def test_manifest_latest_record_wins(tmp_path):
    manifest_file = tmp_path / "manifest.jsonl"

    manifest_file.write_text(
        json.dumps(
            {
                "url": "https://example.com/a.pdf",
                "status": "error",
            }
        )
        + "\n"
        + json.dumps(
            {
                "url": "https://example.com/a.pdf",
                "status": "downloaded",
                "path": "raw/a.pdf",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    manifest = Manifest(manifest_file)

    assert manifest.records["https://example.com/a.pdf"]["status"] == "downloaded"


def test_manifest_ignores_corrupt_line(tmp_path):
    manifest_file = tmp_path / "manifest.jsonl"

    manifest_file.write_text(
        '{"url":"https://example.com/a.pdf","status":"error"}\nthis is invalid json\n',
        encoding="utf-8",
    )

    manifest = Manifest(manifest_file)

    assert "https://example.com/a.pdf" in manifest.records


def test_manifest_repairs_missing_trailing_newline(tmp_path):
    manifest_file = tmp_path / "manifest.jsonl"

    manifest_file.write_text(
        json.dumps(
            {
                "url": "https://example.com/a.pdf",
                "status": "error",
            }
        ),
        encoding="utf-8",
    )

    Manifest(manifest_file)

    assert manifest_file.read_text(encoding="utf-8").endswith("\n")


# --------------------------------------------------
# Constants and Source model
# --------------------------------------------------


def test_max_bytes_is_200_mib():
    assert MAX_BYTES == 200 * 1024 * 1024


def test_source_default_title():
    source = Source(
        url="https://example.com/a.pdf",
        source="Example",
        licence="Terms",
    )

    assert source.title == ""


# --------------------------------------------------
# Resume download tests
# --------------------------------------------------


def test_partial_download_file_is_preserved(tmp_path):
    partial_file = tmp_path / "report.pdf.part"
    partial_content = b"%PDF-partial-content"

    partial_file.write_bytes(partial_content)

    assert partial_file.exists()
    assert partial_file.read_bytes() == partial_content


# --------------------------------------------------
# Actual HTTP resume test
# --------------------------------------------------


def test_download_resumes_from_existing_partial_file(tmp_path, monkeypatch):
    url = "https://example.com/report.pdf"
    existing_bytes = b"%PDF-"
    remaining_bytes = b"remaining-pdf-content"
    full_content = existing_bytes + remaining_bytes

    root = tmp_path / "data"
    manifest_path = tmp_path / "manifest.jsonl"

    partial_file = root / "raw" / f"{file_stem(url)}.pdf.part"
    partial_file.parent.mkdir(parents=True)
    partial_file.write_bytes(existing_bytes)

    def handler(request):
        assert request.headers.get("Range") == (f"bytes={len(existing_bytes)}-")

        return httpx.Response(
            206,
            headers={
                "Content-Type": "application/pdf",
                "Content-Range": (
                    f"bytes {len(existing_bytes)}-{len(full_content) - 1}/{len(full_content)}"
                ),
            },
            content=remaining_bytes,
        )

    async def allow_all(self, client, target_url):
        return True

    async def no_wait(self, host):
        return None

    monkeypatch.setattr(Downloader, "allowed", allow_all)
    monkeypatch.setattr(Downloader, "wait_host", no_wait)

    original_client = httpx.AsyncClient

    def mock_client(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", mock_client)

    source = Source(
        url=url,
        source="Example",
        licence="Test",
        title="Resume test",
    )

    downloader = Downloader(
        root=root,
        manifest=manifest_path,
        delay=0,
        max_retries=0,
    )

    asyncio.run(downloader.run([source]))

    final_file = root / "raw" / f"{file_stem(url)}.pdf"

    assert final_file.exists()
    assert final_file.read_bytes() == full_content

    record = downloader.manifest.records[url]
    assert record["status"] == "downloaded"
    assert record["bytes"] == len(full_content)
    assert record["sha256"] == hashlib.sha256(full_content).hexdigest()
