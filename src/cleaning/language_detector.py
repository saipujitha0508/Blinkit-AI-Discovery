"""
Detect language of review text using langdetect.
"""

from __future__ import annotations

from typing import Any

try:
    from langdetect import detect, LangDetectException
except ImportError:
    # Fallback if langdetect not installed
    detect = None
    LangDetectException = Exception


def detect_language(text: str) -> str:
    """
    Detect the language of a text string.

    Returns ISO 639-1 language code (e.g., 'en' for English, 'hi' for Hindi).
    Returns 'unknown' if detection fails or library not available.

    Args:
        text: Text to analyze

    Returns:
        Language code as string
    """
    if not text or not text.strip():
        return "unknown"

    if detect is None:
        return "unknown"

    try:
        # langdetect returns ISO 639-1 codes
        lang = detect(text)
        return lang
    except LangDetectException:
        return "unknown"
    except Exception:
        return "unknown"


def add_language_to_review(review: dict[str, Any]) -> dict[str, Any]:
    """
    Add detected language to a review dictionary.

    If language is already present, it is not overwritten.

    Args:
        review: Review dictionary

    Returns:
        Review with language field added
    """
    enhanced = review.copy()

    # Only detect if language is not already set
    if not enhanced.get("language") or enhanced.get("language") == "unknown":
        text = enhanced.get("text", "")
        enhanced["language"] = detect_language(text)

    return enhanced


def get_language_distribution(reviews: list[dict[str, Any]]) -> dict[str, int]:
    """
    Count reviews by language.

    Args:
        reviews: List of review dictionaries

    Returns:
        Dictionary mapping language codes to counts
    """
    distribution: dict[str, int] = {}

    for review in reviews:
        lang = review.get("language", "unknown")
        distribution[lang] = distribution.get(lang, 0) + 1

    return distribution
