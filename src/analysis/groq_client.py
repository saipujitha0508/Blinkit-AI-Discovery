"""
Groq AI client for analyzing reviews.

This module handles connection to Groq API as an alternative to Gemini.
"""

from __future__ import annotations

import os
from typing import Any

try:
    from groq import Groq
except ImportError:
    Groq = None


class GroqClient:
    """Client for interacting with Groq API."""

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize the Groq client.

        Args:
            api_key: Groq API key. If None, reads from GROQ_API_KEY env var.
        """
        if Groq is None:
            raise ImportError(
                "groq package not installed. "
                "Run: pip install groq"
            )

        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Set it in .env file or pass as parameter."
            )

        self.client = Groq(api_key=self.api_key)
        # Use Llama 3.3 70B model for best performance
        self.model = "llama-3.3-70b-versatile"

    def test_connection(self) -> str:
        """
        Test the connection to Groq API.

        Returns:
            Response text from Groq
        """
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Connection successful' in one sentence."
                }
            ],
            model=self.model
        )
        return response.choices[0].message.content

    def generate_content(self, prompt: str) -> str:
        """
        Generate content using Groq.

        Args:
            prompt: The prompt to send to Groq

        Returns:
            Generated text response
        """
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=self.model,
            max_tokens=8192
        )
        return response.choices[0].message.content

    def analyze_sentiment(self, text: str) -> dict[str, Any]:
        """
        Analyze sentiment of a text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment analysis results
        """
        prompt = f"""
        Analyze the sentiment of this customer review. 
        Return only a JSON object with these keys:
        - sentiment: "positive", "negative", or "neutral"
        - confidence: a number between 0 and 1
        - reasoning: brief explanation (max 20 words)

        Review: {text}
        """

        response = self.generate_content(prompt)
        return {"raw_response": response, "text": text}

    def extract_themes(self, text: str) -> dict[str, Any]:
        """
        Extract themes from a text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with theme extraction results
        """
        prompt = f"""
        Extract the main themes from this customer review.
        Return only a JSON object with these keys:
        - themes: list of main topics (max 5)
        - reasoning: brief explanation (max 20 words)

        Review: {text}
        """

        response = self.generate_content(prompt)
        return {"raw_response": response, "text": text}
