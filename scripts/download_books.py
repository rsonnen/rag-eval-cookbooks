#!/usr/bin/env python3
"""Download books from a curated corpus.

Reads metadata.json and downloads all PDFs from Internet Archive.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import httpx


def download_corpus(corpus_dir: Path, delay: float = 1.0) -> None:
    """Download all books in a corpus."""
    metadata_path = corpus_dir / "metadata.json"
    if not metadata_path.exists():
        print(f"Error: {metadata_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(metadata_path) as f:
        metadata = json.load(f)

    books_dir = corpus_dir / "books"
    books_dir.mkdir(exist_ok=True)

    books = metadata.get("books", [])
    print(f"Downloading {len(books)} books to {books_dir}")

    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        for i, book in enumerate(books, 1):
            identifier = book["identifier"]
            source_pdf = book.get("source_pdf", f"{identifier}.pdf")
            pdf_url = f"https://archive.org/download/{identifier}/{source_pdf}"
            pdf_path = books_dir / f"{identifier}.pdf"

            if pdf_path.exists():
                print(f"[{i}/{len(books)}] {identifier} - already exists")
                continue

            print(f"[{i}/{len(books)}] {identifier} - downloading...")
            try:
                response = client.get(pdf_url)
                response.raise_for_status()
                pdf_path.write_bytes(response.content)
            except httpx.HTTPError as e:
                print(f"  Error: {e}", file=sys.stderr)

            time.sleep(delay)

    print("Done")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download books from a curated corpus")
    parser.add_argument("corpus", help="Corpus directory (e.g., french_classical)")
    parser.add_argument(
        "--delay", type=float, default=1.0, help="Delay between requests (seconds)"
    )
    args = parser.parse_args()

    # Find corpus directory relative to repo root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    corpus_dir = repo_root / args.corpus

    if not corpus_dir.exists():
        print(f"Error: Corpus directory not found: {corpus_dir}", file=sys.stderr)
        sys.exit(1)

    download_corpus(corpus_dir, args.delay)


if __name__ == "__main__":
    main()
