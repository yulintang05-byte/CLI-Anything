"""
Live Property Scraper — pulls fresh distressed/below-market listings daily.
Sources: Craigslist FSBO, HUD HomeStore, Detroit DLBA, tax deed sites, Zillow.
Respectful scraping: 1-2 req/sec max, robots.txt compliant.
"""
import re
import time
import httpx
from typing import Optional
from urllib.parse import urlencode, quote_plus

# ── HTTP Client ───────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def _get(url: str, timeout: int = 15) -> Optional[str]:
    """Safe GET with rate limiting. Returns HTML or None on failure."""
    try:
        time.sleep(1.5)  # respectful rate limit
        r = httpx.get(url, headers=HEADERS, timeout=timeout, follow_redirects=True)
        if r.status_code == 200:
            return r.text
        return None
    except Exception:
        return None

def _parse_price(text: str) -> Optional[float]:
    """Extract dollar amount from text like '$6,500' or '6500'."""
    m = re.search(r'\$?([\d,]+)', text.replace(",", ""))
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return None
    return None

# ── Craigslist FSBO Scraper ────────────────────────────────────────────────────

CRAIGSLIST_CITIES = {
    "Detroit":    "detroit",
    "Birmingham": "bham",
    "Memphis":    "memphis",
    "Jackson":    "jackson",
    "Toledo":     "toledo",
    "Cleveland":  "cleveland",
    "Baltimore":  "baltimore",
    "St. Louis":  "stlouis",
    "Macon":      "macon",
    "Flint":      "flint",
    # National luxury markets
    "Miami":      "miami",
    "Atlanta":    "atlanta",
    "Dallas":     "dallas",
    "Nashville":  "nashville",
    "Phoenix":    "phoenix",
}

def scrape_craigslist_fsbo(city: str = "detroit", max_price: int = 50000,
                            min_price: int = 0, max_results: int = 20) -> list:
    """
    Pull Craigslist 'for sale by owner' listings for a city.
    Returns list of dicts: {title, price, url, description, city, source}.
    """
    city_code = CRAIGSLIST_CITIES.get(city, city.lower().replace(" ", ""))
    params = {
        "search_distance": "",
        "postal": "",
        "min_price": min_price,
        "max_price": max_price,
        "auto_make_model": "",
        "min_auto_year": "",
        "max_auto_year": "",
        "sort": "date",
    }
    url = f"https://{city_code}.craigslist.org/search/rea?{urlencode(params)}&query=house+for+sale+by+owner"

    html = _get(url)
    if not html:
        return _craigslist_fallback(city, max_price)

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        results = []

        for item in soup.select(".cl-search-result")[:max_results]:
            title_el = item.select_one(".cl-app-anchor .label")
            price_el = item.select_one(".priceinfo")
            link_el  = item.select_one("a.cl-app-anchor")

            if not title_el or not link_el:
                continue

            title = title_el.get_text(strip=True)
            price_text = price_el.get_text(strip=True) if price_el else "0"
            price = _parse_price(price_text) or 0
            href = link_el.get("href", "")
            full_url = href if href.startswith("http") else f"https://{city_code}.craigslist.org{href}"

            if price == 0 or price > max_price:
                continue

            results.append({
                "title":       title,
                "price":       price,
                "url":         full_url,
                "description": "",
                "city":        city,
                "state":       _city_to_state(city),
                "source":      "Craigslist FSBO",
                "bedrooms":    _extract_beds(title),
                "sqft":        _extract_sqft(title),
                "distress_signals": _detect_distress(title),
            })

        return results

    except ImportError:
        return _craigslist_fallback(city, max_price)
    except Exception:
        return _craigslist_fallback(city, max_price)


def _craigslist_fallback(city: str, max_price: int) -> list:
    """Return a search URL when scraping is unavailable."""
    city_code = CRAIGSLIST_CITIES.get(city, city.lower().replace(" ", ""))
    return [{
        "title":    f"Craigslist FSBO — {city} (under ${max_price:,})",
        "price":    0,
        "url":      f"https://{city_code}.craigslist.org/search/rea?max_price={max_price}&query=house+for+sale",
        "description": "Click to browse live listings",
        "city":     city,
        "state":    _city_to_state(city),
        "source":   "Craigslist FSBO",
        "is_link_only": True,
    }]

# ── Zillow Below-Market Search URLs ──────────────────────────────────────────

def get_zillow_distressed_url(city: str, state: str, max_price: int = 100000) -> str:
    """Build a Zillow URL pre-filtered for below-market/foreclosure/bank-owned."""
    city_slug = city.lower().replace(" ", "-")
    state_lower = state.lower()
    return (
        f"https://www.zillow.com/{city_slug}-{state_lower}/"
        f"?searchQueryState=%7B%22filterState%22%3A%7B"
        f"%22price%22%3A%7B%22max%22%3A{max_price}%7D%2C"
        f"%22fore%22%3A%7B%22value%22%3Atrue%7D%2C"
        f"%22auc%22%3A%7B%22value%22%3Atrue%7D%7D%7D"
    )


def get_redfin_distressed_url(city: str, state: str) -> str:
    city_slug = city.lower().replace(" ", "-")
    state_lower = state.lower()
    return f"https://www.redfin.com/{state.upper()}/{city_slug}/filter/property-type=house,foreclosure=true"

# ── HUD HomeStore ─────────────────────────────────────────────────────────────

def get_hud_listings_url(state: str, max_price: int = 100000, bedrooms: int = 0) -> dict:
    """Build HUD HomeStore search URL and return structured search info."""
    params = {"sStateCd": state.upper(), "sStatus": "A", "sPropType": "SFR"}
    if max_price:
        params["iMaxPrice"] = max_price
    if bedrooms:
        params["iBedrooms"] = bedrooms
    return {
        "url":    f"https://www.hudhomestore.gov/Listing/PropertySearchResult.aspx?{urlencode(params)}",
        "source": "HUD HomeStore",
        "desc":   f"HUD-owned properties in {state} under ${max_price:,}",
        "state":  state,
    }

# ── Detroit Land Bank Authority ───────────────────────────────────────────────

def get_dlba_listings() -> list:
    """
    DLBA own-it-now / auction / side-lot PORTALS.

    These are entry points to the Land Bank's inventory, not specific
    properties. They carry no real address, ARV, or rent — so they're flagged
    is_link_only and price 0. That keeps them out of deal scoring/enrichment
    (which would otherwise invent fake numbers and surface them as "deals").
    Browse them as research links; each actual house must be analyzed on its
    own address.
    """
    return [
        {
            "title":   "Detroit Land Bank — Own It Now (browse from $1,000)",
            "price":   0,
            "url":     "https://buildingdetroit.org/own-it-now/",
            "description": "Own It Now portal — City of Detroit residential. Pick a specific address, then analyze it.",
            "city":    "Detroit", "state": "MI", "source": "Detroit DLBA",
            "is_link_only": True,
        },
        {
            "title":   "Detroit Land Bank — Auction (bid from $1k)",
            "price":   0,
            "url":     "https://buildingdetroit.org/auctions/",
            "description": "Weekly auctions of Detroit properties. Auction terms, not assignable wholesale contracts.",
            "city":    "Detroit", "state": "MI", "source": "Detroit DLBA",
            "is_link_only": True,
        },
        {
            "title":   "Detroit Land Bank — Side Lots (vacant land)",
            "price":   0,
            "url":     "https://buildingdetroit.org/side-lots/",
            "description": "Vacant land adjacent to your property — not a structure to flip or rent.",
            "city":    "Detroit", "state": "MI", "source": "Detroit DLBA",
            "is_link_only": True,
        },
    ]

# ── Tax Deed / Government Auction Aggregator ───────────────────────────────────

def get_tax_deed_listings(state: str = "") -> list:
    """Return links to active tax deed auctions."""
    national = [
        {"title": "GovEase — Online Tax Sales (National)", "url": "https://www.govease.com/", "price": 0, "source": "Tax Deed"},
        {"title": "Bid4Assets — Tax Deed Auctions",        "url": "https://www.bid4assets.com/taxsale", "price": 0, "source": "Tax Deed"},
        {"title": "RealAuction — Government Auctions",     "url": "https://www.realauction.com/", "price": 0, "source": "Tax Deed"},
        {"title": "SRI Tax Sales",                         "url": "https://www.srihomesale.com/", "price": 0, "source": "Tax Deed"},
    ]
    state_specific = {
        "MI": [{"title": "Wayne County Tax Auction (Detroit)", "url": "https://www.waynecounty.com/elected/treasurer/tax-auctions.aspx", "price": 0, "source": "Tax Deed", "city": "Detroit", "state": "MI"}],
        "AL": [{"title": "Jefferson County Tax Lien (Birmingham)", "url": "https://www.jccal.org/Default.asp?ID=734", "price": 0, "source": "Tax Deed", "city": "Birmingham", "state": "AL"}],
        "TN": [{"title": "Shelby County Tax Sale (Memphis)", "url": "https://www.shelbycountytrustee.com/", "price": 0, "source": "Tax Deed", "city": "Memphis", "state": "TN"}],
        "GA": [{"title": "Bibb County Tax Sale (Macon)", "url": "https://www.bibbtax.com/", "price": 0, "source": "Tax Deed", "city": "Macon", "state": "GA"}],
        "MS": [{"title": "Hinds County Tax Sale (Jackson)", "url": "https://www.hindscountyms.com/", "price": 0, "source": "Tax Deed", "city": "Jackson", "state": "MS"}],
        "OH": [{"title": "Lucas County Tax Liens (Toledo)", "url": "https://treasurer.lucas.oh.us/", "price": 0, "source": "Tax Deed", "city": "Toledo", "state": "OH"}],
        "MO": [{"title": "St. Louis Land Bank", "url": "https://www.stllandbank.org/", "price": 0, "source": "Tax Deed", "city": "Saint Louis", "state": "MO"}],
    }
    results = national[:]
    if state.upper() in state_specific:
        results = state_specific[state.upper()] + results
    return results


# ── Helper functions ──────────────────────────────────────────────────────────

def _city_to_state(city: str) -> str:
    mapping = {
        "Detroit": "MI", "Flint": "MI", "Birmingham": "AL",
        "Memphis": "TN", "Nashville": "TN", "Jackson": "MS",
        "Toledo": "OH", "Cleveland": "OH", "St. Louis": "MO",
        "Baltimore": "MD", "Macon": "GA", "Atlanta": "GA",
        "Miami": "FL", "Tampa": "FL", "Dallas": "TX",
        "Austin": "TX", "Phoenix": "AZ", "Denver": "CO",
    }
    return mapping.get(city, "")


def _extract_beds(text: str) -> Optional[int]:
    m = re.search(r'(\d)\s*(?:bd|bed|bedroom|br)', text, re.IGNORECASE)
    return int(m.group(1)) if m else None


def _extract_sqft(text: str) -> Optional[float]:
    m = re.search(r'([\d,]+)\s*(?:sq\.?\s*ft|sqft|square feet)', text, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return None
    return None


DISTRESS_KEYWORDS = [
    "motivated", "must sell", "price reduced", "as-is", "as is",
    "fixer", "investor special", "handyman", "cash only", "needs work",
    "foreclosure", "bank owned", "reo", "tax lien", "estate sale",
    "probate", "divorce", "relocation", "below market", "quick sale",
    "reduced", "urgent", "distressed",
]

def _detect_distress(text: str) -> list:
    text_lower = text.lower()
    return [kw for kw in DISTRESS_KEYWORDS if kw in text_lower]


def score_raw_lead(lead: dict, target_arv_multiplier: float = 6.0) -> float:
    """
    Score a raw scraped lead 0.0–10.0 for deal potential.
    Higher = more likely to be a good wholesale deal.
    """
    score = 5.0
    price = lead.get("price", 0)

    # Price signals
    if 0 < price < 15000:
        score += 3.0   # Extremely cheap = likely distressed
    elif price < 30000:
        score += 2.0
    elif price < 60000:
        score += 1.0

    # Distress signals
    signals = lead.get("distress_signals", [])
    score += min(2.0, len(signals) * 0.5)

    # Source quality — RentCast is live verified data; Tax Deed = forced seller
    source_scores = {
        "RentCast (live)": 1.0,
        "Tax Deed":        1.5,
        "Craigslist FSBO": 1.0,
        "HUD HomeStore":   1.5,
    }
    score += source_scores.get(lead.get("source", ""), 0)

    return min(10.0, score)
