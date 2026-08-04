"""
Phase 2 script: collect live reviews and save them into data/raw/

How to run (from the project folder, with venv active):
  python scripts\\collect_reviews.py

What this does:
1. Fetches Google Play reviews for Blinkit
2. Fetches Apple App Store reviews for Blinkit
3. Tries Reddit discussions about Blinkit
4. Saves each successful source as JSON in data/raw/
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.collectors.app_store import collect_app_store_reviews
from src.collectors.play_store import collect_play_store_reviews
from src.collectors.reddit import collect_reddit_discussions
from src.storage.local_store import save_raw_batch


def _run_step(title: str, collector, save_label: str, **kwargs):
    print(f"\n{title}")
    try:
        items = collector(**kwargs)
        if not items:
            print("  No items returned (empty list).")
            return []
        path = save_raw_batch(items, save_label)
        print(f"  Saved {len(items)} items -> {path}")
        return items
    except Exception as exc:  # noqa: BLE001 - show friendly errors to beginners
        print("  ERROR while collecting.")
        print(f"  Reason: {exc}")
        return []


def main() -> None:
    print("=" * 60)
    print("Phase 2: Collecting live customer feedback")
    print("=" * 60)

    play = _run_step(
        "[1/3] Google Play Store reviews...",
        collect_play_store_reviews,
        "google_play",
        count=80,
    )

    appstore = _run_step(
        "[2/3] Apple App Store reviews...",
        collect_app_store_reviews,
        "app_store",
        country="in",
    )

    reddit = _run_step(
        "[3/3] Reddit discussions...",
        collect_reddit_discussions,
        "reddit",
        per_query_limit=15,
    )
    if not reddit:
        print("  Note: Reddit often blocks automated access on some networks.")
        print("  Play Store + App Store data is still enough to continue.")
        print("  Later we can collect Reddit via Apify if needed.")

    total = len(play) + len(appstore) + len(reddit)
    print("\n" + "=" * 60)
    print(f"Done. Total items collected: {total}")
    print(f"  Google Play : {len(play)}")
    print(f"  App Store   : {len(appstore)}")
    print(f"  Reddit      : {len(reddit)}")
    print("Files are in the data/raw/ folder.")
    print("=" * 60)

    if total == 0:
        print("\nNothing was collected. Read the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
