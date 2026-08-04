# Phase 6 — Analyze Reviews (beginner guide)

## Goal

Use Gemini AI to analyze the cleaned reviews and extract sentiment (positive/negative/neutral).

Think of Phase 5 as turning on the stove.  
Phase 6 is cooking the food (analyzing what customers are saying).

## What sentiment analysis does

Sentiment analysis tells us:
- **Positive** — Happy customers, good experiences
- **Negative** — Unhappy customers, problems, complaints  
- **Neutral** — Factual statements, mixed feelings

This helps Blinkit understand what customers like and what needs improvement.

## What Phase 6 does

1. Loads cleaned reviews from Phase 4
2. Sends each review to Gemini for sentiment analysis
3. Gets back: sentiment label, confidence score, and reasoning
4. Saves results to `data/analyzed/`

## What each new file does

| File | Job |
|------|-----|
| `src/analysis/sentiment_analyzer.py` | Handles sentiment analysis with Gemini |
| `scripts/analyze_reviews.py` | Main script to analyze all cleaned reviews |

## How to run

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\analyze_reviews.py
```

## How to check it worked

1. Open `data/analyzed/` in Cursor's left sidebar
2. You should see:
   - `reviews_analyzed.json` — Reviews with sentiment analysis
   - `analysis_summary.json` — Stats on sentiment distribution
3. Open `analysis_summary.json` to see:
   - `total_analyzed` — How many reviews were analyzed
   - `sentiment_distribution` — Count of positive/negative/neutral
   - `average_confidence` — How confident AI was overall

## Understanding the output

Each analyzed review will have new fields:
- `sentiment` — "positive", "negative", or "neutral"
- `sentiment_confidence` — Number between 0 and 1 (higher = more confident)
- `sentiment_reasoning` — Brief explanation from AI

## Processing time considerations

- Analyzing reviews with AI takes time (API calls)
- Free tier has rate limits (we handle this with delays)
- For 6,690 reviews, this may take 30-60 minutes
- Progress is printed so you can see it working

## Certification talking point

**"How the workflow analyzes data"**  
Clean reviews → Gemini sentiment analysis → Structured sentiment data → Ready for theme extraction and insights.

## If something fails

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| Quota exceeded | Too many API requests | Wait for quota reset (usually daily) |
| API key invalid | Key expired or wrong | Check your .env file |
| No cleaned data | Phase 4 not run | Run `python scripts\clean_reviews.py` first |
| Network error | Internet connection | Check connection and retry |

## Optional: Analyze a sample first

To test before analyzing all reviews, you can modify the script to analyze just 10-20 reviews first to make sure everything works.

## Stop point

Phase 6 ends when you have sentiment analysis results in `data/analyzed/`.  
Do **not** start theme generation until you confirm Phase 6.
