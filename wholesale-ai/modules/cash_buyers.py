"""
Cash Buyer Database + Deal Matcher

When a deal scores HIGH MARGIN, this module instantly surfaces:
  1. The buyer types most likely to close this deal
  2. Where to find real buyers in that market right now
  3. What to say to lock them in
  4. Platform shortcuts sorted by speed

Local buyer list stored in ~/.wholesale-ai/buyer_list.json so every buyer
you personally add is remembered and matched on future deals.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


BUYER_DIR  = Path.home() / ".wholesale-ai"
BUYER_FILE = BUYER_DIR / "buyer_list.json"


# ── Buyer type profiles by deal parameters ──────────────────────────────────

BUYER_PROFILES = {
    "Turnkey Landlord": {
        "description": "Buys rent-ready or lightly fixed properties to hold as rentals.",
        "wants":       "Working HVAC/plumbing, decent neighborhood, 1%+ rent-to-price rule.",
        "price_range": "$30k–$150k",
        "daysToClose": "14–30 days",
        "signals":     ["section8_friendly", "cash_flow_positive", "low_vacancy_area"],
        "pitch":       "This one cash flows $X/mo from day one. Tenant ready, easy hold.",
        "find_at": [
            "Local REIA meetings — landlords always attend",
            "Facebook: search '[City] Landlords' or 'Section 8 Landlords Network'",
            "County records: search deed transfers — repeat buyers are landlords",
            "BiggerPockets forums: post in your city's sub-forum",
        ],
    },
    "Fix & Flip Investor": {
        "description": "Buys distressed, does full rehab, sells retail in 3-6 months.",
        "wants":       "Deep discount (65-70% ARV max), clear title, distressed condition OK.",
        "price_range": "$20k–$200k depending on market",
        "daysToClose": "7–21 days (often cash or HML)",
        "signals":     ["high_discount", "needs_rehab", "good_flip_market"],
        "pitch":       "ARV $X. Buy at $Y. Repairs ~$Z. You're all-in at $W — profit $P.",
        "find_at": [
            "Your county recorder's office — pull recent cash sales, call the buyers",
            "PropStream: filter cash buyers in your zip, export list, cold call",
            "Facebook Marketplace: flip investors are often there buying, post your deal",
            "Local contractor referrals — flippers use the same crews repeatedly",
        ],
    },
    "Developer / Builder": {
        "description": "Buys land or teardowns for new construction or large renovations.",
        "wants":       "Right zoning, buildable lot, infill location, fair land price.",
        "price_range": "$100k–$5M",
        "daysToClose": "30–60 days",
        "signals":     ["luxury_market", "infill_lot", "teardown_candidate"],
        "pitch":       "Infill lot in [area]. Zoned [X]. Comps for new builds at $Y+.",
        "find_at": [
            "Building permit records — developers pull permits, their name is public",
            "LoopNet, CoStar — developers list their projects there",
            "LinkedIn: 'real estate developer [City]' — connect and DM",
            "Local AIA (architects) — they know who's building what",
        ],
    },
    "BRRRR Investor": {
        "description": "Buy + rehab + rent + refi + repeat — recycling capital.",
        "wants":       "Buy price + rehab well under 75% ARV. Cash flow after refi.",
        "price_range": "$15k–$80k (low-cost markets)",
        "daysToClose": "14–30 days",
        "signals":     ["brrrr_positive", "low_price_market", "rental_viable"],
        "pitch":       "All-in $X. ARV $Y. Refi at 75% = $Z back. Holds like this do forever.",
        "find_at": [
            "BiggerPockets.com — BRRRR is their #1 strategy, tons of active buyers",
            "Facebook: 'BRRRR real estate investors' group — 50k+ members",
            "Bigger Pockets Marketplace — post deal there directly",
            "Local hard money lenders — their repeat borrowers are BRRRR buyers",
        ],
    },
    "Section 8 Specialist": {
        "description": "Specifically targets rentals to Section 8 voucher holders.",
        "wants":       "HUD-inspectable condition, meets FMR rent, good tenant turnover area.",
        "price_range": "$15k–$80k",
        "daysToClose": "7–21 days",
        "signals":     ["section8_viable", "fmr_covers_rent", "stable_area"],
        "pitch":       "HUD FMR in this area = $X. Gov pays you directly. Near-zero vacancy.",
        "find_at": [
            "GoSection8.com — landlords list there, contact them directly",
            "Facebook: 'Section 8 Landlords Network' (national group 30k+ members)",
            "Local PHA office — they maintain landlord lists, can refer",
            "Affordable Housing Online — landlords are active buyers in S8 areas",
        ],
    },
    "Wholesale Rebuyer / Co-Wholesaler": {
        "description": "Another wholesaler who has a buyer list you don't have yet.",
        "wants":       "Solid spread left after their cut, clean title commitment, proof of contract.",
        "price_range": "Any",
        "daysToClose": "7–14 days",
        "signals":     ["any_deal", "fast_close_needed"],
        "pitch":       "Got a deal, need a buyer. Split the fee. Here's the contract and numbers.",
        "find_at": [
            "Your local REIA — network with other wholesalers",
            "Facebook: 'Wholesale Real Estate Nation' — 200k+ members",
            "Title companies — they know all the active wholesalers, ask for referrals",
            "Cold message 5 BiggerPockets users active in your market today",
        ],
    },
    "Vacation / STR Investor": {
        "description": "Buys properties for Airbnb / short-term rental income.",
        "wants":       "Tourist area, near attractions, allows STR, strong Airbnb comps.",
        "price_range": "$100k–$600k",
        "daysToClose": "21–45 days",
        "signals":     ["tourist_area", "waterfront", "near_attractions"],
        "pitch":       "AirDNA shows $X/mo STR income here. Comps selling at $Y. Price $Z.",
        "find_at": [
            "Airbnb host community groups on Facebook",
            "BiggerPockets STR sub-forum",
            "AirDNA investor marketplace",
            "Local real estate meetups in vacation markets",
        ],
    },
}

# ── Market → Buyer type mapping ──────────────────────────────────────────────

MARKET_BUYER_TYPES = {
    # Low-cost metro markets → landlords + BRRRR + S8
    "detroit":      ["Turnkey Landlord", "BRRRR Investor", "Section 8 Specialist", "Fix & Flip Investor"],
    "birmingham":   ["Turnkey Landlord", "BRRRR Investor", "Section 8 Specialist", "Fix & Flip Investor"],
    "memphis":      ["Turnkey Landlord", "BRRRR Investor", "Section 8 Specialist", "Fix & Flip Investor"],
    "cleveland":    ["Turnkey Landlord", "BRRRR Investor", "Fix & Flip Investor"],
    "baltimore":    ["Turnkey Landlord", "BRRRR Investor", "Section 8 Specialist"],
    "st. louis":    ["Turnkey Landlord", "BRRRR Investor", "Fix & Flip Investor"],
    "jackson":      ["Turnkey Landlord", "BRRRR Investor", "Section 8 Specialist"],
    "indianapolis": ["Turnkey Landlord", "BRRRR Investor", "Fix & Flip Investor"],
    "kansas city":  ["Turnkey Landlord", "BRRRR Investor", "Fix & Flip Investor"],
    "cincinnati":   ["Turnkey Landlord", "Fix & Flip Investor"],
    # Flip-heavy markets
    "atlanta":      ["Fix & Flip Investor", "Turnkey Landlord", "Developer / Builder"],
    "houston":      ["Fix & Flip Investor", "Turnkey Landlord", "Developer / Builder"],
    "dallas":       ["Fix & Flip Investor", "Developer / Builder", "BRRRR Investor"],
    "chicago":      ["Fix & Flip Investor", "Turnkey Landlord", "Section 8 Specialist"],
    "philadelphia": ["Fix & Flip Investor", "Turnkey Landlord", "Section 8 Specialist"],
    "phoenix":      ["Fix & Flip Investor", "BRRRR Investor", "Developer / Builder"],
    # Luxury / developer markets
    "miami":        ["Developer / Builder", "Luxury Buyer", "Vacation / STR Investor"],
    "los angeles":  ["Developer / Builder", "Fix & Flip Investor"],
    "new york":     ["Developer / Builder", "Fix & Flip Investor"],
    "nashville":    ["Fix & Flip Investor", "Vacation / STR Investor", "BRRRR Investor"],
    "tampa":        ["Fix & Flip Investor", "Vacation / STR Investor", "Turnkey Landlord"],
}

# ── Platform speed ranking for finding buyers ─────────────────────────────────

PLATFORMS_BY_SPEED = [
    {
        "name":        "PropStream",
        "url":         "https://www.propstream.com/",
        "speed":       "Same day",
        "cost":        "$99/mo",
        "how":         "Filter: Cash Buyers, by Zip, last 12 months. Export list → cold call.",
        "best_for":    "Finding active flippers and landlords who already closed in your zip.",
    },
    {
        "name":        "Facebook Groups",
        "url":         "https://www.facebook.com/groups/",
        "speed":       "1-2 days",
        "cost":        "Free",
        "how":         "Post deal in 5 local investor groups. DM responders.",
        "best_for":    "Fastest free method — thousands of buyers in every market group.",
    },
    {
        "name":        "BiggerPockets Marketplace",
        "url":         "https://www.biggerpockets.com/deals",
        "speed":       "2-5 days",
        "cost":        "Free to post",
        "how":         "Post deal with address, numbers, photos. Buyers find you.",
        "best_for":    "Serious investors who actually close. Less tire-kickers.",
    },
    {
        "name":        "Connected Investors (CI)",
        "url":         "https://connectedinvestors.com/",
        "speed":       "1-3 days",
        "cost":        "Free tier",
        "how":         "Search cash buyers by zip, filter active investors, DM deals.",
        "best_for":    "Direct cash buyer database — built specifically for wholesalers.",
    },
    {
        "name":        "County Deed Records",
        "url":         "https://publicrecords.netronline.com/",
        "speed":       "2-7 days",
        "cost":        "Free",
        "how":         "Pull cash sales (no mortgage recorded) in your zip last 12 months.",
        "best_for":    "Finding the actual active buyers nobody else is calling.",
    },
    {
        "name":        "ListSource",
        "url":         "https://www.listsource.com/",
        "speed":       "Same day",
        "cost":        "~$0.10/record",
        "how":         "Buy 'absentee owner' or 'cash buyer' list by zip. Cold call list.",
        "best_for":    "Volume calling campaigns to find investors.",
    },
    {
        "name":        "DealMachine",
        "url":         "https://www.dealmachine.com/",
        "speed":       "1-3 days",
        "cost":        "$49–$99/mo",
        "how":         "Driving for dollars + built-in buyer matching. Post deal, match buyers.",
        "best_for":    "Combining lead finding + buyer matching in one app.",
    },
    {
        "name":        "Your Local REIA",
        "url":         "https://nationalreia.org/find-a-reia/",
        "speed":       "Next meeting",
        "cost":        "Free or $10/meeting",
        "how":         "Attend, announce deal in 30-second pitch. Collect business cards.",
        "best_for":    "Building repeat buyer relationships — your best long-term asset.",
    },
]

# ── Buyer outreach scripts ─────────────────────────────────────────────────────

BUYER_PITCH_SCRIPTS = {
    "text": (
        "Hey [Name], this is Alberto. Got a {beds}bd/{baths}ba in {city} at ${price:,.0f}. "
        "ARV ${arv:,.0f}. {strategy}. Interested? I can send pics and numbers now."
    ),
    "email_subject": "Off-Market Deal — {city}: {beds}bd/{baths}ba at ${price:,.0f} ({pct_below}% below ARV)",
    "email_body": (
        "Hi [Name],\n\n"
        "I have an off-market deal I think fits your criteria:\n\n"
        "  📍 {address}\n"
        "  💰 Asking: ${price:,.0f}\n"
        "  🏠 ARV: ${arv:,.0f} ({pct_below}% below market)\n"
        "  🔨 Repairs Est: ${repairs:,.0f}\n"
        "  💵 All-In: ${all_in:,.0f}\n"
        "  🏆 Best Strategy: {strategy}\n\n"
        "Closing by {close_date}. EMD negotiable.\n\n"
        "Reply or call/text me at {phone} if you want to take a look.\n\n"
        "Best,\nAlberto Soriano"
    ),
    "cold_call_opener": (
        "Hey, is this [Name]? Great — this is Alberto. I got your info from the county records — "
        "you bought a property on [their address] last year. I have a similar off-market deal "
        "in {city} — {beds}/{baths}, I'm assigning it at ${price:,.0f}. "
        "ARV is ${arv:,.0f}. Are you still buying in that area?"
    ),
}


# ── Local buyer list (your personal database) ─────────────────────────────────

def _load_buyers() -> list:
    BUYER_DIR.mkdir(exist_ok=True)
    if not BUYER_FILE.exists():
        return []
    try:
        return json.loads(BUYER_FILE.read_text())
    except Exception:
        return []


def _save_buyers(buyers: list):
    BUYER_DIR.mkdir(exist_ok=True)
    BUYER_FILE.write_text(json.dumps(buyers, indent=2))


def add_buyer(
    name: str,
    phone: str = "",
    email: str = "",
    markets: list = None,
    buyer_type: str = "Fix & Flip Investor",
    price_min: float = 0,
    price_max: float = 200000,
    notes: str = "",
) -> dict:
    """Add a real cash buyer to your personal list."""
    buyers = _load_buyers()
    buyer = {
        "id":         str(uuid.uuid4())[:8],
        "name":       name,
        "phone":      phone,
        "email":      email,
        "markets":    markets or [],
        "buyer_type": buyer_type,
        "price_min":  price_min,
        "price_max":  price_max,
        "notes":      notes,
        "added_at":   datetime.now().isoformat(),
        "deals_sent": 0,
        "deals_closed": 0,
    }
    buyers.append(buyer)
    _save_buyers(buyers)
    return buyer


def get_all_buyers() -> list:
    return _load_buyers()


def record_buyer_deal_sent(buyer_id: str):
    buyers = _load_buyers()
    for b in buyers:
        if b.get("id") == buyer_id:
            b["deals_sent"] = b.get("deals_sent", 0) + 1
            break
    _save_buyers(buyers)


def record_buyer_deal_closed(buyer_id: str):
    buyers = _load_buyers()
    for b in buyers:
        if b.get("id") == buyer_id:
            b["deals_closed"] = b.get("deals_closed", 0) + 1
            b["last_closed"] = datetime.now().isoformat()
            break
    _save_buyers(buyers)


# ── Deal matching ─────────────────────────────────────────────────────────────

def match_buyers_to_deal(
    price: float,
    arv: float,
    strategy: str,
    city: str = "",
    state: str = "",
    market_rent: float = 0,
    fmr: float = 0,
    bedrooms: int = 3,
    bathrooms: float = 2,
    repairs: float = 0,
    is_high_margin: bool = False,
) -> dict:
    """
    Given a deal's parameters, return:
    1. Ranked buyer types to target
    2. Personal buyer list matches
    3. Where to find buyers fast
    4. Ready-to-send scripts
    """
    city_lower = city.lower()

    # Determine signals from deal parameters
    discount_pct = ((arv - price) / arv * 100) if arv > 0 else 0
    rent_ratio   = (market_rent / price * 100) if price > 0 else 0
    all_in       = price + repairs

    signals = set()
    if discount_pct >= 30:
        signals.add("high_discount")
    if rent_ratio >= 1.0:
        signals.add("rental_viable")
        signals.add("cash_flow_positive")
    if (fmr >= market_rent and market_rent > 0) or rent_ratio >= 1.0:
        signals.add("section8_viable")
        signals.add("fmr_covers_rent")
    if price < 80000:
        signals.add("low_price_market")
        signals.add("brrrr_positive")
    if repairs > 0:
        signals.add("needs_rehab")
    if price >= 500000:
        signals.add("luxury_market")
    if "Wholesale" in strategy or "Flip" in strategy:
        signals.add("fast_close_needed")
    if "BRRRR" in strategy:
        signals.add("brrrr_positive")
    if "Section 8" in strategy:
        signals.add("section8_friendly")

    # Rank buyer types by signal match
    ranked_types = []
    for bp_name, bp in BUYER_PROFILES.items():
        match_score = sum(1 for sig in bp.get("signals", []) if sig in signals)
        if match_score > 0 or is_high_margin:
            ranked_types.append((match_score, bp_name, bp))

    # Also pull from market default if we know the market
    for mkt_key, mkt_types in MARKET_BUYER_TYPES.items():
        if mkt_key in city_lower:
            for bt in mkt_types:
                if bt not in [r[1] for r in ranked_types]:
                    ranked_types.append((1, bt, BUYER_PROFILES.get(bt, {})))
            break

    ranked_types.sort(reverse=True, key=lambda x: x[0])
    if not ranked_types:
        ranked_types = [(1, "Fix & Flip Investor", BUYER_PROFILES["Fix & Flip Investor"]),
                        (1, "Turnkey Landlord", BUYER_PROFILES["Turnkey Landlord"])]

    # Match from personal buyer list
    personal_matches = []
    all_buyers = _load_buyers()
    for buyer in all_buyers:
        # Market match
        buyer_markets = [m.lower() for m in buyer.get("markets", [])]
        market_match  = not buyer_markets or any(
            city_lower in bm or bm in city_lower for bm in buyer_markets
        )
        # Price match — treat price_max=0 as "no ceiling set"
        p_max = buyer.get("price_max", 0)
        price_match = (
            (buyer.get("price_min", 0) <= price <= p_max)
            if p_max > 0 else True
        )
        # Type match
        type_match = buyer.get("buyer_type") in [r[1] for r in ranked_types[:3]]

        if market_match and price_match and type_match:
            personal_matches.append(buyer)

    # Build scripts
    pct_below = round(discount_pct)
    close_date = "30 days"
    scripts = {
        "text": BUYER_PITCH_SCRIPTS["text"].format(
            beds=bedrooms, baths=bathrooms, city=city or "your market",
            price=price, arv=arv, strategy=strategy,
        ),
        "email_subject": BUYER_PITCH_SCRIPTS["email_subject"].format(
            city=city or "market", beds=bedrooms, baths=bathrooms,
            price=price, pct_below=pct_below,
        ),
        "email_body": BUYER_PITCH_SCRIPTS["email_body"].format(
            address=f"{city}, {state}" if state else city,
            price=price, arv=arv, pct_below=pct_below,
            repairs=repairs, all_in=all_in,
            strategy=strategy, close_date=close_date,
            phone="(your phone)",
        ),
        "cold_call_opener": BUYER_PITCH_SCRIPTS["cold_call_opener"].format(
            city=city or "your market", beds=bedrooms, baths=bathrooms,
            price=price, arv=arv,
        ),
    }

    return {
        "ranked_buyer_types": [(name, profile) for _, name, profile in ranked_types[:4]],
        "personal_matches":   personal_matches,
        "platforms":          PLATFORMS_BY_SPEED[:5],
        "scripts":            scripts,
        "deal_summary": {
            "price":        price,
            "arv":          arv,
            "discount_pct": round(discount_pct, 1),
            "all_in":       all_in,
            "strategy":     strategy,
            "signals":      list(signals),
        },
    }


def buyer_list_summary() -> dict:
    buyers = _load_buyers()
    return {
        "total_buyers": len(buyers),
        "by_type": {},
        "by_market": {},
        "closed": sum(b.get("deals_closed", 0) for b in buyers),
    }
