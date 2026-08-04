"""
Test script for API rate limit handling.

This script tests the rate limit handler with a small sample of reviews.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis.groq_client import GroqClient
from src.analysis.rate_limit_handler import RateLimitHandler, FallbackAnalyzer
from src.storage.local_store import STORE_DIR, load_json


def test_rate_limit_handler():
    """Test the rate limit handler with a small sample."""
    print("=" * 60)
    print("Testing API Rate Limit Handler")
    print("=" * 60)

    # Load a small sample of reviews
    sampled_file = STORE_DIR / "reviews_sampled_3000.json"
    payload = load_json(sampled_file)
    reviews = payload.get("reviews", [])[:10]  # Test with 10 reviews

    print(f"Loaded {len(reviews)} reviews for testing")

    # Initialize client and rate limit handler
    client = GroqClient()
    rate_handler = RateLimitHandler(client)
    fallback_analyzer = FallbackAnalyzer()

    # Test 1: Check rate limit detection
    print("\nTest 1: Rate Limit Detection")
    test_error = "Error code: 429 - Rate limit reached"
    is_rate_limit = rate_handler.is_rate_limit_error(test_error)
    print(f"  Error: {test_error}")
    print(f"  Detected as rate limit: {is_rate_limit}")
    assert is_rate_limit, "Failed to detect rate limit error"

    # Test 2: Check wait time extraction
    print("\nTest 2: Wait Time Extraction")
    test_error = "Please try again in 30m4.512s"
    wait_time = rate_handler.extract_wait_time(test_error)
    print(f"  Error: {test_error}")
    print(f"  Extracted wait time: {wait_time}s")
    assert wait_time > 0, "Failed to extract wait time"

    # Test 3: Check quota status
    print("\nTest 3: Quota Status")
    quota_status = rate_handler.get_quota_status()
    print(f"  Token usage: {quota_status['token_usage']}")
    print(f"  Daily limit: {quota_status['daily_limit']}")
    print(f"  Usage percentage: {quota_status['usage_percentage']:.1f}%")
    print(f"  Status: {quota_status['status']}")

    # Test 4: Test fallback analyzer
    print("\nTest 4: Fallback Analyzer")
    if reviews:
        test_review = reviews[0]
        test_text = test_review.get("text", "This is a test review")
        
        sentiment = fallback_analyzer.analyze_sentiment(test_text)
        print(f"  Sentiment: {sentiment['sentiment']} (confidence: {sentiment['confidence']})")
        
        themes = fallback_analyzer.extract_themes(test_text)
        print(f"  Themes: {themes['themes']}")
        
        print(f"  Fallback method: {sentiment['method']}")

    # Test 5: Test safe API call
    print("\nTest 5: Safe API Call")
    try:
        response = rate_handler.safe_api_call("Test prompt", "Fallback response")
        print(f"  Response received: {response[:100]}...")
    except Exception as e:
        print(f"  API call failed (expected if rate limited): {str(e)[:100]}")

    # Test 6: Print usage report
    print("\nTest 6: Usage Report")
    print(rate_handler.get_usage_report())

    print("\n" + "=" * 60)
    print("Rate Limit Handler Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_rate_limit_handler()
