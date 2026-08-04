"""
Sentiment analysis using Gemini AI.

This module analyzes the sentiment of customer reviews.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

from src.analysis.groq_client import GroqClient
from src.analysis.rate_limit_handler import FallbackAnalyzer, RateLimitHandler


def parse_sentiment_response(response_text: str) -> dict[str, Any]:
    """
    Parse Gemini's response into structured sentiment data.

    Args:
        response_text: Raw response text from Gemini

    Returns:
        Dictionary with sentiment, confidence, and reasoning
    """
    # Default values
    result = {
        "sentiment": "neutral",
        "confidence": 0.5,
        "reasoning": "Could not parse response",
    }

    try:
        # Try to extract JSON from response
        json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            result["sentiment"] = data.get("sentiment", "neutral").lower()
            result["confidence"] = float(data.get("confidence", 0.5))
            result["reasoning"] = data.get("reasoning", response_text[:100])
        else:
            # Fallback: parse from text
            text_lower = response_text.lower()
            if "positive" in text_lower:
                result["sentiment"] = "positive"
            elif "negative" in text_lower:
                result["sentiment"] = "negative"
            result["reasoning"] = response_text[:200]
    except (json.JSONDecodeError, ValueError):
        # If parsing fails, use the raw text
        result["reasoning"] = response_text[:200]

    # Ensure confidence is between 0 and 1
    result["confidence"] = max(0.0, min(1.0, result["confidence"]))

    return result


def analyze_sentiment_batch(client: GroqClient, reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Analyze sentiment for all reviews in efficient batches with rate limit handling.

    Args:
        client: GroqClient instance
        reviews: List of review dictionaries

    Returns:
        List of reviews with sentiment analysis added
    """
    # Initialize rate limit handler
    rate_handler = RateLimitHandler(client)
    fallback_analyzer = FallbackAnalyzer()
    
    batch_size = 50  # Process 50 reviews per API call
    all_sentiments = []
    
    for batch_start in range(0, len(reviews), batch_size):
        batch_reviews = reviews[batch_start:batch_start + batch_size]
        
        # Prepare reviews for batch processing
        reviews_text = []
        for i, review in enumerate(batch_reviews):
            text = review.get("text", "")[:300]  # Limit text length
            reviews_text.append(f"Review {i+1}: {text}")

        # Create batch prompt
        all_reviews = "\n".join(reviews_text)
        prompt = f"""
        Analyze the sentiment of these customer reviews.
        Return ONLY a JSON array with objects having these exact keys:
        - sentiment: "positive", "negative", or "neutral"
        - confidence: a number between 0 and 1
        - reasoning: brief explanation (max 20 words)

        Reviews:
        {all_reviews}
        """

        try:
            # Use rate limit handler for API call
            def api_call():
                return client.generate_content(prompt)
            
            def fallback():
                # Use keyword-based analysis for entire batch
                batch_sentiments = []
                for review in batch_reviews:
                    sentiment = fallback_analyzer.analyze_sentiment(review.get("text", ""))
                    batch_sentiments.append(sentiment)
                return json.dumps(batch_sentiments)
            
            response = rate_handler.execute_with_retry(api_call, fallback, max_retries=2)
            
            # Parse batch response
            sentiments = parse_batch_sentiment_response(response, len(batch_reviews))
            all_sentiments.extend(sentiments)
            print(f"  Processed batch {batch_start//batch_size + 1}/{(len(reviews)-1)//batch_size + 1}")
            
            # Print quota status periodically
            if batch_start % 250 == 0:
                print(f"  {rate_handler.get_usage_report()}")
                
        except Exception as e:
            # Add neutral sentiments for failed batch
            print(f"  Batch {batch_start//batch_size + 1} failed: {str(e)}")
            all_sentiments.extend([{"sentiment": "neutral", "confidence": 0.0, "reasoning": "Failed"}] * len(batch_reviews))
    
    # Add sentiment to each review
    for i, review in enumerate(reviews):
        if i < len(all_sentiments):
            review["sentiment"] = all_sentiments[i].get("sentiment", "neutral")
            review["confidence"] = all_sentiments[i].get("confidence", 0.0)
            review["reasoning"] = all_sentiments[i].get("reasoning", "")
        else:
            review["sentiment"] = "neutral"
            review["confidence"] = 0.0
            review["reasoning"] = "Not analyzed"
    
    # Print final usage report
    print(f"\n{rate_handler.get_usage_report()}")
    
    return reviews


def parse_batch_sentiment_response(response_text: str, expected_count: int) -> list[dict[str, Any]]:
    """
    Parse batch sentiment response from Groq.

    Args:
        response_text: Raw response text from Groq
        expected_count: Expected number of reviews

    Returns:
        List of sentiment dictionaries
    """
    try:
        # Try to extract JSON array from response
        import json
        import re
        
        # Find JSON array in response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            sentiments = json.loads(json_str)
            return sentiments[:expected_count]
        else:
            # Fallback: return neutral sentiments
            return [{"sentiment": "neutral", "confidence": 0.0, "reasoning": "Parse failed"}] * expected_count
    except Exception:
        # Fallback: return neutral sentiments
        return [{"sentiment": "neutral", "confidence": 0.0, "reasoning": "Parse failed"}] * expected_count


def analyze_reviews_batch(
    client: GroqClient,
    reviews: list[dict[str, Any]],
    delay_seconds: float = 1.0,
    max_reviews: int | None = None,
) -> list[dict[str, Any]]:
    """
    Analyze sentiment for a batch of reviews.

    Args:
        client: GroqClient instance
        reviews: List of review dictionaries
        delay_seconds: Delay between API calls to respect rate limits
        max_reviews: Maximum number of reviews to analyze (None = all)

    Returns:
        List of reviews with sentiment analysis added
    """
    if max_reviews:
        reviews = reviews[:max_reviews]

    analyzed_reviews = []
    total = len(reviews)

    for i, review in enumerate(reviews, 1):
        text = review.get("text", "")
        
        print(f"Analyzing review {i}/{total}...")
        
        # Analyze sentiment
        sentiment_result = analyze_sentiment(client, text)
        
        # Add sentiment data to review
        enhanced_review = review.copy()
        enhanced_review.update(sentiment_result)
        enhanced_review["analyzed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        analyzed_reviews.append(enhanced_review)
        
        # Rate limiting delay
        if i < total:
            time.sleep(delay_seconds)

    return analyzed_reviews


def get_sentiment_summary(reviews: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Calculate summary statistics for sentiment analysis.

    Args:
        reviews: List of analyzed review dictionaries

    Returns:
        Dictionary with sentiment distribution and stats
    """
    total = len(reviews)
    if total == 0:
        return {"total_analyzed": 0, "sentiment_distribution": {}}

    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    confidence_sum = 0.0
    error_count = 0

    for review in reviews:
        sentiment = review.get("sentiment", "neutral").lower()
        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1
        
        confidence = review.get("confidence", 0.0)
        if confidence > 0:  # Only count valid confidences
            confidence_sum += confidence
        
        if review.get("error"):
            error_count += 1

    valid_confidence_count = total - error_count
    avg_confidence = confidence_sum / valid_confidence_count if valid_confidence_count > 0 else 0.0

    return {
        "total_analyzed": total,
        "sentiment_distribution": sentiment_counts,
        "sentiment_percentages": {
            k: round(v / total * 100, 1) for k, v in sentiment_counts.items()
        },
        "average_confidence": round(avg_confidence, 3),
        "error_count": error_count,
    }
