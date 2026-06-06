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
from typing import Optional, Union

import httpx

BASE_URL = "https://api.rentcast.io/v1"

# Listing keywords that signal a motivated seller (mirrors web_scraper)
_DISTRESS_KEYWORDS = [
    "motivated", "must sell", "price reduced", "as-is", "as is", "fixer",
    "investor special", "handyman", "cash only", "needs work", "tlc",
    "foreclosure", "bank owned", "reo", "estate sale", "probate",
    "divorce", "relocation", "below market", "quick sale", "bring offers",
]

# Property types that are NOT a rentable/flippable structure. Vacant lots,
# land, and DLBA "infill" parcels have no house to rehab or rent — the AVM
# invents a fake ARV + rent for them, which poisons the deal score. We drop
# them at the source so they never reach the pipeline.
_LAND_PROPERTY_TYPES = {
    "land", "lot", "vacant land", "vacant lot", "vacantland",
    "residential lot", "commercial land", "agricultural", "farm",
}

# Free-text phrases that betray a non-structure listing even when the
# propertyType field is mislabeled (DLBA lots often come through as
# "Single Family" with 0 sqft).
_LAND_TEXT_FLAGS = [
    "infill building", "infill lot", "buildable lot", "vacant lot",
    "vacant land", "build your", "new construction loan",
    "construction plans", "sold as a bundle", "lots totaling",
    "land bank", "dlba", "side lot",
]

# Phrases/names that identify a Detroit Land Bank Authority listing.
# These are real houses with beds/baths/sqft — not vacant lots — but DLBA
# deeds include renovation-compliance clauses; you buy direct, you cannot
# assign the contract. Flag as is_link_only so they're research links only.
_DLBA_OWNERSHIP_FLAGS = [
    "detroit land bank", "building detroit", "own it now",
    "dlba", "land bank authority", "buildingdetroit",
]
# RentCast fields that may carry the listing agent / office / owner name
_AGENT_FIELDS = (
    "listingAgent", "listingAgentName", "agentName",
    "listingOffice", "listingOfficeName", "officeName",
    "ownerName", "sellerName",
)

# A real rental can't yield more than this gross (annual rent / ARV).
# Detroit's best cash-flow houses top out around 18-22%. Anything above
# this is a broken AVM estimate (usually land valued as a house).
MAX_REALISTIC_GROSS_YIELD = 0.25


def has_api_key() -> bool:
    return bool(os.getenv("RENTCAST_API_KEY"))


def _get(path: str, params: dict) -> Optional[Union[list, dict]]:
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

        # Drop vacant land / lots / DLBA infill parcels — they have no
        # structure to rehab, flip, or rent. Leaving them in produces
        # phantom "deals" with invented ARV and rent.
        if _is_non_structure(item):
            continue

        addr = item.get("formattedAddress") or item.get("addressLine1") or "Unknown address"
        dom = item.get("daysOnMarket")
        signals = _signals_from_listing(item)
        # Keep any free-text the listing exposes so downstream filters
        # (owner-finance keyword scan, etc.) can read the real remarks.
        raw_text = " ".join(str(item.get(f, "")) for f in
                            ("listingType", "description", "remarks", "publicRemarks",
                             "listingAgent", "listingOffice", "ownerName")).strip()

        # DLBA-owned houses: real structure but deed bars assignment.
        # Surface as a research link so the user can browse them, but
        # never score them as a wholesale deal or generate outreach.
        is_dlba = _is_land_bank_listing(item)

        lead = {
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
            "property_type":    item.get("propertyType", ""),
            "bedrooms":         item.get("bedrooms"),
            "bathrooms":        item.get("bathrooms"),
            "sqft":             item.get("squareFootage"),
            "year_built":       item.get("yearBuilt"),
            "days_on_market":   dom,
            "lat":              item.get("latitude"),
            "lng":              item.get("longitude"),
            "address_for_avm":  item.get("formattedAddress") or addr,
            "raw_text":         raw_text,
            "distress_signals": signals,
        }
        if is_dlba:
            lead["is_link_only"]   = True
            lead["data_warning"]   = (
                "Detroit Land Bank (DLBA) — buy direct at buildingdetroit.org. "
                "Deed bars assignment; not wholesaleable."
            )
        leads.append(lead)
    return leads


def _is_non_structure(item: dict) -> bool:
    """
    True if this listing is vacant land / a lot / a non-rentable parcel
    rather than an actual house or building.

    Three independent checks (any one trips it):
      1. propertyType explicitly says Land/Lot/Vacant/etc.
      2. Free-text remarks describe an infill lot, land bank parcel, or
         "build your own" (catches DLBA lots mislabeled as Single Family).
      3. Structural signature of a lot: no bedrooms AND no living area.
         (A real house always reports beds or sqft; a lot reports neither.)
    """
    ptype = str(item.get("propertyType", "")).strip().lower()
    if ptype in _LAND_PROPERTY_TYPES or "land" in ptype or ptype == "lot":
        return True

    blob = " ".join(str(item.get(f, "")) for f in
                    ("description", "remarks", "publicRemarks", "listingType")).lower()
    if any(flag in blob for flag in _LAND_TEXT_FLAGS):
        return True

    beds = item.get("bedrooms") or 0
    baths = item.get("bathrooms") or 0
    sqft = item.get("squareFootage") or 0
    if beds == 0 and baths == 0 and sqft == 0:
        return True

    return False


def _is_land_bank_listing(item: dict) -> bool:
    """
    True if this listing is owned/sold by the Detroit Land Bank Authority
    (or any municipal land bank). These are real houses with beds/baths/sqft,
    so they pass _is_non_structure, but they can't be wholesaled — DLBA deeds
    require the buyer to renovate and pass inspection; assignment is barred.
    """
    # Check structured agent/office/owner fields first
    for field in _AGENT_FIELDS:
        val = str(item.get(field, "")).lower()
        if val and any(flag in val for flag in _DLBA_OWNERSHIP_FLAGS):
            return True

    # Check every text field in the raw listing
    blob = " ".join(str(item.get(f, "")) for f in (
        "description", "remarks", "publicRemarks", "listingType",
        "listingAgent", "listingOffice", "ownerName", "sellerName",
    )).lower()
    return any(flag in blob for flag in _DLBA_OWNERSHIP_FLAGS)


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


# ── Owner-finance candidate search ──────────────────────────────────────────────

_OWNER_FINANCE_KEYWORDS = [
    "owner financing", "owner finance", "seller financing", "seller finance",
    "owner will carry", "owc", "will carry", "contract for deed",
    "rent to own", "rent-to-own", "lease to own", "lease option",
    "no bank", "no banks", "terms available", "flexible terms",
]


def search_owner_finance(
    city: str = "", state: str = "", zip_code: str = "",
    max_price: int = 0, limit: int = 100,
) -> list:
    """
    Pull listings and surface owner-finance candidates two ways:
      1. Explicit keyword hit ("owner financing" in the remarks) — high confidence
      2. Free & clear / long-DOM signals — likely-to-carry candidates

    Returns the leads sorted with explicit owner-finance hits first.
    Each lead gets 'owner_finance_signal' and 'owner_finance_confidence'.
    """
    leads = search_sale_listings(
        city=city, state=state, zip_code=zip_code,
        max_price=max_price, limit=limit,
    )
    scored = []
    for lead in leads:
        blob = (f"{lead.get('raw_text','')} {lead.get('description','')} "
                f"{' '.join(lead.get('distress_signals', []))}").lower()
        hits = [kw for kw in _OWNER_FINANCE_KEYWORDS if kw in blob]
        dom = lead.get("days_on_market") or 0

        if hits:
            lead["owner_finance_signal"] = f"Listing says: {hits[0]}"
            lead["owner_finance_confidence"] = "high"
            rank = 0
        elif dom >= 90:
            lead["owner_finance_signal"] = f"On market {dom} days — owner may be open to carrying"
            lead["owner_finance_confidence"] = "medium"
            rank = 1
        else:
            lead["owner_finance_signal"] = "Worth asking — every seller is a maybe"
            lead["owner_finance_confidence"] = "low"
            rank = 2
        scored.append((rank, lead))

    scored.sort(key=lambda x: x[0])
    return [l for _, l in scored]


# ── Luxury / developer-wholesale search ─────────────────────────────────────────

def search_luxury(
    city: str = "", state: str = "", zip_code: str = "",
    min_price: int = 500000, max_price: int = 0, limit: int = 100,
) -> list:
    """
    High-end for-sale listings for developer/luxury wholesale ($500k+ default).
    Same lead shape; flags days-on-market so you can spot stale luxury inventory
    (the ones developers will negotiate hardest on).
    """
    leads = search_sale_listings(
        city=city, state=state, zip_code=zip_code,
        min_price=min_price, max_price=max_price, limit=limit,
    )
    for lead in leads:
        dom = lead.get("days_on_market") or 0
        if dom >= 120:
            lead["luxury_note"] = f"Stale — {dom} days on market, developer leverage"
        elif dom >= 60:
            lead["luxury_note"] = f"{dom} days on market"
        else:
            lead["luxury_note"] = "Fresh listing"
    return leads


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
