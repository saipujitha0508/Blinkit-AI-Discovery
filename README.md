# Blinkit AI Discovery Engine

An AI-powered system that collects customer reviews, cleans them, analyses them with Gemini, and shows product insights on a dashboard.

**Business goal:** Help more Blinkit customers try at least one new product category each month.

---

## Who this is for

This project is built step by step for beginners. You do not need prior coding experience to follow along.

## Tech stack (simple)

| Tool | Purpose |
|------|---------|
| Python | Main programming language |
| Streamlit | Dashboard (website UI) |
| Apify | Collect live reviews |
| Gemini API | AI analysis |
| Supabase | Cloud database (later phases) |
| Render | Deploy online (final phase) |

## Project folders

```
Blinkit-AI-Discovery/
├── app/                 # Dashboard pages (Streamlit)
├── src/
│   ├── collectors/      # Fetch reviews from Play Store, Reddit, etc.
│   ├── cleaning/        # Clean text, remove duplicates, language
│   ├── analysis/        # Gemini sentiment, themes, insights
│   ├── validation/      # Check AI quality vs human labels
│   └── storage/         # Save and load data
├── data/
│   ├── raw/             # Original reviews (untouched)
│   ├── cleaned/         # After cleaning
│   └── analyzed/        # After AI analysis
├── notebooks/           # Optional experiments
├── tests/               # Automated checks
├── scripts/             # Helper commands
├── docs/                # Written guides
├── .env.example         # Sample secret keys (never put real keys here)
├── .gitignore           # Files Git should ignore
├── requirements.txt     # Python packages we need
└── README.md            # This file
```

## Current progress

- [x] **Phase 1** — Project setup and folder structure
- [x] **Phase 2** — Live data collection (Play Store + App Store + Apify)
- [x] **Phase 3** — Store data (master JSON + CSV)
- [ ] Phase 4 — Clean data
- [ ] Phase 5 — Connect Gemini
- [ ] Phase 6 — Analyse reviews
- [ ] Phase 7 — Generate themes
- [ ] Phase 8 — Generate insights
- [ ] Phase 9 — Build dashboard
- [ ] Phase 10 — Deploy on Render

## Run live collection (Phase 2)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\collect_reviews.py
```

Then open files inside `data/raw/`.

## Store master dataset (Phase 3)

```powershell
python scripts\store_reviews.py
```

Then open `data/store/reviews_master.csv` or `reviews_master.json`.

## How to open this project in Cursor

1. Open **Cursor**.
2. Click **File → Open Folder**.
3. Choose `C:\Users\hp\Documents\Blinkit-AI-Discovery`.
4. You should see the folders listed above in the left sidebar (Explorer).

## Next step

After you confirm Phase 1 looks good, we will start **Phase 2: live data collection**.
