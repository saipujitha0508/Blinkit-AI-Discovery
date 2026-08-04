# Phase 7 — Generate Themes (beginner guide)

## Goal

Use Gemini AI to extract main themes and topics from the analyzed reviews.

Think of Phase 6 as knowing if customers are happy or sad.  
Phase 7 is understanding **what** they're talking about (delivery, app issues, product quality, etc.).

## What theme extraction does

Theme extraction identifies:
- **Main topics** — What customers are discussing (delivery, pricing, app performance)
- **Categories** — Grouping similar feedback together
- **Keywords** — Important words that appear frequently

This helps Blinkit understand the key areas that matter most to customers.

## What Phase 7 does

1. Loads analyzed reviews from Phase 6
2. Sends each review to Gemini for theme extraction
3. Gets back: main themes, categories, and relevant keywords
4. Saves results to `data/analyzed/` (augmenting Phase 6 data)

## What each new file does

| File | Job |
|------|-----|
| `src/analysis/theme_extractor.py` | Handles theme extraction with Gemini |
| `scripts/generate_themes.py` | Main script to extract themes from analyzed reviews |

## How to run

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\generate_themes.py
```

## How to check it worked

1. Open `data/analyzed/` in Cursor's left sidebar
2. You should see:
   - `reviews_with_themes.json` — Reviews with theme analysis
   - `themes_summary.json` — Stats on theme distribution
3. Open `themes_summary.json` to see:
   - `total_analyzed` — How many reviews had themes extracted
   - `top_themes` — Most common themes across all reviews
   - `theme_distribution` — Count of each theme

## Understanding the output

Each analyzed review will have new fields:
- `themes` — List of main themes (e.g., ["delivery", "app performance"])
- `theme_categories` — Broader categories (e.g., ["service", "technical"])
- `theme_keywords` — Important keywords from the review

## Processing time considerations

- Theme extraction requires AI API calls (similar to Phase 6)
- Rate limits apply (we handle this with delays)
- For 6,690 reviews, this may take 30-60 minutes
- Progress is printed so you can see it working

## Certification talking point

**"How the workflow extracts themes"**  
Analyzed reviews → Gemini theme extraction → Structured theme data → Ready for insights generation and dashboard.

## If something fails

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| Quota exceeded | Too many API requests | Wait for quota reset (usually daily) |
| API key invalid | Key expired or wrong | Check your .env file |
| No analyzed data | Phase 6 not run | Run `python scripts\analyze_reviews.py` first |
| Network error | Internet connection | Check connection and retry |

## Optional: Extract themes from a sample first

To test before processing all reviews, you can modify the script to extract themes from just 10-20 reviews first.

## Stop point

Phase 7 ends when you have theme extraction results in `data/analyzed/`.  
Do **not** start insights generation until you confirm Phase 7.
