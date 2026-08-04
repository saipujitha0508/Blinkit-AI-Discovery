"""
Collect live Reddit discussions about Blinkit / quick commerce.

How it works (plain English):
1. We ask Reddit's public search for posts matching our keywords.
2. We read the post title + text.
3. We convert each post into our shared review format.

No Reddit account or API key is required for this light search.
Please be polite: we send a clear User-Agent and do not hammer Reddit.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import requests

from src.collectors.schema import make_review

# Who we are when talking to Reddit (required by Reddit etiquette)
USER_AGENT = "BlinkitAIDiscoveryEngine/1.0 (PM certification education project)"

# Searches that help us learn about category discovery / shopping habits
DEFAULT_QUERIES = [
    "blinkit",
    "blinkit groceries",
    "blinkit review",
    "blinkit vs zepto",
    "quick commerce india",
]


def _reddit_search(query: str, limit: int = 25) -> list[dict[str, Any]]:
    """Call Reddit public search JSON for one query."""
    url = "https://www.reddit.com/search.json"
    params = {
        "q": query,
        "sort": "new",
        "limit": min(limit, 100),
        "t": "year",
    }
    headers = {"User-Agent": USER_AGENT}

    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    payload = response.json()

    children = payload.get("data", {}).get("children", [])
    return [child.get("data", {}) for child in children]


def collect_reddit_discussions(
    queries: list[str] | None = None,
    per_query_limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Download Reddit posts for several Blinkit-related searches.

    We de-duplicate by post id so the same post is not saved twice
    if it matches more than one query.
    """
    queries = queries or DEFAULT_QUERIES
    seen_ids: set[str] = set()
    results: list[dict[str, Any]] = []

    for query in queries:
        posts = _reddit_search(query, limit=per_query_limit)
        # Small pause so we do not request too quickly
        time.sleep(1)

        for post in posts:
            post_id = str(post.get("id") or "")
            if not post_id or post_id in seen_ids:
                continue
            seen_ids.add(post_id)

            title = (post.get("title") or "").strip()
            body = (post.get("selftext") or "").strip()
            text = title if not body else f"{title}\n\n{body}"
            if not text.strip():
                continue

            created_utc = post.get("created_utc")
            date_str = None
            if created_utc:
                date_str = datetime.fromtimestamp(created_utc, tz=timezone.utc).isoformat()

            permalink = post.get("permalink") or ""
            url = f"https://www.reddit.com{permalink}" if permalink else post.get("url")

            results.append(
                make_review(
                    review_id=f"reddit_{post_id}",
                    source="reddit",
                    text=text,
                    rating=None,
                    date=date_str,
                    author=post.get("author"),
                    url=url,
                    language=None,
                    metadata={
                        "subreddit": post.get("subreddit"),
                        "score": post.get("score"),
                        "num_comments": post.get("num_comments"),
                        "query": query,
                    },
                )
            )

    return results
