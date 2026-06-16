"""
Lender Directory — Hard Money, DSCR, and Bridge lenders for real estate investors.
Updated May 2026. Verify current rates directly with each lender.
"""

# ── Hard Money Lenders ────────────────────────────────────────────────────────

HARD_MONEY_LENDERS = [
    {
        "name":       "Kiavi (formerly LendingHome)",
        "url":        "https://www.kiavi.com/",
        "specialty":  "Fix & Flip, Bridge",
        "rates":      "9.5–12%",
        "ltv":        "Up to 90% of purchase + 100% of rehab (up to 75% ARV)",
        "loan_range": "$75k–$3M",
        "min_credit": 640,
        "states":     "44 states",
        "close_time": "5–10 business days",
        "pro":        "Online application, fast close, works with first-time investors",
        "note":       "Best for beginners — streamlined process",
    },
    {
        "name":       "LendingOne",
        "url":        "https://www.lendingone.com/",
        "specialty":  "Fix & Flip, Bridge, DSCR Rental",
        "rates":      "10–13%",
        "ltv":        "85% LTC, up to 70% ARV",
        "loan_range": "$75k–$10M",
        "min_credit": 620,
        "states":     "Nationwide",
        "close_time": "7–14 days",
        "pro":        "Handles both flips and DSCR in one place",
        "note":       "Great if you plan to refi into DSCR after rehab",
    },
    {
        "name":       "Lima One Capital",
        "url":        "https://www.limaone.com/",
        "specialty":  "Fix & Flip, Rental, New Construction",
        "rates":      "9–13%",
        "ltv":        "Up to 90% LTC, 75% ARV",
        "loan_range": "$75k–$5M",
        "min_credit": 600,
        "states":     "Nationwide",
        "close_time": "10–14 days",
        "pro":        "Low credit minimum, volume pricing after 3+ deals",
        "note":       "Offers repeat borrower discounts",
    },
    {
        "name":       "RCN Capital",
        "url":        "https://www.rcncapital.com/",
        "specialty":  "Fix & Flip, Bridge, Multifamily",
        "rates":      "9–12%",
        "ltv":        "85% LTC, 70% ARV",
        "loan_range": "$50k–$2.5M",
        "min_credit": 620,
        "states":     "Nationwide (select states)",
        "close_time": "7–10 days",
        "pro":        "Broker-friendly, works with investors who use other people's money",
        "note":       "Good for JV deals",
    },
    {
        "name":       "New Silver",
        "url":        "https://newsilver.com/",
        "specialty":  "Fix & Flip, New Construction",
        "rates":      "9.5–12.5%",
        "ltv":        "90% LTC, 75% ARV",
        "loan_range": "$100k–$5M",
        "min_credit": 650,
        "states":     "40+ states",
        "close_time": "5 days (instant approval)",
        "pro":        "Instant pre-approval online, integrates with deal analysis tools",
        "note":       "Tech-first lender — fastest approval process",
    },
    {
        "name":       "Easy Street Capital",
        "url":        "https://easystreetcap.com/",
        "specialty":  "Fix & Flip, BRRRR, Rental",
        "rates":      "10–13%",
        "ltv":        "90% LTC, 75% ARV",
        "loan_range": "$75k–$5M",
        "min_credit": 620,
        "states":     "Most states",
        "close_time": "7–14 days",
        "pro":        "Explicitly markets to BRRRR investors, handles refi in-house",
        "note":       "Best for BRRRR strategy",
    },
    {
        "name":       "CoreVest Finance",
        "url":        "https://www.corevestfinance.com/",
        "specialty":  "Rental Portfolio, Bridge, DSCR",
        "rates":      "8.5–11%",
        "ltv":        "Up to 80%",
        "loan_range": "$75k–$100M (portfolio loans)",
        "min_credit": 680,
        "states":     "Nationwide",
        "close_time": "14–21 days",
        "pro":        "Portfolio lenders — can finance 5+ properties at once",
        "note":       "For scaling — once you have multiple rentals",
    },
    {
        "name":       "Groundfloor",
        "url":        "https://www.groundfloor.com/",
        "specialty":  "Fix & Flip, Short-term Bridge",
        "rates":      "6.5–14% (grade-based)",
        "ltv":        "Up to 90% of purchase",
        "loan_range": "$75k–$2M",
        "min_credit": 640,
        "states":     "All 50 states",
        "close_time": "14–21 days",
        "pro":        "Crowdfunded model — often lower rates for strong deals",
        "note":       "Rate depends on deal quality (A-G grading)",
    },
    {
        "name":       "Visio Lending",
        "url":        "https://www.visiolending.com/",
        "specialty":  "DSCR Rental, Portfolio",
        "rates":      "7–10% (DSCR based)",
        "ltv":        "Up to 80%",
        "loan_range": "$75k–$2M",
        "min_credit": 680,
        "states":     "All 50 states + DC",
        "close_time": "21–30 days",
        "pro":        "No income verification — DSCR only, great for self-employed",
        "note":       "Specializes ONLY in rental loans — best DSCR lender",
    },
    {
        "name":       "Civic Financial Services",
        "url":        "https://www.civicfs.com/",
        "specialty":  "Fix & Flip, Bridge, DSCR",
        "rates":      "9–13%",
        "ltv":        "Up to 90% LTC",
        "loan_range": "$100k–$7.5M",
        "min_credit": 620,
        "states":     "Nationwide",
        "close_time": "7–14 days",
        "pro":        "Strong in California, great for coastal markets",
        "note":       "",
    },
]

# ── DSCR-Only Lenders (for rental loans, no income verification) ───────────────

DSCR_LENDERS = [
    {
        "name":        "Visio Lending",
        "url":         "https://www.visiolending.com/",
        "min_credit":  680,
        "min_dscr":    1.0,
        "ltv":         "Up to 80%",
        "rates":       "7–10%",
        "loan_min":    75000,
        "loan_max":    2000000,
        "states":      "All 50 states",
        "note":        "DSCR specialists — best in class",
    },
    {
        "name":        "Griffin Funding",
        "url":         "https://griffinfunding.com/dscr-loans/",
        "min_credit":  620,
        "min_dscr":    0.75,
        "ltv":         "Up to 80%",
        "rates":       "7.5–11%",
        "loan_min":    100000,
        "loan_max":    5000000,
        "states":      "Most states",
        "note":        "Accepts DSCR below 1.0 with strong compensating factors",
    },
    {
        "name":        "NewFi Lending",
        "url":         "https://www.newfi.com/dscr/",
        "min_credit":  660,
        "min_dscr":    1.0,
        "ltv":         "Up to 80%",
        "rates":       "7–10%",
        "loan_min":    75000,
        "loan_max":    3000000,
        "states":      "40+ states",
        "note":        "Strong tech platform, fast pre-approval",
    },
    {
        "name":        "A&D Mortgage",
        "url":         "https://admortgage.com/dscr-loan/",
        "min_credit":  620,
        "min_dscr":    1.0,
        "ltv":         "Up to 80%",
        "rates":       "7–10.5%",
        "loan_min":    75000,
        "loan_max":    3000000,
        "states":      "All 50 states",
        "note":        "Great for condos and non-warrantable properties",
    },
    {
        "name":        "Angel Oak Mortgage",
        "url":         "https://angeloakmortgage.com/dscr/",
        "min_credit":  660,
        "min_dscr":    1.0,
        "ltv":         "Up to 80%",
        "rates":       "7–9.5%",
        "loan_min":    150000,
        "loan_max":    3000000,
        "states":      "Most states",
        "note":        "Known for competitive rates on strong deals",
    },
    {
        "name":        "Trident Home Loans",
        "url":         "https://www.tridenthomeloans.com/",
        "min_credit":  640,
        "min_dscr":    1.0,
        "ltv":         "Up to 80%",
        "rates":       "7.5–11%",
        "loan_min":    75000,
        "loan_max":    2000000,
        "states":      "30+ states",
        "note":        "Specializes in low-income housing markets (Detroit, Birmingham, etc.)",
    },
]


def get_hml_for_deal(price: float, arv: float, credit_score: int, state: str = "") -> list:
    """Return lenders most likely to approve this specific deal."""
    ltv_needed = price / arv if arv > 0 else 1.0
    eligible = []
    for lender in HARD_MONEY_LENDERS:
        if lender["min_credit"] <= credit_score:
            eligible.append(lender)
    # Sort by rate (cheapest first)
    eligible.sort(key=lambda x: float(x["rates"].split("–")[0].replace("%", "")))
    return eligible[:5]


def get_dscr_for_deal(dscr_ratio: float, credit_score: int, loan_amount: float) -> list:
    """Return DSCR lenders that would approve this rental deal."""
    eligible = []
    for lender in DSCR_LENDERS:
        if (lender["min_credit"] <= credit_score
                and lender["min_dscr"] <= dscr_ratio
                and lender["loan_min"] <= loan_amount):
            eligible.append(lender)
    return eligible


def get_lender_summary() -> str:
    """Quick summary for display."""
    return (
        f"Hard Money: {len(HARD_MONEY_LENDERS)} lenders | "
        f"DSCR Rental: {len(DSCR_LENDERS)} lenders | "
        f"Rates: HML 9-13% | DSCR 7-11% | Min credit: 620"
    )
