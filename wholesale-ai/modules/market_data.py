"""
Market data helpers — property value estimates, rent comps, and deal sourcing intel.
"""
import httpx
from typing import Optional


def get_zip_info(zip_code: str) -> dict:
    """
    Look up basic zip code info via free public API (no auth needed).
    Returns city, state, county for a zip.
    """
    try:
        with httpx.Client(timeout=10) as client:
            r = client.get(f"https://api.zippopotam.us/us/{zip_code}")
            if r.status_code == 200:
                data = r.json()
                place = data.get("places", [{}])[0]
                return {
                    "zip": zip_code,
                    "city": place.get("place name", ""),
                    "state": place.get("state abbreviation", ""),
                    "state_full": place.get("state", ""),
                    "county": place.get("county", ""),
                    "lat": place.get("latitude", ""),
                    "lon": place.get("longitude", ""),
                }
    except Exception:
        pass
    return {"zip": zip_code, "error": "Could not look up zip code"}


def estimate_arv_by_market(market_type: str, sqft: float, bedrooms: int, condition: str) -> dict:
    """
    Rough ARV estimation by market tier. Replace with real comps from MLS/Zillow.
    Market types: 'hot', 'warm', 'cool', 'rural'
    """
    # $/sqft ranges by market — these are conservative estimates
    # User should always verify with real comps (Zillow, Redfin, PropStream)
    price_per_sqft = {
        "hot":   {"light": 180, "medium": 160, "heavy": 140, "gut": 120},
        "warm":  {"light": 130, "medium": 115, "heavy": 100, "gut": 85},
        "cool":  {"light": 90,  "medium": 78,  "heavy": 68,  "gut": 55},
        "rural": {"light": 65,  "medium": 55,  "heavy": 45,  "gut": 35},
    }

    market = market_type.lower()
    if market not in price_per_sqft:
        market = "warm"

    cond = condition.lower()
    if cond not in price_per_sqft[market]:
        cond = "medium"

    ppsf = price_per_sqft[market][cond]
    arv = ppsf * sqft

    # Bedroom adjustment
    if bedrooms <= 1:
        arv *= 0.85
    elif bedrooms == 2:
        arv *= 0.93
    elif bedrooms >= 5:
        arv *= 1.10

    return {
        "estimated_arv": round(arv, -3),  # Round to nearest $1k
        "price_per_sqft": ppsf,
        "market_type": market,
        "condition": cond,
        "disclaimer": "ESTIMATE ONLY — pull real comps from Zillow/Redfin/PropStream before making offers",
        "comp_sources": [
            "https://www.zillow.com/homes/recently-sold/",
            "https://www.redfin.com/",
            "https://www.realtor.com/realestateandhomes-search/",
        ],
    }


def get_repair_cost_guide() -> dict:
    """Standard repair cost ranges for wholesalers. Always get contractor bids."""
    return {
        "disclaimer": "These are rough national averages. Always get 2-3 contractor bids.",
        "systems": {
            "Roof (full replace, 1500sqft)": "$8,000 - $15,000",
            "HVAC (full system)": "$5,000 - $12,000",
            "Electrical (full rewire)": "$8,000 - $20,000",
            "Plumbing (full repipe)": "$5,000 - $15,000",
            "Foundation repair": "$3,000 - $30,000+",
            "Sewer line replace": "$3,000 - $8,000",
        },
        "interior": {
            "Kitchen remodel (mid)": "$15,000 - $30,000",
            "Bathroom remodel (each)": "$5,000 - $15,000",
            "Flooring per sqft": "$3 - $8",
            "Paint interior per sqft": "$1.50 - $3",
            "Drywall per sqft": "$2 - $5",
            "Windows (each)": "$400 - $900",
            "Doors (each)": "$200 - $600",
        },
        "exterior": {
            "Siding (vinyl, per sqft)": "$3 - $10",
            "Paint exterior": "$2,000 - $6,000",
            "Landscaping (basic)": "$500 - $2,500",
            "Driveway (asphalt)": "$2,000 - $5,000",
            "Deck/porch": "$3,000 - $12,000",
        },
        "quick_estimates": {
            "light (cosmetic only)": "$10 - $20/sqft",
            "medium (some systems)": "$25 - $45/sqft",
            "heavy (major systems)": "$45 - $65/sqft",
            "gut (full rehab)": "$65 - $100+/sqft",
        },
    }


def get_wholesale_checklist() -> list:
    """Step-by-step wholesale deal checklist."""
    return [
        "1. FIND THE DEAL — Source from gov lists, tax delinquent, driving for dollars, bandit signs",
        "2. VERIFY OWNERSHIP — County recorder, NETR Online (publicrecords.netronline.com)",
        "3. PULL COMPS — Zillow, Redfin, Realtor.com sold in last 90 days, same neighborhood",
        "4. ESTIMATE REPAIRS — Drive by first, then walkthrough (use $25/sqft for unknown)",
        "5. RUN MAO — (ARV × 0.70) - Repairs - Your fee = Maximum Allowable Offer",
        "6. MAKE CONTACT — Call/door knock seller, build rapport, find their motivation",
        "7. GET IT UNDER CONTRACT — Use your state's standard purchase agreement + assignment clause",
        "8. COLLECT EMD — $500-$2,000 earnest money to show good faith",
        "9. INSPECT — Use inspection period to walk property, scope repairs, verify comps",
        "10. MARKET TO BUYERS — Post to cash buyer list, Facebook groups, Craigslist, BiggerPockets",
        "11. COLLECT ASSIGNMENT FEE — Buyer pays you the spread at closing",
        "12. CLOSE & GET PAID — Title company handles the rest",
    ]


def get_motivated_seller_sources() -> dict:
    """Free and low-cost sources for finding motivated sellers."""
    return {
        "Government / Public Records (Free)": {
            "Tax Delinquent Lists": "Contact county tax assessor — request list of properties with unpaid taxes",
            "Probate Court Records": "Visit county courthouse or search online court records",
            "Notice of Default (NOD)": "Check county recorder for lis pendens filings",
            "Code Violation Lists": "Request from city/county code enforcement office",
            "Vacant Property Registry": "Many cities maintain public lists of vacant properties",
            "Absentee Owner Lists": "Property taxes mailed to address different from property",
        },
        "Government Property Sales (Free to Search)": {
            "HUD Home Store": "https://www.hudhomestore.gov — gov foreclosures 10-30% below market",
            "HomePath (Fannie Mae)": "https://www.homepath.com — Fannie Mae REO properties",
            "HomeSteps (Freddie Mac)": "https://www.homesteps.com — Freddie Mac REO properties",
            "USDA Rural Properties": "https://properties.sc.egov.usda.gov/resales/ — rural gov-owned",
            "GSA Auctions": "https://propertyforsale.gsa.gov/ — federal surplus properties",
            "US Marshals Seizures": "https://www.usmarshals.gov/what-we-do/asset-forfeiture/current-sales",
            "IRS Auctions": "https://www.treasury.gov/auctions/irs/ — seized property",
            "FDIC Failed Banks": "https://www.fdic.gov/bank/individual/failed/ — bank-owned REO",
        },
        "Low Cost / Free Marketing": {
            "Driving for Dollars": "Drive neighborhoods, note vacant/distressed homes, skip trace owners",
            "Bandit Signs": "$1-3/sign — 'We Buy Houses Cash' with your number",
            "Facebook Marketplace": "Post 'Looking to buy houses' in local groups (free)",
            "Craigslist": "Post in Real Estate Wanted section (free)",
            "Direct Mail": "Send yellow letters to absentee owners (~$0.50-1/piece)",
            "Cold Calling": "Pull lists, call with a script (costs your time only)",
            "Door Knocking": "Most effective — zero cost, high conversion",
            "BiggerPockets": "https://www.biggerpockets.com — network with sellers/buyers",
        },
    }
