"""
Normalize text by cleaning spaces, special characters, and formatting.
"""

from __future__ import annotations

import re
from typing import Any


def normalize_text(text: str) -> str:
    """
    Clean and normalize review text.

    This includes:
    - Removing extra whitespace
    - Removing leading/trailing spaces
    - Normalizing multiple spaces to single space
    - Removing weird unicode characters when possible

    Args:
        text: Raw review text

    Returns:
        Normalized text
    """
    if not text:
        return ""

    # Remove leading/trailing whitespace
    text = text.strip()

    # Replace multiple spaces/tabs/newlines with single space
    text = re.sub(r"\s+", " ", text)

    # Remove common problematic unicode characters
    # Keep basic punctuation and letters
    text = re.sub(r"[\u200b\u200c\u200d\u200e\u200f\ufeff]", "", text)

    return text.strip()


def normalize_review(review: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize the text field in a review dictionary.

    Args:
        review: Review dictionary

    Returns:
        Review with normalized text field
    """
    normalized = review.copy()
    if "text" in normalized:
        normalized["text"] = normalize_text(normalized.get("text", ""))
    return normalized
