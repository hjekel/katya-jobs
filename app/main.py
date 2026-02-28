"""FastAPI application — Katya's JobFinder."""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.database import (
    get_jobs, get_job_by_id, get_job_count, get_stats, get_filter_counts,
    hide_job, init_db, mark_all_seen,
    save_application, update_application, remove_application, get_applications,
)
from app.scorer import generate_fit_analysis, generate_cover_letter, get_commute_info, compute_posting_age
from app.scrapers import scrape_all

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

_scrape_lock = asyncio.Lock()
_last_scrape: Optional[str] = None
_scraping = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized")
    yield


app = FastAPI(title="Katya's JobFinder", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def index():
    return FileResponse("app/static/index.html")


@app.get("/applications")
async def applications_page():
    return FileResponse("app/static/applications.html")


# ---- Jobs API ----

@app.get("/api/jobs")
async def api_jobs(
    source: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    only_new: bool = Query(False),
    min_salary: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    posting_type: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    sort: str = Query("newest"),
    limit: int = Query(200, le=500),
    offset: int = Query(0, ge=0),
):
    jobs = get_jobs(
        source=source, search=search, only_new=only_new,
        min_salary=min_salary, category=category, city=city,
        posting_type=posting_type, company=company, sort=sort,
        limit=limit, offset=offset,
    )
    total = get_job_count(
        source=source, search=search, only_new=only_new,
        min_salary=min_salary, category=category, city=city,
        posting_type=posting_type, company=company,
    )
    # Enrich each job with posting age
    for job in jobs:
        age = compute_posting_age(job.get("date_posted"), job.get("date_scraped"))
        job["posting_age_text"] = age["text"]
        job["posting_age_color"] = age["color"]
    return {"jobs": jobs, "total": total}


@app.get("/api/filters")
async def api_filters():
    """Return counts for all filter panels."""
    return get_filter_counts()


@app.get("/api/stats")
async def api_stats():
    stats = get_stats()
    stats["last_scrape"] = _last_scrape
    stats["scraping"] = _scraping
    return stats


@app.post("/api/scrape")
async def api_scrape():
    global _last_scrape, _scraping

    if _scraping:
        return JSONResponse({"status": "already_running"}, status_code=409)

    async def run_scrape():
        global _last_scrape, _scraping
        _scraping = True
        try:
            results = await scrape_all()
            _last_scrape = datetime.now(timezone.utc).isoformat()
            return results
        finally:
            _scraping = False

    if _scrape_lock.locked():
        return JSONResponse({"status": "already_running"}, status_code=409)

    async with _scrape_lock:
        results = await run_scrape()

    return {"status": "completed", "results": results, "scraped_at": _last_scrape}


@app.post("/api/jobs/{job_id}/hide")
async def api_hide_job(job_id: int):
    hide_job(job_id)
    return {"status": "ok"}


@app.post("/api/jobs/mark-seen")
async def api_mark_seen():
    mark_all_seen()
    return {"status": "ok"}


@app.get("/api/fit")
async def api_fit(title: str = Query(""), snippet: str = Query(""), location: str = Query("")):
    return generate_fit_analysis(title, snippet, location)


@app.get("/api/commute")
async def api_commute(location: str = Query("")):
    return get_commute_info(location)


# ---- Cover letter ----

@app.get("/api/cover-letter")
async def api_cover_letter(job_id: int = Query(...)):
    job = get_job_by_id(job_id)
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    letter = generate_cover_letter(
        title=job["title"],
        company=job.get("company", ""),
        location=job.get("location", ""),
        snippet=job.get("snippet", ""),
    )
    return {"letter": letter}


# ---- Application tracker API ----

@app.get("/api/applications")
async def api_get_applications():
    return {"applications": get_applications()}


@app.post("/api/applications/{job_id}/save")
async def api_save_application(job_id: int):
    created = save_application(job_id)
    return {"status": "created" if created else "exists"}


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    reminder_date: Optional[str] = None
    date_applied: Optional[str] = None


@app.put("/api/applications/{job_id}")
async def api_update_application(job_id: int, body: ApplicationUpdate):
    update_application(
        job_id=job_id,
        status=body.status,
        notes=body.notes,
        reminder_date=body.reminder_date,
        date_applied=body.date_applied,
    )
    return {"status": "ok"}


@app.delete("/api/applications/{job_id}")
async def api_remove_application(job_id: int):
    remove_application(job_id)
    return {"status": "ok"}
