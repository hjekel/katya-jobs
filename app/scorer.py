"""Score, filter, cover letter, and salary extraction for Katya's JobFinder."""

import re
from datetime import datetime, timezone
from typing import Optional

from app.config import (
    ROLE_SCORES,
    ENGLISH_BONUS,
    ENGLISH_ENV_SIGNALS,
    ENGLISH_ENV_BONUS,
    LANGUAGE_ASSET_BONUS,
    TEMP_CONTRACT_BONUS,
    CITY_BONUS,
    EXCLUDE_KEYWORDS,
    EXCLUDE_TITLE_KEYWORDS,
    DUTCH_WORDS,
    DUTCH_WORD_THRESHOLD_TITLE,
    DUTCH_WORD_THRESHOLD_BODY,
    SENIORITY_PENALTY,
    SENIORITY_BONUS,
    HOME_ADDRESS_ENCODED,
    COMMUTE_ESTIMATES,
    TARGET_CITIES,
)

_WORD_SPLIT = re.compile(r"[^a-zA-Zéèëïöüà]+")

# Salary extraction patterns (EUR)
_SALARY_NUM = r"(\d[\d.,]*\d|\d+)"  # matches "3000", "3.000", "3,000", "3.500,00"

_SALARY_PATTERNS = [
    # "€3.000 - €4.000" or "€3000-€4000" or "EUR 3000 - 4000"
    re.compile(
        r"(?:€|EUR)\s*" + _SALARY_NUM + r"\s*[-–—to]+\s*(?:€|EUR)?\s*" + _SALARY_NUM,
        re.IGNORECASE,
    ),
    # "3000 - 4000 euro" or "3.000 - 4.000 per month"
    re.compile(
        _SALARY_NUM + r"\s*[-–—to]+\s*" + _SALARY_NUM + r"\s*(?:euro|eur|per\s+m)",
        re.IGNORECASE,
    ),
    # "€3.000" or "€3000" single value
    re.compile(r"(?:€|EUR)\s*" + _SALARY_NUM, re.IGNORECASE),
    # "salary: 3000"
    re.compile(r"salary[:\s]+(\d{3,6})", re.IGNORECASE),
]


def _parse_salary_number(s: str) -> int:
    """Parse '3.000' or '3,000' or '3000' into 3000."""
    s = s.replace(".", "").replace(",", "")
    return int(s)


def extract_salary(text: str) -> Optional[dict]:
    """Extract salary info from text. Returns {min, max, raw} or None."""
    if not text:
        return None
    for pat in _SALARY_PATTERNS:
        m = pat.search(text)
        if m:
            groups = m.groups()
            if len(groups) == 2:
                lo = _parse_salary_number(groups[0])
                hi = _parse_salary_number(groups[1])
                # Sanity: salary should be between 500 and 20000/month
                if 500 <= lo <= 20000 and 500 <= hi <= 20000:
                    return {"min": lo, "max": hi, "raw": m.group(0).strip()}
            elif len(groups) == 1:
                val = _parse_salary_number(groups[0])
                if 500 <= val <= 20000:
                    return {"min": val, "max": val, "raw": m.group(0).strip()}
    return None


# --------------------------------------------------------------------------
# Dutch detection
# --------------------------------------------------------------------------

def _count_dutch_words(text: str) -> int:
    words = set(_WORD_SPLIT.split(text.lower()))
    text_lower = text.lower()
    hits = 0
    for dw in DUTCH_WORDS:
        if " " in dw:
            if dw in text_lower:
                hits += 1
        else:
            if dw in words:
                hits += 1
    return hits


def is_dutch_text(title: str, description: str = "") -> bool:
    title_hits = _count_dutch_words(title)
    if title_hits >= DUTCH_WORD_THRESHOLD_TITLE:
        return True
    if description:
        body_hits = _count_dutch_words(description)
        if body_hits >= DUTCH_WORD_THRESHOLD_BODY:
            return True
        if title_hits >= 1 and body_hits >= 3:
            return True
    return False


def should_exclude(title: str, description: str = "") -> bool:
    title_lower = title.lower()
    desc_lower = description.lower()
    combined = f"{title_lower} {desc_lower}"

    for kw in EXCLUDE_KEYWORDS:
        if kw in combined:
            return True
    for kw in EXCLUDE_TITLE_KEYWORDS:
        if kw in title_lower:
            return True
    if is_dutch_text(title, description):
        return True
    return False


# --------------------------------------------------------------------------
# Category classification
# --------------------------------------------------------------------------

CATEGORY_RULES = [
    ("Finance & Accounting", [
        "accountant", "bookkeeper", "finance", "accounting", "accounts payable",
        "accounts receivable", "financial", "fiscal", "boekhouder", "administrateur",
        "credit control", "invoice", "billing", "payroll", "tax",
    ]),
    ("Administration & Office", [
        "admin", "office", "secretary", "receptionist", "office manager", "back office",
        "administrative", "office assistant",
    ]),
    ("Customer Service", [
        "customer service", "customer support", "helpdesk", "call centre",
        "call center", "klantenservice",
    ]),
    ("Operations & Logistics", [
        "operations", "logistics", "supply chain", "warehouse", "planning",
    ]),
    ("Data Entry & Processing", [
        "data entry", "data processing", "document", "scanning", "archiving",
    ]),
    ("Retail", [
        "retail", "sales assistant", "shop", "store", "winkel", "verkoop",
    ]),
]


def classify_category(title: str, description: str = "") -> str:
    """Classify a job into a category based on title and description keywords."""
    combined = f"{title} {description}".lower()
    for category, keywords in CATEGORY_RULES:
        if any(kw in combined for kw in keywords):
            return category
    return "Other"


# --------------------------------------------------------------------------
# City extraction
# --------------------------------------------------------------------------

# Normalise common location variants
_CITY_ALIASES = {
    "amsterdam-zuidoost": "Amsterdam",
    "amsterdam zuidoost": "Amsterdam",
    "amsterdam zuid": "Amsterdam",
    "amsterdam west": "Amsterdam",
    "amsterdam noord": "Amsterdam",
    "schiphol-rijk": "Schiphol",
    "nieuw-vennep": "Nieuw-Vennep",
}


def extract_city(location: str) -> str:
    """Extract and normalise the city name from a job location string."""
    if not location:
        return ""
    loc_lower = location.lower().strip()

    # Check aliases first
    for alias, city in _CITY_ALIASES.items():
        if alias in loc_lower:
            return city

    # Check target cities
    for city in TARGET_CITIES:
        if city.lower() in loc_lower:
            return city

    # Fallback: use the first comma-separated part cleaned up
    first_part = location.split(",")[0].strip()
    # Remove common prefixes/suffixes
    for prefix in ["Regio ", "regio ", "Area ", "area ", "Omgeving ", "omgeving "]:
        if first_part.startswith(prefix):
            first_part = first_part[len(prefix):]
    return first_part if first_part else ""


# --------------------------------------------------------------------------
# Recruiter detection
# --------------------------------------------------------------------------

KNOWN_RECRUITERS = {
    "randstad", "hays", "michael page", "robert half", "page personnel",
    "brunel", "yer", "adecco", "tempo-team", "tempo team", "manpower",
    "olympia", "yacht", "undutchables", "adams multilingual recruitment",
    "adams recruitment", "unique", "start people", "staffing group",
    "kelly services", "sander & partners", "progressive", "connected",
}

JOB_BOARD_SOURCES = {"indeed", "linkedin", "glassdoor"}


def detect_posting_type(company: str, source: str) -> str:
    """Detect whether a posting is direct, via recruiter, or from a job board.
    Returns 'direct', 'recruiter', or 'job_board'."""
    company_lower = (company or "").lower().strip()

    # Check if company is a known recruiter
    for recruiter in KNOWN_RECRUITERS:
        if recruiter in company_lower:
            return "recruiter"

    # Check source-level (e.g. undutchables is always a recruiter site)
    source_lower = (source or "").lower()
    if source_lower in ("undutchables", "adams"):
        return "recruiter"

    # Job boards that aggregate
    if source_lower in JOB_BOARD_SOURCES:
        return "job_board"

    return "direct"


# --------------------------------------------------------------------------
# Posting age
# --------------------------------------------------------------------------

def compute_posting_age(date_posted: Optional[str], date_scraped: Optional[str] = None) -> dict:
    """Compute human-readable posting age and freshness indicator.
    Returns {text, color} where color is 'green', 'orange', or 'grey'."""
    if not date_posted:
        return {"text": "", "color": "grey"}

    try:
        # Try parsing ISO format or common date strings
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d %b %Y", "%B %d, %Y", "%d-%m-%Y"):
            try:
                posted_dt = datetime.strptime(date_posted.split("+")[0].split("Z")[0].strip(), fmt)
                break
            except ValueError:
                continue
        else:
            # Try relative dates like "3 days ago", "Just posted", etc.
            lower = date_posted.lower().strip()
            if "just" in lower or "today" in lower or "now" in lower:
                return {"text": "Just posted", "color": "green"}
            if "yesterday" in lower or "1 day" in lower:
                return {"text": "1 day ago", "color": "green"}
            # Try to extract number of days
            import re as _re
            m = _re.search(r"(\d+)\s*day", lower)
            if m:
                days = int(m.group(1))
                if days <= 3:
                    return {"text": f"{days} days ago", "color": "green"}
                elif days <= 7:
                    return {"text": f"{days} days ago", "color": "orange"}
                elif days <= 14:
                    return {"text": "2 weeks ago", "color": "grey"}
                elif days <= 21:
                    return {"text": "3 weeks ago", "color": "grey"}
                else:
                    return {"text": "Older", "color": "grey"}
            m = _re.search(r"(\d+)\s*week", lower)
            if m:
                weeks = int(m.group(1))
                if weeks <= 1:
                    return {"text": "1 week ago", "color": "orange"}
                elif weeks <= 2:
                    return {"text": "2 weeks ago", "color": "grey"}
                elif weeks <= 3:
                    return {"text": "3 weeks ago", "color": "grey"}
                else:
                    return {"text": "Older", "color": "grey"}
            m = _re.search(r"(\d+)\s*month", lower)
            if m:
                return {"text": "Older", "color": "grey"}
            # Unknown format — return raw text
            return {"text": date_posted, "color": "grey"}

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        delta = now - posted_dt
        days = delta.days

        if days < 0:
            days = 0
        if days == 0:
            return {"text": "Just posted", "color": "green"}
        elif days == 1:
            return {"text": "1 day ago", "color": "green"}
        elif days <= 3:
            return {"text": f"{days} days ago", "color": "green"}
        elif days <= 7:
            return {"text": f"{days} days ago", "color": "orange"}
        elif days <= 14:
            return {"text": "2 weeks ago", "color": "grey"}
        elif days <= 21:
            return {"text": "3 weeks ago", "color": "grey"}
        else:
            return {"text": "Older", "color": "grey"}
    except Exception:
        return {"text": date_posted or "", "color": "grey"}


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------

def compute_score(title: str, company: str = "", location: str = "", description: str = "") -> int:
    title_lower = title.lower()
    desc_lower = description.lower()
    combined = f"{title_lower} {desc_lower}"

    score = 0

    # Role match
    best_role_score = 0
    for keyword, points in ROLE_SCORES.items():
        if keyword in combined:
            best_role_score = max(best_role_score, points)
    score += best_role_score
    if best_role_score == 0:
        score = 20

    # Seniority
    for keyword, penalty in SENIORITY_PENALTY.items():
        if keyword in title_lower:
            score += penalty
            break
    for keyword, bonus in SENIORITY_BONUS.items():
        if keyword in title_lower or keyword in desc_lower:
            score += bonus
            break

    # English bonus
    english_signals = ["english", "english-speaking", "international", "expat", "no dutch"]
    if any(signal in combined for signal in english_signals):
        score += ENGLISH_BONUS

    # English environment bonus (stronger signal)
    if any(signal in combined for signal in ENGLISH_ENV_SIGNALS):
        score += ENGLISH_ENV_BONUS

    # Ukrainian/Russian as asset bonus
    if any(lang in combined for lang in ["ukrainian", "russian", "oekraïens", "russisch"]):
        score += LANGUAGE_ASSET_BONUS

    # Temp/contract bonus
    temp_signals = ["temporary", "temp ", "contract", "freelance", "interim", "fixed-term", "fixed term"]
    if any(signal in combined for signal in temp_signals):
        score += TEMP_CONTRACT_BONUS

    # Location bonus
    location_lower = (location or "").lower()
    for city, bonus in CITY_BONUS.items():
        if city.lower() in location_lower:
            score += bonus
            break

    # Other bonuses
    if "refugee" in combined or "newcomer" in combined or "status holder" in combined:
        score += 10
    if "part-time" in combined or "part time" in combined:
        score += 3
    if "zara" in combined or "inditex" in combined:
        score += 5

    return max(0, min(score, 150))


def compute_score_breakdown(title: str, company: str = "", location: str = "", description: str = "") -> dict:
    """Compute score with detailed per-component breakdown."""
    title_lower = (title or "").lower()
    desc_lower = (description or "").lower()
    combined = f"{title_lower} {desc_lower}"

    components = []
    total = 0

    # Role match
    best_role_score = 0
    best_role_keyword = ""
    for keyword, points in ROLE_SCORES.items():
        if keyword in combined and points > best_role_score:
            best_role_score = points
            best_role_keyword = keyword

    if best_role_score > 0:
        components.append({"label": f"Role match ({best_role_keyword})", "points": best_role_score})
        total += best_role_score
    else:
        components.append({"label": "Base score", "points": 20})
        total = 20

    # Seniority penalty
    for keyword, penalty in SENIORITY_PENALTY.items():
        if keyword in title_lower:
            components.append({"label": f"Seniority ({keyword})", "points": penalty})
            total += penalty
            break

    # Seniority bonus
    for keyword, bonus in SENIORITY_BONUS.items():
        if keyword in title_lower or keyword in desc_lower:
            components.append({"label": f"Seniority ({keyword})", "points": bonus})
            total += bonus
            break

    # English bonus
    english_signals = ["english", "english-speaking", "international", "expat", "no dutch"]
    if any(signal in combined for signal in english_signals):
        components.append({"label": "English-friendly", "points": ENGLISH_BONUS})
        total += ENGLISH_BONUS

    # English environment bonus
    if any(signal in combined for signal in ENGLISH_ENV_SIGNALS):
        components.append({"label": "English work environment", "points": ENGLISH_ENV_BONUS})
        total += ENGLISH_ENV_BONUS

    # Language asset bonus
    if any(lang in combined for lang in ["ukrainian", "russian", "oekra\u00efens", "russisch"]):
        components.append({"label": "Ukrainian/Russian asset", "points": LANGUAGE_ASSET_BONUS})
        total += LANGUAGE_ASSET_BONUS

    # Temp/contract bonus
    temp_signals = ["temporary", "temp ", "contract", "freelance", "interim", "fixed-term", "fixed term"]
    if any(signal in combined for signal in temp_signals):
        components.append({"label": "Temp/contract", "points": TEMP_CONTRACT_BONUS})
        total += TEMP_CONTRACT_BONUS

    # Location bonus
    location_lower = (location or "").lower()
    for city, bonus in CITY_BONUS.items():
        if city.lower() in location_lower:
            components.append({"label": f"Location ({city})", "points": bonus})
            total += bonus
            break

    # Other bonuses
    if "refugee" in combined or "newcomer" in combined or "status holder" in combined:
        components.append({"label": "Newcomer-friendly", "points": 10})
        total += 10
    if "part-time" in combined or "part time" in combined:
        components.append({"label": "Part-time", "points": 3})
        total += 3
    if "zara" in combined or "inditex" in combined:
        components.append({"label": "ZARA/Inditex", "points": 5})
        total += 5

    total = max(0, min(total, 150))
    return {"components": components, "total": total}


# --------------------------------------------------------------------------
# Commute info
# --------------------------------------------------------------------------

def get_commute_info(location: str) -> dict:
    """Get commute info for a job location."""
    if not location:
        return {"maps_url": None, "estimate": None}

    location_lower = location.lower()
    estimate = None
    for city_key, info in COMMUTE_ESTIMATES.items():
        if city_key in location_lower:
            estimate = info
            break

    loc_encoded = location.replace(" ", "+").replace(",", "%2C")
    maps_url = (
        f"https://www.google.com/maps/dir/"
        f"{HOME_ADDRESS_ENCODED}/{loc_encoded}"
        f"?travelmode=transit"
    )

    return {"maps_url": maps_url, "estimate": estimate}


# --------------------------------------------------------------------------
# Fit analysis
# --------------------------------------------------------------------------

def generate_fit_analysis(title: str, snippet: str = "", location: str = "") -> dict:
    title_lower = title.lower()
    snippet_lower = (snippet or "").lower()
    combined = f"{title_lower} {snippet_lower}"
    loc_lower = (location or "").lower()

    bullets = []

    # Detect job categories (multiple can be true)
    is_finance = any(kw in combined for kw in [
        "accountant", "bookkeeper", "accounts payable", "accounts receivable",
        "financial", "finance", "accounting", "invoice", "billing",
        "credit control", "payroll", "tax",
    ])
    is_admin = any(kw in combined for kw in [
        "admin", "administration", "back office", "office manager",
        "data entry", "office assistant", "secretary", "receptionist",
    ])
    is_customer = any(kw in combined for kw in [
        "customer service", "customer support", "helpdesk", "call cent",
        "front desk",
    ])
    is_operations = any(kw in combined for kw in [
        "operations", "logistics", "supply chain", "warehouse", "planning",
        "coordinator",
    ])
    is_retail = any(kw in combined for kw in [
        "sales assistant", "retail", "shop assistant", "store",
    ])
    has_ukrainian_russian = any(kw in combined for kw in [
        "ukrainian", "russian", "oekra\u00efens", "russisch",
    ])
    has_english = any(kw in combined for kw in [
        "english", "english-speaking", "international", "expat",
    ])
    is_hoofddorp = "hoofddorp" in loc_lower
    is_haarlem = "haarlem" in loc_lower

    # Build tagline based on best match
    if is_finance:
        tagline = "Strong match \u2014 12 years of accounting and finance experience."
    elif is_admin:
        tagline = "Great fit \u2014 strong organisational skills and office experience."
    elif is_customer:
        tagline = "Good match \u2014 customer-facing experience at ZARA Netherlands."
    elif is_operations:
        tagline = "Relevant skills \u2014 operations planning and coordination experience."
    elif is_retail:
        tagline = "Direct experience \u2014 currently working in Dutch retail."
    else:
        tagline = "Transferable skills \u2014 finance background and Dutch work experience."

    # Add category-specific bullets
    if is_finance:
        if "payroll" in combined:
            bullets.append("12 years handling payroll, bookkeeping, and financial reporting in Ukraine")
        elif "tax" in combined:
            bullets.append("12 years of accounting experience including tax filing and compliance")
        elif "invoice" in combined or "billing" in combined:
            bullets.append("Extensive experience processing invoices, purchase orders, and billing cycles")
        else:
            bullets.append("12 years of accounts payable/receivable, reconciliations, and month-end closing")
        bullets.append("Nuffic-recognised Master\u2019s degree in Economics/Finance")

    if is_admin:
        if "data entry" in combined:
            bullets.append("Experienced in accurate data entry, record keeping, and database management")
        elif "back office" in combined:
            bullets.append("Background in back-office financial operations: filing, reporting, and compliance")
        else:
            bullets.append("12 years managing office administration, documentation, and filing systems")
        if not is_finance:
            bullets.append("Advanced Excel and office software proficiency")

    if is_customer:
        bullets.append("Recent customer service experience at ZARA (Hoofddorp), handling high-volume interactions")
        if not is_finance and not is_admin:
            bullets.append("Professional problem-solving skills developed over 12 years in finance")

    if is_operations:
        bullets.append("Experience in planning, coordination, and process management from finance roles")
        if not is_finance and not is_admin:
            bullets.append("Strong analytical and organisational skills from 12 years in professional settings")

    if is_retail:
        bullets.append("Currently working at ZARA Netherlands \u2014 hands-on Dutch retail experience")
        if not is_customer:
            bullets.append("Strong numerical skills from finance background \u2014 accurate cash handling")

    # Language-specific bullets
    if has_ukrainian_russian:
        bullets.append("Native Ukrainian and Russian speaker \u2014 valuable language asset for this role")
    if has_english:
        bullets.append("Improving English proficiency with experience in international work environments")

    # Location-specific bullets
    if is_haarlem:
        bullets.append("Lives in Haarlem \u2014 no commute needed")
    elif is_hoofddorp:
        bullets.append("Already commutes to Hoofddorp for ZARA \u2014 knows the area well")
    elif any(c in loc_lower for c in ["amsterdam", "schiphol", "amstelveen"]):
        bullets.append("Easy public transport commute from Haarlem")

    # If we still have fewer than 3 bullets, add general ones
    general_pool = [
        "Nuffic-recognised Master\u2019s degree in Economics/Finance",
        "Quick learner who adapted to a new country and work culture",
        "Fluent in English, Ukrainian, and Russian",
        "Reliable and motivated \u2014 proven adaptability at ZARA Netherlands",
    ]
    for g in general_pool:
        if len(bullets) >= 4:
            break
        if g not in bullets:
            bullets.append(g)

    return {"tagline": tagline, "bullets": bullets[:4]}


# --------------------------------------------------------------------------
# Cover letter generator
# --------------------------------------------------------------------------

def generate_cover_letter(title: str, company: str = "", location: str = "", snippet: str = "") -> str:
    """Generate a cover letter template tailored to the job."""
    title_lower = title.lower()
    snippet_lower = (snippet or "").lower()
    combined = f"{title_lower} {snippet_lower}"
    company_name = company or "your company"

    is_finance = any(kw in combined for kw in [
        "accountant", "bookkeeper", "accounts payable", "accounts receivable",
        "financial", "finance", "accounting", "invoice", "billing",
        "credit control", "payroll", "tax",
    ])
    is_admin = any(kw in combined for kw in [
        "admin", "administration", "back office", "office manager",
        "data entry", "operations", "office assistant",
    ])
    is_customer = any(kw in combined for kw in [
        "customer service", "customer support", "receptionist", "front desk",
    ])

    # Build paragraphs
    opening = (
        f"Dear Hiring Manager,\n\n"
        f"I am writing to express my strong interest in the {title} position "
        f"at {company_name}. With 12 years of professional experience in finance "
        f"and administration, combined with my recent work experience in the "
        f"Netherlands, I am confident I can make a valuable contribution to your team."
    )

    if is_finance:
        body = (
            f"Throughout my career in Ukraine, I have developed extensive expertise "
            f"in bookkeeping, accounts payable and receivable, financial reporting, "
            f"and month-end closing procedures. I hold a Nuffic-recognised Master\u2019s "
            f"degree in Economics and Finance, which provides me with a solid "
            f"theoretical foundation to complement my practical experience.\n\n"
            f"I am proficient in Excel, accounting software, and ERP systems, and "
            f"I bring strong analytical skills and meticulous attention to detail "
            f"to every task. My experience includes ledger management, bank "
            f"reconciliations, VAT reporting, and financial analysis."
        )
    elif is_admin:
        body = (
            f"Over the past 12 years, I have managed financial administration, "
            f"documentation, and data management in professional office environments. "
            f"I hold a Nuffic-recognised Master\u2019s degree in Economics and Finance, "
            f"and I am experienced in data entry, filing systems, and maintaining "
            f"accurate records and databases.\n\n"
            f"Currently working at ZARA Netherlands, I have demonstrated my ability "
            f"to prioritise tasks, work under pressure, and adapt quickly to new "
            f"environments and systems. I am proficient in Microsoft Office, "
            f"particularly Excel, and comfortable learning new software tools."
        )
    elif is_customer:
        body = (
            f"I am currently working at ZARA Netherlands in Hoofddorp, where I "
            f"provide customer service in a fast-paced retail environment. This "
            f"role has sharpened my communication skills, problem-solving abilities, "
            f"and capacity to work effectively under pressure.\n\n"
            f"Prior to moving to the Netherlands, I spent 12 years working in "
            f"finance and administration in Ukraine, developing strong organisational "
            f"and analytical skills. I hold a Nuffic-recognised Master\u2019s degree "
            f"in Economics and Finance."
        )
    else:
        body = (
            f"I bring 12 years of professional experience in finance and "
            f"administration from Ukraine, complemented by my current role at "
            f"ZARA Netherlands in Hoofddorp. My background has equipped me with "
            f"strong organisational, analytical, and problem-solving skills.\n\n"
            f"I hold a Nuffic-recognised Master\u2019s degree in Economics and "
            f"Finance, and I am proficient in Microsoft Office and various "
            f"professional software tools."
        )

    languages = (
        f"I am fluent in English and also speak Ukrainian and Russian, which "
        f"enables me to communicate effectively in diverse, international teams."
    )

    closing = (
        f"I am a quick learner who has successfully adapted to life and work in "
        f"the Netherlands. I am motivated, reliable, and eager to contribute "
        f"my skills to {company_name}. I would welcome the opportunity to "
        f"discuss how my experience aligns with your needs.\n\n"
        f"Thank you for considering my application. I look forward to hearing "
        f"from you.\n\n"
        f"Kind regards,\n"
        f"Kateryna Kravchenko"
    )

    return f"{opening}\n\n{body}\n\n{languages}\n\n{closing}"
