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

    # HIGH MARGIN flag: Tranchi flags if CoC > 100% or below market > 70%
    high_margin = (coc > 100) or (below_market_pct > 60) or (dscr > 5)

    # DSCR label
    if dscr >= 10:
        dscr_label = "Strong"
    elif dscr >= 2:
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
