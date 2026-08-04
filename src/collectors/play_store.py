"""
Collect live Google Play Store reviews for the Blinkit Android app.

Supports large targets by:
1. Paginating with continuation tokens
2. Trying multiple sort orders (newest / rating / relevance)
3. Trying more than one language (en, hi)
"""

from __future__ import annotations

from typing import Any

from google_play_scraper import Sort, reviews as gp_reviews

from src.collectors.schema import make_review

BLINKIT_APP_ID = "com.grofers.customerapp"

SORT_OPTIONS = {
    "newest": Sort.NEWEST,
    "rating": Sort.RATING,
    "relevance": Sort.MOST_RELEVANT,
}


def _convert(item: dict[str, Any], lang: str, country: str) -> dict[str, Any] | None:
    review_id = str(item.get("reviewId") or "")
    text = (item.get("content") or "").strip()
    if not review_id or not text:
        return None

    at_value = item.get("at")
    date_str = at_value.isoformat() if hasattr(at_value, "isoformat") else str(at_value)

    return make_review(
        review_id=f"play_{review_id}",
        source="google_play",
        text=text,
        rating=item.get("score"),
        date=date_str,
        author=item.get("userName"),
        url=f"https://play.google.com/store/apps/details?id={BLINKIT_APP_ID}&hl={lang}",
        language=lang,
        metadata={
            "thumbs_up": item.get("thumbsUpCount"),
            "reply_content": item.get("replyContent"),
            "app_id": BLINKIT_APP_ID,
            "country": country,
            "raw_review_id": review_id,
        },
    )


def collect_play_store_reviews(
    count: int = 100,
    lang: str = "en",
    country: str = "in",
    sort: str = "newest",
) -> list[dict[str, Any]]:
    """Download Play Store reviews (single sort/language), with pagination."""
    sort_enum = SORT_OPTIONS.get(sort, Sort.NEWEST)
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    token = None

    while len(results) < count:
        batch_size = min(200, count - len(results))
        raw_reviews, token = gp_reviews(
            BLINKIT_APP_ID,
            lang=lang,
            country=country,
            sort=sort_enum,
            count=batch_size,
            filter_score_with=None,
            continuation_token=token,
        )
        if not raw_reviews:
            break

        for item in raw_reviews:
            converted = _convert(item, lang, country)
            if not converted:
                continue
            rid = converted["id"]
            if rid in seen:
                continue
            seen.add(rid)
            results.append(converted)
            if len(results) >= count:
                break

        if not token:
            break

    return results[:count]


def collect_play_store_bulk(
    target: int = 2000,
    country: str = "in",
) -> list[dict[str, Any]]:
    """
    Collect a larger unique set by combining sorts + languages.

    Plain English:
    Google shows reviews in different "views" (newest, top rated, most relevant)
    and languages. We collect from several views and keep unique review IDs.
    """
    seen: set[str] = set()
    combined: list[dict[str, Any]] = []

    plans = [
        ("en", "newest"),
        ("en", "relevance"),
        ("en", "rating"),
        ("hi", "newest"),
        ("hi", "relevance"),
    ]

    per_plan = max(400, target // len(plans) + 100)

    for lang, sort_name in plans:
        print(f"  Free Play scrape: lang={lang}, sort={sort_name}, up to {per_plan}")
        batch = collect_play_store_reviews(
            count=per_plan,
            lang=lang,
            country=country,
            sort=sort_name,
        )
        added = 0
        for review in batch:
            if review["id"] in seen:
                continue
            seen.add(review["id"])
            combined.append(review)
            added += 1
            if len(combined) >= target:
                break
        print(f"    +{added} unique (running total: {len(combined)})")
        if len(combined) >= target:
            break

    return combined
