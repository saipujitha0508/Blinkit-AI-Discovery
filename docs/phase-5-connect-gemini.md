# Phase 5 — Connect Gemini (beginner guide)

## Goal

Connect the project to Google's Gemini AI API so we can analyze reviews with AI.

Think of Phase 4 as preparing ingredients.  
Phase 5 is turning on the stove (AI) so we can cook (analyze).

## What Gemini does

Gemini is Google's AI model that can:
- Understand text in multiple languages (Hindi, English, etc.)
- Analyze sentiment (positive/negative/neutral)
- Extract themes and topics
- Generate insights from customer feedback

## What you need

1. **Google account** - Any Gmail account works
2. **Gemini API key** - Free tier available
3. **.env file** - To store your API key securely

## Step-by-step setup

### Step A — Get a Gemini API key

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API key"
4. Copy the API key (it looks like: `AIzaSy...`)
5. **Important:** Never share this key or commit it to Git

### Step B — Add API key to .env

1. Copy `.env.example` to `.env`:
   ```powershell
   copy .env.example .env
   ```

2. Open `.env` in Cursor
3. Add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

4. Save the file

### Step C — Test the connection

Run the test script:
```powershell
.\.venv\Scripts\Activate.ps1
python scripts\test_gemini.py
```

You should see a successful test message from Gemini.

## What each new file does

| File | Job |
|------|-----|
| `src/analysis/gemini_client.py` | Handles connection to Gemini API |
| `scripts/test_gemini.py` | Simple test to verify connection works |

## How Gemini pricing works

- **Free tier:** 15 requests per minute, enough for this project
- **No credit card needed** for basic usage
- You only pay if you exceed free limits (unlikely for this project)

## What Phase 5 does NOT do

- Does not analyze all reviews yet (that's Phase 6)
- Does not generate themes (that's Phase 7)
- Does not build the dashboard (that's Phase 9)

Phase 5 is just about getting the connection working.

## Certification talking point

**"How the workflow connects to AI"**  
Clean data → Gemini API connection → Ready for sentiment analysis and theme extraction.

## If something fails

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| `GEMINI_API_KEY not found` | .env file missing or key not set | Create .env and add the key |
| `API key invalid` | Wrong key copied | Double-check the key from Google |
| `Quota exceeded` | Too many requests | Wait a few minutes, free tier resets |
| `Import error` | Package not installed | Run `pip install google-generativeai` |

## Stop point

Phase 5 ends when the test script runs successfully and shows a response from Gemini.  
Do **not** start analyzing all reviews until you confirm Phase 5 works.
