"""
Market Intelligence Module — Real Estate Wholesale Automation CLI
All data is hardcoded/calculated. No external API dependencies.
Data reflects approximate 2024 market conditions. Always verify with local comps.
"""

from typing import Optional


# ---------------------------------------------------------------------------
# PRIMARY MARKET DATA
# ---------------------------------------------------------------------------

MARKET_DATA = {
    "Detroit": {
        "avg_price_sqft": 45,
        "avg_arv_3br": 50_000,
        "avg_rent_3br": 900,
        "appreciation_1yr": 4.0,
        "vacancy_rate": 12.0,
        "landlord_friendly": True,
        "avg_days_on_market": 45,
        "cash_buyer_pct": 55,
        "rehab_cost_sqft": 18,
        "best_strategy": "BRRRR",
        "hot_zip_codes": ["48205", "48224", "48228"],
        "risk_level": "medium",
        "notes": "Lowest entry prices in major markets; high cash buyer demand but vacancy and blight require careful neighborhood selection.",
    },
    "Birmingham": {
        "avg_price_sqft": 55,
        "avg_arv_3br": 70_000,
        "avg_rent_3br": 800,
        "appreciation_1yr": 5.5,
        "vacancy_rate": 9.0,
        "landlord_friendly": True,
        "avg_days_on_market": 35,
        "cash_buyer_pct": 45,
        "rehab_cost_sqft": 20,
        "best_strategy": "BRRRR",
        "hot_zip_codes": ["35208", "35211", "35215"],
        "risk_level": "low",
        "notes": "Strong Section 8 demand and landlord-friendly Alabama laws make this a top BRRRR market for buy-and-hold investors.",
    },
    "Memphis": {
        "avg_price_sqft": 60,
        "avg_arv_3br": 85_000,
        "avg_rent_3br": 950,
        "appreciation_1yr": 6.0,
        "vacancy_rate": 8.0,
        "landlord_friendly": True,
        "avg_days_on_market": 30,
        "cash_buyer_pct": 40,
        "rehab_cost_sqft": 22,
        "best_strategy": "BRRRR",
        "hot_zip_codes": ["38109", "38127", "38116"],
        "risk_level": "low",
        "notes": "One of the top Section 8 markets nationally; Tennessee's landlord-friendly laws and steady rent demand drive strong cash flow.",
    },
    "Cleveland": {
        "avg_price_sqft": 65,
        "avg_arv_3br": 80_000,
        "avg_rent_3br": 950,
        "appreciation_1yr": 5.0,
        "vacancy_rate": 10.0,
        "landlord_friendly": True,
        "avg_days_on_market": 40,
        "cash_buyer_pct": 50,
        "rehab_cost_sqft": 20,
        "best_strategy": "BRRRR",
        "hot_zip_codes": ["44105", "44108", "44135"],
        "risk_level": "medium",
        "notes": "Rust Belt market with improving fundamentals; cash-on-cash returns rival Detroit without the same vacancy risk.",
    },
    "Jackson MS": {
        "avg_price_sqft": 40,
        "avg_arv_3br": 55_000,
        "avg_rent_3br": 750,
        "appreciation_1yr": 3.5,
        "vacancy_rate": 14.0,
        "landlord_friendly": True,
        "avg_days_on_market": 50,
        "cash_buyer_pct": 60,
        "rehab_cost_sqft": 16,
        "best_strategy": "Wholesale",
        "hot_zip_codes": ["39209", "39212", "39204"],
        "risk_level": "high",
        "notes": "Cheapest entry prices in the southeast; primarily a volume wholesale play — buy low, assign fast, do not hold long-term.",
    },
    "Houston": {
        "avg_price_sqft": 130,
        "avg_arv_3br": 185_000,
        "avg_rent_3br": 1_550,
        "appreciation_1yr": 5.0,
        "vacancy_rate": 7.0,
        "landlord_friendly": True,
        "avg_days_on_market": 28,
        "cash_buyer_pct": 30,
        "rehab_cost_sqft": 28,
        "best_strategy": "Flip",
        "hot_zip_codes": ["77051", "77033", "77088"],
        "risk_level": "low",
        "notes": "No state income tax and massive population growth make Houston a top flip and wholesale market with deep cash buyer pools.",
    },
    "Dallas": {
        "avg_price_sqft": 160,
        "avg_arv_3br": 240_000,
        "avg_rent_3br": 1_800,
        "appreciation_1yr": 7.0,
        "vacancy_rate": 5.5,
        "landlord_friendly": True,
        "avg_days_on_market": 22,
        "cash_buyer_pct": 28,
        "rehab_cost_sqft": 32,
        "best_strategy": "Flip",
        "hot_zip_codes": ["75216", "75224", "75211"],
        "risk_level": "low",
        "notes": "DFW's rapid corporate relocation growth keeps demand high; flips move fast and wholesalers benefit from a huge rehabber network.",
    },
    "Nashville": {
        "avg_price_sqft": 210,
        "avg_arv_3br": 320_000,
        "avg_rent_3br": 2_000,
        "appreciation_1yr": 12.0,
        "vacancy_rate": 4.0,
        "landlord_friendly": True,
        "avg_days_on_market": 18,
        "cash_buyer_pct": 25,
        "rehab_cost_sqft": 30,
        "best_strategy": "Flip",
        "hot_zip_codes": ["37208", "37207", "37013"],
        "risk_level": "medium",
        "notes": "Highest appreciation in the southeast; entry costs are climbing fast but flip margins remain strong for well-sourced deals.",
    },
    "Miami": {
        "avg_price_sqft": 320,
        "avg_arv_3br": 480_000,
        "avg_rent_3br": 2_800,
        "appreciation_1yr": 8.0,
        "vacancy_rate": 3.0,
        "landlord_friendly": False,
        "avg_days_on_market": 20,
        "cash_buyer_pct": 35,
        "rehab_cost_sqft": 45,
        "best_strategy": "Luxury Wholesale",
        "hot_zip_codes": ["33142", "33147", "33167"],
        "risk_level": "high",
        "notes": "International cash buyer demand is unmatched; Florida's eviction laws are tough but luxury wholesale assignments can yield six-figure fees.",
    },
    "Atlanta": {
        "avg_price_sqft": 175,
        "avg_arv_3br": 250_000,
        "avg_rent_3br": 1_700,
        "appreciation_1yr": 7.5,
        "vacancy_rate": 6.0,
        "landlord_friendly": True,
        "avg_days_on_market": 25,
        "cash_buyer_pct": 32,
        "rehab_cost_sqft": 28,
        "best_strategy": "Flip",
        "hot_zip_codes": ["30310", "30315", "30318"],
        "risk_level": "low",
        "notes": "Film industry and tech migration keep Atlanta demand strong; inner-city zip codes offer wholesale deals while suburbs attract flippers.",
    },
    "Tampa": {
        "avg_price_sqft": 200,
        "avg_arv_3br": 290_000,
        "avg_rent_3br": 2_100,
        "appreciation_1yr": 9.0,
        "vacancy_rate": 4.5,
        "landlord_friendly": False,
        "avg_days_on_market": 22,
        "cash_buyer_pct": 30,
        "rehab_cost_sqft": 35,
        "best_strategy": "Flip",
        "hot_zip_codes": ["33605", "33610", "33619"],
        "risk_level": "medium",
        "notes": "Post-pandemic migration into Tampa Bay keeps inventory tight; flip velocity is high but rehab costs rival South Florida.",
    },
    "Phoenix": {
        "avg_price_sqft": 200,
        "avg_arv_3br": 310_000,
        "avg_rent_3br": 1_900,
        "appreciation_1yr": 6.0,
        "vacancy_rate": 6.5,
        "landlord_friendly": True,
        "avg_days_on_market": 28,
        "cash_buyer_pct": 27,
        "rehab_cost_sqft": 30,
        "best_strategy": "Flip",
        "hot_zip_codes": ["85031", "85033", "85040"],
        "risk_level": "medium",
        "notes": "Phoenix saw a price correction in 2023 creating wholesale opportunities; investor-heavy market with strong rehabber demand.",
    },
    "Kansas City": {
        "avg_price_sqft": 120,
        "avg_arv_3br": 155_000,
        "avg_rent_3br": 1_200,
        "appreciation_1yr": 6.5,
        "vacancy_rate": 6.0,
        "landlord_friendly": True,
        "avg_days_on_market": 30,
        "cash_buyer_pct": 38,
        "rehab_cost_sqft": 22,
        "best_strategy": "BRRRR",
        "hot_zip_codes": ["64130", "64128", "64134"],
        "risk_level": "low",
        "notes": "Affordable midwest market with solid rent-to-price ratios; BRRRR investors love KC for its consistent cash flow and low entry costs.",
    },
    "St Louis": {
        "avg_price_sqft": 110,
        "avg_arv_3br": 130_000,
        "avg_rent_3br": 1_050,
        "appreciation_1yr": 5.0,
        "vacancy_rate": 8.5,
        "landlord_friendly": True,
        "avg_days_on_market": 38,
        "cash_buyer_pct": 42,
        "rehab_cost_sqft": 20,
        "best_strategy": "BRRRR",
        "hot_zip_codes": ["63115", "63120", "63136"],
        "risk_level": "medium",
        "notes": "Split between strong north-side wholesale opportunities and gentrifying south-side flips; neighborhoods vary wildly so due diligence is critical.",
    },
    "Indianapolis": {
        "avg_price_sqft": 130,
        "avg_arv_3br": 165_000,
        "avg_rent_3br": 1_250,
        "appreciation_1yr": 6.0,
        "vacancy_rate": 5.5,
        "landlord_friendly": True,
        "avg_days_on_market": 28,
        "cash_buyer_pct": 35,
        "rehab_cost_sqft": 23,
        "best_strategy": "BRRRR",
        "hot_zip_codes": ["46218", "46226", "46241"],
        "risk_level": "low",
        "notes": "One of the most investor-friendly cities in the country; strong Section 8 program and consistent rent demand support long-term holds.",
    },
    "Columbus OH": {
        "avg_price_sqft": 145,
        "avg_arv_3br": 195_000,
        "avg_rent_3br": 1_400,
        "appreciation_1yr": 7.0,
        "vacancy_rate": 5.0,
        "landlord_friendly": True,
        "avg_days_on_market": 25,
        "cash_buyer_pct": 30,
        "rehab_cost_sqft": 25,
        "best_strategy": "BRRRR",
        "hot_zip_codes": ["43207", "43211", "43223"],
        "risk_level": "low",
        "notes": "Intel chip plant investment and Ohio State University keep rental demand growing; strong appreciation relative to price point.",
    },
    "Charlotte": {
        "avg_price_sqft": 190,
        "avg_arv_3br": 270_000,
        "avg_rent_3br": 1_850,
        "appreciation_1yr": 8.5,
        "vacancy_rate": 4.5,
        "landlord_friendly": True,
        "avg_days_on_market": 22,
        "cash_buyer_pct": 28,
        "rehab_cost_sqft": 28,
        "best_strategy": "Flip",
        "hot_zip_codes": ["28208", "28216", "28269"],
        "risk_level": "low",
        "notes": "Banking hub with steady corporate relocation demand; Charlotte offers flip velocity comparable to Nashville at lower entry prices.",
    },
}


# ---------------------------------------------------------------------------
# NATIONAL MARKET TRENDS 2024
# ---------------------------------------------------------------------------

MARKET_TRENDS_2024 = {
    "interest_rates": "7.0-7.5% (30yr fixed as of mid-2024)",
    "investor_activity": "Cash buyers 26% of all sales nationally",
    "rental_demand": "Vacancy at record lows in sunbelt cities; midwest stabilizing",
    "home_price_trend": "National median up ~3-4% YoY after 2023 correction; sunbelt cooling, midwest rising",
    "wholesale_assignment_fees": "Average wholesale fee $12,000-$22,000 nationally; luxury markets $40,000-$100,000+",
    "days_on_market_national": "42 days average nationally for distressed/investor-grade properties",
    "hot_strategies": [
        "BRRRR in midwest (Detroit, Cleveland, Indianapolis, Kansas City)",
        "Fix & flip in southeast (Atlanta, Charlotte, Birmingham)",
        "Luxury wholesale in Miami and Dallas luxury pockets",
        "Section 8 BRRRR in Memphis and Birmingham",
        "Tax lien investing in Florida, New Jersey, Illinois",
    ],
    "cooling_strategies": [
        "Short-term rental (Airbnb) in over-saturated markets",
        "New construction wholesale — margins compressed by rising materials costs",
        "High-LTV flips in high interest rate environment",
    ],
    "tax_lien_states": [
        "Florida — 18% interest rate on tax lien certificates",
        "New Jersey — up to 18% interest",
        "Illinois — 36% penalty if not redeemed within 6 months",
        "Arizona — up to 16% interest",
        "Maryland — up to 20% penalty",
        "Iowa — up to 24% maximum interest",
    ],
    "landlord_friendly_states": [
        "Texas — no state income tax, fast eviction process (3-30 days)",
        "Georgia — 30-day eviction process, no rent control",
        "Tennessee — strong landlord protections, fast eviction courts",
        "Indiana — 45-day eviction max, no rent control statewide",
        "Michigan — no rent control, court-ordered eviction ~30 days",
        "Alabama — fastest eviction timelines in the southeast (~14 days)",
        "Missouri — landlord-friendly statutes, low property taxes",
        "Ohio — no rent control, streamlined eviction process",
    ],
    "tenant_friendly_states_to_avoid": [
        "California — rent control, 3-12 month eviction timelines",
        "New York — extreme tenant protections, 6-18 month evictions",
        "Oregon — statewide rent control cap",
        "New Jersey — strong tenant protections in many municipalities",
        "Illinois (Chicago) — rent control in city limits",
    ],
    "emerging_markets_2024": [
        "Huntsville AL — defense sector growth, rapidly appreciating",
        "Greenville SC — manufacturing boom, affordable entry prices",
        "San Antonio TX — military and tech growth, below-state-average prices",
        "Columbus OH — Intel investment driving appreciation",
        "Raleigh-Durham NC — Research Triangle tech growth",
    ],
    "market_risks_2024": [
        "Interest rate sensitivity — ARV compression when buyers cannot qualify",
        "Insurance costs rising 20-40% in Florida and Texas coastal areas",
        "Flood zone recertification affecting coastal property values",
        "Overbuilt multifamily in sunbelt suppressing rent growth temporarily",
        "Municipal code enforcement crackdowns on vacant properties in midwest",
    ],
}


# ---------------------------------------------------------------------------
# SCORING ENGINE
# ---------------------------------------------------------------------------

def WHOLESALE_MARKET_SCORE(market: str) -> dict:
    """
    Analyze a market by name and return a comprehensive score dict.

    Parameters
    ----------
    market : str
        Market name matching a key in MARKET_DATA (case-insensitive partial match allowed).

    Returns
    -------
    dict with keys: overall_score, entry_barrier, exit_speed, rental_yield,
                    appreciation_outlook, recommended_for, warnings, verdict
    """
    # Resolve market name with case-insensitive fuzzy match
    resolved = _resolve_market(market)
    if resolved is None:
        return {
            "error": f"Market '{market}' not found. Available: {', '.join(MARKET_DATA.keys())}",
            "overall_score": 0,
        }

    data = MARKET_DATA[resolved]

    # --- Entry Barrier ---
    arv = data["avg_arv_3br"]
    if arv <= 80_000:
        entry_barrier = "low"
        entry_score = 9
    elif arv <= 175_000:
        entry_barrier = "medium"
        entry_score = 6
    else:
        entry_barrier = "high"
        entry_score = 3

    # --- Exit Speed (assign/close velocity) ---
    dom = data["avg_days_on_market"]
    cash_pct = data["cash_buyer_pct"]
    if dom <= 22 and cash_pct >= 30:
        exit_speed = "fast"
        exit_score = 9
    elif dom <= 35 and cash_pct >= 25:
        exit_speed = "moderate"
        exit_score = 6
    else:
        exit_speed = "slow"
        exit_score = 3

    # --- Rental Yield (gross annual rent / ARV) ---
    annual_rent = data["avg_rent_3br"] * 12
    gross_yield = (annual_rent / arv) * 100 if arv > 0 else 0
    if gross_yield >= 14:
        rental_yield = f"{gross_yield:.1f}% gross (excellent)"
        yield_score = 10
    elif gross_yield >= 10:
        rental_yield = f"{gross_yield:.1f}% gross (strong)"
        yield_score = 8
    elif gross_yield >= 7:
        rental_yield = f"{gross_yield:.1f}% gross (good)"
        yield_score = 6
    elif gross_yield >= 5:
        rental_yield = f"{gross_yield:.1f}% gross (average)"
        yield_score = 4
    else:
        rental_yield = f"{gross_yield:.1f}% gross (weak)"
        yield_score = 2

    # --- Appreciation Outlook ---
    appr = data["appreciation_1yr"]
    if appr >= 10:
        appreciation_outlook = "very high"
        appr_score = 10
    elif appr >= 7:
        appreciation_outlook = "high"
        appr_score = 8
    elif appr >= 5:
        appreciation_outlook = "moderate"
        appr_score = 6
    else:
        appreciation_outlook = "low"
        appr_score = 4

    # --- Vacancy penalty ---
    vacancy = data["vacancy_rate"]
    if vacancy >= 12:
        vacancy_penalty = 2
    elif vacancy >= 8:
        vacancy_penalty = 1
    else:
        vacancy_penalty = 0

    # --- Landlord friendly bonus ---
    ll_bonus = 1 if data["landlord_friendly"] else -1

    # --- Composite score (1-10) ---
    raw = (
        entry_score * 0.20
        + exit_score * 0.20
        + yield_score * 0.25
        + appr_score * 0.20
        + (10 - vacancy * 0.5) * 0.15
    )
    raw = raw + ll_bonus - vacancy_penalty
    overall_score = max(1.0, min(10.0, round(raw, 1)))

    # --- Recommended strategies ---
    recommended_for = [data["best_strategy"]]
    if gross_yield >= 12:
        if "Section 8" not in recommended_for:
            recommended_for.append("Section 8")
    if entry_barrier == "low" and cash_pct >= 40:
        if "Wholesale" not in recommended_for:
            recommended_for.append("Wholesale")
    if appr >= 8 and entry_barrier != "high":
        if "Flip" not in recommended_for:
            recommended_for.append("Flip")
    if data["landlord_friendly"] and gross_yield >= 8:
        if "Buy & Hold" not in recommended_for:
            recommended_for.append("Buy & Hold")

    # --- Warnings ---
    warnings = []
    if vacancy >= 10:
        warnings.append(f"High vacancy rate ({vacancy}%) — screen tenants carefully, choose neighborhoods wisely")
    if not data["landlord_friendly"]:
        warnings.append("Tenant-friendly state — budget for long eviction timelines and legal fees")
    if entry_barrier == "high":
        warnings.append("High entry costs require significant capital or hard money access")
    if data["risk_level"] == "high":
        warnings.append(f"Risk level is HIGH — this market requires local market knowledge")
    if appr < 4:
        warnings.append("Low appreciation — focus on cash flow, not equity plays")
    if data["rehab_cost_sqft"] >= 40:
        warnings.append(f"High rehab costs (${data['rehab_cost_sqft']}/sqft) — verify contractor bids carefully")

    # --- Verdict ---
    if overall_score >= 8:
        verdict = f"{resolved} is a top-tier wholesale/investment market — strong fundamentals across all metrics."
    elif overall_score >= 6:
        verdict = f"{resolved} is a solid market for {data['best_strategy']} strategies with manageable risks."
    elif overall_score >= 4:
        verdict = f"{resolved} has niche opportunities but requires specialized knowledge to execute profitably."
    else:
        verdict = f"{resolved} is a high-risk market — wholesale only for experienced operators with local boots on the ground."

    return {
        "market": resolved,
        "overall_score": overall_score,
        "entry_barrier": entry_barrier,
        "exit_speed": exit_speed,
        "rental_yield": rental_yield,
        "gross_yield_pct": round(gross_yield, 2),
        "appreciation_outlook": appreciation_outlook,
        "appreciation_rate_pct": appr,
        "vacancy_rate_pct": vacancy,
        "cash_buyer_pct": cash_pct,
        "avg_arv_3br": arv,
        "avg_rent_3br": data["avg_rent_3br"],
        "avg_price_sqft": data["avg_price_sqft"],
        "rehab_cost_sqft": data["rehab_cost_sqft"],
        "landlord_friendly": data["landlord_friendly"],
        "best_strategy": data["best_strategy"],
        "hot_zip_codes": data["hot_zip_codes"],
        "risk_level": data["risk_level"],
        "recommended_for": recommended_for,
        "warnings": warnings,
        "notes": data["notes"],
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# COMPARISON & REPORTING FUNCTIONS
# ---------------------------------------------------------------------------

def get_market_comparison(markets: list) -> list:
    """
    Compare multiple markets side by side.

    Parameters
    ----------
    markets : list of str
        List of market names (e.g. ["Detroit", "Memphis", "Atlanta"]).

    Returns
    -------
    list of score dicts sorted by overall_score descending.
    """
    results = []
    for m in markets:
        score = WHOLESALE_MARKET_SCORE(m)
        results.append(score)
    results.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
    return results


def get_market_trends_report() -> dict:
    """
    Return national market trends plus top 5 recommended markets for 2024-2025.

    Returns
    -------
    dict with 'national_trends', 'top_markets_2024_2025', and 'summary'.
    """
    all_scores = []
    for market_name in MARKET_DATA:
        score = WHOLESALE_MARKET_SCORE(market_name)
        all_scores.append(score)
    all_scores.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
    top_5 = all_scores[:5]

    summary_lines = []
    for i, m in enumerate(top_5, 1):
        summary_lines.append(
            f"{i}. {m['market']} — Score {m['overall_score']}/10 | "
            f"Best for: {m['best_strategy']} | ARV: ${m['avg_arv_3br']:,} | "
            f"Yield: {m['gross_yield_pct']}%"
        )

    return {
        "report_date": "2024 (mid-year snapshot)",
        "national_trends": MARKET_TRENDS_2024,
        "top_markets_2024_2025": top_5,
        "top_5_summary": summary_lines,
        "analyst_note": (
            "With rates above 7%, cash flow is king. Midwest BRRRR markets dominate ROI rankings. "
            "Sunbelt flips remain viable for experienced operators with solid contractor relationships. "
            "Luxury wholesale in Miami and Dallas commands premium fees but requires larger buyer lists."
        ),
    }


def get_best_markets_for_strategy(strategy: str) -> list:
    """
    Return top 5 markets sorted by score for a given investment strategy.

    Parameters
    ----------
    strategy : str
        One of: "Wholesale", "BRRRR", "Flip", "Section 8", "Luxury"

    Returns
    -------
    list of up to 5 score dicts, best markets for that strategy.
    """
    strategy_clean = strategy.strip().lower()

    # Strategy-specific scoring weights / filters
    strategy_map = {
        "wholesale": {
            "keywords": ["wholesale", "Wholesale"],
            "favor_high_cash_pct": True,
            "favor_low_entry": True,
            "favor_fast_exit": True,
        },
        "brrrr": {
            "keywords": ["brrrr", "BRRRR", "buy & hold", "Section 8"],
            "favor_high_yield": True,
            "favor_landlord_friendly": True,
            "favor_low_entry": True,
        },
        "flip": {
            "keywords": ["flip", "Flip"],
            "favor_appreciation": True,
            "favor_fast_exit": True,
        },
        "section 8": {
            "keywords": ["section 8", "Section 8", "brrrr", "BRRRR"],
            "favor_high_yield": True,
            "favor_landlord_friendly": True,
            "require_landlord_friendly": True,
        },
        "luxury": {
            "keywords": ["luxury", "Luxury Wholesale"],
            "min_arv": 250_000,
        },
    }

    matched_key = None
    for key in strategy_map:
        if strategy_clean == key or strategy_clean in key or key in strategy_clean:
            matched_key = key
            break

    if matched_key is None:
        # Fallback: score all and return top 5
        return get_market_comparison(list(MARKET_DATA.keys()))[:5]

    cfg = strategy_map[matched_key]
    candidates = []

    for market_name, data in MARKET_DATA.items():
        score = WHOLESALE_MARKET_SCORE(market_name)
        base = score.get("overall_score", 0)

        # Apply strategy-specific bonuses/filters
        bonus = 0.0

        if cfg.get("require_landlord_friendly") and not data["landlord_friendly"]:
            continue  # Hard exclude

        if cfg.get("min_arv") and data["avg_arv_3br"] < cfg["min_arv"]:
            continue  # Hard exclude low-value markets for luxury

        if cfg.get("favor_high_cash_pct") and data["cash_buyer_pct"] >= 40:
            bonus += 1.0
        if cfg.get("favor_low_entry") and data["avg_arv_3br"] <= 175_000:
            bonus += 0.5
        if cfg.get("favor_fast_exit") and data["avg_days_on_market"] <= 28:
            bonus += 0.5
        if cfg.get("favor_high_yield"):
            gross = (data["avg_rent_3br"] * 12 / data["avg_arv_3br"]) * 100
            if gross >= 14:
                bonus += 1.5
            elif gross >= 10:
                bonus += 0.75
        if cfg.get("favor_landlord_friendly") and data["landlord_friendly"]:
            bonus += 0.5
        if cfg.get("favor_appreciation") and data["appreciation_1yr"] >= 8:
            bonus += 1.0

        # Check if strategy is in recommended list
        strategy_keywords = cfg.get("keywords", [])
        for kw in strategy_keywords:
            if kw.lower() in [r.lower() for r in score.get("recommended_for", [])]:
                bonus += 0.5
                break

        score["strategy_score"] = round(min(10.0, base + bonus), 1)
        score["strategy_match"] = matched_key.title()
        candidates.append(score)

    candidates.sort(key=lambda x: x.get("strategy_score", 0), reverse=True)
    return candidates[:5]


def calc_market_appreciation(purchase_price: float, years: int, market: str) -> dict:
    """
    Project future property value based on historical appreciation rate for a market.

    Parameters
    ----------
    purchase_price : float
        Purchase price in dollars.
    years : int
        Number of years to project.
    market : str
        Market name (e.g. "Detroit", "Nashville").

    Returns
    -------
    dict with year-by-year projections and summary.
    """
    resolved = _resolve_market(market)
    if resolved is None:
        return {
            "error": f"Market '{market}' not found. Available: {', '.join(MARKET_DATA.keys())}",
        }

    data = MARKET_DATA[resolved]
    annual_rate = data["appreciation_1yr"] / 100.0
    projections = []
    current_value = purchase_price

    for year in range(1, years + 1):
        current_value = current_value * (1 + annual_rate)
        equity_gained = current_value - purchase_price
        roi_pct = ((current_value - purchase_price) / purchase_price) * 100
        projections.append({
            "year": year,
            "projected_value": round(current_value, 2),
            "equity_gained": round(equity_gained, 2),
            "roi_pct": round(roi_pct, 2),
        })

    final = projections[-1]
    return {
        "market": resolved,
        "purchase_price": purchase_price,
        "years": years,
        "annual_appreciation_rate_pct": data["appreciation_1yr"],
        "projected_final_value": final["projected_value"],
        "total_equity_gained": final["equity_gained"],
        "total_roi_pct": final["roi_pct"],
        "year_by_year": projections,
        "disclaimer": (
            "Projection based on recent 1-year appreciation rate. "
            "Past performance does not guarantee future results. "
            "Market cycles, interest rates, and local economic shifts affect actual outcomes."
        ),
    }


# ---------------------------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------------------------

def _resolve_market(market: str) -> Optional[str]:
    """
    Resolve a market name string to an exact key in MARKET_DATA.
    Tries exact match first, then case-insensitive, then partial match.
    """
    if market in MARKET_DATA:
        return market

    market_lower = market.strip().lower()
    for key in MARKET_DATA:
        if key.lower() == market_lower:
            return key

    for key in MARKET_DATA:
        if market_lower in key.lower() or key.lower() in market_lower:
            return key

    return None


wholesale_market_score = WHOLESALE_MARKET_SCORE


def list_available_markets() -> list:
    """Return a sorted list of all available market names."""
    return sorted(MARKET_DATA.keys())


def get_market_quick_stats(market: str) -> dict:
    """
    Return a compact snapshot of a market without full scoring.

    Parameters
    ----------
    market : str
        Market name.

    Returns
    -------
    dict with key metrics only.
    """
    resolved = _resolve_market(market)
    if resolved is None:
        return {"error": f"Market '{market}' not found."}

    data = MARKET_DATA[resolved]
    gross_yield = round((data["avg_rent_3br"] * 12 / data["avg_arv_3br"]) * 100, 2)
    mao_estimate = round(data["avg_arv_3br"] * 0.70 - (data["rehab_cost_sqft"] * 1200), 2)

    return {
        "market": resolved,
        "avg_arv_3br": f"${data['avg_arv_3br']:,}",
        "avg_rent_3br": f"${data['avg_rent_3br']:,}/mo",
        "gross_yield": f"{gross_yield}%",
        "price_per_sqft": f"${data['avg_price_sqft']}",
        "rehab_cost_sqft": f"${data['rehab_cost_sqft']}",
        "appreciation_1yr": f"{data['appreciation_1yr']}%",
        "vacancy_rate": f"{data['vacancy_rate']}%",
        "cash_buyer_pct": f"{data['cash_buyer_pct']}%",
        "dom_distressed": f"{data['avg_days_on_market']} days",
        "landlord_friendly": data["landlord_friendly"],
        "best_strategy": data["best_strategy"],
        "risk_level": data["risk_level"],
        "hot_zips": data["hot_zip_codes"],
        "estimated_mao_3br_1200sqft": f"${max(0, mao_estimate):,.0f}",
        "notes": data["notes"],
    }
