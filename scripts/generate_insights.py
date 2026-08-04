"""
Phase 8 script: generate business insights from analyzed reviews using Gemini AI.

Run:
  .\\.venv\\Scripts\\python.exe scripts\\generate_insights.py

What it does:
1. Loads reviews with sentiment and themes from Phase 7
2. Aggregates data by sentiment and theme
3. Generates business insights using Gemini AI
4. Saves results to data/analyzed/
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
from src.analysis.insights_generator import (
    aggregate_review_data,
    generate_insights,
    get_insights_summary,
)
from src.storage.local_store import (
    ANALYZED_DIR,
    load_json,
    save_json,
)


def load_reviews_with_themes() -> list[dict[str, Any]]:
    """Load reviews with themes from Phase 7."""
    themes_file = ANALYZED_DIR / "reviews_with_themes.json"
    
    if not themes_file.exists():
        print(f"ERROR: Reviews with themes file not found: {themes_file}")
        print("Please run Phase 7 first: python scripts\\generate_themes.py")
        return []
    
    payload = load_json(themes_file)
    return payload.get("reviews", [])


def save_business_insights(
    insights: dict[str, Any], summary: dict[str, Any]
) -> dict[str, Path]:
    """
    Save business insights and summary to data/analyzed/.

    Args:
        insights: Dictionary with generated insights
        summary: Summary dictionary with insights stats

    Returns:
        Dictionary with paths to saved files
    """
    ANALYZED_DIR.mkdir(parents=True, exist_ok=True)

    # Save business insights
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    insights_json = ANALYZED_DIR / f"business_insights_{stamp}.json"
    latest_json = ANALYZED_DIR / "business_insights.json"

    payload = {
        "insights_generated_at": datetime.now(timezone.utc).isoformat(),
        "insights": insights,
    }

    save_json(payload, insights_json)
    save_json(payload, latest_json)

    # Save summary
    summary_json = ANALYZED_DIR / f"insights_summary_{stamp}.json"
    latest_summary = ANALYZED_DIR / "insights_summary.json"

    summary["insights_generated_at"] = payload["insights_generated_at"]
    summary["insights_json"] = str(insights_json.relative_to(PROJECT_ROOT))
    save_json(summary, summary_json)
    save_json(summary, latest_summary)

    return {
        "insights_json": insights_json,
        "latest_json": latest_json,
        "summary_json": summary_json,
        "latest_summary": latest_summary,
    }


def main() -> None:
    print("=" * 60)
    print("Phase 8: Generate Business Insights with Gemini AI")
    print("=" * 60)

    # Load reviews with themes
    print("\nLoading reviews with themes from Phase 7...")
    reviews_with_themes = load_reviews_with_themes()
    
    if not reviews_with_themes:
        print("ERROR: No reviews with themes found. Exiting.")
        return
    
    print(f"  Loaded {len(reviews_with_themes)} reviews with themes")

    # Aggregate data
    print("\nAggregating review data...")
    aggregated_data = aggregate_review_data(reviews_with_themes)
    print(f"  Total reviews: {aggregated_data['total_reviews']}")
    print(f"  Sentiment distribution: {aggregated_data.get('sentiment_distribution', {})}")
    print(f"  Top themes: {[t['theme'] for t in aggregated_data.get('top_themes', [])[:5]]}")

    # Initialize Groq client
    print("\nInitializing Groq client...")
    try:
        client = GroqClient()
        print("  Client initialized successfully")
    except Exception as e:
        print(f"  ERROR: {e}")
        print("  Please check your GROQ_API_KEY in .env file")
        return

    # Generate insights
    print("\nGenerating business insights...")
    print("  This analyzes aggregated data (faster than individual reviews)...\n")

    insights = generate_insights(client, aggregated_data)

    print(f"  Generated insights successfully")

    # Calculate summary
    print("\nCreating insights summary...")
    summary = get_insights_summary(insights)
    print(f"  Total reviews analyzed: {summary['total_reviews']}")
    print(f"  Key findings: {summary['total_findings']}")
    print(f"  Recommendations: {summary['total_recommendations']}")
    print(f"  Priority areas: {summary['total_priorities']}")
    if summary["has_errors"]:
        print(f"  Note: Some errors occurred during generation")

    # Display key insights
    print("\n" + "=" * 60)
    print("KEY INSIGHTS:")
    print("=" * 60)
    print(f"\nSummary:\n{insights.get('summary', 'No summary available')}")
    
    print(f"\nKey Findings:")
    for i, finding in enumerate(insights.get("key_findings", []), 1):
        print(f"  {i}. {finding}")
    
    print(f"\nTop Priority Areas:")
    for i, area in enumerate(insights.get("priority_areas", []), 1):
        print(f"  {i}. {area}")

    # Save results
    print("\nSaving business insights...")
    paths = save_business_insights(insights, summary)
    print(f"  Insights JSON: {paths['latest_json']}")
    print(f"  Summary: {paths['latest_summary']}")

    print("\n" + "=" * 60)
    print("Phase 8 complete.")
    print(f"  Generated insights from {summary['total_reviews']} reviews")
    print("=" * 60)


if __name__ == "__main__":
    main()
