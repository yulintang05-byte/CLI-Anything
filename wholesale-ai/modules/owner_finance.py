"""
Owner-Financing Finder — low entry, very motivated sellers.

Owner financing (a.k.a. seller financing) is the lowest-barrier way into real
estate: the seller becomes the bank, so there's no loan qualification, often a
small down payment, and fast closes. This module focuses on FINDING the sellers
who will say yes, scoring how good the terms are, and arming you with the pitch.

The math lives in modules.creative_financing.calc_seller_finance — this module
is about sourcing, qualifying the seller, and analyzing total entry cost.
"""

# ── Where owner-financed deals actually live ───────────────────────────────────

OWNER_FINANCE_SOURCES = {
    "Zillow (keyword search)": {
        "url": "https://www.zillow.com/homes/for_sale/",
        "how": "Search the listing keywords: 'owner financing', 'seller financing', "
               "'owner will carry', 'OWC', 'lease to own', 'rent to own', 'contract for deed'.",
        "tip": "Use Zillow's 'Keywords' filter at the bottom of More filters.",
    },
    "Owner Financing on LandWatch": {
        "url": "https://www.landwatch.com/land/owner-financing",
        "how": "Land + rural homes; owner financing is the norm here, not the exception.",
        "tip": "Great for low-entry first deals — sellers expect to carry.",
    },
    "OwnerWillCarry.com": {
        "url": "https://www.ownerwillcarry.com/",
        "how": "Dedicated marketplace for seller-financed properties nationwide.",
        "tip": "Filter by down payment to find true low-entry deals.",
    },
    "Craigslist (real estate by owner)": {
        "url": "https://craigslist.org/",
        "how": "Search 'owner finance', 'rent to own', 'no bank', 'will carry' in the by-owner section.",
        "tip": "FSBO + owner finance keyword = highly motivated, no agent in the middle.",
    },
    "Facebook Marketplace + RE groups": {
        "url": "https://www.facebook.com/marketplace/",
        "how": "Search 'owner financing [city]'; join local 'Owner Finance Homes' groups.",
        "tip": "Sellers post here when they're tired and want it gone fast.",
    },
    "Tired Landlord lists (driving for dollars)": {
        "url": "",
        "how": "Out-of-state owners, code violations, eviction filings, expired rentals. "
               "Pull the list from your county, mail/call: 'Would you consider carrying the note?'",
        "tip": "Tired landlords already have income — many prefer payments over a lump sum (tax spreading).",
    },
    "Free & Clear absentee owners": {
        "url": "",
        "how": "County records: owners with NO mortgage + absentee mailing address. "
               "These are the #1 owner-finance targets — they own it outright.",
        "tip": "List services: PropStream, ListSource, DealMachine. Free route: county GIS + assessor.",
    },
    "Probate & inherited property": {
        "url": "",
        "how": "Heirs who inherited a paid-off house often want income, not management.",
        "tip": "Check probate court filings; offer to carry so they get monthly checks tax-deferred.",
    },
}


# ── Signals a seller will carry the note ───────────────────────────────────────

MOTIVATION_SIGNALS = [
    ("Owns free & clear (no mortgage)",        "STRONGEST — nothing stops them from carrying"),
    ("Older / retired seller",                 "Wants steady monthly income, not a lump sum to manage"),
    ("Tired / out-of-state landlord",          "Done with tenants; payments beat a fire sale"),
    ("Inherited / probate property",           "Heirs want cash flow without the headache"),
    ("Property listed 90+ days",               "Market rejected it — owner is flexible now"),
    ("Vacant property",                        "Carrying costs are bleeding them monthly"),
    ("'Motivated', 'must sell', 'as-is'",      "Explicit distress language in the listing"),
    ("Capital-gains exposure",                 "Installment sale spreads their tax bill — pitch this"),
    ("Failed financing / fell through",        "Buyer's bank killed it; seller is gun-shy on banks"),
    ("Expired listing",                        "Agent couldn't sell it — direct owner-finance offer wins"),
]


# ── Who says yes (ideal seller profile) ────────────────────────────────────────

IDEAL_SELLER_PROFILE = {
    "owns_outright":   "Free & clear is ideal — no underlying lender to satisfy.",
    "needs_income":    "Prefers $X/month for years over a one-time check.",
    "tax_motivated":   "An installment sale spreads capital gains across years (talk to their CPA).",
    "not_in_a_rush":   "Doesn't need 100% of the cash today to buy their next place.",
    "trusts_you":      "Relationship + a fair down payment de-risks it for them.",
    "red_flag":        "If they OWE on it, you need subject-to or a wrap — not clean owner finance.",
}


# ── How to ASK for owner financing (the pitch) ─────────────────────────────────

NEGOTIATION_PITCH = {
    "opening_question": (
        "\"Are you open to receiving your money over time instead of all at once? "
        "I can pay your full asking price if you'd consider carrying the financing.\""
    ),
    "full_price_for_terms": (
        "Trade PRICE for TERMS. Offer closer to (or at) asking price in exchange for "
        "low down payment + low interest. Sellers anchor on price; you win on terms."
    ),
    "the_tax_angle": (
        "\"Selling outright could mean a big capital-gains hit this year. An installment "
        "sale lets you spread that out — your accountant can confirm the savings.\""
    ),
    "the_income_angle": (
        "\"Instead of one check that sits in the bank earning nothing, you'd get "
        "${monthly}/month for {years} years — like keeping the rental without the tenants.\""
    ),
    "de_risk_for_them": [
        "Offer a meaningful (but low-for-you) down payment — 5–10% builds trust.",
        "Agree the note is secured by the property (they foreclose if you default).",
        "Propose a balloon in 3–5 years so they see an end date.",
        "Show proof you'll maintain the property (you're protecting their collateral).",
    ],
    "terms_to_push_for": [
        "Down payment: 0–10% (lower = lower entry)",
        "Interest rate: 0–6% (every point is real money over 30 years)",
        "Amortization: 30 years (lowest monthly payment)",
        "Balloon: 5+ years (gives you time to refi or sell)",
        "No prepayment penalty (so you can refi/sell anytime)",
        "First-position lien only if property is free & clear",
    ],
}


def calc_owner_finance_entry(
    purchase_price: float,
    down_payment_pct: float,
    interest_rate: float,
    loan_years: int,
    monthly_rent: float = 0,
    closing_costs: float = 0,
    monthly_taxes_ins: float = 0,
) -> dict:
    """
    Low-entry analysis for an owner-financed deal: what it costs to get IN,
    what you owe each month, and whether it cash flows as a rental.

    interest_rate is a decimal (0.06 = 6%). down_payment_pct is a decimal too.
    """
    down_payment = purchase_price * down_payment_pct
    loan_amount  = purchase_price - down_payment
    cash_to_close = down_payment + closing_costs

    monthly_rate = interest_rate / 12
    n = max(loan_years * 12, 1)
    if monthly_rate > 0:
        pi = loan_amount * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
    else:
        pi = loan_amount / n

    total_monthly = pi + monthly_taxes_ins
    monthly_cf    = (monthly_rent - total_monthly) if monthly_rent else 0

    # Cash-on-cash on the rental (annual cash flow / cash invested)
    coc = ((monthly_cf * 12) / cash_to_close * 100) if (monthly_rent and cash_to_close > 0) else 0

    if not monthly_rent:
        verdict = "Entry-only (no rent provided) — fill in rent to test cash flow."
        color = "yellow"
    elif monthly_cf >= 500:
        verdict = f"STRONG — cash flows ${monthly_cf:,.0f}/mo as a rental"
        color = "green"
    elif monthly_cf > 0:
        verdict = f"Thin — only ${monthly_cf:,.0f}/mo; negotiate lower payment or price"
        color = "yellow"
    else:
        verdict = f"NEGATIVE — loses ${abs(monthly_cf):,.0f}/mo; push for 0% down or lower rate"
        color = "red"

    return {
        "strategy":          "Owner Financing (low entry)",
        "purchase_price":    purchase_price,
        "down_payment":      round(down_payment, 0),
        "down_payment_pct":  f"{down_payment_pct * 100:.1f}%",
        "loan_amount":       round(loan_amount, 0),
        "cash_to_close":     round(cash_to_close, 0),
        "interest_rate_pct": f"{interest_rate * 100:.2f}%",
        "loan_term_years":   loan_years,
        "monthly_pi":        round(pi, 2),
        "monthly_total":     round(total_monthly, 2),
        "monthly_cash_flow": round(monthly_cf, 2) if monthly_rent else "N/A",
        "cash_on_cash_pct":  round(coc, 1) if monthly_rent else "N/A",
        "verdict":           verdict,
        "verdict_color":     color,
    }
