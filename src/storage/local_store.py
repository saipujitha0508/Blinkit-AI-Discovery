"""
Storage helpers — the project's filing cabinet.

Folders:
  data/raw/       → original downloads (never edit these)
  data/store/     → one merged master dataset (Phase 3)
  data/cleaned/   → tidy text (Phase 4)
  data/analyzed/  → AI results (Phase 6+)
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
STORE_DIR = PROJECT_ROOT / "data" / "store"
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
ANALYZED_DIR = PROJECT_ROOT / "data" / "analyzed"

MASTER_JSON = STORE_DIR / "reviews_master.json"
MASTER_CSV = STORE_DIR / "reviews_master.csv"
STORE_SUMMARY = STORE_DIR / "store_summary.json"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_json(data: Any, path: Path) -> Path:
    _ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_raw_batch(
    reviews: list[dict[str, Any]],
    source_label: str,
) -> Path:
    """Save a batch of raw reviews with a timestamped filename."""
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    safe_label = source_label.replace(" ", "_").lower()
    path = RAW_DIR / f"{safe_label}_{stamp}.json"

    payload = {
        "source_label": source_label,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "count": len(reviews),
        "reviews": reviews,
    }
    return save_json(payload, path)


def list_raw_files() -> list[Path]:
    """Return all raw JSON batch files, newest first."""
    return sorted(RAW_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def load_all_raw_reviews() -> list[dict[str, Any]]:
    """
    Read every file in data/raw/ and return one big list.

    Each review gets an extra field `_raw_file` so we know where it came from.
    """
    reviews: list[dict[str, Any]] = []
    for path in list_raw_files():
        payload = load_json(path)
        for review in payload.get("reviews", []):
            item = dict(review)
            item["_raw_file"] = path.name
            item["_batch_source_label"] = payload.get("source_label")
            reviews.append(item)
    return reviews


def save_master_store(
    reviews: list[dict[str, Any]],
    summary: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """
    Save the merged master dataset as JSON + CSV.

    JSON  → best for the app / AI later
    CSV   → easy to open in Excel / Google Sheets
    """
    _ensure_dir(STORE_DIR)

    payload = {
        "stored_at": datetime.now(timezone.utc).isoformat(),
        "count": len(reviews),
        "reviews": reviews,
    }
    save_json(payload, MASTER_JSON)

    # Flatten for CSV (Excel-friendly)
    fieldnames = [
        "id",
        "source",
        "text",
        "rating",
        "date",
        "author",
        "url",
        "language",
        "collected_at",
    ]
    with MASTER_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for review in reviews:
            row = {key: review.get(key) for key in fieldnames}
            # Keep CSV cells single-line
            if isinstance(row.get("text"), str):
                row["text"] = row["text"].replace("\r", " ").replace("\n", " ").strip()
            writer.writerow(row)

    summary_payload = summary or {"count": len(reviews)}
    summary_payload["stored_at"] = payload["stored_at"]
    summary_payload["master_json"] = str(MASTER_JSON.relative_to(PROJECT_ROOT))
    summary_payload["master_csv"] = str(MASTER_CSV.relative_to(PROJECT_ROOT))
    save_json(summary_payload, STORE_SUMMARY)

    return {
        "json": MASTER_JSON,
        "csv": MASTER_CSV,
        "summary": STORE_SUMMARY,
    }


def load_master_reviews() -> list[dict[str, Any]]:
    """Load reviews from the Phase 3 master JSON file."""
    if not MASTER_JSON.exists():
        return []
    payload = load_json(MASTER_JSON)
    return payload.get("reviews", [])
