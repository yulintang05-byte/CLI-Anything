"""
deal_hunter.py — Honest live wholesale deal engine.

Rebuilt 2026-06-09 (IRVING node, per Irving's mandate) to fix the data-quality
bugs that made the old scan surface fake "high margin" leads:

  1. repairs were $0 on every lead  -> inject real rehab via estimate_by_scope
  2. ARV used raw RentCast AVM (15-33% over market) -> use market PPSF
  3. DLBA / land-bank listings leaked the phantom filter -> text backstop
  4. no channel data -> capture the listing agent (the real contact)

The gate is fixed and non-negotiable:
    honest_fee = 0.70 * ARV_market - real_repairs - asking_price
    PASS only if honest_fee >= MIN_FEE and the lead is real + assignable.

This engine pulls LIVE RentCast for-sale listings (Detroit/Midwest + Florida),
scores each with honest numbers, and ranks the survivors. It does NOT generate
outreach — that happens only after a human/swarm verifies a survivor.
"""
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from modules.rehab_estimator import estimate_by_scope  # noqa: E402

MIN_FEE = 5_000          # Irving's floor (5k-15k target)
ARV_RULE = 0.70          # 70% rule for the end buyer
FEE_SANITY_CEILING = 40_000   # above this, ARV is suspect -> flag for recheck

# Conservative resale ARV $/sqft by metro (after-repair, modest finish).
# Midwest numbers mirror the system's quick_comp_check table.
PPSF = {
    # Midwest / South (cheap acquisition, low ARV)
    "detroit": 55, "flint": 45, "warren": 90, "dearborn": 110, "redford": 75,
    "pontiac": 70, "southfield": 95, "taylor": 95,
    "birmingham": 60, "memphis": 65, "cleveland": 75, "toledo": 60,
    # Florida (higher ARV survives rehab better; skip Miami - too pricey)
    "jacksonville": 165, "orlando": 175, "tampa": 185, "st. petersburg": 200,
    "lakeland": 150, "ocala": 140, "palm bay": 160, "pensacola": 150,
    "cape coral": 190, "port st. lucie": 195, "fort myers": 185,
    "kissimmee": 175, "deltona": 160, "spring hill": 155, "winter haven": 150,
    "tallahassee": 150, "gainesville": 165, "daytona beach": 160,
    "new port richey": 165, "bradenton": 185, "sarasota": 200,
}

# (city, state, max_price). FL needs a higher cap than MI to find inventory.
MARKETS = [
    ("Detroit", "MI", 80_000), ("Flint", "MI", 60_000),
    ("Pontiac", "MI", 90_000), ("Redford", "MI", 110_000),
    ("Birmingham", "AL", 90_000), ("Memphis", "TN", 110_000),
    ("Jacksonville", "FL", 230_000), ("Orlando", "FL", 250_000),
    ("Tampa", "FL", 250_000), ("Lakeland", "FL", 220_000),
    ("Ocala", "FL", 200_000), ("Palm Bay", "FL", 220_000),
    ("Pensacola", "FL", 210_000), ("Deltona", "FL", 220_000),
    ("Spring Hill", "FL", 220_000), ("Winter Haven", "FL", 210_000),
    ("Port St. Lucie", "FL", 250_000),
]

_REGION = {"FL": "southeast", "MI": "midwest", "AL": "south", "TN": "south",
           "OH": "midwest", "GA": "southeast"}

_LANDBANK_FLAGS = ("land bank", "landbank", "buildingdetroit", "own it now",
                   "dlba", "side lot", "bundle", "package deal", "must rehab",
                   "renovation agreement", "compliance period")


def _ppsf(city: str) -> float:
    return PPSF.get(city.strip().lower(), 0)


def _pick_scope(year, asking_ppsf, mkt_ppsf) -> str:
    """Defensible rehab scope from price discount + age (no eyes-on)."""
    disc = (asking_ppsf / mkt_ppsf) if mkt_ppsf else 1.0
    if disc < 0.30:
        return "heavy"            # priced like a shell
    if disc < 0.55:
        return "medium"
    return "light" if (year and year >= 1985) else "medium"


def _rentcast_sale(city: str, state: str, max_price: int, limit: int = 100):
    key = os.getenv("RENTCAST_API_KEY")
    if not key:
        return {"_error": "no RENTCAST_API_KEY"}
    qs = urllib.parse.urlencode({
        "city": city, "state": state, "status": "Active",
        "maxPrice": max_price, "limit": limit,
    })
    url = f"https://api.rentcast.io/v1/listings/sale?{qs}"
    req = urllib.request.Request(url, headers={"X-Api-Key": key,
                                               "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"_error": str(e)}


def _is_landbank(rec: dict) -> bool:
    blob = json.dumps(rec).lower()
    return any(f in blob for f in _LANDBANK_FLAGS)


def evaluate(rec: dict) -> dict | None:
    """Turn one raw RentCast listing into an honestly-scored candidate, or None."""
    price = rec.get("price") or 0
    sqft = rec.get("squareFootage") or 0
    beds = rec.get("bedrooms")
    ptype = (rec.get("propertyType") or "").lower()
    city = rec.get("city") or ""
    state = rec.get("state") or ""

    # Hard rejects: no structure, vacant land, land-bank, no price
    if price <= 0 or not sqft or sqft <= 0 or not beds:
        return None
    if "land" in ptype or "lot" in ptype:
        return None
    # Manufactured/mobile = land-lease park, depreciating, ARV is land-dependent.
    # Our stick-built PPSF wildly overvalues them -> exclude from wholesale hunt.
    if "manufactured" in ptype or "mobile" in ptype:
        return None
    # Sqft outliers = commercial/institutional, not a wholesaleable house.
    if sqft > 4000:
        return None
    if _is_landbank(rec):
        return None

    mkt_ppsf = _ppsf(city)
    if not mkt_ppsf:
        return None  # no defensible ARV -> don't guess

    arv = mkt_ppsf * sqft
    asking_ppsf = price / sqft
    scope = _pick_scope(rec.get("yearBuilt"), asking_ppsf, mkt_ppsf)
    region = _REGION.get(state, "south")
    baths = int(rec.get("bathrooms") or 1)
    rep = estimate_by_scope(sqft, scope, region=region,
                            bedrooms=int(beds), bathrooms=baths)
    repairs = rep["total_mid"]
    repairs_heavy = estimate_by_scope(sqft, "heavy", region=region,
                                      bedrooms=int(beds), bathrooms=baths)["total_mid"]

    fee = ARV_RULE * arv - repairs - price
    fee_heavy = ARV_RULE * arv - repairs_heavy - price

    if fee < MIN_FEE:
        return None  # THE GATE

    agent = rec.get("listingAgent") or {}
    office = rec.get("listingOffice") or {}
    return {
        "address": rec.get("formattedAddress"),
        "city": city, "state": state, "zip": rec.get("zipCode"),
        "price": round(price), "sqft": sqft, "beds": beds,
        "baths": rec.get("bathrooms"), "year_built": rec.get("yearBuilt"),
        "property_type": rec.get("propertyType"),
        "arv_market": round(arv), "ppsf_market": mkt_ppsf,
        "asking_ppsf": round(asking_ppsf, 1),
        "rehab_scope": scope, "repairs": round(repairs),
        "repairs_heavy": round(repairs_heavy),
        "honest_fee": round(fee), "fee_if_heavy": round(fee_heavy),
        "survives_heavy": fee_heavy >= MIN_FEE,
        "fee_flag": "VERIFY ARV (too good)" if fee > FEE_SANITY_CEILING else "",
        "days_on_market": rec.get("daysOnMarket"),
        "listing_type": rec.get("listingType"),
        "mls_number": rec.get("mlsNumber"), "mls_name": rec.get("mlsName"),
        "agent_name": agent.get("name"), "agent_phone": agent.get("phone"),
        "agent_email": agent.get("email"),
        "office_name": office.get("name"),
        "source": "RentCast (live)",
        "rentcast_url": f"https://www.rentcast.io/property/{(rec.get('formattedAddress') or '').replace(' ', '-')}",
    }


def hunt() -> dict:
    started = datetime.now().isoformat()
    pulled = 0
    candidates = []
    market_log = []
    for city, state, cap in MARKETS:
        data = _rentcast_sale(city, state, cap)
        if isinstance(data, dict) and data.get("_error"):
            market_log.append(f"{city},{state}: ERROR {data['_error']}")
            continue
        recs = data if isinstance(data, list) else []
        pulled += len(recs)
        passes = 0
        for rec in recs:
            c = evaluate(rec)
            if c:
                candidates.append(c)
                passes += 1
        market_log.append(f"{city},{state}: {len(recs)} live -> {passes} pass gate")
        time.sleep(0.4)  # be polite to the API

    # dedupe by address, keep best fee
    by_addr = {}
    for c in candidates:
        a = c["address"]
        if a not in by_addr or c["honest_fee"] > by_addr[a]["honest_fee"]:
            by_addr[a] = c
    ranked = sorted(by_addr.values(), key=lambda x: x["honest_fee"], reverse=True)

    result = {
        "generated": started, "finished": datetime.now().isoformat(),
        "listings_pulled": pulled, "candidates_passing_gate": len(ranked),
        "min_fee_gate": MIN_FEE, "market_log": market_log,
        "candidates": ranked,
    }
    out = Path(__file__).resolve().parent.parent / "output" / "deal_candidates.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2, default=str))
    return result


if __name__ == "__main__":
    r = hunt()
    print(f"\n=== HONEST DEAL HUNT ===")
    print(f"Pulled {r['listings_pulled']} live listings across {len(MARKETS)} markets")
    for m in r["market_log"]:
        print("  ", m)
    print(f"\n{r['candidates_passing_gate']} candidates clear the ${MIN_FEE:,}+ honest-fee gate\n")
    for i, c in enumerate(r["candidates"][:15], 1):
        heavy = "✓survives heavy" if c["survives_heavy"] else "✗fails if heavy rehab"
        flag = f"  ⚠{c['fee_flag']}" if c["fee_flag"] else ""
        print(f"{i:>2}. ${c['honest_fee']:>7,} fee | {c['address']}")
        print(f"     ask ${c['price']:,} | ARV(mkt) ${c['arv_market']:,} @${c['ppsf_market']}/sqft | "
              f"{c['beds']}bd/{c['sqft']}sf {c['year_built']} {c['property_type']}")
        print(f"     rehab[{c['rehab_scope']}] ${c['repairs']:,} | {heavy} (fee@heavy ${c['fee_if_heavy']:,}) | "
              f"DOM {c['days_on_market']} | {c['listing_type']}{flag}")
        print(f"     AGENT: {c['agent_name']} | {c['agent_phone']} | {c['agent_email']}")
