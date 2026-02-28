# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Job finder web app for English-speaking roles near Haarlem, Netherlands. Python/FastAPI backend scrapes 4 job boards (Indeed NL, IamExpat, Undutchables, LinkedIn), filters out Dutch-only/driving/senior roles, scores by relevance, stores in SQLite.

## Build & Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload          # dev server at localhost:8000
```

Deploy: `render.yaml` configured for Render.com free tier. Also has `Procfile` for Railway/Heroku.

## Architecture

- **app/main.py** — FastAPI app with lifespan (DB init). Serves static frontend at `/` and JSON API at `/api/*`. Scraping triggered via `POST /api/scrape` with async lock to prevent concurrent runs.
- **app/scrapers.py** — Async scrapers using httpx + BeautifulSoup. Each scraper function returns `list[RawJob]`. `scrape_all()` orchestrates all four and upserts into DB.
- **app/scorer.py** — `should_exclude()` checks exclusion keywords, `compute_score()` returns 0-150 score based on role match (finance=highest), English signals, and city proximity bonuses.
- **app/config.py** — All tunable constants: search queries, target cities, exclusion keywords, role scoring weights, scraper settings.
- **app/database.py** — SQLite via stdlib sqlite3. Context manager pattern with WAL mode. Jobs keyed by `external_id` (MD5 of source+URL) for dedup.
- **app/static/** — Single-page frontend (vanilla HTML/CSS/JS). Calls API, renders job cards, handles search/filter/hide.

## Key Patterns

- Scraper results go through `should_exclude()` before storage — exclusion list is in config
- Jobs are deduped by `external_id` (hash of source + URL) at both scraper and DB level
- Scoring happens at scrape time and is stored in DB, not recomputed on read
- Frontend fetches from `/api/jobs` with query params for source, search text, new-only filter
