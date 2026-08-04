"""
List available Gemini models for the API key.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

try:
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    print("Available models:")
    for model in client.models.list():
        print(f"  - {model.name}")
except Exception as e:
    print(f"Error: {e}")
