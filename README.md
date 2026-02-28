# Katya's JobFinder

Job finder for English-speaking roles near Haarlem, Netherlands. Scrapes multiple job boards, filters out Dutch-only positions, and ranks results by relevance to an accounting/finance + admin profile.

## Job Sources

- **Indeed NL** (nl.indeed.com) — English-language job listings
- **IamExpat** (iamexpat.nl) — Jobs specifically for expats in NL
- **Undutchables** (undutchables.nl) — Non-Dutch-speaking positions
- **LinkedIn** — Public job search results
- **Adams Recruitment** — Multilingual recruitment agency
- **Welcome to NL** — Jobs for internationals

## Features

- Scrapes 6 job boards with configurable search queries
- Dashboard with filter panels: Category, Location, Company, Source
- Auto-classifies jobs by category, city, and posting type (direct/recruiter/job board)
- Posting age indicators with colour-coded freshness dots
- Filters out jobs requiring Dutch, driving licence, or senior management
- Scores/ranks jobs by relevance (finance > admin > customer service > retail)
- Application tracker with Kanban board, notes, reminders, and cover letter generator
- SQLite storage tracks new vs seen jobs
- Responsive design (desktop, tablet, mobile)
- Hide irrelevant jobs, save jobs to tracker

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
  main.py          — FastAPI app and API routes
  scrapers.py      — Job board scrapers (Indeed, IamExpat, Undutchables, LinkedIn, Adams, Welcome to NL)
  scorer.py        — Relevance scoring, category classification, recruiter detection, posting age
  database.py      — SQLite operations with filter support
  config.py        — Search queries, cities, scoring weights, exclusion rules
  static/
    index.html     — Dashboard frontend
    applications.html — Application tracker (Kanban board)
    style.css      — Styles (Ukrainian blue/yellow theme)
    app.js         — Dashboard logic with filter panels
    applications.js — Kanban board logic
    favicon.svg    — Ukrainian Tryzub icon
```

## Configuration

Edit `app/config.py` to:
- Add/remove search queries (`SEARCH_QUERIES`)
- Adjust target cities (`TARGET_CITIES`)
- Tune scoring weights (`ROLE_SCORES`)
- Modify exclusion keywords (`EXCLUDE_KEYWORDS`)
