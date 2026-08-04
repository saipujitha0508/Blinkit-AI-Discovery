"""
Chunking module for RAG implementation.

This module handles chunking of review data into logical chunks for embedding generation.
Chunks are approximately 300-500 tokens each and individual reviews are not split across chunks.
"""

from __future__ import annotations

from typing import Any


class ReviewChunker:
    """Chunker for review data that preserves review boundaries."""

    def __init__(self, target_chunk_size: int = 400) -> None:
        """
        Initialize the review chunker.

        Args:
            target_chunk_size: Target chunk size in tokens (default: 400)
        """
        self.target_chunk_size = target_chunk_size

    def chunk_reviews(self, reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Chunk reviews into logical chunks while preserving review boundaries.

        Args:
            reviews: List of review dictionaries

        Returns:
            List of chunk dictionaries with metadata
        """
        chunks = []
        current_chunk = []
        current_chunk_tokens = 0
        chunk_id = 0

        for review in reviews:
            # Estimate token count for this review (roughly 1 token per 4 characters)
            review_text = self._format_review_for_chunking(review)
            review_tokens = len(review_text) // 4

            # If adding this review would exceed target chunk size significantly,
            # start a new chunk (but don't split the review)
            if current_chunk_tokens > 0 and current_chunk_tokens + review_tokens > self.target_chunk_size * 1.5:
                # Save current chunk
                chunk = self._create_chunk(current_chunk, chunk_id)
                chunks.append(chunk)
                
                # Start new chunk
                current_chunk = [review]
                current_chunk_tokens = review_tokens
                chunk_id += 1
            else:
                # Add review to current chunk
                current_chunk.append(review)
                current_chunk_tokens += review_tokens

        # Don't forget the last chunk
        if current_chunk:
            chunk = self._create_chunk(current_chunk, chunk_id)
            chunks.append(chunk)

        return chunks

    def _format_review_for_chunking(self, review: dict[str, Any]) -> str:
        """
        Format a review for chunking purposes.

        Args:
            review: Review dictionary

        Returns:
            Formatted review text
        """
        text = review.get("text", "")
        rating = review.get("rating", "")
        sentiment = review.get("sentiment", "")
        themes = review.get("themes", [])
        
        formatted = f"Rating: {rating}\n"
        formatted += f"Sentiment: {sentiment}\n"
        formatted += f"Themes: {', '.join(themes)}\n"
        formatted += f"Review: {text}\n"
        
        return formatted

    def _create_chunk(self, reviews: list[dict[str, Any]], chunk_id: int) -> dict[str, Any]:
        """
        Create a chunk dictionary from a list of reviews.

        Args:
            reviews: List of reviews in this chunk
            chunk_id: Unique identifier for this chunk

        Returns:
            Chunk dictionary with metadata
        """
        # Combine all review texts for the chunk
        chunk_text = "\n---\n".join([self._format_review_for_chunking(r) for r in reviews])
        
        # Extract metadata
        review_ids = [r.get("id", f"review_{i}") for i, r in enumerate(reviews)]
        ratings = [r.get("rating") for r in reviews if r.get("rating")]
        sentiments = [r.get("sentiment") for r in reviews if r.get("sentiment")]
        
        # Calculate chunk statistics
        avg_rating = sum(ratings) / len(ratings) if ratings else None
        sentiment_counts = {}
        for sentiment in sentiments:
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

        return {
            "chunk_id": chunk_id,
            "text": chunk_text,
            "review_count": len(reviews),
            "review_ids": review_ids,
            "avg_rating": avg_rating,
            "sentiment_distribution": sentiment_counts,
            "estimated_tokens": len(chunk_text) // 4
        }

    def get_chunk_statistics(self, chunks: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Get statistics about the chunks.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Statistics dictionary
        """
        total_chunks = len(chunks)
        total_reviews = sum(chunk["review_count"] for chunk in chunks)
        total_tokens = sum(chunk["estimated_tokens"] for chunk in chunks)
        avg_chunk_size = total_tokens / total_chunks if total_chunks > 0 else 0
        avg_reviews_per_chunk = total_reviews / total_chunks if total_chunks > 0 else 0

        return {
            "total_chunks": total_chunks,
            "total_reviews": total_reviews,
            "total_tokens": total_tokens,
            "avg_chunk_size_tokens": avg_chunk_size,
            "avg_reviews_per_chunk": avg_reviews_per_chunk,
            "min_chunk_size": min(chunk["estimated_tokens"] for chunk in chunks) if chunks else 0,
            "max_chunk_size": max(chunk["estimated_tokens"] for chunk in chunks) if chunks else 0
        }
