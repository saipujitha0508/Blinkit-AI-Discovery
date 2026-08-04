# Phase 9 — Build Dashboard (beginner guide)

## Goal

Create an interactive Streamlit dashboard to visualize the analyzed reviews, sentiment, themes, and business insights.

Think of Phase 8 as having all the analysis done.  
Phase 9 is creating a beautiful website to show it all to stakeholders.

## What the dashboard does

The dashboard provides:
- **Overview page** — Key metrics and summary statistics
- **Sentiment analysis page** — Visual breakdown of positive/negative/neutral reviews
- **Themes page** — Most common topics and categories
- **Insights page** — Business recommendations and action items

This makes it easy for Blinkit stakeholders to understand customer feedback at a glance.

## What Phase 9 does

1. Creates a Streamlit web application
2. Loads analyzed data from previous phases
3. Creates interactive visualizations
4. Displays business insights in a user-friendly format
5. Runs locally as a web server

## What each new file does

| File | Job |
|------|-----|
| `app/dashboard.py` | Main Streamlit application |
| `app/pages/overview.py` | Overview page with key metrics |
| `app/pages/sentiment.py` | Sentiment analysis visualizations |
| `app/pages/themes.py` | Theme analysis and breakdown |
| `app/pages/insights.py` | Business insights display |

## How to run

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app/dashboard.py
```

The dashboard will open in your browser at http://localhost:8501

## How to use the dashboard

1. **Overview page** — See total reviews, sentiment distribution, and top themes
2. **Sentiment page** — View sentiment breakdown by source and theme
3. **Themes page** — Explore most common themes and categories
4. **Insights page** — Read business recommendations and priority areas

## Dashboard features

- **Interactive charts** — Click to explore data
- **Real-time updates** — Refresh to see new data
- **Responsive design** — Works on different screen sizes
- **Easy navigation** — Sidebar to switch between pages

## Certification talking point

**"How the workflow presents insights"**  
Analyzed data → Streamlit dashboard → Interactive visualizations → Stakeholder-friendly presentation.

## If something fails

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| Streamlit not found | Package not installed | Run `pip install streamlit` |
| No data found | Previous phases not run | Run Phases 4-8 first |
| Port already in use | Another Streamlit app running | Close other app or use different port |
| Charts not displaying | Data format issues | Check data files in data/analyzed/ |

## Stop point

Phase 9 ends when the dashboard runs successfully and displays data.  
Do **not** start deployment until you confirm Phase 9 works locally.
