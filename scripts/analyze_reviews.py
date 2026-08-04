"""
Phase 6 script: analyze reviews with Gemini AI for sentiment.

Run:
  .\\.venv\\Scripts\\python.exe scripts\\analyze_reviews.py

What it does:
1. Loads cleaned reviews from Phase 4
2. Analyzes sentiment using Gemini AI
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
from src.analysis.sentiment_analyzer import (
    analyze_sentiment_batch,
    get_sentiment_summary,
)
from src.storage.local_store import (
    ANALYZED_DIR,
    CLEANED_DIR,
    STORE_DIR,
    load_json,
    save_json,
)


def load_cleaned_reviews() -> list[dict[str, Any]]:
    """Load cleaned reviews from sampled dataset (3,000 mixed reviews)."""
    sampled_file = STORE_DIR / "reviews_sampled_3000.json"
    
    if not sampled_file.exists():
        print(f"ERROR: Sampled reviews file not found: {sampled_file}")
        print("Falling back to master dataset...")
        master_file = STORE_DIR / "reviews_master.json"
        if not master_file.exists():
            print("ERROR: Master reviews file not found either")
            return []
        payload = load_json(master_file)
        reviews = payload.get("reviews", [])
        print(f"Loaded {len(reviews)} reviews from master dataset")
        return reviews
    
    payload = load_json(sampled_file)
    reviews = payload.get("reviews", [])
    print(f"Loaded {len(reviews)} reviews from sampled dataset (mixed sources)")
    return reviews


def save_analyzed_reviews(
    reviews: list[dict[str, Any]], summary: dict[str, Any]
) -> dict[str, Path]:
    """
    Save analyzed reviews and summary to data/analyzed/.

    Args:
        reviews: List of analyzed review dictionaries
        summary: Summary dictionary with analysis stats

    Returns:
        Dictionary with paths to saved files
    """
    ANALYZED_DIR.mkdir(parents=True, exist_ok=True)

    # Save analyzed reviews
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    analyzed_json = ANALYZED_DIR / f"reviews_analyzed_{stamp}.json"
    latest_json = ANALYZED_DIR / "reviews_analyzed.json"

    payload = {
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "count": len(reviews),
        "reviews": reviews,
    }

    save_json(payload, analyzed_json)
    save_json(payload, latest_json)

    # Save summary
    summary_json = ANALYZED_DIR / f"analysis_summary_{stamp}.json"
    latest_summary = ANALYZED_DIR / "analysis_summary.json"

    summary["analyzed_at"] = payload["analyzed_at"]
    summary["analyzed_json"] = str(analyzed_json.relative_to(PROJECT_ROOT))
    save_json(summary, summary_json)
    save_json(summary, latest_summary)

    return {
        "analyzed_json": analyzed_json,
        "latest_json": latest_json,
        "summary_json": summary_json,
        "latest_summary": latest_summary,
    }


def main() -> None:
    print("=" * 60)
    print("Phase 6: Analyze Reviews with Gemini AI")
    print("=" * 60)

    # Load cleaned reviews
    print("\nLoading cleaned reviews from Phase 4...")
    cleaned_reviews = load_cleaned_reviews()
    
    if not cleaned_reviews:
        print("ERROR: No cleaned reviews found. Exiting.")
        return
    
    print(f"  Loaded {len(cleaned_reviews)} cleaned reviews")

    # Initialize Groq client
    print("\nInitializing Groq client...")
    try:
        client = GroqClient()
        print("  Client initialized successfully")
    except Exception as e:
        print(f"  ERROR: {e}")
        print("  Please check your GROQ_API_KEY in .env file")
        return

    # Analyze reviews
    print("\nStarting sentiment analysis...")
    print("  Processing all reviews in single batch API call...")
    print("  This may take a few minutes depending on the number of reviews...\n")

    # Process all reviews in single batch
    analyzed_reviews = analyze_sentiment_batch(client, cleaned_reviews)

    print(f"\n  Analyzed {len(analyzed_reviews)} reviews in single batch")

    # Calculate summary
    print("\nCalculating sentiment summary...")
    summary = get_sentiment_summary(analyzed_reviews)
    print(f"  Total analyzed: {summary['total_analyzed']}")
    print(f"  Sentiment distribution:")
    for sentiment, count in summary["sentiment_distribution"].items():
        percentage = summary["sentiment_percentages"].get(sentiment, 0)
        print(f"    {sentiment}: {count} ({percentage}%)")
    print(f"  Average confidence: {summary['average_confidence']}")
    if summary["error_count"] > 0:
        print(f"  Errors: {summary['error_count']}")

    # Save results
    print("\nSaving analyzed reviews...")
    paths = save_analyzed_reviews(analyzed_reviews, summary)
    print(f"  Analyzed JSON: {paths['latest_json']}")
    print(f"  Summary: {paths['latest_summary']}")

    print("\n" + "=" * 60)
    print(f"Phase 6 complete.")
    print(f"  Analyzed {len(analyzed_reviews)} reviews in single batch")
    print("=" * 60)


if __name__ == "__main__":
    main()
