"""Standalone PMC literature downloader for the pseudocode_algorithm project.

This script queries NCBI's PMC database using E-utilities, retrieves full-text
articles for a given search keyword, and saves them into this project's
``publications`` directory (under the pseudocode_algorithm project root).

Usage (from the project root):

    python scripts/utils/literature_downloader.py "random forest algorithm" --max-results 50 --format json

By default it uses the project NCBI API key but you can override it with
the ``--api-key`` argument. The preferred output format for this project is
JSON, which stores both the raw PMC XML and a simple plain-text version.
"""

import logging
import json
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime

import requests
import xml.etree.ElementTree as ET


# ---------------------------------------------------------------------------
# Project paths and configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PUBLICATIONS_DIR = PROJECT_ROOT / "publications"
PUBLICATIONS_DIR.mkdir(parents=True, exist_ok=True)

# Load NCBI API key from archive folder (can be overridden via --api-key)
API_KEY_FILE = PROJECT_ROOT / "archive" / "ncbi_api_key.txt"
try:
    NCBI_API_KEY = API_KEY_FILE.read_text().strip()
except FileNotFoundError:
    NCBI_API_KEY = ""  # Will require --api-key argument if file doesn't exist
    logger.warning(f"API key file not found: {API_KEY_FILE}. Use --api-key argument.")

# NCBI E-utilities endpoints
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Rate limiting and retry configuration
DEFAULT_RATE_LIMIT = 0.34  # seconds between requests (NCBI guideline: 3 req/sec with API key)
MAX_RETRIES = 3
RETRY_DELAY = 2.0  # seconds
REQUEST_TIMEOUT = 60  # seconds
MAX_WORKERS = 5  # concurrent download threads

logger = logging.getLogger(__name__)


@dataclass
class DownloadStats:
    """Statistics for a download session."""
    keyword: str
    total_found: int
    requested: int
    successful: int
    failed: int
    skipped: int
    unavailable: int
    errors: int
    duration_seconds: float
    output_dir: Path

    def __str__(self) -> str:
        return (
            f"\n{'='*60}\n"
            f"Download Summary\n"
            f"{'='*60}\n"
            f"Keyword:           {self.keyword}\n"
            f"Total found:       {self.total_found}\n"
            f"Requested:         {self.requested}\n"
            f"[OK] Successful:   {self.successful}\n"
            f"[FAIL] Failed:     {self.failed}\n"
            f"  - Unavailable:   {self.unavailable}\n"
            f"  - Errors:        {self.errors}\n"
            f"[SKIP] Skipped:    {self.skipped}\n"
            f"Duration:          {self.duration_seconds:.1f}s\n"
            f"Output directory:  {self.output_dir}\n"
            f"{'='*60}"
        )

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.requested == 0:
            return 0.0
        return (self.successful / self.requested) * 100


def esearch_pmc(term: str, max_results: int, api_key: str, retries: int = MAX_RETRIES) -> Tuple[List[str], int]:
    """Search PMC directly for articles with full-text available.
    
    Strategy: Search db=pmc directly to get PMC IDs that have downloadable full-text.
    This is more effective for interdisciplinary topics (e.g., computer science + medicine).
    
    Args:
        term: Search query string
        max_results: Maximum results to retrieve
        api_key: NCBI API key
        retries: Number of retry attempts on failure
    
    Returns:
        Tuple of (pmcid_list, total_count) where pmcid_list contains PMCIDs as strings
    """
    # Search PMC directly for articles with full-text
    search_params = {
        "db": "pmc",
        "term": term,
        "retmax": max_results,
        "retmode": "json",
        "api_key": api_key,
    }

    search_url = f"{EUTILS_BASE}/esearch.fcgi"
    logger.info("Searching PMC: %s (max %d results)", term, max_results)
    
    pmcids = []
    total_count = 0
    
    for attempt in range(retries):
        try:
            resp = requests.get(search_url, params=search_params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            
            data = resp.json()
            result = data.get("esearchresult", {})
            pmcids = result.get("idlist", [])
            total_count = int(result.get("count", len(pmcids)))
            
            logger.info("Found %d PMC IDs (total available: %d)", len(pmcids), total_count)
            return pmcids, total_count
            
        except (requests.RequestException, ValueError, KeyError) as e:
            logger.warning("Search attempt %d/%d failed: %s", attempt + 1, retries, e)
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                logger.error("All search attempts failed for: %s", term)
                return [], 0
    
    return [], 0


def strip_xml_tags(xml_text: str) -> str:
    """Very simple XML/HTML tag stripper for plain-text export."""

    # Remove tags
    text = re.sub(r"<[^>]+>", " ", xml_text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_metadata_from_pmc_xml(xml_text: str) -> Dict[str, Any]:
    """Extract basic metadata (title, journal, authors, IDs, dates) from PMC XML.

    This is intentionally conservative and resilient; if parsing fails, the
    function returns an empty dictionary and the caller can still use the raw
    XML and plain text representations.
    """

    metadata: Dict[str, Any] = {}

    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return metadata

    # Locate core elements
    article = root.find("article") if root.tag != "article" else root
    if article is None:
        return metadata

    front = article.find("front")
    if front is None:
        return metadata

    journal_meta = front.find("journal-meta")
    article_meta = front.find("article-meta")

    # Journal information
    journal_title = None
    journal_nlm_ta = None
    journal_iso_abbrev = None

    if journal_meta is not None:
        jt_group = journal_meta.find("journal-title-group")
        if jt_group is not None:
            jt = jt_group.find("journal-title")
            if jt is not None:
                journal_title = "".join(jt.itertext()).strip()

        for jid in journal_meta.findall("journal-id"):
            jid_type = jid.get("journal-id-type", "")
            value = (jid.text or "").strip()
            if jid_type == "nlm-ta":
                journal_nlm_ta = value
            elif jid_type == "iso-abbrev":
                journal_iso_abbrev = value

    # Store detailed journal fields and a generic alias used by other tooling
    if journal_title:
        metadata["journal_title"] = journal_title
    if journal_nlm_ta:
        metadata["journal_nlm_ta"] = journal_nlm_ta
    if journal_iso_abbrev:
        metadata["journal_iso_abbrev"] = journal_iso_abbrev

    # Provide a generic "journal" key for compatibility with external tools
    if journal_title:
        metadata["journal"] = journal_title
    elif journal_iso_abbrev:
        metadata["journal"] = journal_iso_abbrev
    elif journal_nlm_ta:
        metadata["journal"] = journal_nlm_ta

    if article_meta is None:
        return metadata

    # Article identifiers
    for aid in article_meta.findall("article-id"):
        id_type = aid.get("pub-id-type", "")
        value = (aid.text or "").strip()
        if id_type == "pmid":
            metadata["pmid"] = value
        elif id_type == "pmcid":
            metadata["pmcid"] = value
        elif id_type == "doi":
            metadata["doi"] = value

    # Title
    title_group = article_meta.find("title-group")
    if title_group is not None:
        at = title_group.find("article-title")
        if at is not None:
            metadata["title"] = "".join(at.itertext()).strip()

    # Publication dates
    # Prefer epub date, fall back to collection year
    pub_date = article_meta.find("pub-date[@pub-type='epub']")
    pub_year = None
    pub_month = None
    pub_day = None
    if pub_date is not None:
        year_el = pub_date.find("year")
        month_el = pub_date.find("month")
        day_el = pub_date.find("day")
        if year_el is not None:
            pub_year = (year_el.text or "").strip()
        if month_el is not None:
            pub_month = (month_el.text or "").strip()
        if day_el is not None:
            pub_day = (day_el.text or "").strip()
    else:
        coll_date = article_meta.find("pub-date[@pub-type='collection']")
        if coll_date is not None:
            year_el = coll_date.find("year")
            if year_el is not None:
                pub_year = (year_el.text or "").strip()

    # Store both flat year/month/day (for this project) and a nested
    # pub_date.year structure compatible with external utilities
    if pub_year is not None:
        metadata["year"] = pub_year
    if pub_month is not None:
        metadata["month"] = pub_month
    if pub_day is not None:
        metadata["day"] = pub_day

    if pub_year is not None:
        metadata["pub_date"] = {"year": pub_year}
        if pub_month is not None:
            metadata["pub_date"]["month"] = pub_month
        if pub_day is not None:
            metadata["pub_date"]["day"] = pub_day

    # Authors (simple list of display names)
    authors: List[str] = []
    for contrib in article_meta.findall("contrib-group/contrib"):
        if contrib.get("contrib-type") != "author":
            continue
        name_el = contrib.find("name")
        if name_el is None:
            continue
        surname = (name_el.findtext("surname") or "").strip()
        given = (name_el.findtext("given-names") or "").strip()
        initials = (name_el.get("initials") or "").strip()
        if given:
            full = f"{surname} {given}".strip()
        elif initials:
            full = f"{surname} {initials}".strip()
        else:
            full = surname
        if full:
            authors.append(full)
    if authors:
        metadata["authors"] = authors

    # Abstract (concatenate all abstract sections)
    abstract_el = article_meta.find("abstract")
    if abstract_el is not None:
        metadata["abstract"] = " ".join(list(abstract_el.itertext())).strip()

    # Keywords / MeSH (if present)
    keywords: List[str] = []
    for kwd in article_meta.findall("kwd-group/kwd"):
        text = "".join(kwd.itertext()).strip()
        if text:
            keywords.append(text)
    if keywords:
        metadata["keywords"] = keywords

    return metadata


def efetch_pmc(pmcid: str, out_dir: Path, fmt: str, api_key: str, retries: int = MAX_RETRIES, include_text: bool = True) -> Tuple[bool, str]:
    """Fetch a single PMC article and save it in the requested format.

    Args:
        pmcid: Numeric PMC database ID (as returned by esearch on db=pmc).
               Do NOT include 'PMC' prefix - use raw ID like '12345678'.
        out_dir: Base directory where files are written.
        fmt: 'xml', 'txt', or 'json'.
        api_key: NCBI API key.
        retries: Number of retry attempts on failure.
        include_text: For JSON format, whether to include the 'text' field
                     (stripped XML). Default True for VS Code search compatibility.

    Returns:
        Tuple of (success: bool, status: str) where status is one of:
        'success', 'unavailable', 'error', 'exists'
    """
    # Use raw numeric ID for efetch (db=pmc expects internal IDs, not PMCIDs)
    pmcid_numeric = str(pmcid).replace("PMC", "") if str(pmcid).startswith("PMC") else str(pmcid)
    
    # Format with PMC prefix for filenames and display only
    pmcid_display = f"PMC{pmcid_numeric}" if not pmcid_numeric.startswith("PMC") else pmcid_numeric

    # Check if file already exists
    out_dir.mkdir(parents=True, exist_ok=True)
    extension = {"xml": ".xml", "json": ".json", "txt": ".txt"}[fmt]
    out_path = out_dir / f"{pmcid_display}{extension}"
    
    if out_path.exists():
        logger.debug("%s already exists, skipping", out_path.name)
        return True, "exists"

    params = {
        "db": "pmc",
        "id": pmcid_numeric,  # Use raw numeric ID for efetch
        "rettype": "full",
        "retmode": "xml",
        "api_key": api_key,
    }

    url = f"{EUTILS_BASE}/efetch.fcgi"
    
    for attempt in range(retries):
        try:
            logger.debug("Downloading %s (attempt %d/%d)", pmcid_display, attempt + 1, retries)
            resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)

            if resp.status_code != 200:
                logger.warning("Failed to fetch %s (status %s)", pmcid_display, resp.status_code)
                if attempt < retries - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return False, "error"

            # Detect error responses where the requested PMCID is not available
            try:
                root = ET.fromstring(resp.text)
                # When a PMCID is unavailable, PMC returns <pmc-articleset><error ...>
                if root.tag == "pmc-articleset":
                    error_el = root.find("error")
                    if error_el is not None:
                        logger.info(
                            "%s not available in PMC: %s",
                            pmcid_display,
                            (error_el.text or "").strip(),
                        )
                        return False, "unavailable"
            except ET.ParseError:
                # If parsing fails, the XML might be malformed
                logger.warning("%s returned malformed XML", pmcid_display)
                if attempt < retries - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return False, "error"

            # Save the article
            if fmt == "xml":
                out_path.write_text(resp.text, encoding="utf-8")
            elif fmt == "json":
                # Store raw XML and structured metadata
                metadata = extract_metadata_from_pmc_xml(resp.text)
                
                # Validate metadata has at least title or pmcid
                if not metadata.get("title") and not metadata.get("pmcid"):
                    logger.warning("%s: extracted metadata is empty or invalid", pmcid_display)
                
                payload = {
                    "pmcid": pmcid_display,
                    "source": "PMC",
                    "download_date": datetime.now().isoformat(),
                    "metadata": metadata,
                    "xml": resp.text,
                }
                
                # Optionally include plain-text version (saves ~30% storage if omitted)
                if include_text:
                    payload["text"] = strip_xml_tags(resp.text)
                
                out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            else:  # txt
                text = strip_xml_tags(resp.text)
                out_path.write_text(text, encoding="utf-8")

            logger.info("[OK] Saved %s", out_path.name)
            return True, "success"
            
        except requests.RequestException as e:
            logger.warning("Download attempt %d/%d failed for %s: %s", attempt + 1, retries, pmcid_display, e)
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                return False, "error"
        except (IOError, OSError) as e:
            logger.error("Failed to write %s: %s", out_path, e)
            return False, "error"
    
    return False, "error"


def search_and_download(
    keyword: str, 
    max_results: int, 
    fmt: str, 
    api_key: str,
    use_concurrent: bool = True,
    max_workers: int = MAX_WORKERS,
    include_text: bool = True
) -> DownloadStats:
    """Search PMC for a keyword and download up to max_results articles.

    Articles are saved into a subdirectory of ``PUBLICATIONS_DIR`` named after
    the keyword (sanitized for filesystem safety), for example:

        publications/random_forest_algorithm/PMCXXXXXXXX.json
    
    Args:
        keyword: Search query string
        max_results: Maximum number of articles to download
        fmt: Output format ('json', 'xml', or 'txt')
        api_key: NCBI API key
        use_concurrent: Use concurrent downloads (default True)
        max_workers: Number of concurrent worker threads
        include_text: For JSON format, include plain-text field (default True for VS Code search)
    
    Returns:
        DownloadStats object with download statistics
    """
    start_time = time.time()
    
    try:
        pmcids, total_available = esearch_pmc(keyword, max_results=max_results, api_key=api_key)
    except Exception as e:
        logger.error("Search failed: %s", e)
        return DownloadStats(
            keyword=keyword,
            total_found=0,
            requested=0,
            successful=0,
            failed=0,
            skipped=0,
            unavailable=0,
            errors=0,
            duration_seconds=time.time() - start_time,
            output_dir=PUBLICATIONS_DIR
        )

    if not pmcids:
        logger.warning("No PMC articles found for: %s", keyword)
        print(f"No results found for '{keyword}'")
        return DownloadStats(
            keyword=keyword,
            total_found=total_available,
            requested=0,
            successful=0,
            failed=0,
            skipped=0,
            unavailable=0,
            errors=0,
            duration_seconds=time.time() - start_time,
            output_dir=PUBLICATIONS_DIR
        )

    # Create keyword-based output directory
    keyword_slug = re.sub(r"[^A-Za-z0-9._-]+", "_", keyword.strip()).strip("_") or "keyword"
    out_dir = PUBLICATIONS_DIR / keyword_slug

    print(
        f"\nFound {len(pmcids)} PMC IDs for '{keyword}' "
        f"(total available: {total_available})\n"
        f"Output directory: {out_dir}\n"
    )

    # Counters
    successful = 0
    unavailable = 0
    errors = 0
    skipped = 0

    if use_concurrent and len(pmcids) > 1:
        # Concurrent download with thread pool
        logger.info("Using concurrent downloads with %d workers", max_workers)
        
        def download_with_delay(pmcid: str) -> Tuple[str, bool, str]:
            """Download with rate limiting."""
            result = efetch_pmc(pmcid, out_dir, fmt=fmt, api_key=api_key, include_text=include_text)
            time.sleep(DEFAULT_RATE_LIMIT)  # Rate limit
            return pmcid, result[0], result[1]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(download_with_delay, pmcid): pmcid for pmcid in pmcids}
            
            for i, future in enumerate(as_completed(futures), start=1):
                try:
                    pmcid, success, status = future.result()
                    
                    if status == "success":
                        successful += 1
                    elif status == "exists":
                        skipped += 1
                    elif status == "unavailable":
                        unavailable += 1
                    else:  # error
                        errors += 1
                    
                    # Progress indicator
                    if i % 10 == 0 or i == len(pmcids):
                        print(f"Progress: {i}/{len(pmcids)} processed "
                              f"(OK:{successful} | FAIL:{unavailable + errors} | SKIP:{skipped})", 
                              end="\r")
                        
                except Exception as e:
                    pmcid = futures[future]
                    logger.error("Unexpected error downloading %s: %s", pmcid, e)
                    errors += 1
        
        print()  # New line after progress
    else:
        # Sequential download
        logger.info("Using sequential downloads")
        
        for i, pmcid in enumerate(pmcids, start=1):
            try:
                success, status = efetch_pmc(pmcid, out_dir, fmt=fmt, api_key=api_key, include_text=include_text)
                
                if status == "success":
                    successful += 1
                elif status == "exists":
                    skipped += 1
                elif status == "unavailable":
                    unavailable += 1
                else:  # error
                    errors += 1
                
                # Progress indicator
                if i % 5 == 0 or i == len(pmcids):
                    print(f"Progress: {i}/{len(pmcids)} processed", end="\r")
                
                # Rate limit
                time.sleep(DEFAULT_RATE_LIMIT)
                
            except Exception as e:
                logger.error("Unexpected error downloading %s: %s", pmcid, e)
                errors += 1
        
        print()  # New line after progress

    duration = time.time() - start_time
    stats = DownloadStats(
        keyword=keyword,
        total_found=total_available,
        requested=len(pmcids),
        successful=successful,
        failed=unavailable + errors,
        skipped=skipped,
        unavailable=unavailable,
        errors=errors,
        duration_seconds=duration,
        output_dir=out_dir
    )
    
    print(stats)
    
    if successful > 0:
        logger.info("Successfully downloaded %d articles to %s", successful, out_dir)
    if unavailable > 0:
        logger.warning("%d articles were not available in PMC full-text", unavailable)
    if errors > 0:
        logger.error("%d articles failed due to errors", errors)
    
    return stats


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Download PMC full-text articles for a given keyword "
            "into this project's publications directory."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download top 50 results as JSON (default, concurrent)
  python scripts/utils/literature_downloader.py "random forest algorithm" --max-results 50
  
  # Sequential download with XML format
  python scripts/utils/literature_downloader.py "gradient boosting" --format xml --sequential
  
  # Verbose logging for debugging
  python scripts/utils/literature_downloader.py "machine learning" --verbose
"""
    )
    parser.add_argument(
        "keyword", 
        help="Search keyword for PMC (e.g. 'random forest algorithm')"
    )
    parser.add_argument(
        "--max-results", 
        type=int, 
        default=100, 
        help="Maximum number of articles to download (default: 100)"
    )
    parser.add_argument(
        "--format", 
        choices=["json", "xml", "txt"], 
        default="json", 
        help="Output format for each article (default: json)"
    )
    parser.add_argument(
        "--api-key", 
        help="Override NCBI API key (uses project default if not specified)"
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Use sequential downloads instead of concurrent (slower but more stable)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=MAX_WORKERS,
        help=f"Number of concurrent worker threads (default: {MAX_WORKERS})"
    )
    parser.add_argument(
        "--verbose", 
        "-v",
        action="store_true",
        help="Enable verbose (DEBUG) logging"
    )
    parser.add_argument(
        "--exclude-text",
        action="store_true",
        help="Exclude plain-text field in JSON output to save ~30% storage (reduces search effectiveness)"
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, 
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    api_key = args.api_key or NCBI_API_KEY
    
    # Run download
    stats = search_and_download(
        keyword=args.keyword, 
        max_results=args.max_results, 
        fmt=args.format, 
        api_key=api_key,
        use_concurrent=not args.sequential,
        max_workers=args.workers,
        include_text=not args.exclude_text
    )
    
    # Exit with appropriate code
    if stats.successful > 0:
        exit(0)  # New downloads succeeded
    elif stats.skipped > 0 and stats.errors == 0:
        exit(0)  # All files already exist (not an error)
    elif stats.requested == 0:
        exit(1)  # No results found
    else:
        exit(2)  # All downloads failed with errors


if __name__ == "__main__":
    main()
