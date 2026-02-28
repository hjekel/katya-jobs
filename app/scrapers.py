"""Job scrapers for Indeed NL, IamExpat, Undutchables, LinkedIn, Adams, Welcome to NL."""

import hashlib
import logging
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote_plus, urljoin

import httpx
from bs4 import BeautifulSoup

from app.config import (
    REQUEST_TIMEOUT,
    USER_AGENT,
)
from app.scorer import compute_score, should_exclude, extract_salary, classify_category, extract_city, detect_posting_type

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class RawJob:
    title: str
    company: Optional[str]
    location: Optional[str]
    snippet: Optional[str]
    url: str
    source: str
    date_posted: Optional[str] = None

    @property
    def external_id(self) -> str:
        raw = f"{self.source}:{self.url}"
        return hashlib.md5(raw.encode()).hexdigest()

    @property
    def score(self) -> int:
        return compute_score(
            self.title,
            self.company or "",
            self.location or "",
            self.snippet or "",
        )

    @property
    def salary(self) -> dict | None:
        return extract_salary(f"{self.title} {self.snippet or ''}")


def _clean(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    return re.sub(r"\s+", " ", text).strip()


def _passes_filter(title: str, snippet: str = "") -> bool:
    """Check that a job passes both keyword exclusion and Dutch language detection."""
    return not should_exclude(title, snippet)


# ---------------------------------------------------------------------------
# Indeed NL
# ---------------------------------------------------------------------------

async def scrape_indeed(client: httpx.AsyncClient) -> list[RawJob]:
    """Scrape Indeed Netherlands for English-speaking jobs near Haarlem."""
    jobs: list[RawJob] = []
    queries_to_use = [
        "accountant english",
        "bookkeeper english",
        "accounts payable english",
        "accounts receivable english",
        "financial administrator english",
        "office administrator english",
        "back office english",
        "customer service english",
        "data entry english",
    ]

    for query in queries_to_use:
        for location in ["Haarlem", "Amsterdam", "Hoofddorp"]:
            url = (
                f"https://nl.indeed.com/jobs"
                f"?q={quote_plus(query)}"
                f"&l={quote_plus(location)}"
                f"&radius=25"
                f"&lang=en"
                f"&fromage=14"
            )
            try:
                resp = await client.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
                if resp.status_code != 200:
                    logger.warning("Indeed returned %s for %s", resp.status_code, query)
                    continue
                soup = BeautifulSoup(resp.text, "lxml")

                cards = soup.select("div.job_seen_beacon") or soup.select("div.jobsearch-ResultsList > div")
                for card in cards:
                    title_el = card.select_one("h2.jobTitle a, h2.jobTitle span")
                    if not title_el:
                        continue
                    title = _clean(title_el.get_text())
                    if not title:
                        continue

                    link_el = card.select_one("h2.jobTitle a")
                    href = link_el.get("href", "") if link_el else ""
                    if href and not href.startswith("http"):
                        href = urljoin("https://nl.indeed.com", href)

                    company_el = card.select_one("[data-testid='company-name'], span.companyName")
                    company = _clean(company_el.get_text()) if company_el else None

                    loc_el = card.select_one("[data-testid='text-location'], div.companyLocation")
                    loc = _clean(loc_el.get_text()) if loc_el else location

                    snippet_el = card.select_one("div.job-snippet, td.resultContent div.css-9446fg")
                    snippet = _clean(snippet_el.get_text()) if snippet_el else None

                    date_el = card.select_one("span.date")
                    date_str = _clean(date_el.get_text()) if date_el else None

                    if not _passes_filter(title, snippet or ""):
                        continue

                    jobs.append(RawJob(
                        title=title, company=company, location=loc,
                        snippet=snippet, url=href or url, source="indeed",
                        date_posted=date_str,
                    ))

            except Exception as e:
                logger.error("Indeed scrape error for '%s' in %s: %s", query, location, e)

    return _dedupe(jobs)


# ---------------------------------------------------------------------------
# IamExpat
# ---------------------------------------------------------------------------

async def scrape_iamexpat(client: httpx.AsyncClient) -> list[RawJob]:
    """Scrape IamExpat jobs portal."""
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
            resp = await client.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                logger.warning("IamExpat returned %s for %s", resp.status_code, query)
                continue
            soup = BeautifulSoup(resp.text, "lxml")

            cards = soup.select("div.views-row, article.node--job, div.job-listing")
            for card in cards:
                title_el = card.select_one("h2 a, h3 a, a.job-title, span.field--name-title a")
                if not title_el:
                    continue
                title = _clean(title_el.get_text())
                if not title:
                    continue

                href = title_el.get("href", "")
                if href and not href.startswith("http"):
                    href = urljoin("https://www.iamexpat.nl", href)

                company_el = card.select_one(".field--name-field-company, .company-name, span.company")
                company = _clean(company_el.get_text()) if company_el else None

                loc_el = card.select_one(".field--name-field-location, .location, span.location")
                loc = _clean(loc_el.get_text()) if loc_el else None

                snippet_el = card.select_one(".field--name-body, .job-description, p")
                snippet = _clean(snippet_el.get_text()[:300]) if snippet_el else None

                if not _passes_filter(title, snippet or ""):
                    continue

                jobs.append(RawJob(
                    title=title, company=company, location=loc,
                    snippet=snippet, url=href or url, source="iamexpat",
                ))

        except Exception as e:
            logger.error("IamExpat scrape error for '%s': %s", query, e)

    return _dedupe(jobs)


# ---------------------------------------------------------------------------
# Undutchables
# ---------------------------------------------------------------------------

async def scrape_undutchables(client: httpx.AsyncClient) -> list[RawJob]:
    """Scrape Undutchables job listings."""
    jobs: list[RawJob] = []
    search_terms = [
        "accountant", "bookkeeper", "finance", "administration",
        "back office", "customer service", "data entry", "office",
    ]

    for query in search_terms:
        url = (
            f"https://undutchables.nl/jobs"
            f"?query={quote_plus(query)}"
            f"&region=noord-holland"
        )
        try:
            resp = await client.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                logger.warning("Undutchables returned %s for %s", resp.status_code, query)
                continue
            soup = BeautifulSoup(resp.text, "lxml")

            cards = soup.select("div.vacancy-item, div.job-item, article.vacancy, div.card.vacancy")
            for card in cards:
                title_el = card.select_one("h2 a, h3 a, a.vacancy-title, .vacancy-item__title a")
                if not title_el:
                    continue
                title = _clean(title_el.get_text())
                if not title:
                    continue

                href = title_el.get("href", "")
                if href and not href.startswith("http"):
                    href = urljoin("https://undutchables.nl", href)

                company_el = card.select_one(".vacancy-company, .company, .vacancy-item__company")
                company = _clean(company_el.get_text()) if company_el else None

                loc_el = card.select_one(".vacancy-location, .location, .vacancy-item__location")
                loc = _clean(loc_el.get_text()) if loc_el else None

                snippet_el = card.select_one(".vacancy-intro, .description, .vacancy-item__description")
                snippet = _clean(snippet_el.get_text()[:300]) if snippet_el else None

                if not _passes_filter(title, snippet or ""):
                    continue

                jobs.append(RawJob(
                    title=title, company=company, location=loc,
                    snippet=snippet, url=href or url, source="undutchables",
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
            resp = await client.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, follow_redirects=True)
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
# Adams Recruitment
# ---------------------------------------------------------------------------

async def scrape_adams(client: httpx.AsyncClient) -> list[RawJob]:
    """Scrape Adams Recruitment job listings."""
    jobs: list[RawJob] = []
    search_terms = [
        "accountant", "bookkeeper", "finance", "administration",
        "back office", "customer service", "data entry", "office",
    ]

    for query in search_terms:
        url = (
            f"https://www.adamsrecruitment.com/jobs/"
            f"?search={quote_plus(query)}"
            f"&location=Noord-Holland"
        )
        try:
            resp = await client.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                logger.warning("Adams returned %s for %s", resp.status_code, query)
                continue
            soup = BeautifulSoup(resp.text, "lxml")

            # Adams uses various card layouts
            cards = soup.select(
                "div.job-item, div.vacancy-card, article.vacancy, "
                "div.card-job, li.job-listing, div.job-result"
            )
            for card in cards:
                title_el = card.select_one(
                    "h2 a, h3 a, a.job-title, .vacancy-title a, "
                    ".job-item__title a, .card-title a"
                )
                if not title_el:
                    continue
                title = _clean(title_el.get_text())
                if not title:
                    continue

                href = title_el.get("href", "")
                if href and not href.startswith("http"):
                    href = urljoin("https://www.adamsrecruitment.com", href)

                company_el = card.select_one(
                    ".company, .job-item__company, .vacancy-company, .employer"
                )
                company = _clean(company_el.get_text()) if company_el else None

                loc_el = card.select_one(
                    ".location, .job-item__location, .vacancy-location, .job-location"
                )
                loc = _clean(loc_el.get_text()) if loc_el else None

                snippet_el = card.select_one(
                    ".description, .job-item__description, .vacancy-intro, p"
                )
                snippet = _clean(snippet_el.get_text()[:300]) if snippet_el else None

                if not _passes_filter(title, snippet or ""):
                    continue

                jobs.append(RawJob(
                    title=title, company=company, location=loc,
                    snippet=snippet, url=href or url, source="adams",
                ))

        except Exception as e:
            logger.error("Adams scrape error for '%s': %s", query, e)

    return _dedupe(jobs)


# ---------------------------------------------------------------------------
# Welcome to NL
# ---------------------------------------------------------------------------

async def scrape_welcome_to_nl(client: httpx.AsyncClient) -> list[RawJob]:
    """Scrape Welcome to NL job listings for internationals."""
    jobs: list[RawJob] = []
    search_terms = [
        "accountant", "bookkeeper", "finance", "administration",
        "back office", "customer service", "data entry", "office",
    ]

    for query in search_terms:
        url = (
            f"https://welcome-to-nl.nl/jobs/"
            f"?search={quote_plus(query)}"
            f"&location=Noord-Holland"
        )
        try:
            resp = await client.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                logger.warning("Welcome to NL returned %s for %s", resp.status_code, query)
                continue
            soup = BeautifulSoup(resp.text, "lxml")

            cards = soup.select(
                "div.job-item, div.vacancy, article.job, "
                "div.card-job, li.job-listing, div.job-result, div.views-row"
            )
            for card in cards:
                title_el = card.select_one(
                    "h2 a, h3 a, a.job-title, .vacancy-title a, "
                    ".job-title a, .card-title a"
                )
                if not title_el:
                    continue
                title = _clean(title_el.get_text())
                if not title:
                    continue

                href = title_el.get("href", "")
                if href and not href.startswith("http"):
                    href = urljoin("https://welcome-to-nl.nl", href)

                company_el = card.select_one(
                    ".company, .employer, .job-company, .organization"
                )
                company = _clean(company_el.get_text()) if company_el else None

                loc_el = card.select_one(
                    ".location, .job-location, .city"
                )
                loc = _clean(loc_el.get_text()) if loc_el else None

                snippet_el = card.select_one(
                    ".description, .job-description, .intro, p"
                )
                snippet = _clean(snippet_el.get_text()[:300]) if snippet_el else None

                if not _passes_filter(title, snippet or ""):
                    continue

                jobs.append(RawJob(
                    title=title, company=company, location=loc,
                    snippet=snippet, url=href or url, source="welcometonl",
                ))

        except Exception as e:
            logger.error("Welcome to NL scrape error for '%s': %s", query, e)

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
        }

        for name, scraper_fn in scrapers.items():
            try:
                logger.info("Scraping %s...", name)
                jobs = await scraper_fn(client)
                new_count = 0
                for job in jobs:
                    sal = job.salary
                    cat = classify_category(job.title, job.snippet or "")
                    city = extract_city(job.location or "")
                    ptype = detect_posting_type(job.company or "", job.source)
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
                    )
                    if inserted:
                        new_count += 1
                results[name] = new_count
                logger.info("  %s: %d jobs found, %d new", name, len(jobs), new_count)
            except Exception as e:
                logger.error("Scraper %s failed: %s", name, e)
                results[name] = 0

    return results
