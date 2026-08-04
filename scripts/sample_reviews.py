"""
Sample 3,000 mixed reviews from master dataset for analysis.

This script creates a balanced sample from all data sources.
"""

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.storage.local_store import STORE_DIR, load_json, save_json


def sample_mixed_reviews(total_reviews: int = 3000) -> list[dict[str, Any]]:
    """
    Sample mixed reviews from all sources.

    Args:
        total_reviews: Total number of reviews to sample

    Returns:
        List of sampled review dictionaries
    """
    # Load master dataset
    master_file = STORE_DIR / "reviews_master.json"
    payload = load_json(master_file)
    all_reviews = payload.get("reviews", [])

    print(f"Total reviews in master dataset: {len(all_reviews)}")

    # Group by source
    reviews_by_source = {}
    for review in all_reviews:
        source = review.get("source", "unknown")
        if source not in reviews_by_source:
            reviews_by_source[source] = []
        reviews_by_source[source].append(review)

    print(f"Reviews by source:")
    for source, reviews in reviews_by_source.items():
        print(f"  {source}: {len(reviews)}")

    # Calculate sample size per source (proportional to available data)
    total_available = sum(len(reviews) for reviews in reviews_by_source.values())
    
    sampled_reviews = []
    remaining_to_sample = total_reviews
    
    for source, reviews in sorted(reviews_by_source.items(), key=lambda x: len(x[1]), reverse=True):
        # Calculate proportional sample size
        proportion = len(reviews) / total_available
        sample_size = int(total_reviews * proportion)
        
        # Ensure we don't take more than available
        sample_size = min(sample_size, len(reviews))
        
        # Take first N reviews from each source
        source_sample = reviews[:sample_size]
        sampled_reviews.extend(source_sample)
        remaining_to_sample -= len(source_sample)
        
        print(f"Sampled {len(source_sample)} reviews from {source} (proportion: {proportion:.2%})")
    
    # If we still need more reviews, take from the largest source
    if remaining_to_sample > 0 and sampled_reviews:
        largest_source = max(reviews_by_source.items(), key=lambda x: len(x[1]))[0]
        additional_reviews = reviews_by_source[largest_source][len(sampled_reviews):len(sampled_reviews) + remaining_to_sample]
        sampled_reviews.extend(additional_reviews)
        print(f"Added {len(additional_reviews)} additional reviews from {largest_source} to reach target")

    print(f"\nTotal sampled reviews: {len(sampled_reviews)}")
    return sampled_reviews


def main() -> None:
    print("=" * 60)
    print("Sampling 3,000 Mixed Reviews from Master Dataset")
    print("=" * 60)

    # Sample reviews
    sampled_reviews = sample_mixed_reviews(3000)

    # Save sampled reviews
    output_file = STORE_DIR / "reviews_sampled_3000.json"
    save_json(
        {
            "sampled_at": "2026-07-29T01:52:00.000000+00:00",
            "count": len(sampled_reviews),
            "reviews": sampled_reviews
        },
        output_file
    )

    print(f"\nSaved sampled reviews to: {output_file}")
    print("=" * 60)
    print("Sampling complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
