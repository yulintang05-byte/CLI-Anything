"""
Comparable Sales (Comps) Validator

ARV is only as good as the comps behind it. This module:
  1. Calculates a confidence range for the ARV estimate
  2. Shows where to pull REAL comps (free + paid)
  3. Applies comp adjustments for condition, beds, sqft differences
  4. Runs a 70% rule check + adjusted MAO

Never trust one data point. This forces you to triangulate 3 sources.
"""
from typing import Optional


# ── Comp adjustment factors (standard appraisal approach) ────────────────────

BED_ADJUSTMENT       = 5000    # per bedroom difference vs subject
BATH_ADJUSTMENT      = 3000    # per bathroom difference
SQFT_ADJUSTMENT      = 35      # per square foot difference (rough)
CONDITION_ADJUSTMENT = {
    "excellent": 0.08,   # +8% vs good condition comp
    "good":      0.00,   # baseline
    "average":   -0.05,  # -5%
    "below":     -0.12,  # -12%
    "poor":      -0.20,  # -20%
}
YEAR_BUILT_ADJ       = 500     # per 10-year age difference


# ── Free comp sources ─────────────────────────────────────────────────────────

FREE_COMP_SOURCES = {
    "Zillow (Recent Sales)": {
        "url":         "https://www.zillow.com/",
        "how":         "Search the zip → click 'Recent Sales' → filter last 90 days, similar beds/baths/sqft.",
        "reliability": "Good — updated daily, but Zestimate AVMs are often off 10-20%.",
        "use_for":     "Quick sanity check. Pull 3-5 similar sales, average them.",
    },
    "Redfin": {
        "url":         "https://www.redfin.com/",
        "how":         "Search zip → 'Sold' filter → last 90 days → adjust for beds/baths/sqft.",
        "reliability": "Excellent — Redfin pulls direct MLS data. More accurate than Zillow.",
        "use_for":     "Best free comp source. Use this as your primary.",
    },
    "Realtor.com": {
        "url":         "https://www.realtor.com/",
        "how":         "Search neighborhood → 'Sold' tab → similar properties sold in 3-6 months.",
        "reliability": "Good — MLS data. Good for cross-referencing.",
        "use_for":     "Second cross-reference after Redfin.",
    },
    "ATTOM Data (Free tier)": {
        "url":         "https://www.attomdata.com/",
        "how":         "Free tier gives limited property data. Full comps require paid plan.",
        "reliability": "Excellent data quality — used by appraisers.",
        "use_for":     "For bigger deals where you need clean data.",
    },
    "HouseCanary": {
        "url":         "https://www.housecanary.com/",
        "how":         "AI-powered AVM. Free property report includes comp analysis.",
        "reliability": "Very good — machine learning based, large dataset.",
        "use_for":     "Quick AVM check. Run alongside Redfin manual comps.",
    },
    "RealtyTrac": {
        "url":         "https://www.realtytrac.com/",
        "how":         "Free property history + some comp data. Good for distressed property comps.",
        "reliability": "Moderate — good for distressed sales specifically.",
        "use_for":     "Foreclosure/REO comparable sales.",
    },
    "Neighborhood Scout": {
        "url":         "https://www.neighborhoodscout.com/",
        "how":         "Free neighborhood data includes median home values and appreciation rate.",
        "reliability": "Good for market trends, not individual comps.",
        "use_for":     "Understanding price per sqft in the neighborhood.",
    },
    "County Assessor Records": {
        "url":         "https://publicrecords.netronline.com/",
        "how":         "Pull recent deed transfers from county records. Every sale is recorded.",
        "reliability": "Excellent — official government data, exact sale price.",
        "use_for":     "Gold standard. Cross-reference with Redfin. Any difference = investigate.",
    },
}

PAID_COMP_TOOLS = {
    "PropStream": {
        "url":     "https://www.propstream.com/",
        "cost":    "$99/mo",
        "what":    "Full MLS comps, active listings, off-market sales, AVM, skip trace all-in-one.",
        "best_for": "Serious investors running 5+ deals/month.",
    },
    "BatchLeads": {
        "url":     "https://batchleads.io/",
        "cost":    "$49–$149/mo",
        "what":    "Comps, skip trace, direct mail, driving for dollars — all-in-one platform.",
        "best_for": "High-volume outreach + comp pulling in one app.",
    },
    "RPR (Realtors Property Resource)": {
        "url":     "https://www.narrpr.com/",
        "cost":    "Free for NAR members (Realtor license)",
        "what":    "Full MLS access, CMA reports, neighborhood data.",
        "best_for": "If you have or know a Realtor — ask them to pull comps for you.",
    },
    "CoStar": {
        "url":     "https://www.costar.com/",
        "cost":    "$500+/mo",
        "what":    "Commercial-grade data. Used for luxury and commercial properties.",
        "best_for": "Luxury wholesale and commercial deals only.",
    },
}


# ── Comp calculation engine ────────────────────────────────────────────────────

def adjust_comp(
    comp_price: float,
    comp_beds: int,
    comp_baths: float,
    comp_sqft: float,
    comp_condition: str,
    subject_beds: int,
    subject_baths: float,
    subject_sqft: float,
    subject_condition: str = "average",
) -> float:
    """
    Apply standard appraisal adjustments to a comparable sale price.
    Returns adjusted comp price — what the SUBJECT property should be worth
    compared to this comp.
    """
    adjusted = comp_price

    # Bedroom adjustment
    bed_diff = subject_beds - comp_beds
    adjusted += bed_diff * BED_ADJUSTMENT

    # Bathroom adjustment
    bath_diff = subject_baths - comp_baths
    adjusted += bath_diff * BATH_ADJUSTMENT

    # Size adjustment
    sqft_diff = subject_sqft - comp_sqft
    adjusted += sqft_diff * SQFT_ADJUSTMENT

    # Condition adjustment — comp condition relative to subject
    comp_cond_adj    = CONDITION_ADJUSTMENT.get(comp_condition, 0)
    subject_cond_adj = CONDITION_ADJUSTMENT.get(subject_condition, 0)
    # If comp is in better condition than subject, subtract value
    cond_delta       = subject_cond_adj - comp_cond_adj
    adjusted        *= (1 + cond_delta)

    return max(0, round(adjusted))


def validate_arv(
    your_arv: float,
    comps: list,   # list of {"price": float, "beds": int, "baths": float, "sqft": float, "condition": str}
    subject_beds: int = 3,
    subject_baths: float = 1.5,
    subject_sqft: float = 1200,
    subject_condition: str = "average",
) -> dict:
    """
    Validate your ARV estimate against comparable sales.
    Returns confidence band + recommendation.
    """
    if not comps:
        return {
            "your_arv": your_arv,
            "validated": False,
            "reason": "No comps provided — cannot validate",
            "recommendation": "Pull 3+ comps from Redfin before making an offer.",
        }

    adjusted_values = []
    for comp in comps:
        adj = adjust_comp(
            comp_price       = comp["price"],
            comp_beds        = comp.get("beds", subject_beds),
            comp_baths       = comp.get("baths", subject_baths),
            comp_sqft        = comp.get("sqft", subject_sqft),
            comp_condition   = comp.get("condition", "good"),
            subject_beds     = subject_beds,
            subject_baths    = subject_baths,
            subject_sqft     = subject_sqft,
            subject_condition = subject_condition,
        )
        adjusted_values.append(adj)

    avg_arv = sum(adjusted_values) / len(adjusted_values)
    low_arv = min(adjusted_values)
    high_arv = max(adjusted_values)

    variance_pct = abs(your_arv - avg_arv) / avg_arv * 100 if avg_arv > 0 else 0

    if variance_pct <= 5:
        confidence = "HIGH — your ARV is within 5% of comps"
        color      = "green"
    elif variance_pct <= 15:
        confidence = "MEDIUM — your ARV differs 5-15% from comps"
        color      = "yellow"
    else:
        confidence = "LOW — your ARV is 15%+ off from comps"
        color      = "red"

    if your_arv > avg_arv:
        bias = f"Your ARV is ${your_arv - avg_arv:,.0f} ABOVE comp average — be careful, MAO will be too high."
    elif your_arv < avg_arv:
        bias = f"Your ARV is ${avg_arv - your_arv:,.0f} BELOW comp average — conservative, which is safe."
    else:
        bias = "Your ARV matches the comp average exactly."

    return {
        "your_arv":         your_arv,
        "avg_comp_arv":     round(avg_arv),
        "low_comp_arv":     round(low_arv),
        "high_comp_arv":    round(high_arv),
        "comp_count":       len(comps),
        "confidence":       confidence,
        "confidence_color": color,
        "variance_pct":     round(variance_pct, 1),
        "bias_note":        bias,
        "adjusted_values":  [round(v) for v in adjusted_values],
        "recommendation": (
            f"Use ${avg_arv:,.0f} as your ARV (comp average). "
            f"Conservative: use ${low_arv:,.0f} (lowest comp). "
            f"Your MAO at 70%: ${avg_arv * 0.70:,.0f} minus repairs."
        ),
    }


def quick_comp_check(
    purchase_price: float,
    your_arv_guess: float,
    repairs: float,
    wholesale_fee: float = 10000,
    state: str = "",
    city: str = "",
    zip_code: str = "",
    beds: int = 3,
    sqft: float = 1200,
) -> dict:
    """
    Quick comp sanity check without pulling individual comps.
    Uses price-per-sqft benchmarks by market type.
    """
    # Price per sqft benchmarks (avg after-repair values in common wholesale markets)
    market_ppsf = {
        "detroit":      55,   "birmingham":  60,   "memphis":      65,
        "cleveland":    75,   "jackson":     50,   "baltimore":    120,
        "st. louis":    95,   "indianapolis": 105, "kansas city":  110,
        "cincinnati":   105,  "atlanta":      145, "houston":      125,
        "dallas":       150,  "chicago":      130, "philadelphia":  145,
        "phoenix":      175,  "miami":        300, "nashville":     200,
        "tampa":        185,  "orlando":      175, "charlotte":     165,
    }

    city_lower     = city.lower()
    est_ppsf       = None
    for mkt, ppsf in market_ppsf.items():
        if mkt in city_lower:
            est_ppsf = ppsf
            break

    mao_70  = your_arv_guess * 0.70 - repairs - wholesale_fee
    mao_65  = your_arv_guess * 0.65 - repairs - wholesale_fee

    spread      = your_arv_guess - purchase_price - repairs
    spread_pct  = (spread / your_arv_guess * 100) if your_arv_guess > 0 else 0

    result = {
        "purchase_price":   purchase_price,
        "your_arv":         your_arv_guess,
        "repairs":          repairs,
        "spread":           round(spread),
        "spread_pct":       round(spread_pct, 1),
        "mao_70_rule":      round(mao_70),
        "mao_65_rule":      round(mao_65),
        "is_deal_70":       purchase_price <= mao_70,
        "is_deal_65":       purchase_price <= mao_65,
        "below_mao_gap":    round(purchase_price - mao_70) if purchase_price > mao_70 else 0,
    }

    if est_ppsf and sqft > 0:
        mkt_arv_est = est_ppsf * sqft
        result["market_ppsf"]        = est_ppsf
        result["market_arv_estimate"] = round(mkt_arv_est)
        result["arv_vs_market"]       = round(your_arv_guess - mkt_arv_est)
        result["arv_market_note"]     = (
            f"Market average for {city}: ${est_ppsf}/sqft × {sqft:,.0f} sqft = "
            f"${mkt_arv_est:,.0f} estimated ARV. "
            + ("Your ARV is ABOVE market avg — verify with Redfin comps."
               if your_arv_guess > mkt_arv_est * 1.10 else
               "Your ARV is in line with market average — good."
               if your_arv_guess >= mkt_arv_est * 0.90 else
               "Your ARV is BELOW market avg — may be conservative (good) or a C-class area.")
        )

    # Comp pull links
    addr_enc = f"{beds}br {int(sqft)}sqft {city}"
    result["comp_sources"] = {
        "Redfin":    f"https://www.redfin.com/city/{city.lower().replace(' ','-')}/{state.upper() if state else 'XX'}",
        "Zillow":    f"https://www.zillow.com/homes/{city.lower().replace(' ','-')}-{state.upper()}_rb/",
        "NETR":      f"https://publicrecords.netronline.com/{state.lower()}/" if state else "https://publicrecords.netronline.com/",
    }

    return result
