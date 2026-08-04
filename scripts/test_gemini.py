"""
Phase 5 script: test Gemini API connection.

Run:
  .\\.venv\\Scripts\\python.exe scripts\\test_gemini.py

What it does:
1. Loads GEMINI_API_KEY from .env
2. Connects to Gemini API
3. Sends a simple test prompt
4. Prints the response
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from src.analysis.gemini_client import GeminiClient


def main() -> None:
    print("=" * 60)
    print("Phase 5: Test Gemini Connection")
    print("=" * 60)

    try:
        print("\nInitializing Gemini client...")
        client = GeminiClient()
        print("  Client initialized successfully")

        print("\nTesting connection with simple prompt...")
        response = client.test_connection()
        print(f"  Gemini response: {response}")

        print("\n" + "=" * 60)
        print("Phase 5 complete. Gemini connection is working!")
        print("=" * 60)

    except ImportError as e:
        print(f"\nERROR: {e}")
        print("Fix: Run 'pip install google-generativeai'")
    except ValueError as e:
        print(f"\nERROR: {e}")
        print("Fix: Add GEMINI_API_KEY to your .env file")
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Check your API key and internet connection")


if __name__ == "__main__":
    main()
