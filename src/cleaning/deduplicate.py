"""
Remove exact duplicate reviews from the dataset.

Duplicates are identified by matching text + source + date.
"""

from __future__ import annotations

from typing import Any


def remove_duplicates(reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Remove exact duplicate reviews from the dataset.

    A review is considered a duplicate if another review has the same:
    - text (case-insensitive, stripped)
    - source
    - date

    Args:
        reviews: List of review dictionaries

    Returns:
        List of reviews with duplicates removed (first occurrence kept)
    """
    seen = set()
    unique_reviews = []

    for review in reviews:
        # Create a signature for duplicate detection
        text = (review.get("text") or "").strip().lower()
        source = review.get("source") or ""
        date = review.get("date") or ""

        signature = (text, source, date)

        if signature not in seen:
            seen.add(signature)
            unique_reviews.append(review)

    return unique_reviews


def get_duplicate_count(reviews: list[dict[str, Any]]) -> int:
    """
    Count how many duplicate reviews would be removed.

    Args:
        reviews: List of review dictionaries

    Returns:
        Number of duplicate reviews
    """
    return len(reviews) - len(remove_duplicates(reviews))
