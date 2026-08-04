"""
Test script for Groq AI connection.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from src.analysis.groq_client import GroqClient

def main() -> None:
    print("=" * 60)
    print("Testing Groq Connection")
    print("=" * 60)

    try:
        print("\nInitializing Groq client...")
        client = GroqClient()
        print("  Client initialized successfully")

        print("\nTesting connection with simple prompt...")
        response = client.test_connection()
        print(f"  Groq response: {response}")

        print("\n" + "=" * 60)
        print("Groq connection is working!")
        print("=" * 60)

    except ImportError as e:
        print(f"\nERROR: {e}")
        print("Fix: Run 'pip install groq'")
    except ValueError as e:
        print(f"\nERROR: {e}")
        print("Fix: Add GROQ_API_KEY to your .env file")
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Check your API key and internet connection")

if __name__ == "__main__":
    main()
