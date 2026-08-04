"""
Phase 7 script: extract themes from analyzed reviews using Gemini AI.

Run:
  .\\.venv\\Scripts\\python.exe scripts\\generate_themes.py

What it does:
1. Loads analyzed reviews from Phase 6
2. Extracts themes using Gemini AI
3. Saves results to data/analyzed/
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from src.analysis.groq_client import GroqClient
from src.analysis.theme_extractor import (
    extract_themes_batch,
    get_theme_summary,
)
from src.storage.local_store import (
    ANALYZED_DIR,
    STORE_DIR,
    load_json,
    save_json,
)


def load_analyzed_reviews() -> list[dict[str, Any]]:
    """Load analyzed reviews from Phase 6."""
    analyzed_file = ANALYZED_DIR / "reviews_analyzed.json"
    
    if not analyzed_file.exists():
        print(f"ERROR: Analyzed reviews file not found: {analyzed_file}")
        print("Please run Phase 6 first: python scripts\\analyze_reviews.py")
        return []
    
    payload = load_json(analyzed_file)
    reviews = payload.get("reviews", [])
    print(f"Loaded {len(reviews)} analyzed reviews")
    return reviews


def save_reviews_with_themes(
    reviews: list[dict[str, Any]], summary: dict[str, Any]
) -> dict[str, Path]:
    """
    Save reviews with themes and summary to data/analyzed/.

    Args:
        reviews: List of review dictionaries with themes
        summary: Summary dictionary with theme stats

    Returns:
        Dictionary with paths to saved files
    """
    ANALYZED_DIR.mkdir(parents=True, exist_ok=True)

    # Save reviews with themes
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    themes_json = ANALYZED_DIR / f"reviews_with_themes_{stamp}.json"
    latest_json = ANALYZED_DIR / "reviews_with_themes.json"

    payload = {
        "themes_extracted_at": datetime.now(timezone.utc).isoformat(),
        "count": len(reviews),
        "reviews": reviews,
    }

    save_json(payload, themes_json)
    save_json(payload, latest_json)

    # Save summary
    summary_json = ANALYZED_DIR / f"themes_summary_{stamp}.json"
    latest_summary = ANALYZED_DIR / "themes_summary.json"

    summary["themes_extracted_at"] = payload["themes_extracted_at"]
    summary["themes_json"] = str(themes_json.relative_to(PROJECT_ROOT))
    save_json(summary, summary_json)
    save_json(summary, latest_summary)

    return {
        "themes_json": themes_json,
        "latest_json": latest_json,
        "summary_json": summary_json,
        "latest_summary": latest_summary,
    }


def main() -> None:
    print("=" * 60)
    print("Phase 7: Generate Themes with Gemini AI")
    print("=" * 60)

    # Load analyzed reviews
    print("\nLoading analyzed reviews from Phase 6...")
    analyzed_reviews = load_analyzed_reviews()
    
    if not analyzed_reviews:
        print("ERROR: No analyzed reviews found. Exiting.")
        return
    
    print(f"  Loaded {len(analyzed_reviews)} analyzed reviews")

    # Initialize Groq client
    print("\nInitializing Groq client...")
    try:
        client = GroqClient()
        print("  Client initialized successfully")
    except Exception as e:
        print(f"  ERROR: {e}")
        print("  Please check your GROQ_API_KEY in .env file")
        return

    # Extract themes
    print("\nStarting theme extraction...")
    print("  Processing all reviews in single batch API call...")
    print("  This may take a few minutes depending on the number of reviews...\n")

    # Process all reviews in single batch
    reviews_with_themes = extract_themes_batch(client, analyzed_reviews)

    print(f"\n  Extracted themes from {len(reviews_with_themes)} reviews in single batch")

    # Calculate summary
    print("\nCalculating theme summary...")
    summary = get_theme_summary(reviews_with_themes)
    print(f"  Total analyzed: {summary['total_analyzed']}")
    print(f"  Total themes extracted: {summary['total_themes_extracted']}")
    print(f"  Top themes:")
    for theme_item in summary["top_themes"][:5]:
        print(f"    {theme_item['theme']}: {theme_item['count']}")
    print(f"  Top categories:")
    for cat_item in summary["top_categories"][:3]:
        print(f"    {cat_item['category']}: {cat_item['count']}")
    if summary["error_count"] > 0:
        print(f"  Errors: {summary['error_count']}")

    # Save results
    print("\nSaving reviews with themes...")
    paths = save_reviews_with_themes(reviews_with_themes, summary)
    print(f"  Themes JSON: {paths['latest_json']}")
    print(f"  Summary: {paths['latest_summary']}")

    print("\n" + "=" * 60)
    print(f"Phase 7 complete.")
    print(f"  Processed {len(reviews_with_themes)} reviews in single batch")
    print("=" * 60)


if __name__ == "__main__":
    main()
