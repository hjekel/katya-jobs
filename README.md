# Katya Jobs

Job finder for English-speaking roles near Haarlem, Netherlands. Scrapes multiple job boards, filters out Dutch-only positions, and ranks results by relevance to an accounting/finance + admin profile.

## Job Sources

- **Indeed NL** (nl.indeed.com) — English-language job listings
- **IamExpat** (iamexpat.nl) — Jobs specifically for expats in NL
- **Undutchables** (undutchables.nl) — Non-Dutch-speaking positions
- **LinkedIn** — Public job search results

## Features

- Scrapes 4 job boards with configurable search queries
- Filters out jobs requiring Dutch, driving licence, or senior management
- Scores/ranks jobs by relevance (finance > admin > customer service > retail)
- SQLite storage tracks new vs seen jobs
- Responsive frontend works on mobile
- Hide irrelevant jobs

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run locally

```bash
uvicorn app.main:app --reload
```

Open http://localhost:8000 and click **Scan for Jobs**.

## Deploy to Render

1. Push to GitHub
2. Connect repo at [render.com](https://render.com)
3. Render uses `render.yaml` for config — deploys automatically

## Project Structure

```
app/
  main.py        — FastAPI app and API routes
  scrapers.py    — Job board scrapers (Indeed, IamExpat, Undutchables, LinkedIn)
  scorer.py      — Relevance scoring engine
  database.py    — SQLite operations
  config.py      — Search queries, cities, scoring weights, exclusion rules
  static/
    index.html   — Frontend page
    style.css    — Styles
    app.js       — Frontend logic
```

## Configuration

Edit `app/config.py` to:
- Add/remove search queries (`SEARCH_QUERIES`)
- Adjust target cities (`TARGET_CITIES`)
- Tune scoring weights (`ROLE_SCORES`)
- Modify exclusion keywords (`EXCLUDE_KEYWORDS`)
