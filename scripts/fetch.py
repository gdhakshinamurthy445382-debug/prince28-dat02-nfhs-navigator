"""CLI for the polite corpus downloader."""

import argparse
import asyncio

from nfhs_navigator.ingest.fetch import (
    Source,
    fetch_manual,
    fetch_urls,
)


def main():
    parser = argparse.ArgumentParser(description="NFHS Navigator corpus fetcher")
    sub = parser.add_subparsers(dest="command", required=True)

    urls = sub.add_parser("urls", help="Download URLs from data/sources.csv")
    urls.add_argument("--sources", default="data/sources.csv")
    urls.add_argument("--root", default="data")
    urls.add_argument("--manifest", default="data/manifest.jsonl")
    urls.add_argument("--delay", type=float, default=3.0)
    urls.add_argument("--concurrency", type=int, default=4)
    urls.add_argument("--retries", type=int, default=3)

    manual = sub.add_parser("manual", help="Register a manually downloaded file")
    manual.add_argument("url")
    manual.add_argument("file")
    manual.add_argument("--source", required=True)
    manual.add_argument("--licence", required=True)
    manual.add_argument("--title", default="")
    manual.add_argument("--root", default="data")
    manual.add_argument("--manifest", default="data/manifest.jsonl")

    args = parser.parse_args()

    if args.command == "urls":
        asyncio.run(
            fetch_urls(
                args.sources,
                root=args.root,
                manifest_path=args.manifest,
                delay=args.delay,
                max_concurrency=args.concurrency,
                max_retries=args.retries,
            )
        )
    elif args.command == "manual":
        fetch_manual(
            Source(args.url, args.source, args.licence, args.title),
            args.file,
            root=args.root,
            manifest_path=args.manifest,
        )


if __name__ == "__main__":
    main()
