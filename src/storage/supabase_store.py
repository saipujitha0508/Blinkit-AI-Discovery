"""
Optional Supabase cloud storage (Phase 3 advanced).

Plain English:
Supabase is an online database. Local files are enough for this project.
Use this only if you create a Supabase account and add keys to .env.

We keep local master files as the main store so beginners are never blocked.
"""

from __future__ import annotations

import os
from typing import Any


def is_supabase_configured() -> bool:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    return bool(url and key) and "your_supabase" not in url and "your_supabase" not in key


def push_reviews_to_supabase(reviews: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Upload reviews to a Supabase table named `reviews`.

    Table columns expected (create once in Supabase SQL editor):
      id text primary key
      source text
      text text
      rating float8
      date text
      author text
      url text
      language text
      collected_at text
      storage_key text
    """
    if not is_supabase_configured():
        return {
            "ok": False,
            "message": "Supabase not configured. Local store is still ready.",
        }

    try:
        from supabase import create_client
    except ImportError:
        return {
            "ok": False,
            "message": "supabase package not installed. Local store is still ready.",
        }

    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    client = create_client(url, key)

    # Upload in small chunks
    chunk_size = 200
    uploaded = 0
    for i in range(0, len(reviews), chunk_size):
        chunk = []
        for review in reviews[i : i + chunk_size]:
            chunk.append(
                {
                    "id": review.get("id"),
                    "source": review.get("source"),
                    "text": review.get("text"),
                    "rating": review.get("rating"),
                    "date": review.get("date"),
                    "author": review.get("author"),
                    "url": review.get("url"),
                    "language": review.get("language"),
                    "collected_at": review.get("collected_at"),
                    "storage_key": review.get("storage_key"),
                }
            )
        client.table("reviews").upsert(chunk).execute()
        uploaded += len(chunk)

    return {"ok": True, "uploaded": uploaded}
