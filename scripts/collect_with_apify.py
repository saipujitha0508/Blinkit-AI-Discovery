"""
Collect MORE Blinkit reviews using Apify.

Before running:
1. Create a free Apify account: https://console.apify.com/sign-up
2. Copy your API token:
   https://console.apify.com/settings/integrations
3. Put it in the project .env file:
   APIFY_API_TOKEN=paste_your_token_here

Then run:
  .\\.venv\\Scripts\\python.exe scripts\\collect_with_apify.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from src.collectors.apify_collectors import (
    collect_apify_play_store,
    collect_apify_reddit,
    is_apify_configured,
)
from src.storage.local_store import save_raw_batch


def main() -> None:
    print("=" * 60)
    print("Collecting MORE reviews with Apify")
    print("=" * 60)

    if not is_apify_configured():
        print("\nApify token not found.")
        print("Do this first:")
        print("  1) Open .env.example")
        print("  2) Copy it to a new file named exactly: .env")
        print("  3) Replace your_apify_token_here with your real Apify token")
        print("  4) Save, then run this script again")
        print("\nGet a token here:")
        print("  https://console.apify.com/settings/integrations")
        sys.exit(1)

    play: list = []
    reddit: list = []

    print("\n[1/2] Google Play Store via Apify (up to 300 reviews)...")
    try:
        play = collect_apify_play_store(max_reviews=300)
        if play:
            path = save_raw_batch(play, "google_play_apify")
            print(f"  Saved {len(play)} reviews -> {path}")
        else:
            print("  No Play Store reviews returned.")
    except Exception as exc:  # noqa: BLE001
        print("  ERROR:")
        print(f"  {exc}")

    print("\n[2/2] Reddit via Apify (Blinkit-related posts)...")
    try:
        reddit = collect_apify_reddit(max_items=80)
        if reddit:
            path = save_raw_batch(reddit, "reddit_apify")
            print(f"  Saved {len(reddit)} posts -> {path}")
        else:
            print("  No Reddit posts returned (or actor returned unrelated items).")
    except Exception as exc:  # noqa: BLE001
        print("  ERROR:")
        print(f"  {exc}")
        print("  Tip: Play Store alone is still useful if Reddit actor fails.")

    total = len(play) + len(reddit)
    print("\n" + "=" * 60)
    print(f"Done. New Apify items: {total}")
    print(f"  Play Store (Apify): {len(play)}")
    print(f"  Reddit (Apify)    : {len(reddit)}")
    print("Check the data/raw/ folder.")
    print("=" * 60)

    if total == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
