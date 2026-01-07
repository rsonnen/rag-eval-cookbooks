# rag-eval-cookbooks

Evaluation corpus of public domain cookbooks for testing RAG systems.

## What This Is

This repository contains **evaluation data for RAG systems**:

- **corpus.yaml** - Evaluation scenarios (in each corpus directory)
- **metadata.json** - Book inventory with Internet Archive identifiers
- **Generated questions** - Validated Q/A pairs (where available)
- **corpus_specs/*.yaml** - Build configurations for creating new corpora

The actual PDF cookbooks are not included. Use `download_books.py` to fetch them from Internet Archive.

## Quick Start

```bash
cd scripts
uv sync
uv run python download_books.py french_classical --max-docs 5
```

## Available Corpora

| Corpus | Books | Questions | Description |
|--------|-------|-----------|-------------|
| `french_classical` | 150 | — | French haute cuisine 1800-1950 |
| `american_regional` | 150 | 424 | Regional American cooking traditions |
| `victorian_british` | 150 | — | Victorian era British cookery |
| `baking_pastry` | 100 | — | Baking and pastry specialization |
| `early_american` | 100 | — | Colonial and frontier American cooking |
| `preserving_canning` | 83 | — | Preserving and food storage |
| `italian_traditional` | 51 | — | Traditional Italian cookbooks 1800-1950 |

Some corpora have fewer items than target because the freely-available supply on Internet Archive was exhausted.

## Directory Structure

```
<corpus>/
    corpus.yaml         # Evaluation configuration
    metadata.json       # Book inventory
    books/              # Downloaded PDFs (gitignored)
    build_state.json    # Resume state (gitignored)
    rejected.json       # Rejected items (gitignored)

scripts/
    download_books.py   # Fetch books from Internet Archive
    build_cookbooks.py  # Build new corpora (discovery + curation)

corpus_specs/
    *.yaml              # Build configurations
```

## Metadata Format

```json
{
  "corpus": "american_regional",
  "source": "internet_archive",
  "search_strategy": {...},
  "curated_at": "2025-12-29T...",
  "total_books": 150,
  "books_evaluated": 398,
  "acceptance_rate": 0.38,
  "books": [
    {
      "identifier": "leprincipaldelac00plum",
      "title": "Le principal de la cuisine de Paris",
      "creator": ["Plumerey", "Carême, M. A."],
      "subjects": ["Cookery, French"],
      "date": "1843-01-01T00:00:00Z",
      "description": ["..."],
      "downloads": 2249,
      "file": "books/leprincipaldelac00plum.pdf",
      "source_pdf": "leprincipaldelac00plum.pdf"
    }
  ]
}
```

## Building New Corpora

The build script discovers books via Internet Archive API and curates using LLM evaluation with a two-stage process:

1. **Metadata pre-filter**: LLM check on title/description to skip obvious non-cookbooks
2. **Vision evaluation**: Render PDF pages to images, send to vision LLM to verify actual recipe content

```bash
cd scripts
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
| `--data-dir` | Output directory (default: parent of scripts) |
| `--limit N` | Override target count (for testing) |
| `--fresh` | Ignore existing progress, start from scratch |

### Resume Capability

The builder saves state after every 10 items. Re-run the same command to resume from where it left off. State includes:
- Current search position (subject/collection/identifier, page, offset)
- Accepted and rejected items
- Processed identifiers (for deduplication)

### Corpus Specs (Build Configuration)

Each corpus has a build config in `corpus_specs/` defining search parameters and LLM evaluation criteria.

```yaml
# corpus_specs/french_classical.yaml (abbreviated)
french_classical:
  description: |
    Classical French cuisine cookbooks 1800-1950

  source: archive

  search_strategy:
    subjects:
      - "Cookery, French"
      - "French cooking"
      # ... 19 more subject terms
    collections:
      - "food_and_cooking"
    collection_subject_filter:
      - "cookery"
      - "cooking"
      - "French"
    date_range: [1800, 1950]
    mediatype: texts

  target_count: 150
  evaluator_model: gpt-5-mini
  confidence_threshold: 0.7

  validation_prompt: |
    You are evaluating whether a document belongs in a corpus of
    HISTORICAL FRENCH COOKBOOKS (1800-1950).
    ...
```

### Evaluation Configuration

Each built corpus contains a `corpus.yaml` with evaluation scenarios:

```yaml
# french_classical/corpus.yaml
name: "French Classical Cookbooks (1800-1950)"

corpus_context: >
  150 French haute cuisine cookbooks spanning 1800-1950...

scenarios:
  culinary_history:
    name: "Culinary History Research"
    description: >
      Questions testing understanding of how culinary practices
      changed across different periods and chefs...

  recipe_retrieval:
    name: "Recipe and Technique Retrieval"
    description: >
      Questions targeting specific preparations, cooking methods,
      or ingredient ratios...

  rag_eval:
    name: "RAG System Evaluation"
    description: >
      Questions with specific, verifiable answers testing whether
      a retrieval system actually read the document...
```

### Search Strategy

The builder searches in three phases:

1. **Subjects**: Searches each subject term sequentially
2. **Collections**: Searches collections with subject filter to narrow results
3. **Identifiers**: Fetches specific Archive identifiers directly (for curated items)

Items in the `inlibrary` collection (lending library) are automatically excluded since they cannot be freely downloaded.

### Rate Limiting

The builder respects Internet Archive:
- 0.5 second delay between search API calls
- 10 second delay between PDF downloads
- Exponential backoff on errors (up to 5 retries)

### Environment

Create `.env` in the scripts directory:

```
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=http://your-litellm-proxy  # optional
```

## Licensing

**This repository**: MIT License

**Cookbooks**: Public domain (published before 1929)
