# Scripts Documentation

This directory contains utility scripts for the pseudocode_algorithm project,
designed to download algorithm research papers from PubMed Central (PMC).

---

## Directory Structure

```
scripts/
├── download_all_literature.py          # Batch downloader for algorithm papers
├── pmc_literature_keywords.csv         # Algorithm research keywords
└── utils/
    ├── literature_downloader.py        # Standalone PMC article downloader
    ├── manage_text_field.py            # JSON text field management
    └── test_pmc_availability.py        # PMC availability checker
```

---

## Utility Scripts

### literature_downloader.py

**Purpose**

High-performance PubMed Central (PMC) downloader for algorithm research papers.
Searches PMC directly for full-text articles on algorithms, machine learning,
and computer science topics, with concurrent downloads, retry logic, and
comprehensive error handling.

**Key Features**

- **Concurrent Downloads**: Multi-threaded downloads (default: 5 workers) for faster retrieval
- **Robust Error Handling**: Automatic retry with exponential backoff for transient failures
- **Smart Detection**: Distinguishes between unavailable articles vs network/parsing errors
- **File Existence Check**: Skips already-downloaded files to support resume
- **Progress Tracking**: Real-time progress indicator with status breakdown
- **Comprehensive Statistics**: Detailed download report with success/failure categorization
- **Metadata Extraction**: Parses PMC XML to extract title, authors, journal, dates, DOI, abstract, keywords
- **Rate Limiting**: Adheres to NCBI guidelines (3 requests/second with API key)
- **Timestamp Tracking**: Records download date in JSON output

**Installation Requirements**

```bash
pip install requests
```

**Basic Usage** (from the project root)

```bash
# Download up to 50 JSON articles (concurrent, default)
python scripts/utils/literature_downloader.py "random forest algorithm" --max-results 50

# Sequential download for stability (slower but more reliable on poor connections)
python scripts/utils/literature_downloader.py "gradient boosting XGBoost" --sequential

# Verbose logging for debugging
python scripts/utils/literature_downloader.py "machine learning algorithms" --verbose --max-results 10

# Custom worker count for concurrent downloads
python scripts/utils/literature_downloader.py "decision trees" --workers 10 --max-results 100

# XML format with custom API key
python scripts/utils/literature_downloader.py "ensemble methods" --format xml --api-key YOUR_KEY
```

**Output Structure**

Articles are organized in keyword-specific subdirectories:

```
publications/
└── xgboost/                  # Keyword slug (filesystem-safe)
    ├── PMC12345678.json
    ├── PMC12345679.json
    └── ...
```

**JSON Output Schema** (preferred format)

```json
{
  "pmcid": "PMC12345678",
  "source": "PMC",
  "download_date": "2025-12-07T11:30:45.123456",
  "metadata": {
    "title": "Article Title",
    "journal": "Journal Name",
    "journal_title": "Full Journal Title",
    "journal_nlm_ta": "J Abbrev",
    "journal_iso_abbrev": "J. Abbrev.",
    "pmid": "12345678",
    "pmcid": "PMC12345678",
    "doi": "10.1234/example",
    "year": "2024",
    "month": "12",
    "day": "15",
    "pub_date": {
      "year": "2024",
      "month": "12",
      "day": "15"
    },
    "authors": ["Smith J", "Doe A", "Johnson B"],
    "abstract": "Full abstract text...",
    "keywords": ["algorithm", "machine learning", "xgboost"]
  },
  "xml": "<?xml version=\"1.0\"?>..."
}
```

**Note**: The `text` field (plain-text version with XML tags stripped) is **included by default** 
for VS Code search compatibility. Use `--exclude-text` to omit it and save ~30% storage, 
or use `scripts/utils/manage_text_field.py` to add/remove it from existing files.

**Download Statistics Output**

```
============================================================
Download Summary
============================================================
Keyword:           random forest algorithm
Total found:       150
Requested:         50
✓ Successful:      42
✗ Failed:          8
  - Unavailable:   5   (Not in PMC full-text collection)
  - Errors:        3   (Network/parsing errors)
○ Skipped:         0   (Already downloaded)
Duration:          45.2s
Output directory:  D:\...\publications\xgboost
============================================================
```

**Command-Line Options**

| Option | Description | Default |
|--------|-------------|---------|
| `keyword` | Search query (positional) | *required* |
| `--max-results` | Maximum articles to download | 100 |
| `--format` | Output format: json, xml, txt | json |
| `--exclude-text` | Exclude text field in JSON (~30% smaller) | *included* |
| `--api-key` | Override NCBI API key | *project key* |
| `--sequential` | Disable concurrent downloads | *concurrent* |
| `--workers` | Number of concurrent threads | 5 |
| `--verbose`, `-v` | Enable DEBUG logging | INFO |

**Exit Codes**

- `0`: At least one article successfully downloaded
- `1`: No results found for the keyword
- `2`: All download attempts failed

**Storage Optimization**

**By default**, the `text` field (XML with tags stripped) is **included** for VS Code search compatibility.
XML format is not search-friendly due to tag pollution, making the text field essential for finding papers.

```bash
# Download with text field (default, better for search)
python scripts/utils/literature_downloader.py "xgboost algorithm"

# Download without text field to save space (~30% smaller, reduced search)
python scripts/utils/literature_downloader.py "xgboost algorithm" --exclude-text

# Manage text field in existing files
python scripts/utils/manage_text_field.py check publications/xgboost
python scripts/utils/manage_text_field.py remove publications/xgboost  # save space
python scripts/utils/manage_text_field.py add publications/xgboost     # regenerate text

# Process all subdirectories recursively
python scripts/utils/manage_text_field.py remove publications --recursive
```

**Storage Impact** (5 articles):
- With text (default): 1290 KB - ✅ **VS Code search finds "algorithm", "pseudocode", etc.**
- Without text: 912 KB - ⚠️ **Search only finds XML tags, not scientific content**
- **Trade-off: 378 KB (29%) for searchability**

**Performance Tips**

1. **For large batches (>100 articles)**: Use concurrent mode (default) with `--workers 8-10`
2. **For unstable networks**: Use `--sequential` mode to avoid connection pool issues
3. **To resume interrupted downloads**: Re-run the same command; already-downloaded files are automatically skipped
4. **For debugging**: Add `--verbose` to see detailed per-article status
5. **For archival storage only**: Use `--exclude-text` to save 30% space (sacrifice search)

**Handling "Not Available" Articles**

Some PMC IDs returned by search may not have full-text available due to:
- Embargoed content (publisher restrictions)
- Withdrawn articles
- Metadata-only records (abstract but no full text)

The script distinguishes these as "unavailable" (not a failure) vs genuine errors.

---

**Last Updated**: December 2025  
**Maintainer**: Pseudocode Algorithm Project
