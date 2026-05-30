"""
Luxury Wholesale — $500k-$5M properties, developer buyers, high-end deals.
Wholesale fees on luxury: $25k-$150k per deal.
"""

LUXURY_MARKETS = [
    {"city": "Miami",       "state": "FL", "avg_price": 850000,  "avg_arv": 1200000, "developer_focus": "Condo conversions, luxury rehabs"},
    {"city": "Los Angeles", "state": "CA", "avg_price": 1200000, "avg_arv": 1800000, "developer_focus": "Teardowns, ADU additions, flips"},
    {"city": "Dallas",      "state": "TX", "avg_price": 650000,  "avg_arv": 950000,  "developer_focus": "Luxury SFR, new construction lots"},
    {"city": "Phoenix",     "state": "AZ", "avg_price": 600000,  "avg_arv": 900000,  "developer_focus": "Luxury flips, new builds"},
    {"city": "Atlanta",     "state": "GA", "avg_price": 550000,  "avg_arv": 800000,  "developer_focus": "Intown teardowns, luxury rehab"},
    {"city": "Nashville",   "state": "TN", "avg_price": 700000,  "avg_arv": 1100000, "developer_focus": "Luxury flips, Airbnb conversions"},
    {"city": "Charlotte",   "state": "NC", "avg_price": 500000,  "avg_arv": 750000,  "developer_focus": "New construction lots, luxury rehab"},
    {"city": "Austin",      "state": "TX", "avg_price": 800000,  "avg_arv": 1300000, "developer_focus": "Teardowns, tech exec buyers"},
    {"city": "Tampa",       "state": "FL", "avg_price": 600000,  "avg_arv": 950000,  "developer_focus": "Waterfront, luxury conversions"},
    {"city": "Denver",      "state": "CO", "avg_price": 700000,  "avg_arv": 1050000, "developer_focus": "Mountain view properties, luxury flips"},
]

LUXURY_DEAL_SOURCES = {
    "Expired Luxury Listings": {
        "description": "Listings that sat on MLS 60-120+ days — sellers are motivated",
        "how_to_find":  "Pull expired listings from MLS through an agent; filter $500k+ properties",
        "source":       "Ask your real estate agent to run expired listing report",
        "typical_discount": "10-20% below original ask",
    },
    "Luxury REO / Bank Owned": {
        "description": "High-end homes banks took back — banks don't want to hold luxury inventory",
        "how_to_find":  "Search Hubzu.com, Auction.com with $500k+ filter",
        "source":       "https://www.hubzu.com/ | https://www.auction.com/residential/",
        "typical_discount": "15-30% below ARV",
    },
    "Luxury Foreclosures": {
        "description": "High-net-worth individuals who over-leveraged, going through foreclosure",
        "how_to_find":  "County courthouse pre-foreclosure lists, PACER for high-value",
        "source":       "https://www.foreclosure.com/ | county courthouse",
        "typical_discount": "20-35% below market",
    },
    "Divorce / Estate Sales": {
        "description": "Luxury properties sold quickly due to life events — price often secondary",
        "how_to_find":  "Divorce court filings (public), probate filings, local estate auction houses",
        "source":       "County probate court | https://www.estatesales.net/",
        "typical_discount": "10-25% below market — speed matters more than price",
    },
    "Developer Overstock": {
        "description": "New construction luxury that didn't sell, builder needs liquidity",
        "how_to_find":  "Contact local luxury builders directly, check new developments with unsold units",
        "source":       "Local homebuilder associations, county permit records",
        "typical_discount": "5-15% on new builds (still good on high prices)",
    },
    "Off-Market Through Agents": {
        "description": "Agent pocket listings — luxury agents often have properties before MLS",
        "how_to_find":  "Build relationships with top 10 luxury agents in your target city",
        "source":       "Coldwell Banker Global Luxury, Sotheby's, Christie's Real Estate agents",
        "typical_discount": "Varies — exclusive access before competition",
    },
    "Fund.com / Luxury Distressed Portfolios": {
        "description": "Institutional investors liquidating luxury portfolios",
        "how_to_find":  "Commercial real estate brokers, institutional seller networks",
        "source":       "https://www.loopnet.com/ | https://www.crexi.com/",
        "typical_discount": "Portfolio discount 10-20%",
    },
}

LUXURY_DEVELOPER_BUYERS = {
    "Types of Developers to Target": [
        "Luxury homebuilders — buy lots and teardowns to build new construction",
        "Boutique developers — buy 1-5 luxury rehabs per year",
        "Condo converters — buy large homes, convert to 2-4 luxury units",
        "Airbnb/STR operators — buy luxury homes for short-term rental",
        "Foreign investor groups — often pay full cash, no financing contingency",
        "Family offices — HNW individuals managing wealth through real estate",
    ],
    "How to Find Them": [
        "Search county records for entities that bought $1M+ in cash in last 12 months",
        "LinkedIn: search 'real estate developer [city]', 'luxury home builder [city]'",
        "Local builder associations: NAHB chapter for your city",
        "Attend luxury REIA events and commercial real estate networking events",
        "Search LoopNet/CoStar for developers active in your target city",
        "Reach out to commercial real estate law firms — they know all the buyers",
    ],
    "How to Approach Them": [
        "Lead with the deal, not the relationship — developers only care about numbers",
        "Have ARV comps ready before reaching out",
        "Know the entitlements/permits: zoning, ADU allowed?, teardown permitted?",
        "Offer co-wholesale: bring them the deal, they bring a buyer, split fee",
        "Build a simple deal sheet: address, ask, ARV, condition, unique angle",
    ],
    "Sites": {
        "LoopNet (commercial)":     "https://www.loopnet.com/",
        "CoStar (institutional)":   "https://www.costar.com/",
        "NAHB (builders)":          "https://www.nahb.org/",
        "CreXi (deals)":            "https://www.crexi.com/",
        "LinkedIn (network)":       "https://www.linkedin.com/",
        "Realtor.com Luxury":       "https://www.realtor.com/luxury/",
    },
}

LUXURY_DEAL_ANALYSIS = {
    "wholesale_fee_range": "$25,000–$150,000 per deal",
    "typical_arv_discount": "15–30% below ARV",
    "mao_rule": "65% of ARV minus repairs (tighter than standard deals)",
    "avg_deal_time": "60–120 days (longer than cheap properties)",
    "key_metrics": [
        "Price per sqft vs comps (most important metric for luxury)",
        "Days on market vs neighborhood average",
        "Lot value alone (sometimes worth more than structure)",
        "Permit history (unpermitted work = massive red flag)",
        "HOA health (luxury communities with struggling HOAs = discount risk)",
    ],
    "red_flags": [
        "Unpermitted additions — lenders won't finance, cash buyers demand discount",
        "Custom features with limited buyer pool (indoor pool in cold climate)",
        "Overimproved for the neighborhood (doesn't appraise)",
        "HOA litigation or special assessments",
        "Flood zone without recent remediation",
    ],
}


def calc_luxury_deal(price: float, arv: float, sqft: float, repairs: float = 0) -> dict:
    """Quick luxury deal analysis — tighter margins, higher fees."""
    mao = (arv * 0.65) - repairs
    wholesale_fee = max(25000, (mao - price) * 0.5)  # Take half the spread
    profit = mao - price
    roi = (profit / price * 100) if price > 0 else 0
    ppsf_ask = price / sqft if sqft > 0 else 0
    ppsf_arv = arv / sqft if sqft > 0 else 0
    discount = ((arv - price) / arv * 100) if arv > 0 else 0

    return {
        "price":          price,
        "arv":            arv,
        "mao":            round(mao, 0),
        "repairs":        repairs,
        "profit":         round(profit, 0),
        "wholesale_fee":  round(wholesale_fee, 0),
        "roi":            round(roi, 1),
        "discount_pct":   round(discount, 1),
        "ppsf_ask":       round(ppsf_ask, 0),
        "ppsf_arv":       round(ppsf_arv, 0),
        "is_deal":        price <= mao and discount >= 15,
        "grade":          "A" if discount >= 30 else ("B" if discount >= 20 else ("C" if discount >= 15 else "F")),
    }
