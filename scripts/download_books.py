#!/usr/bin/env python3
"""Download books from a curated corpus.

Reads metadata.json and downloads all PDFs from Internet Archive.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from tqdm import tqdm


def download_corpus(
    corpus_dir: Path,
    delay: float = 1.0,
    max_docs: int | None = None,
) -> None:
    """Download books in a corpus from Internet Archive.

    Args:
        corpus_dir: Path to corpus directory containing metadata.json.
        delay: Seconds to wait between downloads.
        max_docs: Maximum number of books to download (None for all).
    """
    metadata_path = corpus_dir / "metadata.json"
    if not metadata_path.exists():
        print(f"Error: {metadata_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(metadata_path) as f:
        metadata: dict[str, Any] = json.load(f)

    books_dir = corpus_dir / "books"
    books_dir.mkdir(exist_ok=True)

    books: list[dict[str, Any]] = metadata.get("books", [])
    if max_docs is not None:
        books = books[:max_docs]

    print(f"Downloading {len(books)} books to {books_dir}")

    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        for book in tqdm(books, desc="Downloading", unit="book"):
            identifier: str = book["identifier"]
            source_pdf: str = book.get("source_pdf", f"{identifier}.pdf")
            pdf_url = f"https://archive.org/download/{identifier}/{source_pdf}"
            pdf_path = books_dir / f"{identifier}.pdf"

            if pdf_path.exists():
                continue

            try:
                response = client.get(pdf_url)
                response.raise_for_status()
                pdf_path.write_bytes(response.content)
            except httpx.HTTPError as e:
                tqdm.write(f"Error downloading {identifier}: {e}")

            time.sleep(delay)

    print("Done")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Download books from a curated corpus"
    )
    parser.add_argument("corpus", help="Corpus directory (e.g., french_classical)")
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--max-docs",
        type=int,
        default=None,
        help="Maximum number of books to download (default: all)",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    corpus_dir = repo_root / args.corpus

    if not corpus_dir.exists():
        print(f"Error: Corpus directory not found: {corpus_dir}", file=sys.stderr)
        sys.exit(1)

    download_corpus(corpus_dir, args.delay, args.max_docs)


if __name__ == "__main__":
    main()
