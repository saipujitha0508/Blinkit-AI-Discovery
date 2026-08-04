# Phase 2B — Collect more reviews with Apify (beginner guide)

## What is Apify?

Apify is an online service that runs scrapers for you in the cloud.

You do **not** need to build a scraper yourself.
You only need:
1. A free Apify account
2. An API token (like a password for apps)
3. Our script, which asks Apify to collect Blinkit reviews

## Why use Apify now?

- Get **more** Google Play reviews (e.g. 300 instead of 80)
- Collect **Reddit** even when direct Reddit access is blocked
- Good for your certification: shows a real AI-native data workflow

## Step-by-step setup

### Step 1 — Create an Apify account

1. Open this link in your browser: https://console.apify.com/sign-up
2. Sign up with Google/GitHub/email (free plan is fine)

### Step 2 — Copy your API token

1. Open: https://console.apify.com/settings/integrations
2. Find **API tokens**
3. Click **Create new token** (or copy an existing one)
4. Copy the token text (it looks like a long random string)

### Step 3 — Put the token into this project

1. In Cursor, look at the left sidebar.
2. Open the file `.env.example`
3. Make a copy:
   - Right-click `.env.example` → **Copy**
   - Right-click empty space in the file list → **Paste**
   - Rename the copy to exactly: `.env`
4. Open `.env`
5. Change this line:

```env
APIFY_API_TOKEN=your_apify_token_here
```

to:

```env
APIFY_API_TOKEN=paste_your_real_token_here
```

6. Save the file (`Ctrl + S`)

Important: never share your `.env` file or commit it to Git.

### Step 4 — Install Apify package (one time)

In Cursor terminal:

```powershell
.\.venv\Scripts\Activate.ps1
pip install apify-client python-dotenv
```

### Step 5 — Run Apify collection

```powershell
python scripts\collect_with_apify.py
```

This may take **1–5 minutes** because Apify runs in the cloud.

### Step 6 — Check results

Open `data/raw/` and look for new files like:
- `google_play_apify_....json`
- `reddit_apify_....json`

## Free plan tips

- Free Apify credits are limited each month
- Start with ~200–300 Play Store reviews (our script default is 300)
- If you run out of credits, wait for monthly reset or use our free collector again

## If something fails

| Message | Meaning | Fix |
|---------|---------|-----|
| `APIFY_API_TOKEN is missing` | `.env` not set up | Follow Step 3 |
| Actor failed / 401 | Bad token | Copy token again |
| Actor failed / payment | Out of credits | Lower max reviews or wait |
| Reddit empty | Actor filters / no matches | Play Store data still counts |

## Files added for Apify

| File | Purpose |
|------|---------|
| `src/collectors/apify_collectors.py` | Talks to Apify actors |
| `scripts/collect_with_apify.py` | One-click collection command |
| `docs/phase-2b-apify-setup.md` | This guide |
