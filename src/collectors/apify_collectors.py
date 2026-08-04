"""
Collect more Blinkit reviews using Apify (cloud scrapers).

Plain English:
1. You put your Apify API token in the .env file.
2. We ask Apify to run a ready-made scraper ("Actor").
3. Apify downloads reviews in the cloud.
4. We save the results into data/raw/.

Actors used:
- Play Store: jamhimself/google-play-reviews-scraper
- Reddit:     trudax/reddit-scraper-lite
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

from src.collectors.schema import make_review

load_dotenv()

BLINKIT_PLAY_APP_ID = "com.grofers.customerapp"
PLAY_ACTOR_ID = "jamhimself/google-play-reviews-scraper"
REDDIT_ACTOR_ID = "trudax/reddit-scraper-lite"


def is_apify_configured() -> bool:
    token = os.getenv("APIFY_API_TOKEN", "").strip()
    return bool(token) and token != "your_apify_token_here"


def _get_client():
    token = os.getenv("APIFY_API_TOKEN", "").strip()
    if not token or token == "your_apify_token_here":
        raise RuntimeError(
            "APIFY_API_TOKEN is missing.\n"
            "Put your token in the .env file and try again."
        )

    try:
        from apify_client import ApifyClient
    except ImportError as exc:
        raise RuntimeError(
            "apify-client is not installed. Run:\n"
            "  .\\.venv\\Scripts\\pip.exe install apify-client python-dotenv"
        ) from exc

    return ApifyClient(token)


def _dataset_id(run: Any) -> str | None:
    """
    Newer apify-client returns a Run object (not a plain dict).
    This helper reads the dataset id safely either way.
    """
    if run is None:
        return None
    value = getattr(run, "default_dataset_id", None)
    if value:
        return str(value)
    try:
        return str(run["defaultDatasetId"])
    except Exception:  # noqa: BLE001
        return None


def _as_text(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def collect_apify_play_store(max_reviews: int = 300) -> list[dict[str, Any]]:
    """Collect Blinkit Google Play reviews via Apify."""
    client = _get_client()
    print(f"  Starting Apify actor: {PLAY_ACTOR_ID}")
    print(f"  App: {BLINKIT_PLAY_APP_ID} (Blinkit)")
    print(f"  Requesting up to {max_reviews} reviews...")

    run = client.actor(PLAY_ACTOR_ID).call(
        run_input={
            "appId": BLINKIT_PLAY_APP_ID,
            "maxReviews": max_reviews,
            "sort": "newest",
            "language": "en",
            "country": "IN",
        }
    )

    dataset_id = _dataset_id(run)
    if not dataset_id:
        print("  Apify finished but returned no dataset id.")
        return []

    results: list[dict[str, Any]] = []
    for item in client.dataset(dataset_id).iterate_items():
        # Safety: only keep Blinkit app reviews
        app_id = _as_text(item, "appId", "app_id")
        if app_id and app_id != BLINKIT_PLAY_APP_ID:
            continue

        text = _as_text(item, "text", "content", "reviewText", "review")
        title = _as_text(item, "title")
        if title and text and title not in text:
            text = f"{title}\n\n{text}"
        elif title and not text:
            text = title
        if not text:
            continue

        review_id = _as_text(item, "reviewId", "id") or str(len(results))
        rating = item.get("rating")
        if rating is None:
            rating = item.get("score")
        date = _as_text(item, "date", "reviewDate", "at", "publishedAt")
        author = _as_text(item, "userName", "author") or None

        results.append(
            make_review(
                review_id=f"apify_play_{review_id}",
                source="google_play_apify",
                text=text,
                rating=rating,
                date=date or None,
                author=author,
                url=_as_text(item, "url")
                or f"https://play.google.com/store/apps/details?id={BLINKIT_PLAY_APP_ID}",
                language=item.get("language") or "en",
                metadata={
                    "provider": "apify",
                    "actor": PLAY_ACTOR_ID,
                    "app_id": BLINKIT_PLAY_APP_ID,
                    "raw_review_id": review_id,
                    "thumbs_up": item.get("thumbsUpCount") or item.get("thumbsUp"),
                    "reply_text": item.get("replyContent") or item.get("replyText"),
                    "app_version": item.get("appVersion") or item.get("version"),
                },
            )
        )

    return results


def collect_apify_reddit(
    queries: list[str] | None = None,
    max_items: int = 50,
) -> list[dict[str, Any]]:
    """Collect Blinkit-related Reddit posts via Apify."""
    client = _get_client()
    queries = queries or [
        "blinkit",
        "blinkit review",
        "blinkit groceries",
        "blinkit vs zepto",
    ]

    start_urls = [
        {"url": f"https://www.reddit.com/search/?q={q.replace(' ', '+')}&sort=new"}
        for q in queries
    ]

    print(f"  Starting Apify actor: {REDDIT_ACTOR_ID}")
    print(f"  Searching Reddit for: {', '.join(queries)}")

    run = client.actor(REDDIT_ACTOR_ID).call(
        run_input={
            "startUrls": start_urls,
            "maxItems": max_items,
            "skipComments": True,
            "searchSort": "new",
            "searchTime": "year",
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
            },
        }
    )

    dataset_id = _dataset_id(run)
    if not dataset_id:
        print("  Apify finished but returned no dataset id.")
        return []

    results: list[dict[str, Any]] = []
    seen: set[str] = set()

    for item in client.dataset(dataset_id).iterate_items():
        post_id = _as_text(item, "id", "parsedId", "postId") or str(len(results))
        if post_id in seen:
            continue
        seen.add(post_id)

        title = _as_text(item, "title")
        body = _as_text(item, "body", "selftext", "text")
        text = title if not body else f"{title}\n\n{body}"
        if not text:
            continue

        lowered = text.lower()
        if not any(
            word in lowered
            for word in ("blinkit", "zepto", "instamart", "quick commerce", "grofers")
        ):
            continue

        results.append(
            make_review(
                review_id=f"apify_reddit_{post_id}",
                source="reddit_apify",
                text=text,
                rating=None,
                date=_as_text(item, "createdAt", "created_utc", "date") or None,
                author=_as_text(item, "username", "author") or None,
                url=_as_text(item, "url", "communityUrl", "parsedUrl") or None,
                language=None,
                metadata={
                    "provider": "apify",
                    "actor": REDDIT_ACTOR_ID,
                    "communityName": item.get("communityName") or item.get("subreddit"),
                    "upVotes": item.get("upVotes") or item.get("score"),
                },
            )
        )

    return results
