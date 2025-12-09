#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Batch Literature Downloader for Algorithm Research Keywords

Reads keywords from pmc_literature_keywords.csv and downloads relevant
PMC articles for each keyword related to algorithms and computer science,
organizing them by priority level.
"""

import os
import sys
import time
import pandas as pd
import subprocess
from pathlib import Path
from datetime import datetime

# Add utils directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / "utils"))

def download_for_keyword(keyword, max_results, category, priority):
    """
    Download articles for a single keyword using literature_downloader.py
    
    Args:
        keyword: Search keyword
        max_results: Maximum number of articles to download
        category: Keyword category for organization
        priority: Priority level (Critical, High, Medium, Low)
    
    Returns:
        tuple: (success_count, total_attempted, error_message)
    """
    print(f"\n{'='*80}")
    print(f"Keyword: {keyword}")
    print(f"Category: {category} | Priority: {priority}")
    print(f"Max Results: {max_results}")
    print(f"{'='*80}")
    
    # Build command (downloader handles output directory automatically)
    downloader_script = script_dir / "utils" / "literature_downloader.py"
    cmd = [
        "python",
        str(downloader_script),
        keyword,
        "--max-results", str(max_results),
        "--format", "json"
    ]
    
    try:
        # Run downloader (do not capture output, let it stream to console)
        result = subprocess.run(
            cmd,
            capture_output=False,
            timeout=600  # 10 minute timeout per keyword
        )
        
        # Parse output is unreliable; rely on file count instead
        # Check how many files were actually downloaded
        keyword_slug = keyword.lower().replace(' ', '_').replace('-', '_')
        keyword_slug = ''.join(c for c in keyword_slug if c.isalnum() or c == '_')
        keyword_dir = Path(__file__).parent.parent / "publications" / keyword_slug
        
        if keyword_dir.exists():
            pmc_files = list(keyword_dir.glob("PMC*.json"))
            success_count = len(pmc_files)
        else:
            success_count = 0
        
        if result.returncode == 0:
            print(f"[OK] Success: {success_count} articles in {keyword_slug}/")
            return (success_count, success_count, None)
        elif result.returncode == 1:
            print(f"[WARN] No results found for this keyword")
            return (0, 0, "No results found")
        else:
            print(f"[FAIL] Download errors occurred (return code {result.returncode})")
            return (success_count, success_count, f"Errors during download (code {result.returncode})")
            
    except subprocess.TimeoutExpired:
        print(f"[FAIL] Timeout: Keyword took longer than 10 minutes")
        return (0, 0, "Timeout after 10 minutes")
    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
        return (0, 0, str(e))


def main():
    """Main execution function"""
    
    # Paths
    project_root = Path(__file__).parent.parent
    keywords_file = project_root / "scripts" / "pmc_literature_keywords.csv"
    output_base = project_root / "publications" / "algorithm_systematic_review"
    
    # Create output directory
    output_base.mkdir(parents=True, exist_ok=True)
    
    # Load keywords
    print(f"\n{'='*80}")
    print(f"ALGORITHM LITERATURE BATCH DOWNLOADER")
    print(f"{'='*80}")
    print(f"Keywords file: {keywords_file}")
    print(f"Output directory: {output_base}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not keywords_file.exists():
        print(f"\n[ERROR] Keywords file not found: {keywords_file}")
        sys.exit(1)
    
    df = pd.read_csv(keywords_file)
    print(f"\nLoaded {len(df)} keywords")
    
    # Priority order
    priority_order = {'Critical': 1, 'High': 2, 'Medium': 3, 'Low': 4}
    df['priority_rank'] = df['Priority'].map(priority_order)
    df = df.sort_values('priority_rank')
    
    # Summary statistics
    print(f"\nKeyword Distribution:")
    print(df['Priority'].value_counts().sort_index())
    print(f"\nCategory Distribution:")
    print(df['Category'].value_counts())
    
    # Ask for confirmation
    print(f"\n{'='*80}")
    total_expected = df['Expected_Articles'].apply(lambda x: int(x.split('-')[1]) if '-' in str(x) else 50).sum()
    print(f"WARNING: This will attempt to download ~{total_expected} articles")
    print(f"Estimated time: {len(df) * 2} - {len(df) * 5} minutes")
    print(f"{'='*80}")
    
    response = input("\nProceed with batch download? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Download cancelled.")
        sys.exit(0)
    
    # Download loop
    results = []
    start_time = time.time()
    
    for idx, row in df.iterrows():
        keyword = row['Keyword']
        category = row['Category']
        priority = row['Priority']
        
        # Parse expected articles (use upper bound)
        expected_str = str(row['Expected_Articles'])
        if '-' in expected_str:
            max_results = int(expected_str.split('-')[1])
        else:
            max_results = 50
        
        # Limit max results to reasonable number
        max_results = min(max_results, 100)
        
        # Download
        success, total, error = download_for_keyword(
            keyword, max_results, category, priority
        )
        
        # Record result
        results.append({
            'keyword': keyword,
            'category': category,
            'priority': priority,
            'success_count': success,
            'attempted': total,
            'error': error,
            'timestamp': datetime.now()
        })
        
        # Brief pause between requests (be nice to NCBI servers)
        time.sleep(2)
    
    # Save results
    results_df = pd.DataFrame(results)
    results_file = output_base / f"download_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    results_df.to_csv(results_file, index=False)
    
    # Summary report
    elapsed = time.time() - start_time
    total_success = results_df['success_count'].sum()
    total_attempted = results_df['attempted'].sum()
    failed_keywords = results_df[results_df['error'].notna()]
    
    print(f"\n{'='*80}")
    print(f"DOWNLOAD COMPLETE")
    print(f"{'='*80}")
    print(f"Total time: {elapsed/60:.1f} minutes")
    print(f"Keywords processed: {len(results_df)}")
    print(f"Articles downloaded: {total_success}")
    print(f"Articles found: {total_attempted}")
    print(f"Success rate: {(total_success/total_attempted*100 if total_attempted > 0 else 0):.1f}%")
    print(f"\nFailed keywords: {len(failed_keywords)}")
    if len(failed_keywords) > 0:
        print("\nFailed keyword list:")
        for _, row in failed_keywords.iterrows():
            print(f"  - {row['keyword']}: {row['error']}")
    
    print(f"\nResults saved to: {results_file}")
    print(f"\nPublications organized in: {output_base}")
    print(f"  Structure: Priority/Category/Keyword/PMC*.json")
    
    # Priority-level summary
    print(f"\n{'='*80}")
    print("DOWNLOADS BY PRIORITY LEVEL:")
    print(f"{'='*80}")
    priority_summary = results_df.groupby('priority').agg({
        'success_count': 'sum',
        'attempted': 'sum',
        'keyword': 'count'
    }).rename(columns={'keyword': 'num_keywords'})
    print(priority_summary)
    
    print(f"\n{'='*80}")
    print("TOP 10 MOST SUCCESSFUL KEYWORDS:")
    print(f"{'='*80}")
    top_keywords = results_df.nlargest(10, 'success_count')[['keyword', 'priority', 'success_count']]
    for _, row in top_keywords.iterrows():
        print(f"  [{row['priority']:8s}] {row['keyword'][:60]:60s} ({row['success_count']} articles)")


if __name__ == "__main__":
    main()
