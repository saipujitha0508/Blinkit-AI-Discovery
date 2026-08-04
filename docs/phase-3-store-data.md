# Phase 3 — Store Data (beginner guide)

## Goal

Take all the separate download files in `data/raw/` and store them as **one master dataset**.

Think of Phase 2 as buying groceries in many bags.  
Phase 3 is putting everything into one pantry (and throwing away exact duplicates).

## What we store

| File | What it is | Who uses it |
|------|------------|-------------|
| `data/store/reviews_master.json` | Full master list | Our Python / AI code |
| `data/store/reviews_master.csv` | Same data in table form | Excel / Google Sheets |
| `data/store/store_summary.json` | Counts and stats | Quick project summary |

Raw files in `data/raw/` are **not deleted**. They stay as the original backup.

## What Phase 3 does NOT do

- Does not rewrite review sentences
- Does not translate Hindi/English
- Does not run Gemini AI

Those belong to later phases (cleaning + analysis).

## How to run

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\store_reviews.py
```

## How to check it worked

1. Open `data/store/` in Cursor’s left sidebar
2. Open `store_summary.json` — check `unique_rows`
3. Optional: open `reviews_master.csv` in Excel

## Optional: Supabase (cloud database)

Local files are enough. Supabase is optional.

If you want cloud storage later:
1. Create a project at https://supabase.com
2. Add `SUPABASE_URL` and `SUPABASE_KEY` to `.env`
3. Create a `reviews` table (see `src/storage/supabase_store.py` comments)
4. Re-run `python scripts\store_reviews.py`

## Certification talking point

**“How the workflow stores data”**  
Collectors save batches → Phase 3 merges batches → master JSON/CSV becomes the single source of truth for cleaning and AI.
