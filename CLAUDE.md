# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Katya's JobFinder — job finder web app for English-speaking roles near Haarlem, Netherlands. Python/FastAPI backend scrapes 6 job boards (Indeed NL, IamExpat, Undutchables, LinkedIn, Adams, Welcome to NL), filters out Dutch-only/driving/senior roles, scores by relevance, stores in SQLite. Dashboard frontend with filter panels (category, location, company, source type).

## Build & Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload          # dev server at localhost:8000
```

Deploy: `render.yaml` configured for Render.com free tier. Also has `Procfile` for Railway/Heroku.

## Architecture

- **app/main.py** — FastAPI app with lifespan (DB init). Serves static frontend at `/` and JSON API at `/api/*`. Scraping triggered via `POST /api/scrape` with async lock to prevent concurrent runs. Filter counts endpoint at `GET /api/filters`.
- **app/scrapers.py** — Async scrapers using httpx + BeautifulSoup. Each scraper function returns `list[RawJob]`. `scrape_all()` orchestrates all six and upserts into DB with category/city/posting_type classification.
- **app/scorer.py** — `should_exclude()` checks exclusion keywords, `compute_score()` returns 0-150 score. Also: `classify_category()`, `extract_city()`, `detect_posting_type()`, `compute_posting_age()`.
- **app/config.py** — All tunable constants: search queries, target cities, exclusion keywords, role scoring weights, scraper settings.
- **app/database.py** — SQLite via stdlib sqlite3. Context manager pattern with WAL mode. Jobs keyed by `external_id` (MD5 of source+URL) for dedup. Supports filtering by category, city, company, posting_type, source.
- **app/static/** — Dashboard frontend (vanilla HTML/CSS/JS). Filter panels for category/location/company/source. Application tracker Kanban board.

## Key Patterns

- Scraper results go through `should_exclude()` before storage — exclusion list is in config
- Jobs are deduped by `external_id` (hash of source + URL) at both scraper and DB level
- Scoring and classification (category, city, posting type) happen at scrape time and are stored in DB
- Frontend fetches from `/api/jobs` with query params for category, city, company, posting_type, source, sort
- Filter panel counts fetched from `GET /api/filters` endpoint
- Posting age computed on-the-fly from date_posted when serving `/api/jobs`
