"""
Filter reviews based on quality criteria like length and content.
"""

from __future__ import annotations

from typing import Any


def is_valid_review(review: dict[str, Any], min_word_count: int = 3) -> bool:
    """
    Check if a review meets minimum quality criteria.

    Args:
        review: Review dictionary
        min_word_count: Minimum number of words required (default: 3)

    Returns:
        True if review passes filters, False otherwise
    """
    text = review.get("text", "")

    # Check if text exists
    if not text or not text.strip():
        return False

    # Check word count
    words = text.strip().split()
    if len(words) < min_word_count:
        return False

    return True


def filter_reviews(
    reviews: list[dict[str, Any]], min_word_count: int = 3
) -> list[dict[str, Any]]:
    """
    Filter reviews to keep only those meeting quality criteria.

    Args:
        reviews: List of review dictionaries
        min_word_count: Minimum number of words required (default: 3)

    Returns:
        Filtered list of reviews
    """
    return [
        review for review in reviews if is_valid_review(review, min_word_count)
    ]


def get_filtered_count(
    reviews: list[dict[str, Any]], min_word_count: int = 3
) -> int:
    """
    Count how many reviews would be removed by filtering.

    Args:
        reviews: List of review dictionaries
        min_word_count: Minimum number of words required (default: 3)

    Returns:
        Number of reviews that would be removed
    """
    return len(reviews) - len(filter_reviews(reviews, min_word_count))
