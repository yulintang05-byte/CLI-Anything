"""
Deal Browser — surfaces Tax Deed, Gov Seized, and distressed properties
from real government sources. Matches Tranchi.ai's "Browse Deals" page.

Markets shown in Tranchi.ai: Detroit MI, Birmingham AL, Memphis TN,
Macon GA, Jackson MS, Toledo OH, Saint Louis MO
"""
from typing import Optional


# ── Real Government Property Sources by Market ───────────────────────────────

GOV_SOURCES = {
    "Tax Deed / Tax Lien Auctions": {
        "RealAuction (National)":    "https://www.realauction.com/",
        "GovEase (National)":        "https://www.govease.com/",
        "Bid4Assets (National)":     "https://www.bid4assets.com/taxsale",
        "SRI Tax Sales (National)":  "https://www.srihomesale.com/",
    },
    "Detroit, MI (Hot Market — $4k-$15k homes)": {
        "Detroit Land Bank (DLBA)":         "https://buildingdetroit.org/",
        "Wayne County Tax Auction":         "https://www.waynecounty.com/elected/treasurer/tax-auctions.aspx",
        "Wayne County Forfeiture":          "https://www.waynecounty.com/elected/treasurer/tax-foreclosure.aspx",
        "Detroit Auction Search":           "https://gis.waynecounty.com/",
    },
    "Birmingham, AL": {
        "Jefferson County Tax Lien":        "https://www.jccal.org/Default.asp?ID=734&pg=Tax+Lien+Certificate+Sale",
        "Alabama Revenue Tax Sales":        "https://www.revenue.alabama.gov/property-tax/",
        "City of Birmingham Land Reuse":    "https://www.birminghamal.gov/",
    },
    "Memphis, TN": {
        "Shelby County Tax Sale":           "https://www.shelbycountytrustee.com/",
        "Memphis Area Legal Services":      "https://www.malsi.org/",
        "Shelby County Assessor":           "https://www.assessor.shelby.tn.us/",
    },
    "Macon, GA": {
        "Bibb County Tax Sales":            "https://www.bibbtax.com/",
        "Georgia Tax Sales":                "https://www.gsccca.org/search",
    },
    "Jackson, MS": {
        "Hinds County Tax Sales":           "https://www.hindscountyms.com/",
        "Mississippi Tax Sales":            "https://www.dor.ms.gov/",
    },
    "Toledo, OH": {
        "Lucas County Tax Liens":           "https://co.lucas.oh.us/",
        "Ohio Tax Sales":                   "https://treasurer.lucas.oh.us/",
    },
    "Saint Louis, MO": {
        "St. Louis Land Bank":              "https://www.stllandbank.org/",
        "City of St. Louis Properties":     "https://www.stlouis-mo.gov/",
        "LRA Surplus Property":             "https://lranorthstl.org/",
    },
    "Government-Owned REO": {
        "HUD Home Store":                   "https://www.hudhomestore.gov/",
        "HomePath (Fannie Mae)":            "https://www.homepath.com/",
        "HomeSteps (Freddie Mac)":          "https://www.homesteps.com/",
        "USDA Rural":                       "https://properties.sc.egov.usda.gov/resales/",
        "GSA PropertyForSale":              "https://propertyforsale.gsa.gov/",
        "VA REO":                           "https://www.ocwen.com/home-search",
        "US Marshals Seized":              "https://www.usmarshals.gov/what-we-do/asset-forfeiture/current-sales",
        "IRS Seized Property":             "https://www.treasury.gov/auctions/irs/",
        "FDIC Failed Bank REO":            "https://www.fdic.gov/bank/individual/failed/banklist.html",
    },
    "Sheriff Sales": {
        "National Auction (Auction.com)":   "https://www.auction.com/residential/",
        "Hubzu Bank-Owned":                 "https://www.hubzu.com/",
        "Foreclosure.com":                  "https://www.foreclosure.com/",
        "RealtyTrac":                       "https://www.realtytrac.com/",
    },
    "Motivated Sellers / Off-Market": {
        "BatchLeads (skip trace)":          "https://batchleads.io/",
        "PropStream":                       "https://propstream.com/",
        "DealMachine":                      "https://www.dealmachine.com/",
        "REIPro":                           "https://www.reipro.com/",
    },
}

DEAL_CATEGORIES = [
    "All Deals",
    "Tax Deed",
    "Gov Seized",
    "Foreclosure",
    "Land Bank",
    "Sheriff Sale",
    "Bank Seized",
    "Section 8",
    "Seller Finance",
    "DSCR",
    "Motivated Seller",
    "Probate",
]

DEAL_BADGES = {
    "Tax Deed":       ("TAX DEED", "green"),
    "Gov Seized":     ("GOV SEIZED", "purple"),
    "Section 8":      ("SECTION 8", "blue"),
    "Seller Finance": ("SELLER FINANCE", "cyan"),
    "DSCR":           ("DSCR", "yellow"),
    "Foreclosure":    ("FORECLOSURE", "red"),
    "Land Bank":      ("LAND BANK", "magenta"),
    "Below Market":   ("BELOW MARKET", "gold"),
    "High Margin":    ("HIGH MARGIN", "bold green"),
}

HOT_MARKETS = [
    {"city": "Detroit",     "state": "MI", "avg_price": 6500,  "avg_rent": 1050, "url": "https://buildingdetroit.org/"},
    {"city": "Birmingham",  "state": "AL", "avg_price": 18000, "avg_rent": 900,  "url": "https://www.jccal.org/Default.asp?ID=734"},
    {"city": "Memphis",     "state": "TN", "avg_price": 22000, "avg_rent": 950,  "url": "https://www.shelbycountytrustee.com/"},
    {"city": "Macon",       "state": "GA", "avg_price": 15000, "avg_rent": 875,  "url": "https://www.bibbtax.com/"},
    {"city": "Jackson",     "state": "MS", "avg_price": 12000, "avg_rent": 850,  "url": "https://www.hindscountyms.com/"},
    {"city": "Toledo",      "state": "OH", "avg_price": 20000, "avg_rent": 900,  "url": "https://treasurer.lucas.oh.us/"},
    {"city": "Saint Louis", "state": "MO", "avg_price": 16000, "avg_rent": 925,  "url": "https://www.stllandbank.org/"},
    {"city": "Baltimore",   "state": "MD", "avg_price": 30000, "avg_rent": 1200, "url": "https://www.bid4assets.com/taxsale"},
    {"city": "Cleveland",   "state": "OH", "avg_price": 18000, "avg_rent": 875,  "url": "https://www.cuyahogacounty.us/"},
    {"city": "Flint",       "state": "MI", "avg_price": 8000,  "avg_rent": 850,  "url": "https://www.geneseeconnects.org/"},
]


def get_sources_by_category(category: str) -> dict:
    """Return relevant sources for a deal category."""
    mapping = {
        "Tax Deed":       ["Tax Deed / Tax Lien Auctions"],
        "Gov Seized":     ["Government-Owned REO"],
        "Foreclosure":    ["Government-Owned REO", "Sheriff Sales"],
        "Sheriff Sale":   ["Sheriff Sales"],
        "Bank Seized":    ["Sheriff Sales"],
        "Land Bank":      ["Detroit, MI (Hot Market — $4k-$15k homes)", "Saint Louis, MO"],
        "Motivated Seller": ["Motivated Sellers / Off-Market"],
        "Section 8":      ["Government-Owned REO"],
        "DSCR":           ["Tax Deed / Tax Lien Auctions", "Government-Owned REO"],
        "Seller Finance": ["Motivated Sellers / Off-Market"],
        "Probate":        ["Motivated Sellers / Off-Market"],
    }

    keys = mapping.get(category, list(GOV_SOURCES.keys()))
    result = {}
    for key in keys:
        if key in GOV_SOURCES:
            result[key] = GOV_SOURCES[key]
    return result


def analyze_deal_card(
    price: float,
    arv: float,
    est_rent: float,
    monthly_mortgage: float,
    monthly_tax: float,
    monthly_insurance: float,
    mgmt_rate: float = 0.08,
    vacancy_rate: float = 0.08,
) -> dict:
    """
    Calculate all deal card metrics the same way Tranchi.ai does.
    Returns: cash_flow, dscr, coc_return, cap_rate, high_margin flag.
    """
    eff_rent = est_rent * (1 - vacancy_rate)
    mgmt = eff_rent * mgmt_rate
    total_piti = monthly_mortgage + monthly_tax + monthly_insurance + mgmt
    cash_flow = eff_rent - total_piti

    # DSCR
    noi_annual = (eff_rent - monthly_tax - monthly_insurance - mgmt) * 12
    debt_annual = monthly_mortgage * 12
    dscr = noi_annual / debt_annual if debt_annual > 0 else 999

    # Cap rate
    cap_rate = (noi_annual / price) * 100 if price > 0 else 0

    # Cash on Cash (assuming 20% down + $5k rehab)
    cash_in = (price * 0.20) + 5000
    coc = (cash_flow * 12 / cash_in) * 100 if cash_in > 0 else 0

    # Below market %
    below_market_pct = ((arv - price) / arv * 100) if arv > 0 else 0

    # HIGH MARGIN flag — kept consistent with all_strategies_analysis (>= 60)
    high_margin = (coc > 100) or (below_market_pct >= 60) or (dscr > 5)

    # DSCR label — meaningful tiers (lenders require 1.25 min)
    if dscr >= 2.0:
        dscr_label = "Excellent"
    elif dscr >= 1.5:
        dscr_label = "Strong"
    elif dscr >= 1.25:
        dscr_label = "Moderate"
    else:
        dscr_label = "Weak"

    return {
        "cash_flow": round(cash_flow, 0),
        "dscr": round(dscr, 2),
        "dscr_label": dscr_label,
        "cap_rate": round(cap_rate, 1),
        "coc_return": round(coc, 1),
        "noi_annual": round(noi_annual, 0),
        "total_piti": round(total_piti, 0),
        "below_market_pct": round(below_market_pct, 1),
        "high_margin": high_margin,
        "is_cashflow_positive": cash_flow > 0,
        "monthly_mortgage": round(monthly_mortgage, 2),
        "monthly_tax": round(monthly_tax, 2),
        "monthly_insurance": round(monthly_insurance, 2),
        "mgmt_fee": round(mgmt, 2),
    }


def all_strategies_analysis(
    price: float,
    arv: float,
    market_rent: float,
    sqft: float = 1000,
    bedrooms: int = 3,
    state: str = "MI",
    condition: str = "medium",
    repair_override: float = None,
    buyer_credit_score: int = 730,
    buyer_cash: float = 12000,
) -> dict:
    """
    Calculate all 4 exit strategies simultaneously for a single deal.
    This is the core Tranchi.ai feature — every property card shows
    Flip, BRRRR, DSCR, and Section 8 pre-calculated side by side.
    """
    # ── Repair estimate ────────────────────────────────────────────────────
    # Per-sqft rates for hot markets like Detroit/Birmingham (lower COL = lower labor)
    REPAIR_RATES = {"light": 12, "medium": 20, "heavy": 38, "gut": 60}
    repairs = repair_override if repair_override is not None else sqft * REPAIR_RATES.get(condition.lower(), 30)
    all_in = price + repairs

    # ── Holding cost estimates (based on ARV) ─────────────────────────────
    # Property tax: roughly 2% of ARV annually for hot markets
    est_monthly_tax = max(30, round(arv * 0.02 / 12, 2))
    # Insurance: landlord policy ~0.8% of ARV annually
    est_monthly_ins = max(40, round(arv * 0.008 / 12, 2))

    # ── Effective rent (8% vacancy) ───────────────────────────────────────
    vacancy_rate = 0.08
    mgmt_rate = 0.08
    eff_rent = market_rent * (1 - vacancy_rate)
    mgmt_fee = eff_rent * mgmt_rate

    # ── STRATEGY 1: FIX & FLIP ────────────────────────────────────────────
    closing_sell = arv * 0.06         # Agent + closing costs when selling
    holding_costs_flip = (est_monthly_tax + est_monthly_ins) * 6  # 6-month hold
    flip_profit = arv - price - repairs - closing_sell - holding_costs_flip
    flip_roi = (flip_profit / (price + repairs) * 100) if (price + repairs) > 0 else 0
    # MAO: what you can pay and still make money wholesaling to a flipper
    mao = (arv * 0.70) - repairs - 3000  # 3k for buyer closing costs
    wholesale_profit = mao - price if mao > price else 0

    if flip_profit >= 25000:
        flip_verdict = "STRONG FLIP"
    elif flip_profit >= 15000:
        flip_verdict = "GOOD FLIP"
    elif flip_profit >= 5000:
        flip_verdict = "MARGINAL"
    else:
        flip_verdict = "SKIP"

    # ── STRATEGY 2: BRRRR (Buy, Rehab, Rent, Refinance, Repeat) ──────────
    refi_ltv = 0.75
    refi_rate = 0.075          # Current DSCR/investment loan rate
    refi_n = 30 * 12
    monthly_refi_rate = refi_rate / 12
    refi_loan = arv * refi_ltv

    if monthly_refi_rate > 0:
        refi_payment = refi_loan * (monthly_refi_rate * (1 + monthly_refi_rate) ** refi_n) / \
                       ((1 + monthly_refi_rate) ** refi_n - 1)
    else:
        refi_payment = refi_loan / refi_n

    cash_back = refi_loan - all_in
    capital_recycled_pct = max(0, min(100, (cash_back / all_in * 100))) if all_in > 0 else 0

    brrrr_expenses = refi_payment + est_monthly_tax + est_monthly_ins + mgmt_fee
    brrrr_cf = eff_rent - brrrr_expenses

    if cash_back >= all_in and brrrr_cf > 0:
        brrrr_verdict = "PERFECT BRRRR"
    elif cash_back >= all_in * 0.90 and brrrr_cf > 0:
        brrrr_verdict = "EXCELLENT"
    elif cash_back >= all_in * 0.75 and brrrr_cf > 0:
        brrrr_verdict = "GOOD"
    elif brrrr_cf > 0:
        brrrr_verdict = "PARTIAL — cash flows"
    else:
        brrrr_verdict = "DOESN'T WORK"

    # ── STRATEGY 3: DSCR RENTAL LOAN ─────────────────────────────────────
    # DSCR loan at 20% down (or cash-then-refi — same result)
    dscr_down = price * 0.20  # standard 20% down on a DSCR purchase loan
    if price < 50000:
        # Small properties: usually buy cash, then DSCR refi at 75% ARV
        dscr_payment = refi_payment
        dscr_down = all_in
    else:
        dscr_loan_amt = price * 0.80
        if monthly_refi_rate > 0:
            dscr_payment = dscr_loan_amt * (monthly_refi_rate * (1 + monthly_refi_rate) ** refi_n) / \
                           ((1 + monthly_refi_rate) ** refi_n - 1)
        else:
            dscr_payment = dscr_loan_amt / refi_n

    noi_annual = (eff_rent - est_monthly_tax - est_monthly_ins - mgmt_fee) * 12
    dscr_ratio = noi_annual / (dscr_payment * 12) if dscr_payment > 0 else 0
    dscr_qualifies = dscr_ratio >= 1.25 and buyer_credit_score >= 680

    dscr_cf = eff_rent - (dscr_payment + est_monthly_tax + est_monthly_ins + mgmt_fee)
    cash_in_dscr = dscr_down + 3000  # down + closing
    coc_dscr = (dscr_cf * 12 / cash_in_dscr * 100) if cash_in_dscr > 0 else 0

    # ── STRATEGY 4: SECTION 8 (Housing Choice Voucher) ────────────────────
    # HUD Fair Market Rent is typically 10-20% above market rent
    fmr_est = round(market_rent * 1.15)
    sec8_eff_rent = fmr_est * (1 - vacancy_rate * 0.5)  # Lower vacancy on Section 8
    sec8_cf = sec8_eff_rent - brrrr_expenses  # Same PITI as BRRRR scenario
    sec8_annual = fmr_est * 12
    sec8_coc = (sec8_cf * 12 / all_in * 100) if all_in > 0 else 0

    # ── BUYER POSITION (personalized to their actual numbers) ─────────────
    # Hard money: typically 10-12% rate, 80% LTV of ARV, 2 points
    hml_loan = arv * 0.80
    hml_needed_down = max(0, all_in - hml_loan)  # cash needed beyond HML
    hml_points_cost = hml_loan * 0.02
    hml_total_cash_needed = hml_needed_down + hml_points_cost + 2000  # 2k buffer

    can_wholesale  = True
    can_flip_cash  = buyer_cash >= all_in
    can_flip_hml   = buyer_cash >= hml_total_cash_needed
    can_brrrr_cash = buyer_cash >= all_in
    can_brrrr_hml  = buyer_cash >= hml_total_cash_needed
    # For small properties (<$50k), buyer buys with HML then does DSCR cash-out refi
    can_dscr = buyer_credit_score >= 680 and (
        buyer_cash >= cash_in_dscr
        or (price < 50000 and (can_brrrr_cash or can_brrrr_hml))
    )

    # ── BEST STRATEGY RECOMMENDATION ─────────────────────────────────────
    if cash_back >= all_in * 0.80 and brrrr_cf > 0 and (can_brrrr_cash or can_brrrr_hml):
        best_strategy = "BRRRR"
        best_reason = (
            f"Get ${max(0, cash_back):,.0f} back at refi + ${brrrr_cf:,.0f}/mo cash flow forever. "
            f"Recycle your capital and repeat."
        )
    elif sec8_cf > 200 and (can_brrrr_cash or can_brrrr_hml):
        best_strategy = "SECTION 8 + BRRRR"
        best_reason = (
            f"${fmr_est:,.0f}/mo gov-guaranteed rent. Buy, rehab, place Section 8 tenant, refi."
        )
    elif flip_profit >= 20000 and (can_flip_cash or can_flip_hml):
        best_strategy = "FIX & FLIP"
        best_reason = f"${flip_profit:,.0f} profit in 3-6 months. Fast cash."
    elif can_wholesale and mao > price:
        best_strategy = "WHOLESALE"
        best_reason = f"Assign contract for ${wholesale_profit:,.0f} fee. Zero money needed."
    else:
        best_strategy = "NEGOTIATE DOWN"
        best_reason = f"Numbers need seller at ${mao:,.0f} or below. Current ask too high."

    below_market_pct = ((arv - price) / arv * 100) if arv > 0 else 0
    high_margin = (below_market_pct >= 60) or (cash_back >= all_in * 0.90) or (flip_profit >= 20000)

    return {
        "price":             price,
        "arv":               arv,
        "repairs":           round(repairs, 0),
        "all_in":            round(all_in, 0),
        "below_market_pct":  round(below_market_pct, 1),
        "high_margin":       high_margin,
        "est_monthly_tax":   est_monthly_tax,
        "est_monthly_ins":   est_monthly_ins,
        "market_rent":       market_rent,
        "eff_rent":          round(eff_rent, 2),

        "flip": {
            "mao":             round(mao, 0),
            "repairs":         round(repairs, 0),
            "profit":          round(flip_profit, 0),
            "roi":             round(flip_roi, 1),
            "wholesale_fee":   round(wholesale_profit, 0),
            "timeline":        "3–6 months",
            "verdict":         flip_verdict,
            "can_do":          can_flip_cash or can_flip_hml,
        },

        "brrrr": {
            "all_in":              round(all_in, 0),
            "refi_loan":           round(refi_loan, 0),
            "cash_back":           round(cash_back, 0),
            "capital_recycled":    round(capital_recycled_pct, 1),
            "refi_payment":        round(refi_payment, 2),
            "monthly_cf":          round(brrrr_cf, 2),
            "verdict":             brrrr_verdict,
            "can_do_cash":         can_brrrr_cash,
            "can_do_hml":          can_brrrr_hml,
            "hml_cash_needed":     round(hml_total_cash_needed, 0),
        },

        "dscr": {
            "ratio":               round(dscr_ratio, 2),
            "qualifies":           dscr_qualifies,
            "down_payment":        round(cash_in_dscr, 0),
            "monthly_payment":     round(dscr_payment, 2),
            "monthly_cf":          round(dscr_cf, 2),
            "coc_return":          round(coc_dscr, 1),
            "credit_needed":       680,
            "credit_score":        buyer_credit_score,
            "can_do":              can_dscr,
        },

        "section8": {
            "fmr_est":             fmr_est,
            "market_rent":         market_rent,
            "monthly_cf":          round(sec8_cf, 2),
            "annual_income":       sec8_annual,
            "coc_return":          round(sec8_coc, 1),
            "gov_pays":            "100% of FMR",
            "vacancy_risk":        "VERY LOW",
            "can_do":              can_brrrr_cash or can_brrrr_hml,
        },

        "buyer": {
            "cash":                buyer_cash,
            "credit":              buyer_credit_score,
            "can_wholesale":       can_wholesale,
            "can_flip":            can_flip_cash or can_flip_hml,
            "can_brrrr":           can_brrrr_cash or can_brrrr_hml,
            "can_dscr":            can_dscr,
            "hml_needed":          round(hml_total_cash_needed, 0),
        },

        "best_strategy":   best_strategy,
        "best_reason":     best_reason,
        "noi_annual":      round(noi_annual, 0),
    }


def get_section8_guide() -> dict:
    """Section 8 / Housing Choice Voucher program guide."""
    return {
        "what_it_is": (
            "Section 8 (Housing Choice Voucher) is a federal program where the government "
            "pays 70-100% of the tenant's rent directly to the landlord. Tenants pay the "
            "remaining portion based on income. Government typically pays 10-20% ABOVE "
            "market rate (Fair Market Rent)."
        ),
        "benefits": [
            "Guaranteed rent payment from government (never bounces)",
            "FMR is often 10-20% above market rate",
            "Stable long-term tenants (they don't want to lose the voucher)",
            "Tenant pays security deposit, you receive gov payment monthly",
            "Works perfectly with cheap tax deed / gov seized properties",
        ],
        "how_to_apply": [
            "1. Get your property ready (meet HUD Housing Quality Standards)",
            "2. Register as a Section 8 landlord at your local HUD/PHA office",
            "3. HUD inspector visits and approves the property",
            "4. Find tenant with voucher through your local Housing Authority",
            "5. Agree on rent (must be at or below FMR for your area)",
            "6. Sign HAP (Housing Assistance Payments) contract with HUD",
            "7. Receive government portion directly every month",
        ],
        "find_your_pha": "https://www.hud.gov/program_offices/public_indian_housing/pha/contacts",
        "fmr_lookup":   "https://www.huduser.gov/portal/datasets/fmr.html",
        "section8_apply": "https://www.hud.gov/topics/housing_choice_voucher_program_section_8",
        "tenant_finder": "https://www.gosection8.com/",
        "rental_rates":  "https://www.affordablehousingonline.com/",
        "vash_program": {
            "name": "VASH — Veterans Affairs Supportive Housing",
            "what": (
                "VASH is Section 8 specifically for homeless and at-risk veterans. "
                "The VA pays the rent directly to you. Veterans are some of the most "
                "responsible tenants — they lose the voucher if they violate lease terms."
            ),
            "how_to_list": "List your property on GoSection8.com and check the VASH box. "
                           "Your local VA Housing Coordinator will reach out.",
            "va_contact": "https://www.va.gov/homeless/hchv.asp",
            "gosection8":  "https://www.gosection8.com/",
            "vash_detail": "https://www.hud.gov/program_offices/public_indian_housing/programs/hcv/vash",
            "pro_tip": (
                "Properties near VA hospitals or military bases rent faster to VASH tenants. "
                "Birmingham AL, Memphis TN, and Detroit MI all have large VA offices — "
                "perfect overlap with your hot markets."
            ),
        },
        "pro_tip": (
            "Buy in Section 8 markets like Detroit, Birmingham, Memphis, Jackson — "
            "government will pay $850-$1,200/mo on a house you bought for $4k-$20k. "
            "That's 400-2,000%+ cash-on-cash return."
        ),
    }


def get_llc_formation_guide() -> dict:
    """LLC formation for real estate investing."""
    return {
        "why_llc": [
            "Liability protection — your personal assets are shielded",
            "Professional credibility with sellers and lenders",
            "Tax advantages (pass-through taxation, deductions)",
            "Easier to scale — add properties under one entity",
        ],
        "types": {
            "Single Member LLC": "Best for beginners — simple, cheap, full protection",
            "Series LLC": "Advanced — one master LLC with sub-LLCs per property (TX, DE, IL)",
            "Land Trust + LLC": "Maximum privacy — hides your name from public records",
        },
        "how_to_form": [
            "1. Choose your state (Wyoming or Delaware for best protection)",
            "2. File Articles of Organization (~$50-$100)",
            "3. Get EIN (free at IRS.gov)",
            "4. Open business bank account (Mercury Bank recommended)",
            "5. Get Registered Agent ($50-$150/year)",
        ],
        "resources": {
            "Fikor Associates (Tranchi Partner)":   "https://fikor.com/",
            "ZenBusiness (Low Cost)":               "https://www.zenbusiness.com/",
            "Northwest Registered Agent":           "https://www.northwestregisteredagent.com/",
            "IRS EIN Application (Free)":           "https://www.irs.gov/businesses/small-businesses-self-employed/apply-for-an-employer-identification-number-ein-online",
            "Mercury Bank (Free Business Account)": "https://mercury.com/",
        },
        "cost": "$50-$500 total to get started (DIY) or $500-$2,000 with a service",
    }
