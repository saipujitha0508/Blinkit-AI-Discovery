"""
Optional Apify collectors (for later / larger scrapes).

Plain English:
Apify is a cloud scraping service. You create an account, get a token,
and ask an "Actor" (a ready-made scraper) to collect data for you.

In Phase 2 we use free live collectors first (Play Store + Reddit)
so you can learn without paying or creating an Apify account.

This file is ready for when you want Apify. It will only run if
APIFY_API_TOKEN is set in your .env file.
"""

from __future__ import annotations

import os
from typing import Any

from src.collectors.schema import make_review


def is_apify_configured() -> bool:
    """Return True if the user has added an Apify token."""
    return bool(os.getenv("APIFY_API_TOKEN"))


def collect_with_apify_play_store(
    app_id: str = "com.grofers.customerapp",
    max_reviews: int = 100,
    token: str | None = None,
) -> list[dict[str, Any]]:
    """
    Example Apify path for Play Store reviews.

    Requires:
      pip install apify-client
      APIFY_API_TOKEN in .env

    Actor used: compass/google-play-reviews-scraper
    (You can change the actor id later if Apify recommends another.)
    """
    token = token or os.getenv("APIFY_API_TOKEN")
    if not token:
        raise RuntimeError(
            "APIFY_API_TOKEN is missing. Copy .env.example to .env and add your token."
        )

    try:
        from apify_client import ApifyClient
    except ImportError as exc:
        raise RuntimeError(
            "apify-client is not installed. Run: pip install apify-client"
        ) from exc

    client = ApifyClient(token)
    run = client.actor("compass/google-play-reviews-scraper").call(
        run_input={
            "startUrls": [
                {"url": f"https://play.google.com/store/apps/details?id={app_id}"}
            ],
            "maxReviews": max_reviews,
            "reviewsSort": "newest",
            "language": "en",
            "country": "in",
        }
    )

    results: list[dict[str, Any]] = []
    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        return results

    for item in client.dataset(dataset_id).iterate_items():
        text = item.get("text") or item.get("content") or item.get("reviewText") or ""
        if not str(text).strip():
            continue
        review_id = str(item.get("id") or item.get("reviewId") or len(results))
        results.append(
            make_review(
                review_id=f"apify_play_{review_id}",
                source="google_play_apify",
                text=str(text),
                rating=item.get("score") or item.get("rating"),
                date=str(item.get("date") or item.get("at") or ""),
                author=item.get("userName") or item.get("author"),
                url=item.get("url"),
                language=item.get("language"),
                metadata={"provider": "apify", "raw_keys": list(item.keys())[:20]},
            )
        )

    return results
