"""Configuration constants for Katya Jobs."""

# Home address for commute calculations
HOME_ADDRESS = "Laan van Decima 1B, Haarlem"
HOME_ADDRESS_ENCODED = "Laan+van+Decima+1B,+Haarlem"

# Haarlem coordinates
HAARLEM_LAT = 52.3874
HAARLEM_LNG = 4.6462
MAX_DISTANCE_KM = 25

# Cities within ~25km of Haarlem reachable by public transport
TARGET_CITIES = [
    "Haarlem", "Amsterdam", "Hoofddorp", "Amstelveen", "Zaandam",
    "Schiphol", "Heemstede", "Beverwijk", "Leiden", "IJmuiden",
    "Velsen", "Bloemendaal", "Zandvoort", "Hillegom", "Lisse",
    "Nieuw-Vennep", "Badhoevedorp", "Halfweg", "Spaarndam",
]

# Approximate travel times from Haarlem by public transport (minutes)
COMMUTE_ESTIMATES = {
    "haarlem": {"time": "5-10 min", "distance": "2 km"},
    "heemstede": {"time": "10-15 min", "distance": "5 km"},
    "bloemendaal": {"time": "10-15 min", "distance": "4 km"},
    "zandvoort": {"time": "20 min", "distance": "10 km"},
    "hoofddorp": {"time": "20-30 min", "distance": "15 km"},
    "schiphol": {"time": "20-25 min", "distance": "16 km"},
    "amsterdam": {"time": "15-20 min", "distance": "20 km"},
    "amstelveen": {"time": "30-40 min", "distance": "22 km"},
    "zaandam": {"time": "25-35 min", "distance": "18 km"},
    "ijmuiden": {"time": "25-30 min", "distance": "12 km"},
    "velsen": {"time": "15-20 min", "distance": "8 km"},
    "beverwijk": {"time": "20-30 min", "distance": "15 km"},
    "leiden": {"time": "25-35 min", "distance": "25 km"},
    "hillegom": {"time": "15-20 min", "distance": "10 km"},
    "lisse": {"time": "25-35 min", "distance": "15 km"},
    "nieuw-vennep": {"time": "25-35 min", "distance": "18 km"},
    "badhoevedorp": {"time": "25-35 min", "distance": "17 km"},
    "halfweg": {"time": "15-25 min", "distance": "12 km"},
    "spaarndam": {"time": "10-15 min", "distance": "5 km"},
    "amsterdam-zuidoost": {"time": "35-45 min", "distance": "28 km"},
    "diemen": {"time": "30-40 min", "distance": "25 km"},
    "aalsmeer": {"time": "35-45 min", "distance": "24 km"},
}

# Role types to search for
SEARCH_QUERIES = [
    "accountant",
    "bookkeeper",
    "accounts payable",
    "accounts receivable",
    "financial administrator",
    "office administrator",
    "administration",
    "back office",
    "customer service english",
    "data entry",
    "operations support",
    "sales assistant",
]

# Exclusion keywords (lowercase) — if found in title or description, skip the job
EXCLUDE_KEYWORDS = [
    "dutch required", "dutch speaking", "dutch native", "native dutch",
    "nederlandstalig", "vloeiend nederlands", "dutch is a must",
    "dutch language required", "speaking dutch", "fluent dutch",
    "taaleis: nederlands", "goede beheersing van de nederlandse taal",
    "driving licence", "driving license", "driver's license",
    "rijbewijs", "own car", "eigen auto",
    "chief", "director", "vp ", "vice president", "head of", "c-level",
    "cfo", "cto", "ceo",
]

# Exclusion patterns in title specifically
EXCLUDE_TITLE_KEYWORDS = [
    "senior manager", "senior director", "managing director",
    "head of", "vp ", "chief",
]

# --------------------------------------------------------------------------
# Dutch language detection
# --------------------------------------------------------------------------
DUTCH_WORDS = {
    "vacature", "werkervaring", "functie", "functieomschrijving", "solliciteer",
    "sollicitatie", "arbeidsovereenkomst", "dienstverband", "werknemer",
    "werkgever", "salaris", "maand", "uur", "fulltime", "parttime",
    "zoeken", "bieden", "werken", "kunnen", "hebben", "worden", "binnen",
    "jouw", "onze", "deze", "voor", "naar", "bent", "wordt", "staat",
    "beschikbaar", "ervaring", "minimaal", "kennis", "overleg", "overleggen",
    "zoals", "omdat", "daarnaast", "tevens", "echter", "indien", "graag",
    "bijvoorbeeld", "hieronder", "hierbij", "waarbij", "waardoor",
    "medewerker", "collega", "afdeling", "bedrijf", "organisatie",
    "klant", "klanten", "kantoor", "omgeving", "regio", "gemeente",
    "opleiding", "diploma", "hbo", "mbo", "wo",
    "administratief", "financieel", "financiele", "boekhouder", "boekhouding",
    "assistent", "gevorderd", "verantwoordelijk", "zelfstandig",
    "het", "een", "aan", "met", "ook", "nog", "wel", "niet", "maar",
    "zeer", "alle", "meer", "geen", "bij", "als", "hun",
    "wij zoeken", "wat bied", "wat ga je doen", "wat verwachten wij",
    "jij bent", "jij hebt", "je beschikt over",
    "sociale", "economie", "maatschappij", "impact",
    "ter versterking", "ons team", "per direct",
}

DUTCH_WORD_THRESHOLD_TITLE = 2
DUTCH_WORD_THRESHOLD_BODY = 5

# Scoring weights — higher = better match for Katya's profile
ROLE_SCORES = {
    # Finance (highest — 12 years experience)
    "accountant": 100,
    "bookkeeper": 95,
    "accounts payable": 95,
    "accounts receivable": 95,
    "financial": 90,
    "finance": 90,
    "accounting": 90,
    "credit control": 85,
    "invoice": 85,
    "billing": 85,
    "payroll": 80,
    "tax": 80,
    # Admin (high)
    "office admin": 75,
    "administration": 70,
    "administrative": 70,
    "back office": 70,
    "office manager": 65,
    "data entry": 65,
    "operations support": 60,
    "office assistant": 60,
    # Customer service (medium)
    "customer service": 50,
    "customer support": 50,
    "receptionist": 45,
    "front desk": 45,
    # Retail/sales (lower but still relevant — ZARA experience)
    "sales assistant": 35,
    "retail": 30,
    "shop assistant": 30,
    "store": 25,
}

# Seniority adjustments
SENIORITY_PENALTY = {
    "senior": -20,
    "manager": -15,
    "lead": -10,
    "principal": -20,
    "head": -15,
    "expert": -10,
}

SENIORITY_BONUS = {
    "junior": 15,
    "assistant": 12,
    "entry level": 15,
    "entry-level": 15,
    "starter": 15,
    "trainee": 15,
    "graduate": 12,
    "medior": 5,
    "intern": 10,
    "stagiair": 10,
}

# Bonus points
ENGLISH_BONUS = 15
ENGLISH_ENV_SIGNALS = [
    "english-speaking environment", "no dutch required", "no dutch needed",
    "dutch not required", "english is the working language",
    "english only", "working language is english",
]
ENGLISH_ENV_BONUS = 15  # extra on top of ENGLISH_BONUS

LANGUAGE_ASSET_BONUS = 20  # Ukrainian or Russian mentioned as asset

TEMP_CONTRACT_BONUS = 5  # temp/contract roles

CITY_BONUS = {
    "Haarlem": 10,
    "Hoofddorp": 8,
    "Heemstede": 8,
    "Schiphol": 7,
    "Amsterdam": 5,
    "Amstelveen": 5,
}

# Salary
DEFAULT_MIN_SALARY = 3000  # EUR bruto/month

# Scraper settings
REQUEST_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)
SCRAPE_INTERVAL_HOURS = 6

DATABASE_PATH = "jobs.db"
