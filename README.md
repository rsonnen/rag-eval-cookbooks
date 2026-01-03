# rag-eval-cookbooks

Evaluation corpus of curated public domain cookbooks for testing RAG (Retrieval-Augmented Generation) systems.

## What This Is

This repository contains **evaluation data for RAG systems**:

- **corpus.yaml** - Evaluation configuration defining domain context and testing scenarios
- **Generated questions** - Validated Q/A pairs for evaluation (where available)
- **metadata.json** - Book inventory with Internet Archive identifiers
- **Build tools** - Scripts for curating new cookbook collections

The actual PDF cookbooks are not included - they are public domain works hosted by Internet Archive.

## Quick Start

Download books from a pre-curated corpus:

```bash
cd scripts
uv sync
uv run python download_books.py french_classical
```

## Purpose

Recipe collections represent a practical consumer use case. This corpus tests:

- **Retrieval**: Recipe lookup, ingredient-based search, technique synthesis
- **Document processing**: Scanned historical PDFs, period typography, recipe formatting
- **Query types**: "How do I make X?", "What recipes use ingredient Y?", "What's the technique for Z?"

## The Challenge

Internet Archive has thousands of items tagged with cooking-related subjects, but most are not actual cookbooks:
- Food history and memoirs
- Restaurant guides without recipes
- Agricultural manuals
- Novels that mention food
- Pharmaceutical/medical texts

Subject-based searches alone produce ~15% acceptance rates. This builder uses a two-stage LLM evaluation:

1. **Metadata pre-filter**: Quick LLM check on title/description to skip obvious non-cookbooks
2. **Vision evaluation**: Render PDF pages to images, send to vision LLM to verify actual recipe content

## Building New Corpora

```bash
cd scripts
uv sync

uv run python build_cookbooks.py \
    --config ../corpus_specs/french_classical.yaml \
    --corpus french_classical \
    --data-dir ..
```

### Options

| Option | Description |
|--------|-------------|
| `--config` | Path to corpus YAML configuration |
| `--corpus` | Corpus name (must match key in config) |
| `--data-dir` | Output directory (default: parent of scripts dir) |
| `--limit N` | Override target count (for testing) |
| `--fresh` | Ignore existing progress, start from scratch |

### Resume Capability

The builder saves state after every 10 items. Re-run the same command to resume from where it left off. State includes:
- Current search position (subject/collection/identifier, page, offset)
- Accepted and rejected items
- Processed identifiers (for deduplication)

## Corpus Specs

Each corpus has a YAML config in `corpus_specs/` defining search parameters and evaluation criteria.

```yaml
french_classical:
  description: |
    French haute cuisine cookbooks 1800-1950

  source: archive

  search_strategy:
    subjects:
      - "Cooking, French"
      - "Cookery, French"
    collections:
      - "food_and_cooking"
    collection_subject_filter:
      - "cooking"
      - "cuisine"
    date_range: [1800, 1950]
    mediatype: texts
    # Direct identifiers for curated items that don't appear in searches
    identifiers:
      - specific-archive-id-1
      - specific-archive-id-2

  target_count: 150
  evaluator_model: gpt-5-mini
  confidence_threshold: 0.7

  validation_prompt: |
    You are evaluating whether a document belongs in a corpus of
    HISTORICAL FRENCH COOKBOOKS (1800-1950).
    ...
```

### Search Strategy

The builder searches in three phases:

1. **Subjects**: Searches each subject term sequentially
2. **Collections**: Searches collections with subject filter to narrow results
3. **Identifiers**: Fetches specific Archive identifiers directly (for curated items)

Items in the `inlibrary` collection (lending library) are automatically excluded since they cannot be freely downloaded.

## Available Corpora

| Corpus | Documents | Description |
|--------|-----------|-------------|
| `french_classical` | 150 | French haute cuisine and classical techniques |
| `american_regional` | 150 | Regional American cooking traditions |
| `victorian_british` | 150 | Victorian era British cookery |
| `baking_pastry` | 100 | Baking and pastry specialization |
| `early_american` | 100 | Early American colonial and frontier cooking |
| `preserving_canning` | 83 | Preserving, canning, and food storage (exhausted) |
| `italian_traditional` | 51 | Traditional Italian cookbooks 1800-1950 |

Note: Some corpora have fewer items than target because the freely-available supply on Internet Archive was exhausted.

## Output Structure

```
<corpus>/
    corpus.yaml             # Evaluation configuration
    books/                  # Downloaded PDFs (gitignored)
        identifier.pdf
    build_state.json        # Resume state (gitignored)
    metadata.json           # Final corpus metadata
    rejected.json           # Rejected items with reasons (gitignored)

scripts/
    download_books.py       # Fetch books from Internet Archive
    build_cookbooks.py      # Build new corpora (discovery + curation)
```

### Metadata Format

```json
{
  "corpus": "french_classical",
  "source": "internet_archive",
  "search_strategy": {...},
  "curated_at": "2024-12-28T...",
  "total_books": 150,
  "books_evaluated": 523,
  "acceptance_rate": 0.287,
  "books": [
    {
      "identifier": "leavesfromourtu01rossgoog",
      "title": "Leaves from our Tuscan kitchen",
      "creator": "Ross, Janet",
      "subjects": ["Cookery, Italian"],
      "date": "1900-01-01T00:00:00Z",
      "file": "books/leavesfromourtu01rossgoog.pdf",
      "source_pdf": "leavesfromourtu01rossgoog.pdf"
    }
  ]
}
```

## Vision Evaluation

The builder extracts 4 sample pages from each PDF (skipping frontmatter) and sends them to a vision-capable LLM with a corpus-specific prompt. The LLM evaluates whether the visual content shows actual recipes with:

- Ingredient lists
- Cooking instructions
- Recipe formatting (titles, measurements, steps)

Low-confidence acceptances are rejected to maintain corpus quality.

## Rate Limiting

The builder respects Internet Archive:
- 0.5 second delay between search API calls
- 10 second delay between PDF downloads
- Exponential backoff on errors (up to 5 retries)

## Requirements

Create `.env` in the scripts directory:

```
OPENAI_BASE_URL=http://your-litellm-proxy  # optional
OPENAI_API_KEY=your-key
```

### Dependencies

- Python 3.11+
- `internetarchive` - Official IA Python client
- `PyMuPDF` (fitz) - PDF rendering
- `openai` - Vision API calls
- `pyyaml`, `tqdm`, `pydantic`

See `pyproject.toml` for full dependency list.

## Licensing

**This repository** (scripts, configurations): MIT License

**Cookbooks**: Public domain works from Internet Archive (published before 1929 or explicitly marked public domain).
