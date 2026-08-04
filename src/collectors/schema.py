"""
Shared shape for one customer review / discussion.

Every collector (Play Store, Reddit, Apify, etc.) converts its data
into this same format so the rest of the project stays simple.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    """Return the current time in a standard text format."""
    return datetime.now(timezone.utc).isoformat()


def make_review(
    *,
    review_id: str,
    source: str,
    text: str,
    rating: float | None = None,
    date: str | None = None,
    author: str | None = None,
    url: str | None = None,
    language: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build one review dictionary.

    Think of this like filling a form with the same fields every time.
    """
    return {
        "id": review_id,
        "source": source,
        "text": (text or "").strip(),
        "rating": rating,
        "date": date,
        "author": author,
        "url": url,
        "language": language,
        "collected_at": utc_now_iso(),
        "metadata": metadata or {},
    }
