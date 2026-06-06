"""
Property Management Directory — by market.
Covers the top wholesale markets with local and national PM companies,
typical fee structures, what to look for, and how to vet a PM fast.
"""

from typing import Optional


# ── National PM chains with local presence ───────────────────────────────────

NATIONAL_PM_COMPANIES = [
    {
        "name":        "Renters Warehouse",
        "url":         "https://renterswarehouse.com/",
        "fee_range":   "6–10% monthly + leasing fee (50–100% 1st month rent)",
        "markets":     ["Detroit", "Minneapolis", "Phoenix", "Atlanta", "Charlotte", "Dallas", "Houston", "Tampa", "Nashville", "Indianapolis", "Columbus"],
        "min_rent":    800,
        "specialty":   "SFR, small multifamily",
        "pro":         "Flat-fee model in some markets, tenant placement guarantee",
        "note":        "Good for out-of-state investors — one call covers multiple markets",
    },
    {
        "name":        "Mynd Property Management",
        "url":         "https://www.mynd.co/",
        "fee_range":   "8% monthly + leasing fee",
        "markets":     ["Atlanta", "Dallas", "Houston", "Tampa", "Phoenix", "Charlotte", "Columbus", "Indianapolis", "Kansas City", "St. Louis"],
        "min_rent":    900,
        "specialty":   "SFR, tech-enabled platform",
        "pro":         "Owner dashboard, 24/7 maintenance, eviction protection plan",
        "note":        "Best for investors with 1–50 units across multiple markets",
    },
    {
        "name":        "Pathlight Property Management",
        "url":         "https://www.pathlightmgt.com/",
        "fee_range":   "8–10% monthly",
        "markets":     ["Atlanta", "Dallas", "Houston", "Tampa", "Phoenix", "Charlotte", "Nashville", "Memphis", "Birmingham"],
        "min_rent":    800,
        "specialty":   "SFR in Sun Belt markets",
        "pro":         "Institutional quality, good for BRRRR hold strategy",
        "note":        "Primarily serves Sun Belt; strong in southern markets",
    },
    {
        "name":        "Real Property Management",
        "url":         "https://www.realpropertymgt.com/",
        "fee_range":   "6–12% monthly (franchise varies)",
        "markets":     "500+ locations nationwide",
        "min_rent":    600,
        "specialty":   "SFR, small multifamily",
        "pro":         "Largest franchise network — local operator with national support",
        "note":        "Quality varies by franchise; interview the local operator carefully",
    },
    {
        "name":        "Roofstock Property Management",
        "url":         "https://www.roofstock.com/property-management",
        "fee_range":   "8% monthly + leasing fee",
        "markets":     ["Atlanta", "Dallas", "Houston", "Tampa", "Phoenix", "Kansas City", "Indianapolis", "Memphis", "Birmingham", "Cleveland", "Detroit"],
        "min_rent":    750,
        "specialty":   "Turnkey SFR, out-of-state investors",
        "pro":         "Pairs with Roofstock marketplace — buy + manage in one platform",
        "note":        "Strong for investors who bought via Roofstock",
    },
]


# ── Local PM companies by market ──────────────────────────────────────────────

LOCAL_PM_BY_MARKET = {
    "Detroit": [
        {
            "name":      "Domu Detroit",
            "url":       "https://www.domu.com/detroit",
            "fee":       "8–10% monthly",
            "specialty": "SFR + small multifamily, Section 8 experience",
            "note":      "Strong knowledge of Detroit rental market + MSHDA compliance",
        },
        {
            "name":      "Real Property Management Greater Detroit",
            "url":       "https://www.realpropertymgt.com/office/greater-detroit",
            "fee":       "8–9% monthly + 50% leasing fee",
            "specialty": "SFR, duplexes",
            "note":      "Large local team, handles Section 8",
        },
        {
            "name":      "Century 21 Curran & Oberski Property Mgmt",
            "url":       "https://c21curranandroberski.com/",
            "fee":       "8% monthly",
            "specialty": "SFR, condos",
            "note":      "Established brand; strong tenant screening",
        },
    ],
    "Birmingham": [
        {
            "name":      "HomeRiver Group Birmingham",
            "url":       "https://homerivergroup.com/",
            "fee":       "8–10% monthly",
            "specialty": "SFR, BRRRR holds",
            "note":      "Nationwide + local; good for out-of-state holders",
        },
        {
            "name":      "Real Property Management Rocket City (NW Alabama)",
            "url":       "https://www.realpropertymgt.com/",
            "fee":       "8–9% monthly",
            "specialty": "SFR, small multifamily",
            "note":      "Section 8 compliant; covers Birmingham + Huntsville corridor",
        },
        {
            "name":      "Landmark Property Management AL",
            "url":       "https://landmarkpmal.com/",
            "fee":       "7–9% monthly",
            "specialty": "SFR, Section 8",
            "note":      "Long track record in Birmingham; strong Section 8 relationships",
        },
    ],
    "Memphis": [
        {
            "name":      "HomeRiver Group Memphis",
            "url":       "https://homerivergroup.com/",
            "fee":       "8–10% monthly",
            "specialty": "SFR, Section 8, BRRRR holds",
            "note":      "Top-rated nationally; Memphis office specializes in investor rentals",
        },
        {
            "name":      "Paragon Property Management",
            "url":       "https://paragonmemphis.com/",
            "fee":       "7–9% monthly",
            "specialty": "SFR, small multifamily",
            "note":      "Local shop with tight tenant screening; hands-on",
        },
        {
            "name":      "Invest Memphis / Crossroads PM",
            "url":       "https://investmemphis.com/",
            "fee":       "8–10% monthly",
            "specialty": "Turnkey rentals, investor-focused",
            "note":      "Works with many out-of-state buyers of Memphis turnkeys",
        },
    ],
    "Atlanta": [
        {
            "name":      "Mynd Atlanta",
            "url":       "https://www.mynd.co/atlanta",
            "fee":       "8% monthly",
            "specialty": "SFR, tech-enabled",
            "note":      "Owner portal, 24/7 maintenance; strong in OTP (outside perimeter)",
        },
        {
            "name":      "Evernest (formerly Boss Asset Mgmt)",
            "url":       "https://www.evernest.co/atlanta",
            "fee":       "8–10% monthly",
            "specialty": "SFR, small multifamily",
            "note":      "Fast-growing; works well with BRRRR investors",
        },
        {
            "name":      "Pathlight Atlanta",
            "url":       "https://www.pathlightmgt.com/",
            "fee":       "8–9% monthly",
            "specialty": "SFR, Sun Belt holds",
            "note":      "Institutional quality for larger portfolios",
        },
    ],
    "Houston": [
        {
            "name":      "Green Residential",
            "url":       "https://www.greenresidential.com/",
            "fee":       "8% monthly",
            "specialty": "SFR, condos, small multifamily",
            "note":      "Top Houston local PM; investors highly recommend them",
        },
        {
            "name":      "Mynd Houston",
            "url":       "https://www.mynd.co/houston",
            "fee":       "8% monthly",
            "specialty": "SFR",
            "note":      "Good for out-of-state investors; tech-enabled",
        },
        {
            "name":      "Apex Leasing & Property Management",
            "url":       "https://apexleasingtx.com/",
            "fee":       "8–10% monthly",
            "specialty": "SFR, small multifamily, Section 8",
            "note":      "Strong Section 8 / voucher experience across Harris County",
        },
    ],
    "Dallas": [
        {
            "name":      "HomeRiver Group DFW",
            "url":       "https://homerivergroup.com/",
            "fee":       "8–10% monthly",
            "specialty": "SFR, investor-focused",
            "note":      "Strong DFW presence; works with out-of-state BRRRR investors",
        },
        {
            "name":      "Mynd Dallas",
            "url":       "https://www.mynd.co/dallas",
            "fee":       "8% monthly",
            "specialty": "SFR, tech-enabled",
            "note":      "Fast leasing, online platform",
        },
        {
            "name":      "Renters Warehouse DFW",
            "url":       "https://renterswarehouse.com/locations/dallas-fort-worth",
            "fee":       "6–8% monthly",
            "specialty": "SFR, small multifamily",
            "note":      "Flat-fee available; good for investors with 3+ doors",
        },
    ],
    "Nashville": [
        {
            "name":      "Evernest Nashville",
            "url":       "https://www.evernest.co/nashville",
            "fee":       "8–10% monthly",
            "specialty": "SFR, small multifamily",
            "note":      "Growing fast with Nashville's investor wave",
        },
        {
            "name":      "Park Avenue Properties Nashville",
            "url":       "https://parkavenueprop.com/",
            "fee":       "8–9% monthly",
            "specialty": "SFR, condo, townhome",
            "note":      "Local; strong tenant screening in hot Nashville market",
        },
    ],
    "Tampa": [
        {
            "name":      "Mynd Tampa",
            "url":       "https://www.mynd.co/tampa",
            "fee":       "8% monthly",
            "specialty": "SFR",
            "note":      "Good for out-of-state investors; handles Hillsborough + Pinellas",
        },
        {
            "name":      "Suncoast Property Management",
            "url":       "https://www.suncoastpm.com/",
            "fee":       "8–10% monthly",
            "specialty": "SFR, condo, small multifamily",
            "note":      "Local Tampa Bay specialist; well-reviewed",
        },
    ],
    "Phoenix": [
        {
            "name":      "Mynd Phoenix",
            "url":       "https://www.mynd.co/phoenix",
            "fee":       "8% monthly",
            "specialty": "SFR",
            "note":      "Strong Phoenix/Mesa/Scottsdale coverage",
        },
        {
            "name":      "Real Property Management Phoenix Valley",
            "url":       "https://www.realpropertymgt.com/",
            "fee":       "8–10% monthly",
            "specialty": "SFR, small multifamily",
            "note":      "Large local team; handles Section 8 vouchers",
        },
    ],
    "Indianapolis": [
        {
            "name":      "REI Nation (formerly Memphis Invest) Indianapolis",
            "url":       "https://reinationinvest.com/",
            "fee":       "9–10% monthly",
            "specialty": "Turnkey SFR, out-of-state investors",
            "note":      "Premium service, high-quality tenants; suits BRRRR hold strategy",
        },
        {
            "name":      "Evernest Indianapolis",
            "url":       "https://www.evernest.co/",
            "fee":       "8–10% monthly",
            "specialty": "SFR",
            "note":      "Growing presence in Indy investor market",
        },
    ],
    "Columbus": [
        {
            "name":      "Short North Property Management",
            "url":       "https://shortnorthpropertymanagement.com/",
            "fee":       "8–10% monthly",
            "specialty": "SFR, small multifamily",
            "note":      "Local Columbus specialist; strong in urban neighborhoods",
        },
        {
            "name":      "Evernest Columbus",
            "url":       "https://www.evernest.co/",
            "fee":       "8–10% monthly",
            "specialty": "SFR, investor-friendly",
            "note":      "Growing Columbus office; works with BRRRR investors",
        },
    ],
    "Kansas City": [
        {
            "name":      "HomeRiver Group Kansas City",
            "url":       "https://homerivergroup.com/",
            "fee":       "8–10% monthly",
            "specialty": "SFR, small multifamily",
            "note":      "Strong KC investor network; covers MO + KS sides",
        },
        {
            "name":      "Real Property Management Kansas City",
            "url":       "https://www.realpropertymgt.com/",
            "fee":       "8–9% monthly",
            "specialty": "SFR",
            "note":      "Solid local office; handles Section 8",
        },
    ],
    "Cleveland": [
        {
            "name":      "Howard Hanna Property Management",
            "url":       "https://howardhanna.com/",
            "fee":       "8–10% monthly",
            "specialty": "SFR, small multifamily",
            "note":      "Largest local brand in NE Ohio; strong tenant placement",
        },
        {
            "name":      "Innova Property Management",
            "url":       "https://innovapm.com/",
            "fee":       "7–9% monthly",
            "specialty": "SFR, Section 8",
            "note":      "Cleveland-focused; good Section 8 / Cuyahoga Metro Housing experience",
        },
    ],
    "St. Louis": [
        {
            "name":      "Evernest St. Louis",
            "url":       "https://www.evernest.co/",
            "fee":       "8–10% monthly",
            "specialty": "SFR, small multifamily",
            "note":      "Growing St. Louis presence; investor-friendly",
        },
        {
            "name":      "Real Property Management St. Louis",
            "url":       "https://www.realpropertymgt.com/",
            "fee":       "8–10% monthly",
            "specialty": "SFR",
            "note":      "Franchise; interview local operator; covers both city and county",
        },
    ],
    "Charlotte": [
        {
            "name":      "Mynd Charlotte",
            "url":       "https://www.mynd.co/charlotte",
            "fee":       "8% monthly",
            "specialty": "SFR",
            "note":      "Tech-enabled; solid for remote investors",
        },
        {
            "name":      "Evernest Charlotte",
            "url":       "https://www.evernest.co/",
            "fee":       "8–10% monthly",
            "specialty": "SFR, small multifamily",
            "note":      "Growing Charlotte office; BRRRR investor focus",
        },
    ],
    "Miami": [
        {
            "name":      "Keyes Property Management",
            "url":       "https://www.keyes.com/property-management",
            "fee":       "8–10% monthly",
            "specialty": "SFR, condo, small multifamily",
            "note":      "Largest local real estate brand in South Florida",
        },
        {
            "name":      "Continental Property Management FL",
            "url":       "https://www.continentalpm.com/",
            "fee":       "8–12% monthly",
            "specialty": "SFR, condo, luxury",
            "note":      "Good for high-end Miami/Fort Lauderdale rentals",
        },
    ],
}


# ── Fee structure guide ───────────────────────────────────────────────────────

FEE_BREAKDOWN = {
    "monthly_mgmt": {
        "typical": "6–10% of collected rent",
        "low_market": "6–7% (Cleveland, Detroit, St. Louis)",
        "mid_market": "8% (most markets)",
        "high_market": "9–12% (Miami, Nashville, Phoenix)",
        "note": "Always negotiate — volume (3+ doors) gets 1–2% off",
    },
    "leasing_fee": {
        "typical": "50–100% of first month's rent",
        "note": "Charged every time a new tenant is placed; shop this hard",
    },
    "maintenance_markup": {
        "typical": "10–15% markup on contractor invoices",
        "note": "Some PMs use in-house crews; ask for their labor rates upfront",
    },
    "lease_renewal_fee": {
        "typical": "$100–$300 or 1 month rent",
        "note": "Often negotiable — good PMs waive this to keep long-term tenants",
    },
    "vacancy_fee": {
        "typical": "None (most), some charge $50–100/mo during vacancy",
        "note": "Avoid PMs that charge during vacancy — zero incentive to fill fast",
    },
    "eviction_fee": {
        "typical": "$200–500 + legal costs",
        "note": "Some offer eviction protection plans ($15–25/mo — worth it in tenant-friendly states)",
    },
}


# ── What to ask when vetting a PM ────────────────────────────────────────────

PM_VET_QUESTIONS = [
    "How many units do you currently manage in this market?",
    "What is your average days-to-lease for vacant units?",
    "What is your average tenant retention rate (lease renewals)?",
    "Do you handle Section 8 / housing vouchers? (If yes: what % of your portfolio?)",
    "How do you handle maintenance? In-house or contracted? What markup?",
    "What software do you use for owner reporting? Can I see a sample statement?",
    "What is your eviction rate? How long does a typical eviction take in this state?",
    "Can you provide 3 references from investors you've managed for 2+ years?",
    "What is your fee structure — monthly, leasing, renewal, and maintenance markup?",
    "Do you have an eviction protection plan? What does it cost?",
    "How many properties does each property manager handle? (More than 100 = thin service)",
]


# ── Section 8 / voucher PM notes ─────────────────────────────────────────────

SECTION8_PM_TIPS = [
    "Not all PMs accept Section 8 — confirm before hiring.",
    "Section 8 PMs need experience with HUD inspections and HOTMA compliance.",
    "Ask: 'How many Section 8 tenants do you currently manage?'",
    "A PM who manages 50+ Section 8 units knows the inspection process cold.",
    "Section 8 rents are paid directly to the PM by the PHA — zero collection risk.",
    "Look for PMs who do pre-HQS inspections before the official HUD walkthrough.",
    "Detroit, Memphis, Birmingham, Cleveland — most strong local PMs accept Section 8.",
    "Miami, Nashville, Phoenix — Section 8 acceptance is more selective; ask specifically.",
]


# ── Main functions ────────────────────────────────────────────────────────────

def get_pm_for_market(market: str) -> dict:
    """Return local + national PM options for a given market."""
    market_clean = market.strip().title()
    # Fuzzy match
    for key in LOCAL_PM_BY_MARKET:
        if key.lower() in market_clean.lower() or market_clean.lower() in key.lower():
            market_clean = key
            break

    local = LOCAL_PM_BY_MARKET.get(market_clean, [])
    national = [
        pm for pm in NATIONAL_PM_COMPANIES
        if isinstance(pm["markets"], list) and any(
            m.lower() in market_clean.lower() or market_clean.lower() in m.lower()
            for m in pm["markets"]
        ) or (isinstance(pm["markets"], str) and "nationwide" in pm["markets"].lower())
    ]
    return {
        "market":   market_clean,
        "local":    local,
        "national": national,
        "found":    bool(local or national),
    }


def estimate_pm_cost(monthly_rent: float, mgmt_pct: float = 0.08) -> dict:
    """Quick PM cost breakdown for a given rent and management fee %."""
    monthly_fee  = monthly_rent * mgmt_pct
    annual_fee   = monthly_fee * 12
    leasing_fee  = monthly_rent * 0.75   # midpoint estimate
    renewal_fee  = 200.0
    annual_total = annual_fee + leasing_fee + renewal_fee
    net_annual   = (monthly_rent * 12) - annual_total

    return {
        "monthly_rent":    monthly_rent,
        "mgmt_pct":        mgmt_pct,
        "monthly_mgmt":    monthly_fee,
        "annual_mgmt":     annual_fee,
        "leasing_fee":     leasing_fee,
        "renewal_fee":     renewal_fee,
        "annual_total_pm": annual_total,
        "net_annual":      net_annual,
        "net_monthly":     net_annual / 12,
    }


def list_covered_markets() -> list:
    return sorted(LOCAL_PM_BY_MARKET.keys())
