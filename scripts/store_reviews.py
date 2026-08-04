"""
Phase 3 script: store all raw reviews into one master dataset.

Run:
  .\\.venv\\Scripts\\python.exe scripts\\store_reviews.py

What it does:
1. Reads every file in data/raw/
2. Merges them
3. Removes duplicate reviews
4. Saves:
   - data/store/reviews_master.json
   - data/store/reviews_master.csv
   - data/store/store_summary.json
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from src.storage.local_store import load_all_raw_reviews, list_raw_files, save_master_store
from src.storage.merge_raw import merge_reviews
from src.storage.supabase_store import is_supabase_configured, push_reviews_to_supabase


def main() -> None:
    print("=" * 60)
    print("Phase 3: Store reviews")
    print("=" * 60)

    raw_files = list_raw_files()
    print(f"\nRaw batch files found: {len(raw_files)}")
    for path in raw_files[:8]:
        print(f"  - {path.name}")
    if len(raw_files) > 8:
        print(f"  ... and {len(raw_files) - 8} more")

    print("\nLoading all raw reviews...")
    raw_reviews = load_all_raw_reviews()
    print(f"  Loaded rows: {len(raw_reviews)}")

    print("\nMerging + removing duplicates...")
    master, summary = merge_reviews(raw_reviews)
    print(f"  Unique rows kept: {summary['unique_rows']}")
    print(f"  Duplicates removed: {summary['duplicates_removed']}")
    print("  By source:")
    for source, count in sorted(summary["by_source"].items(), key=lambda x: -x[1]):
        print(f"    {source}: {count}")

    print("\nSaving master store (JSON + CSV)...")
    paths = save_master_store(master, summary)
    print(f"  JSON : {paths['json']}")
    print(f"  CSV  : {paths['csv']}")
    print(f"  Summary: {paths['summary']}")

    print("\nOptional Supabase upload...")
    if is_supabase_configured():
        result = push_reviews_to_supabase(master)
        print(f"  {result}")
    else:
        print("  Skipped (no SUPABASE_URL / SUPABASE_KEY in .env).")
        print("  Local files are enough for the next phases.")

    print("\n" + "=" * 60)
    print(f"Phase 3 complete. Master dataset has {summary['unique_rows']} reviews.")
    print("=" * 60)


if __name__ == "__main__":
    main()
