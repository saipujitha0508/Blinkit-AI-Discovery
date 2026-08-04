# Phase 2 — Live Data Collection (beginner guide)

## Goal

Automatically collect **live** customer feedback about Blinkit and save it into `data/raw/`.

## Easiest approach (what we use now)

| Source | Method | Need an account? |
|--------|--------|------------------|
| Google Play Store | `google-play-scraper` Python library | No |
| Apple App Store | Apple public RSS feed | No |
| Reddit discussions | Reddit public search JSON | No (may be blocked on some networks) |
| Apify scrapers | Optional cloud scrapers | Yes (later / optional) |

**Why not Apify first?** Apify is powerful, but needs an account, token, and credits.  
For learning, free live collectors are simpler and still count as live data.

**Reddit note:** Some networks (including many cloud/office networks) get `403 Blocked` from Reddit.  
If that happens on your PC too, we still continue with Play Store + App Store, and can add Reddit via Apify later.

## What each new file does

| File | Job |
|------|-----|
| `src/collectors/schema.py` | Shared "form" every review must fill |
| `src/collectors/play_store.py` | Downloads Blinkit Play Store reviews |
| `src/collectors/app_store.py` | Downloads Blinkit iOS App Store reviews |
| `src/collectors/reddit.py` | Downloads Reddit posts about Blinkit |
| `src/collectors/apify_play_store.py` | Optional Apify path (needs token) |
| `src/storage/local_store.py` | Saves JSON files into `data/raw/` |
| `scripts/collect_reviews.py` | One command that runs collection |

## Setup steps (do this on your computer)

### Step A — Open a terminal in Cursor

1. In Cursor, click **Terminal → New Terminal**.
2. Make sure the path shows your project folder:
   `C:\Users\hp\Documents\Blinkit-AI-Discovery`

### Step B — Create a virtual environment (a clean Python bubble)

Run:

```powershell
python -m venv .venv
```

This creates a folder named `.venv`. It keeps project packages separate from the rest of your PC.

### Step C — Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If Windows blocks that, run this once, then try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

When it works, you should see `(.venv)` at the start of your terminal line.

### Step D — Install packages

```powershell
pip install -r requirements.txt
```

### Step E — Collect live data

```powershell
python scripts\collect_reviews.py
```

### Step F — Check the result

1. Open the `data/raw/` folder in Cursor's left sidebar.
2. You should see files like:
   - `google_play_YYYY-MM-DD_HHMMSS.json`
   - `app_store_YYYY-MM-DD_HHMMSS.json`
   - `reddit_YYYY-MM-DD_HHMMSS.json` (only if Reddit allows your network)
3. Open one file. You should see review text, source, date, rating (for Play Store).

## Optional: Apify later

1. Create an account at https://apify.com
2. Copy your API token
3. Copy `.env.example` to `.env` and paste the token as `APIFY_API_TOKEN=...`
4. We can wire the Apify collector into the main script in a later phase

## How this demonstrates certification needs

1. **How the workflow gathers data** → `scripts/collect_reviews.py` calls Play Store + Reddit collectors
2. Raw files land in `data/raw/` untouched (cleaning comes in Phase 4)

## If something fails

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| `python` not found | Python not on PATH | Reinstall Python and tick "Add to PATH" |
| Activate.ps1 error | PowerShell policy | Run the ExecutionPolicy command above |
| Play Store error | Network / library issue | Retry; check internet |
| Reddit error / 429 | Too many requests | Wait 1–2 minutes, run again |
| 0 items collected | Both sources failed | Read the printed error text |

## Stop point

Phase 2 ends when you have JSON files in `data/raw/`.  
Do **not** start cleaning or Gemini until you confirm Phase 2.
