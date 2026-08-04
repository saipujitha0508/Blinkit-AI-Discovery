"""
Collect until we have about 3000 unique Blinkit reviews/posts.

Strategy (easiest + most reliable):
1. Free Google Play bulk scrape (multiple sorts/languages)
2. Apify Google Play large batch
3. Apple App Store refresh
4. Keep everything in data/raw/, then report unique count

Run:
  .\\.venv\\Scripts\\python.exe scripts\\collect_target_3000.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from src.collectors.app_store import collect_app_store_reviews
from src.collectors.apify_collectors import collect_apify_play_store, is_apify_configured
from src.collectors.play_store import collect_play_store_bulk
from src.storage.local_store import save_raw_batch

TARGET = 3000
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def _normalize_key(review: dict) -> str:
    """Build a stable unique key so free + Apify duplicates collapse."""
    meta = review.get("metadata") or {}
    raw_id = meta.get("raw_review_id")
    if raw_id:
        return f"play::{raw_id}"

    rid = str(review.get("id") or "")
    for prefix in ("apify_play_", "play_", "appstore_", "apify_reddit_", "reddit_"):
        if rid.startswith(prefix):
            return f"{prefix.rstrip('_')}::{rid[len(prefix):]}"
    text = (review.get("text") or "").strip().lower()[:180]
    return f"{review.get('source')}::{text}"


def count_unique_existing() -> tuple[int, set[str]]:
    keys: set[str] = set()
    for path in RAW_DIR.glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for review in payload.get("reviews", []):
            keys.add(_normalize_key(review))
    return len(keys), keys


def main() -> None:
    print("=" * 60)
    print(f"Collecting toward ~{TARGET} unique Blinkit records")
    print("=" * 60)

    existing_count, existing_keys = count_unique_existing()
    print(f"\nAlready on disk (unique): {existing_count}")
    needed = max(0, TARGET - existing_count)
    print(f"Still needed: {needed}")

    # 1) Free Play bulk
    print("\n[1/3] Free Google Play bulk scrape...")
    free_target = max(needed + 200, 1500)
    free_items = collect_play_store_bulk(target=free_target)
    if free_items:
        path = save_raw_batch(free_items, "google_play_bulk")
        print(f"  Saved {len(free_items)} -> {path.name}")

    # 2) Apify large batch
    print("\n[2/3] Apify Google Play large batch...")
    if is_apify_configured():
        # Request enough to cover remaining gap after free scrape
        current, _ = count_unique_existing()
        still = max(500, TARGET - current + 100)
        apify_count = min(2500, still)
        print(f"  Requesting {apify_count} reviews from Apify...")
        print("  Note: Apify may use paid credits beyond the free allowance.")
        try:
            apify_items = collect_apify_play_store(max_reviews=apify_count)
            if apify_items:
                # Ensure raw_review_id exists for dedupe
                for item in apify_items:
                    rid = str(item.get("id") or "")
                    if rid.startswith("apify_play_"):
                        item.setdefault("metadata", {})["raw_review_id"] = rid[len("apify_play_") :]
                path = save_raw_batch(apify_items, "google_play_apify")
                print(f"  Saved {len(apify_items)} -> {path.name}")
            else:
                print("  No Apify items returned.")
        except Exception as exc:  # noqa: BLE001
            print(f"  Apify error: {exc}")
    else:
        print("  Apify token missing — skipped.")

    # 3) App Store refresh
    print("\n[3/3] Apple App Store refresh...")
    try:
        app_items = collect_app_store_reviews()
        if app_items:
            path = save_raw_batch(app_items, "app_store")
            print(f"  Saved {len(app_items)} -> {path.name}")
    except Exception as exc:  # noqa: BLE001
        print(f"  App Store error: {exc}")

    final_count, _ = count_unique_existing()
    print("\n" + "=" * 60)
    print(f"UNIQUE TOTAL NOW: {final_count}")
    if final_count >= TARGET:
        print(f"Target reached (>= {TARGET}).")
    else:
        print(f"Below target by {TARGET - final_count}.")
        print("We can run again or increase Apify max_reviews.")
    print("=" * 60)


if __name__ == "__main__":
    main()
