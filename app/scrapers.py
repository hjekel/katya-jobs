"""Job scrapers for Indeed NL, IamExpat, Undutchables, LinkedIn, Adams, Welcome to NL, Remote OK, We Work Remotely."""

import asyncio
import hashlib
import json
import logging
import random
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote_plus, urljoin

import httpx
from bs4 import BeautifulSoup

from app.config import (
    REQUEST_TIMEOUT,
    USER_AGENTS,
    REMOTE_RELEVANT_TAGS,
)
from app.scorer import (
    compute_score, should_exclude, extract_salary,
    classify_category, extract_city, detect_posting_type,
    detect_dutch_level, detect_work_model,
)

logger = logging.getLogger(__name__)


def _random_headers(referer: str = "") -> dict:
    """Return request headers with a random user agent."""
    ua = random.choice(USER_AGENTS)
    h = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if referer:
        h["Referer"] = referer
    return h


async def _delay():
    """Small random delay between requests."""
    await asyncio.sleep(random.uniform(0.5, 1.5))


@dataclass
class RawJob:
    title: str
    company: Optional[str]
    location: Optional[str]
    snippet: Optional[str]
    url: str
    source: str
    date_posted: Optional[str] = None
    work_model: str = ""

    @property
    def external_id(self) -> str:
        raw = f"{self.source}:{self.url}"
        return hashlib.md5(raw.encode()).hexdigest()

    @property
    def dutch_level(self) -> str:
        return detect_dutch_level(self.title, self.snippet or "")

    @property
    def score(self) -> int:
        return compute_score(
            self.title,
            self.company or "",
            self.location or "",
            self.snippet or "",
            dutch_level=self.dutch_level,
        )

    @property
    def salary(self) -> dict | None:
        return extract_salary(f"{self.title} {self.snippet or ''}")

    @property
    def detected_work_model(self) -> str:
        if self.work_model:
            return self.work_model
        return detect_work_model(self.title, self.snippet or "", self.location or "", self.source)


def _clean(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    return re.sub(r"\s+", " ", text).strip()


def _passes_filter(title: str, snippet: str = "") -> bool:
    """Check that a job passes both keyword exclusion and Dutch language detection."""
    return not should_exclude(title, snippet)


# ---------------------------------------------------------------------------
# Indeed NL (RSS feed — direct scraping returns 403)
# ---------------------------------------------------------------------------

async def scrape_indeed(client: httpx.AsyncClient, extra_queries: list[str] | None = None) -> list[RawJob]:
    """Scrape Indeed Netherlands — currently blocked (403/404). Returns 0 gracefully."""
    # Indeed blocks both RSS and direct scraping with 403/404.
    # Keeping the function as a placeholder for future proxy/API integration.
    logger.info("Indeed: skipped (blocked by anti-bot protection)")
    return []


# ---------------------------------------------------------------------------
# IamExpat (Next.js — extract __NEXT_DATA__ JSON)
# ---------------------------------------------------------------------------

async def scrape_iamexpat(client: httpx.AsyncClient) -> list[RawJob]:
    """Scrape IamExpat jobs — Tailwind card layout with a[href*='/career/jobs-netherlands/']."""
    jobs: list[RawJob] = []
    search_terms = [
        "accountant", "bookkeeper", "finance", "administration",
        "back office", "customer service", "data entry", "office",
    ]

    for query in search_terms:
        url = (
            f"https://www.iamexpat.nl/career/jobs-netherlands"
            f"?search={quote_plus(query)}"
            f"&location=Haarlem"
            f"&distance=25"
        )
        try:
            await _delay()
            resp = await client.get(url, headers=_random_headers("https://www.iamexpat.nl/"), timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                logger.warning("IamExpat returned %s for %s", resp.status_code, query)
                continue

            soup = BeautifulSoup(resp.text, "lxml")

            # Cards are <a> tags linking to individual job pages
            cards = soup.select("a[href*='/career/jobs-netherlands/']")
            for card in cards:
                href = card.get("href", "")
                if not href or href.rstrip("/") == "/career/jobs-netherlands":
                    continue
                if not href.startswith("http"):
                    href = urljoin("https://www.iamexpat.nl", href)

                # Title is in span.title-7 inside the card
                title_el = card.select_one("span.title-7")
                if not title_el:
                    # Fallback: try any heading or bold text
                    title_el = card.select_one("h2, h3, h4, strong, span[class*='title']")
                if not title_el:
                    continue
                title = _clean(title_el.get_text())
                if not title or len(title) < 5:
                    continue

                # Location/date in div.JobBoardItemCard_jobInfoElement__*
                info_els = card.select("div[class*='jobInfoElement'], div[class*='JobBoardItemCard_jobInfo']")
                loc = None
                date_str = None
                for i, el in enumerate(info_els):
                    text = _clean(el.get_text())
                    if i == 0 and text:
                        loc = text
                    elif i == 1 and text:
                        date_str = text

                # Company from div.body-small or similar
                company_el = card.select_one("div.body-small, span[class*='company'], div[class*='company']")
                company = _clean(company_el.get_text()) if company_el else None

                if not _passes_filter(title, ""):
                    continue

                jobs.append(RawJob(
                    title=title, company=company, location=loc,
                    snippet=None, url=href, source="iamexpat",
                    date_posted=date_str,
                ))

        except Exception as e:
            logger.error("IamExpat scrape error for '%s': %s", query, e)

    return _dedupe(jobs)


# ---------------------------------------------------------------------------
# Undutchables (corrected URL: /vacancies)
# ---------------------------------------------------------------------------

async def scrape_undutchables(client: httpx.AsyncClient) -> list[RawJob]:
    """Scrape Undutchables — cards are a.vacancy-item with h4 title + div.location."""
    jobs: list[RawJob] = []
    search_terms = [
        "accountant", "bookkeeper", "finance", "administration",
        "back office", "customer service", "data entry", "office",
    ]

    for query in search_terms:
        url = (
            f"https://undutchables.nl/vacancies"
            f"?search={quote_plus(query)}"
        )
        try:
            await _delay()
            resp = await client.get(url, headers=_random_headers("https://undutchables.nl/"), timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                logger.warning("Undutchables returned %s for %s", resp.status_code, query)
                continue
            soup = BeautifulSoup(resp.text, "lxml")

            # Primary: a.vacancy-item cards
            cards = soup.select("a.vacancy-item")
            # Fallback: any link to /vacancies/<slug>
            if not cards:
                cards = [
                    a for a in soup.select("a[href*='/vacancies/']")
                    if a.get("href", "").rstrip("/") != "/vacancies"
                    and len(a.get_text(strip=True)) > 5
                ]

            for card in cards:
                href = card.get("href", "")
                if not href or href.rstrip("/") == "/vacancies":
                    continue
                if not href.startswith("http"):
                    href = urljoin("https://undutchables.nl", href)

                # Title in <h4> inside the card
                title_el = card.select_one("h4")
                if not title_el:
                    title_el = card.select_one("h3, h2, strong")
                if title_el:
                    title = _clean(title_el.get_text())
                else:
                    # Last resort: full card text minus location
                    title = _clean(card.get_text())
                if not title or len(title) < 5:
                    continue

                # Location in div.location
                loc_el = card.select_one("div.location, span.location, .vacancy-location")
                loc = _clean(loc_el.get_text()) if loc_el else None

                # Remove location text from title if it was concatenated
                if loc and title.endswith(loc):
                    title = title[: -len(loc)].strip()

                company = None  # Undutchables doesn't show company on list page

                if not _passes_filter(title, ""):
                    continue

                jobs.append(RawJob(
                    title=title, company=company, location=loc,
                    snippet=None, url=href, source="undutchables",
                ))

        except Exception as e:
            logger.error("Undutchables scrape error for '%s': %s", query, e)

    return _dedupe(jobs)


# ---------------------------------------------------------------------------
# LinkedIn (public search URL scraping)
# ---------------------------------------------------------------------------

async def scrape_linkedin(client: httpx.AsyncClient) -> list[RawJob]:
    """Scrape LinkedIn public job search pages."""
    jobs: list[RawJob] = []
    queries_to_use = [
        "accountant english",
        "bookkeeper",
        "finance administrator",
        "office administrator english",
        "back office english",
        "customer service english",
    ]

    for query in queries_to_use:
        url = (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={quote_plus(query)}"
            f"&location={quote_plus('Haarlem, North Holland, Netherlands')}"
            f"&distance=25"
            f"&f_TPR=r604800"  # past week
        )
        try:
            await _delay()
            resp = await client.get(url, headers=_random_headers("https://www.linkedin.com/"), timeout=REQUEST_TIMEOUT, follow_redirects=True)
            if resp.status_code != 200:
                logger.warning("LinkedIn returned %s for %s", resp.status_code, query)
                continue
            soup = BeautifulSoup(resp.text, "lxml")

            cards = soup.select("div.base-card, li.result-card, div.job-search-card")
            for card in cards:
                title_el = card.select_one("h3.base-search-card__title, h3.result-card__title")
                if not title_el:
                    continue
                title = _clean(title_el.get_text())
                if not title:
                    continue

                link_el = card.select_one("a.base-card__full-link, a.result-card__full-card-link")
                href = link_el.get("href", "") if link_el else ""
                if "?" in href:
                    href = href.split("?")[0]

                company_el = card.select_one("h4.base-search-card__subtitle, h4.result-card__subtitle")
                company = _clean(company_el.get_text()) if company_el else None

                loc_el = card.select_one("span.job-search-card__location")
                loc = _clean(loc_el.get_text()) if loc_el else None

                date_el = card.select_one("time")
                date_str = date_el.get("datetime") if date_el else None

                if not _passes_filter(title, ""):
                    continue

                jobs.append(RawJob(
                    title=title, company=company, location=loc,
                    snippet=None, url=href or url, source="linkedin",
                    date_posted=date_str,
                ))

        except Exception as e:
            logger.error("LinkedIn scrape error for '%s': %s", query, e)

    return _dedupe(jobs)


# ---------------------------------------------------------------------------
# Adams Recruitment (broader selectors)
# ---------------------------------------------------------------------------

async def scrape_adams(client: httpx.AsyncClient) -> list[RawJob]:
    """Scrape Adams Recruitment — article.matador-job cards from base /jobs/ page."""
    jobs: list[RawJob] = []
    # Adams redirects www to non-www and rate-limits aggressively.
    # Use non-www domain and scrape base listing pages (no search params).
    pages_to_scrape = [
        "https://adamsrecruitment.com/jobs/",
        "https://adamsrecruitment.com/jobs/page/2/",
        "https://adamsrecruitment.com/jobs/page/3/",
    ]

    for page_url in pages_to_scrape:
        try:
            await asyncio.sleep(random.uniform(2.0, 3.5))  # longer delay for Adams rate limiting
            resp = await client.get(page_url, headers=_random_headers("https://adamsrecruitment.com/"), timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                logger.warning("Adams returned %s for %s", resp.status_code, page_url)
                continue
            soup = BeautifulSoup(resp.text, "lxml")

            # Primary: article.matador-job cards
            cards = soup.select("article.matador-job")
            if not cards:
                # Fallback: any article with job links
                cards = soup.select("article[class*='job'], div[class*='job-listing']")

            for card in cards:
                # Title: h3.matador-job-title a  or  h3.entry-title a
                title_el = card.select_one(
                    "h3.matador-job-title a, h3.entry-title a, h3 a, h2 a"
                )
                if not title_el:
                    continue
                title = _clean(title_el.get_text())
                if not title or len(title) < 5:
                    continue

                href = title_el.get("href", "")
                if href and not href.startswith("http"):
                    href = urljoin("https://adamsrecruitment.com", href)

                # Location: div.job-field.location .field-text
                loc_el = card.select_one(
                    "div.job-field.location .field-text, "
                    "div.location .field-text, "
                    "span.job-location, "
                    "div.matador-job-location"
                )
                loc = _clean(loc_el.get_text()) if loc_el else None

                # Salary: div.job-field.salary .field-text
                salary_el = card.select_one(
                    "div.job-field.salary .field-text, "
                    "div.salary .field-text"
                )
                salary_text = _clean(salary_el.get_text()) if salary_el else None

                # Type: div.job-field.type .field-text
                type_el = card.select_one(
                    "div.job-field.type .field-text, "
                    "div.type .field-text"
                )

                # Company from card metadata if available
                company_el = card.select_one(
                    "div.job-field.company .field-text, "
                    "span.company, div.employer"
                )
                company = _clean(company_el.get_text()) if company_el else "Adams Recruitment"

                snippet = salary_text or None

                if not _passes_filter(title, snippet or ""):
                    continue

                jobs.append(RawJob(
                    title=title, company=company, location=loc,
                    snippet=snippet, url=href or page_url, source="adams",
                ))

        except Exception as e:
            logger.error("Adams scrape error for %s: %s", page_url, e)

    return _dedupe(jobs)


# ---------------------------------------------------------------------------
# Welcome to NL (correct domain: www.welcome-to-nl.nl)
# ---------------------------------------------------------------------------

async def scrape_welcome_to_nl(client: httpx.AsyncClient) -> list[RawJob]:
    """Scrape Welcome to NL — Nuxt.js client-rendered, no scrapable job data."""
    # Welcome to NL uses Nuxt.js with client-side rendering.
    # Jobs are loaded dynamically via JS, not present in SSR HTML.
    # Would need a headless browser (Playwright/Selenium) to scrape.
    logger.info("Welcome to NL: skipped (client-rendered Nuxt.js, needs headless browser)")
    return []


# ---------------------------------------------------------------------------
# Remote OK (JSON API)
# ---------------------------------------------------------------------------

async def scrape_remoteok(client: httpx.AsyncClient) -> list[RawJob]:
    """Scrape Remote OK via JSON API, filter for relevant roles."""
    jobs: list[RawJob] = []
    url = "https://remoteok.com/api"
    try:
        resp = await client.get(url, headers={
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json",
        }, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            logger.warning("Remote OK API returned %s", resp.status_code)
            return jobs

        data = resp.json()
        # First element is metadata, skip it
        listings = data[1:] if isinstance(data, list) and len(data) > 1 else data

        for item in listings:
            if not isinstance(item, dict):
                continue
            position = item.get("position", "")
            if not position:
                continue

            # Check relevance by tags and position
            tags = [t.lower() for t in (item.get("tags") or [])]
            combined = f"{position.lower()} {' '.join(tags)}"
            is_relevant = any(tag in combined for tag in REMOTE_RELEVANT_TAGS)
            if not is_relevant:
                continue

            company = item.get("company", "")
            desc = item.get("description", "")
            snippet = _clean(BeautifulSoup(desc[:500], "html.parser").get_text()) if desc else None
            job_url = item.get("url", "")
            if job_url and not job_url.startswith("http"):
                job_url = f"https://remoteok.com{job_url}"
            date_str = item.get("date", "")

            # Build location from salary info
            loc = item.get("location", "Remote")

            if not _passes_filter(position, snippet or ""):
                continue

            jobs.append(RawJob(
                title=position, company=company, location=loc,
                snippet=snippet, url=job_url or url, source="remoteok",
                date_posted=date_str, work_model="remote",
            ))

    except Exception as e:
        logger.error("Remote OK scrape error: %s", e)

    return _dedupe(jobs)


# ---------------------------------------------------------------------------
# We Work Remotely (RSS feeds)
# ---------------------------------------------------------------------------

async def scrape_weworkremotely(client: httpx.AsyncClient) -> list[RawJob]:
    """Scrape We Work Remotely via RSS feeds for relevant categories."""
    jobs: list[RawJob] = []
    feeds = [
        "https://weworkremotely.com/categories/remote-customer-support-jobs.rss",
        "https://weworkremotely.com/categories/remote-management-and-finance-jobs.rss",
    ]

    for feed_url in feeds:
        try:
            await _delay()
            resp = await client.get(feed_url, headers={
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "application/rss+xml,application/xml,text/xml",
            }, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                logger.warning("WWR RSS returned %s for %s", resp.status_code, feed_url)
                continue

            soup = BeautifulSoup(resp.text, "xml")
            items = soup.find_all("item")

            for item in items:
                title_el = item.find("title")
                link_el = item.find("link")
                desc_el = item.find("description")
                pub_el = item.find("pubDate")

                if not title_el or not link_el:
                    continue
                raw_title = _clean(title_el.get_text())
                if not raw_title:
                    continue

                href = link_el.get_text().strip() if link_el else ""

                # Title format: "Company: Position"
                company = None
                title = raw_title
                if ": " in raw_title:
                    parts = raw_title.split(": ", 1)
                    company = parts[0].strip()
                    title = parts[1].strip()

                # Filter for relevant positions
                title_lower = title.lower()
                is_relevant = any(tag in title_lower for tag in REMOTE_RELEVANT_TAGS)
                if not is_relevant:
                    continue

                snippet_raw = desc_el.get_text() if desc_el else None
                snippet = _clean(BeautifulSoup(snippet_raw[:500], "html.parser").get_text()) if snippet_raw else None
                date_str = pub_el.get_text().strip() if pub_el else None

                if not _passes_filter(title, snippet or ""):
                    continue

                jobs.append(RawJob(
                    title=title, company=company, location="Remote",
                    snippet=snippet, url=href or feed_url, source="weworkremotely",
                    date_posted=date_str, work_model="remote",
                ))

        except Exception as e:
            logger.error("WWR scrape error for %s: %s", feed_url, e)

    return _dedupe(jobs)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dedupe(jobs: list[RawJob]) -> list[RawJob]:
    """Remove duplicate jobs based on external_id."""
    seen: set[str] = set()
    unique: list[RawJob] = []
    for job in jobs:
        if job.external_id not in seen:
            seen.add(job.external_id)
            unique.append(job)
    return unique


async def scrape_all() -> dict[str, int]:
    """Run all scrapers and return counts of new jobs per source."""
    from app.database import upsert_job

    results: dict[str, int] = {}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        scrapers = {
            "indeed": scrape_indeed,
            "iamexpat": scrape_iamexpat,
            "undutchables": scrape_undutchables,
            "linkedin": scrape_linkedin,
            "adams": scrape_adams,
            "welcometonl": scrape_welcome_to_nl,
            "remoteok": scrape_remoteok,
            "weworkremotely": scrape_weworkremotely,
        }

        for name, scraper_fn in scrapers.items():
            try:
                logger.info("Scraping %s...", name)
                raw_jobs = await scraper_fn(client)
                new_count = 0
                for job in raw_jobs:
                    sal = job.salary
                    cat = classify_category(job.title, job.snippet or "")
                    city = extract_city(job.location or "")
                    ptype = detect_posting_type(job.company or "", job.source)
                    dl = job.dutch_level
                    wm = job.detected_work_model
                    inserted = upsert_job(
                        external_id=job.external_id,
                        title=job.title,
                        company=job.company,
                        location=job.location,
                        snippet=job.snippet,
                        url=job.url,
                        source=job.source,
                        score=job.score,
                        date_posted=job.date_posted,
                        salary_min=sal["min"] if sal else None,
                        salary_max=sal["max"] if sal else None,
                        salary_raw=sal["raw"] if sal else None,
                        category=cat,
                        city=city,
                        posting_type=ptype,
                        dutch_level=dl,
                        work_model=wm,
                    )
                    if inserted:
                        new_count += 1
                results[name] = new_count
                logger.info("  %s: %d jobs found, %d new", name, len(raw_jobs), new_count)
            except Exception as e:
                logger.error("Scraper %s failed: %s", name, e)
                results[name] = 0

    return results
