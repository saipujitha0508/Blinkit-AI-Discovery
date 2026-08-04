# Phase 8 — Generate Insights (beginner guide)

## Goal

Use Gemini AI to generate actionable business insights from the analyzed reviews with sentiment and themes.

Think of Phase 7 as knowing what customers are talking about.  
Phase 8 is understanding **what Blinkit should do** based on that feedback.

## What insights generation does

Insights generation provides:
- **Actionable recommendations** — Specific steps Blinkit can take
- **Priority areas** — What matters most to customers
- **Trend analysis** — Patterns in customer feedback
- **Business impact** — How changes might affect customer satisfaction

This helps Blinkit make data-driven decisions to improve the customer experience.

## What Phase 8 does

1. Loads reviews with sentiment and themes from Phase 7
2. Aggregates data by sentiment and theme
3. Sends aggregated data to Gemini for insights generation
4. Gets back: recommendations, priorities, and action items
5. Saves results to `data/analyzed/`

## What each new file does

| File | Job |
|------|-----|
| `src/analysis/insights_generator.py` | Handles insights generation with Gemini |
| `scripts/generate_insights.py` | Main script to generate business insights |

## How to run

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\generate_insights.py
```

## How to check it worked

1. Open `data/analyzed/` in Cursor's left sidebar
2. You should see:
   - `business_insights.json` — Generated business insights
   - `insights_summary.json` — Summary of key findings
3. Open `business_insights.json` to see:
   - `key_findings` — Main discoveries from the data
   - `recommendations` — Actionable suggestions
   - `priority_areas` — What to focus on first

## Understanding the output

The insights will include:
- **Key findings** — What the data tells us
- **Recommendations** — Specific actions to take
- **Priority areas** — High-impact focus areas
- **Opportunities** — Areas for improvement
- **Risks** — Potential issues to address

## Processing time considerations

- Insights generation requires fewer API calls than previous phases
- It analyzes aggregated data rather than individual reviews
- Should complete in 1-2 minutes
- No rate limiting issues expected

## Certification talking point

**"How the workflow generates insights"**  
Reviews with sentiment + themes → Aggregated analysis → Gemini insights generation → Actionable business recommendations.

## If something fails

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| No themed data | Phase 7 not run | Run `python scripts\generate_themes.py` first |
| API quota exceeded | Too many requests | Wait for quota reset (usually daily) |
| Empty insights | Data aggregation failed | Check that Phase 6-7 completed successfully |

## Stop point

Phase 8 ends when you have business insights in `data/analyzed/`.  
Do **not** start dashboard building until you confirm Phase 8.
