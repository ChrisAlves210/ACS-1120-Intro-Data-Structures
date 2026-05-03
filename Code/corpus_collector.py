#!python
"""Collect a text corpus from URLs using the Diffbot Article API.

Usage examples:
    export DIFFBOT_TOKEN="your_token_here"
    python corpus_collector.py data/pages.txt --output data/corpus.txt

    python corpus_collector.py data/pages.txt --token your_token_here \
        --output data/corpus.txt --timeout 20 --pause 0.1
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import requests

DIFFBOT_API_URL = "https://api.diffbot.com/v3/article"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch article text from URLs using Diffbot and build corpus.txt"
    )
    parser.add_argument(
        "urls_file",
        help="Path to text file with one URL per line (blank lines/# comments ignored)",
    )
    parser.add_argument(
        "--output",
        default="data/corpus.txt",
        help="Path to output corpus file (default: data/corpus.txt)",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("DIFFBOT_TOKEN"),
        help="Diffbot API token (default: DIFFBOT_TOKEN env var)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="HTTP timeout in seconds (default: 15)",
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=0.0,
        help="Optional pause between API requests in seconds (default: 0)",
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="Continue processing remaining URLs when one request fails",
    )
    return parser.parse_args()


def read_urls(urls_path: Path) -> list[str]:
    if not urls_path.is_file():
        raise FileNotFoundError(f"URLs file not found: {urls_path}")

    urls: list[str] = []
    for line in urls_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        urls.append(stripped)
    return urls


def get_article_text(url: str, token: str, timeout: float) -> str:
    params = {
        "token": token,
        "url": url,
        "discussion": "false",
    }
    response = requests.get(DIFFBOT_API_URL, params=params, timeout=timeout)
    response.raise_for_status()

    payload = response.json()
    objects = payload.get("objects") or []
    if not objects:
        raise ValueError("Diffbot response has no 'objects' array")

    text = objects[0].get("text", "")
    if not text.strip():
        raise ValueError("Diffbot response object has empty 'text'")

    return text


def collect_corpus(urls: list[str], token: str, timeout: float, pause: float, keep_going: bool) -> str:
    chunks: list[str] = []

    for index, url in enumerate(urls, start=1):
        try:
            article_text = get_article_text(url, token=token, timeout=timeout)
            chunks.append(article_text.strip())
            print(f"[{index}/{len(urls)}] ok: {url}")
        except Exception as error:
            print(f"[{index}/{len(urls)}] failed: {url} ({error})", file=sys.stderr)
            if not keep_going:
                raise

        if pause > 0:
            time.sleep(pause)

    return "\n\n".join(chunks).strip() + "\n"


def main() -> int:
    args = parse_args()

    if not args.token:
        print(
            "Missing token: pass --token or set DIFFBOT_TOKEN in environment.",
            file=sys.stderr,
        )
        return 2

    urls_path = Path(args.urls_file)
    output_path = Path(args.output)

    try:
        urls = read_urls(urls_path)
    except Exception as error:
        print(error, file=sys.stderr)
        return 2

    if not urls:
        print(f"No URLs found in {urls_path}", file=sys.stderr)
        return 2

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        corpus_text = collect_corpus(
            urls=urls,
            token=args.token,
            timeout=args.timeout,
            pause=args.pause,
            keep_going=args.keep_going,
        )
    except Exception as error:
        print(f"Collection failed: {error}", file=sys.stderr)
        return 1

    output_path.write_text(corpus_text, encoding="utf-8")
    total_words = len(corpus_text.split())

    print(f"Saved corpus to {output_path}")
    print(f"URLs processed: {len(urls)}")
    print(f"Approx word count: {total_words}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
