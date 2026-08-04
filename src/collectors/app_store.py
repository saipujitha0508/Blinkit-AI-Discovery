"""
Collect live Apple App Store reviews for Blinkit (iOS).

How it works (plain English):
Apple publishes a public RSS feed of recent reviews.
We download that feed and convert each review into our shared format.

No Apple developer account is required.
Blinkit iOS app id: 960335206
"""

from __future__ import annotations

from typing import Any

import requests

from src.collectors.schema import make_review

BLINKIT_IOS_APP_ID = "960335206"
ITUNES_RSS_URL = (
    f"https://itunes.apple.com/in/rss/customerreviews/"
    f"id={BLINKIT_IOS_APP_ID}/sortBy=mostRecent/json"
)


def collect_app_store_reviews(country: str = "in") -> list[dict[str, Any]]:
    """
    Download recent App Store reviews from Apple's public RSS feed.

    Note: Apple usually returns up to ~50 most recent reviews per request.
    """
    url = (
        f"https://itunes.apple.com/{country}/rss/customerreviews/"
        f"id={BLINKIT_IOS_APP_ID}/sortBy=mostRecent/json"
    )
    headers = {
        "User-Agent": "BlinkitAIDiscoveryEngine/1.0 (PM certification education project)"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    payload = response.json()

    entries = payload.get("feed", {}).get("entry", [])
    results: list[dict[str, Any]] = []

    for entry in entries:
        # The first entry is sometimes app metadata (no rating) — skip those
        rating_node = entry.get("im:rating")
        content_node = entry.get("content")
        if not rating_node or not content_node:
            continue

        review_id = entry.get("id", {}).get("label", "")
        title = entry.get("title", {}).get("label", "")
        body = content_node.get("label", "")
        text = title if not body else f"{title}\n\n{body}"
        if not str(text).strip():
            continue

        author = None
        author_node = entry.get("author", {})
        if isinstance(author_node, dict):
            author = author_node.get("name", {}).get("label")

        updated = entry.get("updated", {}).get("label")
        link = None
        link_node = entry.get("link", {})
        if isinstance(link_node, dict):
            link = link_node.get("attributes", {}).get("href")

        try:
            rating = float(rating_node.get("label"))
        except (TypeError, ValueError):
            rating = None

        results.append(
            make_review(
                review_id=f"appstore_{review_id}",
                source="app_store",
                text=text,
                rating=rating,
                date=updated,
                author=author,
                url=link
                or f"https://apps.apple.com/in/app/id{BLINKIT_IOS_APP_ID}",
                language=None,
                metadata={
                    "app_id": BLINKIT_IOS_APP_ID,
                    "country": country,
                    "vote_sum": entry.get("im:voteSum", {}).get("label"),
                    "vote_count": entry.get("im:voteCount", {}).get("label"),
                },
            )
        )

    return results
