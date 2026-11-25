"""Polite, resumable corpus downloader."""

import asyncio
import csv
import hashlib
import json
import random
import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit

import httpx
from protego import Protego

CONTACT = "https://github.com/YOUR-GITHUB-USERNAME/prince28-dat02-nfhs-navigator"
ROBOTS_TOKEN = "examate-student-bot"
USER_AGENT = f"{ROBOTS_TOKEN}/0.1 (student project; +{CONTACT})"

RETRYABLE = {408, 425, 429, 500, 502, 503, 504}
MAX_WAIT = 120.0
MAX_BYTES = 200 * 1024 * 1024
ATTEMPT_TIMEOUT = 300.0

KNOWN_EXT = {
    ".pdf",
    ".html",
    ".htm",
    ".json",
    ".txt",
    ".md",
    ".mdx",
    ".rst",
    ".adoc",
    ".csv",
    ".xml",
    ".yaml",
    ".yml",
    ".zip",
    ".docx",
    ".xlsx",
    ".xls",
}

EXT_BY_TYPE = {
    "application/pdf": ".pdf",
    "text/html": ".html",
    "application/json": ".json",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/csv": ".csv",
    "application/xml": ".xml",
    "text/xml": ".xml",
    "application/zip": ".zip",
    "application/yaml": ".yaml",
}


@dataclass(frozen=True)
class Source:
    url: str
    source: str
    licence: str
    title: str = ""


class DownloadError(Exception):
    def __init__(self, message, *, code=None, retry_after=None):
        super().__init__(message)
        self.code = code
        self.retry_after = retry_after


def now_iso():
    return datetime.now(UTC).isoformat(timespec="seconds")


def slug(text, limit=60):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:limit] or "file"


def file_stem(url):
    parts = urlsplit(url)
    last = unquote(parts.path.rstrip("/").rsplit("/", 1)[-1]) or parts.netloc
    name = last.rsplit(".", 1)[0] if "." in last else last
    return f"{slug(name)}-{hashlib.sha256(url.encode()).hexdigest()[:8]}"


def pick_ext(url, content_type):
    suffix = Path(urlsplit(url).path).suffix.lower()

    if suffix in KNOWN_EXT:
        return suffix

    return EXT_BY_TYPE.get(
        content_type.split(";")[0].strip().lower(),
        ".bin",
    )


def backoff_delay(attempt, base=1.0, cap=60.0):
    return random.uniform(0, min(cap, base * 2**attempt))


def retry_after_seconds(value):
    if not value:
        return None

    value = value.strip()

    if value.isdigit():
        return float(value)

    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None

    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)

    return max(
        0.0,
        (when - datetime.now(UTC)).total_seconds(),
    )


def read_sources(path):
    sources = []
    seen = set()

    with path.open(encoding="utf-8-sig", newline="") as handle:
        lines = (ln for ln in handle if ln.strip() and not ln.lstrip().startswith("#"))

        for number, row in enumerate(csv.DictReader(lines), start=1):
            url = (row.get("url") or "").strip()
            name = (row.get("source") or "").strip()
            licence = (row.get("licence") or "").strip()

            if urlsplit(url).scheme not in {"http", "https"}:
                raise ValueError(f"sources row {number}: invalid URL: {url!r}")

            if not name or not licence:
                raise ValueError(f"sources row {number}: source and licence required")

            if url not in seen:
                seen.add(url)
                sources.append(
                    Source(
                        url,
                        name,
                        licence,
                        (row.get("title") or "").strip(),
                    )
                )

    return sources


class Manifest:
    """Append-only log; latest record for each URL wins."""

    def __init__(self, path):
        self.path = path
        self.records = {}

        if path.exists():
            text = path.read_text(encoding="utf-8")

            for line in text.splitlines():
                try:
                    record = json.loads(line)

                    if "url" in record:
                        self.records[record["url"]] = record

                except json.JSONDecodeError:
                    continue

            if text and not text.endswith("\n"):
                with path.open("a", encoding="utf-8") as handle:
                    handle.write("\n")

    def done(self, url, root):
        record = self.records.get(url)

        return bool(
            record
            and record.get("status") == "downloaded"
            and (root / record.get("path", "")).is_file()
        )

    def add(self, record):
        self.records[record["url"]] = record
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


class Downloader:
    def __init__(
        self,
        root,
        manifest,
        *,
        delay=3.0,
        max_concurrency=4,
        max_retries=3,
        sleep=asyncio.sleep,
    ):
        self.root = Path(root)
        self.manifest = Manifest(Path(manifest))
        self.delay = max(0.0, delay)
        self.semaphore = asyncio.Semaphore(max(1, max_concurrency))
        self.max_retries = max(0, max_retries)
        self.sleep = sleep
        self.last_request = {}
        self.robots_cache = {}
        self.robots_locks = {}
        self.host_locks = {}

    async def wait_host(self, host):
        lock = self.host_locks.setdefault(host, asyncio.Lock())

        async with lock:
            elapsed = time.monotonic() - self.last_request.get(host, 0)

            if elapsed < self.delay:
                await self.sleep(self.delay - elapsed)

            self.last_request[host] = time.monotonic()

    async def allowed(self, client, url):
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"

        if origin not in self.robots_cache:
            lock = self.robots_locks.setdefault(origin, asyncio.Lock())

            async with lock:
                if origin not in self.robots_cache:
                    robots_url = f"{origin}/robots.txt"

                    try:
                        response = await client.get(robots_url)

                        if response.status_code in (401, 403):
                            parser = Protego.parse("User-agent: *\nDisallow: /\n")

                        elif response.status_code == 404:
                            parser = Protego.parse("")

                        elif response.status_code >= 400:
                            parser = Protego.parse("User-agent: *\nDisallow: /\n")

                        else:
                            parser = Protego.parse(response.text)

                        self.robots_cache[origin] = parser

                    except httpx.HTTPError:
                        self.robots_cache[origin] = Protego.parse("User-agent: *\nDisallow: /\n")

        parser = self.robots_cache[origin]
        return parser.can_fetch(USER_AGENT, url)

    async def download_one(self, client, source):
        url = source.url
        host = urlsplit(url).netloc
        prefix = file_stem(url)
        raw_dir = self.root / "raw"

        if self.manifest.done(url, self.root):
            print(f"SKIP {url}")
            return

        if not await self.allowed(client, url):
            print(f"ROBOTS BLOCKED {url}")

            self.manifest.add(
                {
                    "url": url,
                    "status": "blocked",
                    "reason": "robots.txt",
                    "time": now_iso(),
                }
            )
            return

        async with self.semaphore:
            for attempt in range(self.max_retries + 1):
                await self.wait_host(host)

                try:
                    raw_dir.mkdir(parents=True, exist_ok=True)

                    # Find an existing partial file.
                    candidates = list(raw_dir.glob(f"{prefix}.*.part"))

                    partial_file = candidates[0] if candidates else None

                    partial_size = partial_file.stat().st_size if partial_file is not None else 0

                    # Remove oversized partials.
                    if partial_size > MAX_BYTES:
                        partial_file.unlink()
                        partial_file = None
                        partial_size = 0

                    request_headers = {}

                    # Request only the missing bytes.
                    if partial_size > 0:
                        request_headers["Range"] = f"bytes={partial_size}-"

                    async with client.stream(
                        "GET",
                        url,
                        headers=request_headers,
                    ) as response:
                        # A stale partial can produce 416.
                        # Remove it so the next retry starts fresh.
                        if response.status_code == 416:
                            if partial_file is not None:
                                partial_file.unlink(missing_ok=True)

                            raise DownloadError("Range rejected; partial removed")

                        if response.status_code in RETRYABLE:
                            raise DownloadError(
                                f"HTTP {response.status_code}",
                                code=response.status_code,
                                retry_after=retry_after_seconds(
                                    response.headers.get("Retry-After")
                                ),
                            )

                        if response.status_code >= 400:
                            raise DownloadError(
                                f"HTTP {response.status_code}",
                                code=response.status_code,
                            )

                        content_type = response.headers.get(
                            "Content-Type",
                            "application/octet-stream",
                        )

                        ext = pick_ext(url, content_type)

                        rel = Path("raw") / f"{prefix}{ext}"
                        final = self.root / rel
                        temp = final.with_suffix(final.suffix + ".part")

                        final.parent.mkdir(
                            parents=True,
                            exist_ok=True,
                        )

                        # Server ignored Range (200):
                        # discard the old partial and restart.
                        if response.status_code == 200:
                            partial_size = 0

                            if partial_file is not None and partial_file != temp:
                                partial_file.unlink(missing_ok=True)

                        # Server accepted Range (206).
                        elif response.status_code == 206:
                            content_range = response.headers.get("Content-Range", "")

                            expected = f"bytes {partial_size}-"

                            if not content_range.startswith(expected):
                                raise DownloadError("Invalid Content-Range")

                            # Move partial to the expected extension.
                            if partial_file is not None and partial_file != temp:
                                if temp.exists():
                                    temp.unlink()

                                partial_file.replace(temp)

                        digest = hashlib.sha256()
                        size = 0

                        # Hash already downloaded bytes.
                        if partial_size > 0 and temp.exists():
                            with temp.open("rb") as existing:
                                while True:
                                    chunk = existing.read(65536)

                                    if not chunk:
                                        break

                                    size += len(chunk)
                                    digest.update(chunk)

                        mode = "ab" if partial_size > 0 else "wb"

                        # Resume or start downloading.
                        with temp.open(mode) as handle:
                            async for chunk in response.aiter_bytes(65536):
                                size += len(chunk)

                                if size > MAX_BYTES:
                                    raise DownloadError("File exceeds size limit")

                                digest.update(chunk)
                                handle.write(chunk)

                        if size == 0:
                            raise DownloadError("Empty file")

                        if final.suffix.lower() == ".pdf":
                            # Reject HTML or other non-PDF content.
                            with temp.open("rb") as handle:
                                signature = handle.read(5)

                            if signature != b"%PDF-":
                                raise DownloadError("Invalid PDF signature")

                        temp.replace(final)

                        record = {
                            "url": url,
                            "status": "downloaded",
                            "path": str(rel).replace("\\", "/"),
                            "sha256": digest.hexdigest(),
                            "bytes": size,
                            "source": source.source,
                            "licence": source.licence,
                            "title": source.title,
                            "time": now_iso(),
                        }

                        self.manifest.add(record)
                        print(f"OK {url} ({size} bytes)")
                        return

                except (
                    httpx.HTTPError,
                    DownloadError,
                    OSError,
                ) as exc:
                    code = getattr(exc, "code", None)
                    retry_after = getattr(exc, "retry_after", None)

                    if attempt >= self.max_retries:
                        self.manifest.add(
                            {
                                "url": url,
                                "status": "error",
                                "reason": str(exc),
                                "time": now_iso(),
                            }
                        )

                        print(f"ERROR {url}: {exc}")
                        return

                    if code is not None and code not in RETRYABLE:
                        self.manifest.add(
                            {
                                "url": url,
                                "status": "error",
                                "reason": str(exc),
                                "time": now_iso(),
                            }
                        )

                        print(f"ERROR {url}: {exc}")
                        return

                    wait = retry_after if retry_after is not None else backoff_delay(attempt)

                    wait = min(MAX_WAIT, wait)

                    print(f"RETRY {url} in {wait:.1f}s ({exc})")

                    await self.sleep(wait)

    async def run(self, sources):
        self.root.mkdir(parents=True, exist_ok=True)

        timeout = httpx.Timeout(ATTEMPT_TIMEOUT)

        limits = httpx.Limits(
            max_connections=max(1, self.semaphore._value),
            max_keepalive_connections=max(1, self.semaphore._value),
        )

        headers = {"User-Agent": USER_AGENT}

        async with httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            headers=headers,
            follow_redirects=True,
        ) as client:
            tasks = [self.download_one(client, source) for source in sources]

            await asyncio.gather(*tasks)


async def fetch_urls(
    sources_path,
    root="data",
    manifest_path="data/manifest.jsonl",
    delay=3.0,
    max_concurrency=4,
    max_retries=3,
):
    sources = read_sources(Path(sources_path))

    downloader = Downloader(
        root,
        manifest_path,
        delay=delay,
        max_concurrency=max_concurrency,
        max_retries=max_retries,
    )

    await downloader.run(sources)
    return downloader.manifest.records


def fetch_manual(
    source,
    file_path,
    root="data",
    manifest_path="data/manifest.jsonl",
):
    """Register a manually downloaded file into the same corpus manifest."""

    source = source if isinstance(source, Source) else Source(**source)

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    size = file_path.stat().st_size

    if size == 0:
        raise ValueError("Empty file")

    if size > MAX_BYTES:
        raise ValueError("File exceeds size limit")

    digest = hashlib.sha256()

    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)

    root = Path(root)
    rel = Path("raw") / file_path.name
    final = root / rel
    final.parent.mkdir(parents=True, exist_ok=True)

    if file_path.resolve() != final.resolve():
        final.write_bytes(file_path.read_bytes())

    record = {
        "url": source.url,
        "status": "downloaded",
        "path": str(rel).replace("\\", "/"),
        "sha256": digest.hexdigest(),
        "bytes": size,
        "source": source.source,
        "licence": source.licence,
        "title": source.title,
        "method": "manual",
        "time": now_iso(),
    }

    manifest = Manifest(Path(manifest_path))
    manifest.add(record)

    print(f"REGISTERED {final} ({size} bytes)")
    return record
