"""
Gemini AI client for analyzing reviews.

This module handles connection to Google's Gemini API.
"""

from __future__ import annotations

import os
from typing import Any

try:
    from google import genai
    from google.genai import types
except ImportError:
    try:
        import google.generativeai as genai
        types = None
    except ImportError:
        genai = None
        types = None


class GeminiClient:
    """Client for interacting with Google's Gemini API."""

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize the Gemini client.

        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
        """
        if genai is None:
            raise ImportError(
                "google-generativeai package not installed. "
                "Run: pip install google-generativeai"
            )

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Set it in .env file or pass as parameter."
            )

        # Check if using new google-genai API
        if types is not None:
            # New API
            self.client = genai.Client(api_key=self.api_key)
            self.use_new_api = True
        else:
            # Old API
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.use_new_api = False

    def test_connection(self) -> str:
        """
        Test the connection to Gemini API.

        Returns:
            Response text from Gemini
        """
        if self.use_new_api:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents="Say 'Connection successful' in one sentence."
            )
            return response.text
        else:
            response = self.model.generate_content("Say 'Connection successful' in one sentence.")
            return response.text

    def generate_content(self, prompt: str) -> str:
        """
        Generate content using Gemini.

        Args:
            prompt: The prompt to send to Gemini

        Returns:
            Generated text response
        """
        if self.use_new_api:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text
        else:
            response = self.model.generate_content(prompt)
            return response.text

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

        response = self.model.generate_content(prompt)
        return {"raw_response": response.text, "text": text}

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

        response = self.model.generate_content(prompt)
        return {"raw_response": response.text, "text": text}
