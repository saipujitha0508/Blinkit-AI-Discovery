"""
Merge many raw batch files into one master list for storage.

Phase 3 job (plain English):
- Collect all reviews from data/raw/
- Remove exact duplicates (same review appearing in multiple downloads)
- Keep one clean master list in data/store/

Heavy text cleaning (punctuation, language translate, etc.) is Phase 4.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


def unique_key(review: dict[str, Any]) -> str:
    """
    Build a stable ID so the same review from free scrape + Apify
    is stored only once.
    """
    meta = review.get("metadata") or {}
    raw_id = meta.get("raw_review_id")
    if raw_id:
        return f"play::{raw_id}"

    rid = str(review.get("id") or "").strip()
    for prefix in ("apify_play_", "play_", "appstore_", "apify_reddit_", "reddit_"):
        if rid.startswith(prefix):
            kind = prefix.replace("_", "").replace("apify", "apify_")
            # normalize kinds
            if "play" in prefix:
                return f"play::{rid[len(prefix):]}"
            if "appstore" in prefix:
                return f"appstore::{rid[len(prefix):]}"
            if "reddit" in prefix:
                return f"reddit::{rid[len(prefix):]}"
            return f"{kind}::{rid[len(prefix):]}"

    text = (review.get("text") or "").strip().lower()
    source = review.get("source") or "unknown"
    return f"{source}::text::{text[:200]}"


def merge_reviews(reviews: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Merge reviews and drop duplicates.

    Returns:
      (unique_reviews, summary_stats)
    """
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    source_counts: Counter[str] = Counter()
    duplicate_count = 0

    for review in reviews:
        key = unique_key(review)
        if key in seen:
            duplicate_count += 1
            continue
        seen.add(key)

        # Prefer a clean source label for storage
        source = str(review.get("source") or "unknown")
        if source.endswith("_apify"):
            source = source.replace("_apify", "")
        if source == "google_play_apify":
            source = "google_play"

        stored = {
            "id": review.get("id"),
            "source": source,
            "text": (review.get("text") or "").strip(),
            "rating": review.get("rating"),
            "date": review.get("date"),
            "author": review.get("author"),
            "url": review.get("url"),
            "language": review.get("language"),
            "collected_at": review.get("collected_at"),
            "metadata": review.get("metadata") or {},
            "storage_key": key,
            "_raw_file": review.get("_raw_file"),
        }

        # Skip empty text rows
        if not stored["text"]:
            continue

        merged.append(stored)
        source_counts[stored["source"]] += 1

    summary = {
        "input_rows": len(reviews),
        "unique_rows": len(merged),
        "duplicates_removed": duplicate_count,
        "by_source": dict(source_counts),
        "with_rating": sum(1 for r in merged if r.get("rating") is not None),
        "without_rating": sum(1 for r in merged if r.get("rating") is None),
    }
    return merged, summary
