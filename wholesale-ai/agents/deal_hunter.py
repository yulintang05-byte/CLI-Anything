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

# ── LANDLORD / CASH-FLOW GATE ────────────────────────────────────────────────
# Detroit/Midwest are RENTAL markets, not flip markets. A $40k house renting
# Section 8 at $1,200/mo is a real wholesale-to-landlord deal even when the flip
# spread is thin. The flip-only gate threw all of these away (Irving's scan:
# 1,628 listings -> 0). This second gate catches the cash-flow deals — honestly.
#
# Honesty rails (so we never resurrect a fake "deal"):
#   - Rents are the conservative Section-8-collectable floor (HUD-FMR-style), not
#     optimistic Zillow market rent.
#   - Real Detroit-grade carrying costs: high property tax + insurance + 31% of
#     gross to vacancy/maintenance/management/capex.
#   - A buyer-required cap rate by region (Midwest C-class demands more than FL).
#   - Same scope-based rehab as the flip path (conservative; rentals often need
#     less, so we under-claim our fee, never over-claim).

# Conservative monthly rent by city -> {bedrooms: rent}. Section-8 floor, not
# top-of-market. Mirrors the baked-constant philosophy of the PPSF table above.
RENT_FMR = {
    # Detroit metro
    "detroit": {1: 750, 2: 950, 3: 1200, 4: 1400},
    "flint": {1: 650, 2: 800, 3: 1000, 4: 1200},
    "warren": {1: 900, 2: 1150, 3: 1450, 4: 1650},
    "dearborn": {1: 950, 2: 1200, 3: 1500, 4: 1700},
    "redford": {1: 900, 2: 1100, 3: 1400, 4: 1600},
    "pontiac": {1: 850, 2: 1050, 3: 1300, 4: 1500},
    "southfield": {1: 950, 2: 1200, 3: 1500, 4: 1750},
    "taylor": {1: 900, 2: 1100, 3: 1400, 4: 1600},
    # South / Midwest
    "birmingham": {1: 800, 2: 950, 3: 1200, 4: 1400},
    "memphis": {1: 850, 2: 1050, 3: 1300, 4: 1550},
    "cleveland": {1: 750, 2: 950, 3: 1200, 4: 1400},
    "toledo": {1: 700, 2: 850, 3: 1050, 4: 1250},
    # Florida
    "jacksonville": {1: 1100, 2: 1350, 3: 1600, 4: 1900},
    "orlando": {1: 1350, 2: 1600, 3: 1900, 4: 2250},
    "tampa": {1: 1400, 2: 1650, 3: 2000, 4: 2400},
    "st. petersburg": {1: 1450, 2: 1700, 3: 2050, 4: 2450},
    "lakeland": {1: 1150, 2: 1350, 3: 1650, 4: 1950},
    "ocala": {1: 1000, 2: 1200, 3: 1450, 4: 1700},
    "palm bay": {1: 1200, 2: 1400, 3: 1700, 4: 2000},
    "pensacola": {1: 1050, 2: 1250, 3: 1550, 4: 1850},
    "cape coral": {1: 1350, 2: 1600, 3: 1900, 4: 2250},
    "port st. lucie": {1: 1450, 2: 1700, 3: 2000, 4: 2400},
    "fort myers": {1: 1300, 2: 1550, 3: 1850, 4: 2200},
    "kissimmee": {1: 1350, 2: 1600, 3: 1900, 4: 2250},
    "deltona": {1: 1200, 2: 1400, 3: 1700, 4: 2000},
    "spring hill": {1: 1150, 2: 1350, 3: 1650, 4: 1950},
    "winter haven": {1: 1100, 2: 1300, 3: 1600, 4: 1900},
    "tallahassee": {1: 1050, 2: 1250, 3: 1550, 4: 1850},
    "gainesville": {1: 1150, 2: 1350, 3: 1650, 4: 1950},
    "daytona beach": {1: 1150, 2: 1350, 3: 1650, 4: 1950},
    "new port richey": {1: 1200, 2: 1400, 3: 1700, 4: 2000},
    "bradenton": {1: 1350, 2: 1600, 3: 1900, 4: 2250},
    "sarasota": {1: 1500, 2: 1750, 3: 2100, 4: 2500},
}

# Annual property tax as a % of acquisition basis (price + rehab). Detroit's
# effective non-homestead rate is among the highest in the US — model it honestly.
STATE_TAX_RATE = {"MI": 0.030, "OH": 0.020, "AL": 0.006, "TN": 0.009,
                  "FL": 0.013, "GA": 0.011}
# Annual landlord insurance ($). FL is in an insurance crisis; Detroit age/crime.
STATE_INSURANCE = {"MI": 1500, "OH": 1300, "AL": 1500, "TN": 1300,
                   "FL": 2600, "GA": 1400}
# Variable operating expenses as a fraction of gross rent.
VACANCY, MAINTENANCE, MANAGEMENT, CAPEX = 0.08, 0.10, 0.08, 0.05
VAR_OPEX = VACANCY + MAINTENANCE + MANAGEMENT + CAPEX  # 0.31

# Buyer-required cap rate (net yield). Midwest C-class buyers demand more than FL.
REQ_CAP = {"midwest": 0.10, "south": 0.09, "southeast": 0.07}


def _ppsf(city: str) -> float:
    return PPSF.get(city.strip().lower(), 0)


def _rent_estimate(city: str, beds) -> int:
    """Conservative Section-8-collectable monthly rent for a city + bed count."""
    table = RENT_FMR.get(city.strip().lower())
    if not table:
        return 0
    try:
        b = int(beds)
    except (TypeError, ValueError):
        b = 3
    b = max(1, min(4, b))
    return table.get(b, table.get(3, 0))


def _landlord_eval(price, rehab, city, state, region, beds) -> "dict | None":
    """
    Score the buy-and-hold path: what an end landlord can pay (incl. our fee) and
    still hit their required net yield. Returns the metrics + our fee room, or
    None if there's no rent data / the deal can't cash flow.
    """
    rent = _rent_estimate(city, beds)
    if not rent:
        return None
    gross = rent * 12
    basis = price + rehab                       # acquisition basis for tax/yield
    taxes = basis * STATE_TAX_RATE.get(state, 0.013)
    insurance = STATE_INSURANCE.get(state, 1500)
    opex = gross * VAR_OPEX + taxes + insurance
    noi = gross - opex
    if noi <= 0:
        return None
    req_cap = REQ_CAP.get(region, 0.09)
    max_all_in = noi / req_cap                   # most a buyer pays incl. our fee
    landlord_fee = max_all_in - rehab - price    # room left for the assignment
    gross_yield = gross / basis if basis else 0
    return {
        "monthly_rent": rent,
        "annual_gross": round(gross),
        "noi": round(noi),
        "req_cap": req_cap,
        "max_all_in": round(max_all_in),
        "landlord_fee": round(landlord_fee),
        "gross_yield": round(gross_yield, 3),
    }


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

    # ── Path 1: FLIP (70% rule for a fix-and-flip buyer) ──────────────────────
    flip_fee = ARV_RULE * arv - repairs - price
    fee_heavy = ARV_RULE * arv - repairs_heavy - price

    # ── Path 2: LANDLORD (cash-flow buyer — the real Detroit/Midwest lever) ───
    ll = _landlord_eval(price, repairs, city, state, region, beds)
    landlord_fee = ll["landlord_fee"] if ll else 0

    # A candidate survives if EITHER buyer type leaves us room for our fee.
    best_fee = max(flip_fee, landlord_fee)
    if best_fee < MIN_FEE:
        return None  # THE GATE — fails for both flippers and landlords

    flip_ok = flip_fee >= MIN_FEE
    landlord_ok = landlord_fee >= MIN_FEE
    deal_type = ("both" if (flip_ok and landlord_ok)
                 else "flip" if flip_ok else "landlord")
    # The fee we lead with is the buyer type that pays the most.
    primary_fee = flip_fee if flip_fee >= landlord_fee else landlord_fee

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
        # Flip path
        "flip_fee": round(flip_fee), "fee_if_heavy": round(fee_heavy),
        "survives_heavy": fee_heavy >= MIN_FEE,
        # Landlord path
        "deal_type": deal_type,
        "landlord_fee": round(landlord_fee),
        "monthly_rent": ll["monthly_rent"] if ll else 0,
        "annual_gross": ll["annual_gross"] if ll else 0,
        "noi": ll["noi"] if ll else 0,
        "cap_rate_target": ll["req_cap"] if ll else 0,
        "gross_yield": ll["gross_yield"] if ll else 0,
        "landlord_max_all_in": ll["max_all_in"] if ll else 0,
        # Combined ranking fee + back-compat alias
        "honest_fee": round(primary_fee), "best_fee": round(best_fee),
        "fee_flag": "VERIFY (too good — check rent/ARV)" if best_fee > FEE_SANITY_CEILING else "",
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

    # dedupe by address, keep best combined fee
    by_addr = {}
    for c in candidates:
        a = c["address"]
        if a not in by_addr or c["best_fee"] > by_addr[a]["best_fee"]:
            by_addr[a] = c
    ranked = sorted(by_addr.values(), key=lambda x: x["best_fee"], reverse=True)

    flips = sum(1 for c in ranked if c["deal_type"] in ("flip", "both"))
    landlords = sum(1 for c in ranked if c["deal_type"] in ("landlord", "both"))
    result = {
        "generated": started, "finished": datetime.now().isoformat(),
        "listings_pulled": pulled, "candidates_passing_gate": len(ranked),
        "flip_candidates": flips, "landlord_candidates": landlords,
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
    print(f"\n{r['candidates_passing_gate']} candidates clear the ${MIN_FEE:,}+ gate "
          f"({r['flip_candidates']} flip / {r['landlord_candidates']} landlord)\n")
    for i, c in enumerate(r["candidates"][:15], 1):
        heavy = "✓survives heavy" if c["survives_heavy"] else "✗fails if heavy rehab"
        flag = f"  ⚠{c['fee_flag']}" if c["fee_flag"] else ""
        print(f"{i:>2}. ${c['best_fee']:>7,} fee [{c['deal_type'].upper()}] | {c['address']}")
        print(f"     ask ${c['price']:,} | ARV(mkt) ${c['arv_market']:,} @${c['ppsf_market']}/sqft | "
              f"{c['beds']}bd/{c['sqft']}sf {c['year_built']} {c['property_type']}")
        print(f"     rehab[{c['rehab_scope']}] ${c['repairs']:,} | flip fee ${c['flip_fee']:,} "
              f"({heavy}) | landlord fee ${c['landlord_fee']:,}")
        if c["monthly_rent"]:
            print(f"     RENT ${c['monthly_rent']:,}/mo | NOI ${c['noi']:,}/yr | "
                  f"gross yield {c['gross_yield']*100:.1f}% | buyer pays ≤${c['landlord_max_all_in']:,}{flag}")
        print(f"     AGENT: {c['agent_name']} | {c['agent_phone']} | {c['agent_email']}")
