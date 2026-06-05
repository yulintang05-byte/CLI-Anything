"""
RentCast API connector — the REAL data feed.

This is the fuel for the lead agents. RentCast returns clean JSON for:
  - For-sale listings by city / state / ZIP (no scraping, no 403 bans)
  - Property records (beds, baths, sqft, year, owner-occupancy)
  - AVM value estimate  -> real ARV
  - AVM long-term rent   -> real rent for cash-flow math

Get a key at https://app.rentcast.io  (free tier = 50 calls/mo, then paid).
Set it as an env var:  RENTCAST_API_KEY=your_key_here   (or put it in .env)

Docs: https://developers.rentcast.io/reference/introduction

Every public function degrades gracefully when no key is set or the network
is unavailable: it returns an empty list / None and logs why, so the rest of
the app keeps working on sample data instead of crashing.
"""
import os
from typing import Optional

import httpx

BASE_URL = "https://api.rentcast.io/v1"

# Listing keywords that signal a motivated seller (mirrors web_scraper)
_DISTRESS_KEYWORDS = [
    "motivated", "must sell", "price reduced", "as-is", "as is", "fixer",
    "investor special", "handyman", "cash only", "needs work", "tlc",
    "foreclosure", "bank owned", "reo", "estate sale", "probate",
    "divorce", "relocation", "below market", "quick sale", "bring offers",
]


def has_api_key() -> bool:
    return bool(os.getenv("RENTCAST_API_KEY"))


def _get(path: str, params: dict) -> Optional[list | dict]:
    """
    Authenticated GET against RentCast. Returns parsed JSON, or None on any
    failure (no key, network wall, rate limit, bad response).
    """
    key = os.getenv("RENTCAST_API_KEY")
    if not key:
        return None
    try:
        r = httpx.get(
            f"{BASE_URL}{path}",
            headers={"X-Api-Key": key, "Accept": "application/json"},
            params={k: v for k, v in params.items() if v not in (None, "", 0)},
            timeout=20,
        )
        if r.status_code == 200:
            return r.json()
        # 401 bad key, 429 rate limit, 4xx/5xx — surface nothing, caller handles
        return {"_error": r.status_code, "_body": r.text[:200]}
    except Exception as e:  # network wall, DNS, timeout
        return {"_error": "network", "_body": str(e)[:200]}


# ── For-sale listings ──────────────────────────────────────────────────────────

def search_sale_listings(
    city: str = "",
    state: str = "",
    zip_code: str = "",
    max_price: int = 0,
    min_price: int = 0,
    property_type: str = "",     # "Single Family", "Multi-Family", "Condo", ...
    limit: int = 50,
    status: str = "Active",
) -> list:
    """
    Pull live for-sale listings. Returns leads in the SAME shape the scraper
    produces, so they flow straight into LeadAgent enrichment/scoring.

    Returns [] if no key / network blocked (so the app falls back cleanly).
    """
    data = _get("/listings/sale", {
        "city": city,
        "state": state,
        "zipCode": zip_code,
        "propertyType": property_type,
        "status": status,
        "limit": min(max(limit, 1), 500),
    })

    if not isinstance(data, list):
        return []   # error dict or None — caller decides what to do

    leads = []
    for item in data:
        price = item.get("price") or 0
        if max_price and price > max_price:
            continue
        if min_price and price < min_price:
            continue

        addr = item.get("formattedAddress") or item.get("addressLine1") or "Unknown address"
        dom = item.get("daysOnMarket")
        signals = _signals_from_listing(item)

        leads.append({
            "title":            addr,
            "price":            float(price),
            "url":              f"https://www.rentcast.io/property/{item.get('id','')}",
            "description":      f"{item.get('propertyType','')} · {item.get('bedrooms','?')}bd/"
                                f"{item.get('bathrooms','?')}ba · "
                                f"{item.get('squareFootage','?')} sqft · "
                                f"{dom if dom is not None else '?'} days on market",
            "city":             item.get("city", city),
            "state":            item.get("state", state),
            "zip":              item.get("zipCode", zip_code),
            "source":           "RentCast (live)",
            "bedrooms":         item.get("bedrooms"),
            "bathrooms":        item.get("bathrooms"),
            "sqft":             item.get("squareFootage"),
            "year_built":       item.get("yearBuilt"),
            "days_on_market":   dom,
            "lat":              item.get("latitude"),
            "lng":              item.get("longitude"),
            "address_for_avm":  item.get("formattedAddress") or addr,
            "distress_signals": signals,
        })
    return leads


def _signals_from_listing(item: dict) -> list:
    """Derive motivated-seller signals from structured listing fields + text."""
    signals = []

    dom = item.get("daysOnMarket")
    if isinstance(dom, (int, float)):
        if dom >= 120:
            signals.append("on market 120+ days")
        elif dom >= 90:
            signals.append("on market 90+ days")

    # Price history: any cut is a motivation signal
    history = item.get("history") or {}
    prices = [v.get("price") for v in history.values() if isinstance(v, dict) and v.get("price")]
    if len(prices) >= 2 and prices[0] > prices[-1]:
        signals.append("price reduced")

    # Keyword scan over any free-text RentCast exposes
    blob = " ".join(str(item.get(f, "")) for f in
                    ("listingType", "description", "remarks", "publicRemarks")).lower()
    for kw in _DISTRESS_KEYWORDS:
        if kw in blob and kw not in signals:
            signals.append(kw)

    return signals


# ── AVM: real ARV + real rent ───────────────────────────────────────────────────

def get_value_estimate(address: str) -> Optional[float]:
    """Real AVM value (use as ARV). Returns None if unavailable."""
    data = _get("/avm/value", {"address": address})
    if isinstance(data, dict) and "price" in data:
        return float(data["price"])
    return None


def get_rent_estimate(address: str) -> Optional[float]:
    """Real long-term monthly rent estimate. Returns None if unavailable."""
    data = _get("/avm/rent/long-term", {"address": address})
    if isinstance(data, dict) and "rent" in data:
        return float(data["rent"])
    return None


def enrich_with_avm(lead: dict) -> dict:
    """
    Replace crude ARV/rent guesses with REAL RentCast AVM data when possible.
    Adds 'arv_real' and 'rent_real' keys; leaves lead untouched on failure.
    Costs 2 API calls per lead — only call this on leads worth analyzing.
    """
    addr = lead.get("address_for_avm") or lead.get("title")
    if not addr:
        return lead
    arv = get_value_estimate(addr)
    rent = get_rent_estimate(addr)
    if arv:
        lead["arv_real"] = arv
    if rent:
        lead["rent_real"] = rent
    return lead


# ── Connectivity self-test ──────────────────────────────────────────────────────

def diagnose() -> dict:
    """
    One-call health check. Tells you exactly what's wrong if no data flows:
    missing key, bad key, network wall, or all good.
    """
    if not has_api_key():
        return {"ok": False, "reason": "no_key",
                "fix": "Set RENTCAST_API_KEY in your environment or .env file"}
    probe = _get("/listings/sale", {"city": "Detroit", "state": "MI", "limit": 1})
    if isinstance(probe, list):
        return {"ok": True, "reason": "connected", "sample_count": len(probe)}
    if isinstance(probe, dict) and probe.get("_error") == 401:
        return {"ok": False, "reason": "bad_key",
                "fix": "Your RENTCAST_API_KEY was rejected (401). Recheck the key."}
    if isinstance(probe, dict) and probe.get("_error") == "network":
        return {"ok": False, "reason": "network_blocked",
                "fix": "Outbound network is blocked here. Run on your Mac, not the cloud sandbox.",
                "detail": probe.get("_body", "")}
    return {"ok": False, "reason": "unknown",
            "detail": probe if isinstance(probe, dict) else str(probe)}
