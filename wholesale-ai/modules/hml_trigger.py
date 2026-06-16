"""
Hard Money Lender Auto-Trigger — fires automatically when a BRRRR deal
scores high enough to warrant an immediate lender match + pre-qual checklist.

Thresholds (all must pass):
  • ARV known
  • Purchase price ≤ 70% ARV
  • Estimated rehab ≤ 40% ARV
  • After-rehab equity (ARV - purchase - rehab) ≥ $15,000
  • Projected DSCR after refi ≥ 1.10

When triggered, returns the top 3 matched HML lenders + a pre-qual packet
the investor can send or print.
"""

from typing import Optional
from modules.lender_directory import HARD_MONEY_LENDERS, DSCR_LENDERS


# ── Trigger thresholds ────────────────────────────────────────────────────────

BRRRR_HML_TRIGGER = {
    "max_purchase_to_arv":  0.70,   # don't pay more than 70% of ARV
    "max_rehab_to_arv":     0.40,   # rehab ≤ 40% ARV keeps numbers clean
    "min_equity_after":     15_000, # min equity left after purchase + rehab
    "min_dscr_after_refi":  1.10,   # DSCR threshold to hold as rental
    "min_arv":              50_000, # below this most HMLs won't touch it
}

# Typical DSCR refi assumption for trigger calc
REFI_RATE_ASSUMPTION   = 0.075   # 7.5% DSCR loan rate
REFI_TERM_YEARS        = 30
REFI_LTV               = 0.75    # cash-out refi at 75% ARV
VACANCY_RATE           = 0.08    # 8% vacancy
EXPENSE_RATIO          = 0.45    # 45% of gross rent = expenses (taxes, ins, mgmt, repairs)


# ── Core trigger logic ────────────────────────────────────────────────────────

def _monthly_payment(principal: float, annual_rate: float, years: int) -> float:
    if annual_rate == 0:
        return principal / (years * 12)
    r = annual_rate / 12
    n = years * 12
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def evaluate_brrrr_trigger(
    purchase_price:  float,
    estimated_rehab: float,
    arv:             float,
    monthly_rent:    float,
    credit_score:    int = 680,
    state:           str = "",
) -> dict:
    """
    Evaluate whether this BRRRR deal should auto-trigger the HML matching flow.

    Returns:
        triggered (bool)
        reason (str) — why it did or didn't trigger
        metrics (dict) — all calculated values
        matched_lenders (list) — top 3 HML lenders if triggered
        pre_qual_checklist (list) — what to gather before calling lenders
    """
    t = BRRRR_HML_TRIGGER

    purchase_to_arv = purchase_price / arv if arv > 0 else 999
    rehab_to_arv    = estimated_rehab / arv if arv > 0 else 999
    total_in        = purchase_price + estimated_rehab
    equity_after    = arv - total_in
    refi_loan       = arv * REFI_LTV
    refi_payment    = _monthly_payment(refi_loan, REFI_RATE_ASSUMPTION, REFI_TERM_YEARS)
    effective_rent  = monthly_rent * (1 - VACANCY_RATE)
    noi_monthly     = effective_rent * (1 - EXPENSE_RATIO)
    dscr            = noi_monthly / refi_payment if refi_payment > 0 else 0
    cash_at_close   = total_in - refi_loan   # leftover cash needed after cash-out refi

    metrics = {
        "purchase_price":    purchase_price,
        "estimated_rehab":   estimated_rehab,
        "arv":               arv,
        "total_in":          total_in,
        "purchase_to_arv":   round(purchase_to_arv * 100, 1),
        "rehab_to_arv":      round(rehab_to_arv * 100, 1),
        "equity_after":      equity_after,
        "refi_loan":         refi_loan,
        "refi_payment_mo":   round(refi_payment, 2),
        "effective_rent":    round(effective_rent, 2),
        "noi_monthly":       round(noi_monthly, 2),
        "dscr_after_refi":   round(dscr, 2),
        "cash_at_close":     round(cash_at_close, 2),
        "monthly_cash_flow": round(noi_monthly - refi_payment, 2),
    }

    # Check each threshold
    fails = []
    if arv < t["min_arv"]:
        fails.append(f"ARV ${arv:,.0f} is below ${t['min_arv']:,.0f} HML minimum")
    if purchase_to_arv > t["max_purchase_to_arv"]:
        fails.append(
            f"Purchase is {purchase_to_arv*100:.0f}% of ARV "
            f"(max {t['max_purchase_to_arv']*100:.0f}%)"
        )
    if rehab_to_arv > t["max_rehab_to_arv"]:
        fails.append(
            f"Rehab is {rehab_to_arv*100:.0f}% of ARV "
            f"(max {t['max_rehab_to_arv']*100:.0f}%)"
        )
    if equity_after < t["min_equity_after"]:
        fails.append(
            f"Equity after rehab is ${equity_after:,.0f} "
            f"(need ≥${t['min_equity_after']:,.0f})"
        )
    if dscr < t["min_dscr_after_refi"]:
        fails.append(
            f"Projected DSCR {dscr:.2f} is below {t['min_dscr_after_refi']:.2f} threshold"
        )

    if fails:
        return {
            "triggered":           False,
            "reason":              " | ".join(fails),
            "fails":               fails,
            "metrics":             metrics,
            "matched_lenders":     [],
            "pre_qual_checklist":  [],
        }

    # Triggered — match lenders
    matched = _match_hml_lenders(purchase_price, credit_score, state)
    checklist = _build_pre_qual_checklist(metrics)

    return {
        "triggered":          True,
        "reason":             (
            f"All thresholds passed — DSCR {dscr:.2f}, equity ${equity_after:,.0f}, "
            f"purchase at {purchase_to_arv*100:.0f}% ARV"
        ),
        "fails":              [],
        "metrics":            metrics,
        "matched_lenders":    matched,
        "pre_qual_checklist": checklist,
    }


def _match_hml_lenders(purchase_price: float, credit_score: int, state: str) -> list:
    """Return top 3 HML lenders sorted by fit for the given deal parameters."""
    candidates = []
    for lender in HARD_MONEY_LENDERS:
        # Parse loan range
        try:
            lo_str = lender.get("loan_range", "$0–$999M").replace("$", "").replace(",", "").split("–")[0].replace("k", "000").replace("M", "000000")
            hi_str = lender.get("loan_range", "$0–$999M").replace("$", "").replace(",", "").split("–")[-1].replace("k", "000").replace("M", "000000")
            lo = float(lo_str)
            hi = float(hi_str)
        except Exception:
            lo, hi = 0, 999_000_000

        if not (lo <= purchase_price <= hi):
            continue

        min_credit = lender.get("min_credit", 600)
        if credit_score < min_credit:
            continue

        states_str = lender.get("states", "Nationwide").lower()
        if state and "nationwide" not in states_str and state.lower() not in states_str:
            pass  # still include — many lenders say 44+ states; don't over-filter

        score = 0
        if credit_score >= 680:
            score += 1
        if "nationwide" in states_str.lower():
            score += 1
        if "brrrr" in lender.get("specialty", "").lower() or "rental" in lender.get("specialty", "").lower():
            score += 2

        candidates.append({**lender, "_score": score})

    candidates.sort(key=lambda x: x["_score"], reverse=True)
    return candidates[:3]


def _build_pre_qual_checklist(metrics: dict) -> list:
    return [
        "Government-issued ID (driver's license or passport)",
        "Last 2 years tax returns (personal + business if applicable)",
        "Last 3 months bank statements (shows liquidity for down payment + reserves)",
        f"Proof of funds or LOC for estimated down payment (${metrics['cash_at_close']:,.0f})",
        "Property details: address, purchase contract, listing or appraisal",
        f"Scope of work / rehab budget (estimated ${metrics['estimated_rehab']:,.0f})",
        f"ARV support: 3 comparable sales within 1 mile / 6 months (supporting ${metrics['arv']:,.0f})",
        "Rent comparables (3 active rentals near subject — supports your rent estimate)",
        "Entity docs if buying in LLC (articles of organization, EIN letter)",
        "Insurance binder — HML requires hazard insurance at close",
        "Track record summary (past flips or rentals; first-timers add partner bio)",
    ]


# ── BRRRR scenario builder ────────────────────────────────────────────────────

def brrrr_scenarios(arv: float, monthly_rent: float) -> list:
    """
    Return 3 scenarios (conservative, moderate, aggressive) showing what
    purchase + rehab combos work for a given ARV and rent target.
    """
    scenarios = []
    for label, pp_pct, rh_pct in [
        ("Conservative", 0.55, 0.15),
        ("Moderate",     0.60, 0.18),
        ("Aggressive",   0.65, 0.22),
    ]:
        pp = arv * pp_pct
        rh = arv * rh_pct
        result = evaluate_brrrr_trigger(pp, rh, arv, monthly_rent)
        scenarios.append({
            "label":     label,
            "purchase":  pp,
            "rehab":     rh,
            "total_in":  pp + rh,
            "triggered": result["triggered"],
            "dscr":      result["metrics"]["dscr_after_refi"],
            "equity":    result["metrics"]["equity_after"],
            "cash_flow": result["metrics"]["monthly_cash_flow"],
        })
    return scenarios


# ── Quick summary for menu ────────────────────────────────────────────────────

def hml_trigger_summary(result: dict) -> str:
    if result["triggered"]:
        lenders = result["matched_lenders"]
        top = lenders[0]["name"] if lenders else "N/A"
        m = result["metrics"]
        return (
            f"TRIGGERED — DSCR {m['dscr_after_refi']:.2f} | "
            f"Equity ${m['equity_after']:,.0f} | "
            f"Cash flow ${m['monthly_cash_flow']:,.0f}/mo | "
            f"Top lender: {top}"
        )
    return f"NOT triggered — {result['reason']}"
