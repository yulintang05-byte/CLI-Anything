"""
BRRRR Calculator — Buy, Rehab, Rent, Refinance, Repeat.
The strategy Tranchi.ai teaches for building a portfolio with recycled capital.
"""


def calc_brrrr(
    purchase_price: float,
    repair_cost: float,
    arv: float,
    monthly_rent: float,
    refinance_ltv: float = 0.75,
    refinance_rate: float = 0.075,
    refinance_years: int = 30,
    cash_purchase: bool = True,
    hard_money_rate: float = 0.12,
    hard_money_points: float = 2.0,
    hold_months_before_refi: int = 6,
    monthly_tax: float = 0,
    monthly_insurance: float = 0,
    mgmt_rate: float = 0.08,
    vacancy_rate: float = 0.08,
) -> dict:
    """
    Full BRRRR analysis — shows how much capital you get BACK after refinancing.
    """
    # Phase 1: BUY
    all_in_cost = purchase_price + repair_cost

    # Phase 2: REHAB (already factored into all_in_cost)

    # Phase 3: RENT
    eff_rent = monthly_rent * (1 - vacancy_rate)
    mgmt_fee = eff_rent * mgmt_rate

    # Phase 4: REFINANCE
    refi_loan = arv * refinance_ltv
    monthly_rate = refinance_rate / 12
    n = refinance_years * 12
    if monthly_rate > 0:
        refi_payment = refi_loan * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
    else:
        refi_payment = refi_loan / n

    # Cash returned at refinance
    cash_out = refi_loan - all_in_cost  # Positive = you got money back

    # Holding costs before refi (if cash purchase)
    holding_costs = (monthly_tax + monthly_insurance) * hold_months_before_refi

    # Hard money costs (if using HML instead of cash)
    hml_interest = all_in_cost * (hard_money_rate / 12) * hold_months_before_refi
    hml_points = all_in_cost * (hard_money_points / 100)
    hml_total_cost = hml_interest + hml_points

    # Post-refi cash flow
    total_expenses = refi_payment + monthly_tax + monthly_insurance + mgmt_fee
    monthly_cf = eff_rent - total_expenses
    annual_cf = monthly_cf * 12

    # Annual NOI and cap rate
    noi_annual = (eff_rent - monthly_tax - monthly_insurance - mgmt_fee) * 12
    cap_rate = (noi_annual / all_in_cost) * 100 if all_in_cost > 0 else 0

    # Cash left in deal after refi
    cash_left_in = max(0, all_in_cost - refi_loan)
    coc_return = (annual_cf / cash_left_in * 100) if cash_left_in > 0 else 999

    # Equity at purchase (all-in vs ARV)
    equity_created = arv - all_in_cost
    equity_pct = (equity_created / arv * 100) if arv > 0 else 0

    return {
        # Phase breakdown
        "purchase_price":    purchase_price,
        "repair_cost":       repair_cost,
        "all_in_cost":       all_in_cost,
        "arv":               arv,
        "equity_created":    round(equity_created, 0),
        "equity_pct":        round(equity_pct, 1),

        # Refinance
        "refi_loan_amount":  round(refi_loan, 0),
        "refi_ltv_pct":      f"{refinance_ltv * 100:.0f}%",
        "refi_payment":      round(refi_payment, 2),
        "cash_returned":     round(cash_out, 0),
        "cash_left_in":      round(cash_left_in, 0),

        # Capital recycling
        "full_recycle":      cash_out >= all_in_cost,
        "partial_recycle":   0 < cash_out < all_in_cost,
        "capital_recycled_pct": round((cash_out / all_in_cost * 100), 1) if all_in_cost > 0 else 0,

        # Post-refi performance
        "monthly_rent":      monthly_rent,
        "effective_rent":    round(eff_rent, 2),
        "refi_payment":      round(refi_payment, 2),
        "monthly_tax":       monthly_tax,
        "monthly_insurance": monthly_insurance,
        "mgmt_fee":          round(mgmt_fee, 2),
        "total_expenses":    round(total_expenses, 2),
        "monthly_cash_flow": round(monthly_cf, 2),
        "annual_cash_flow":  round(annual_cf, 2),
        "cap_rate":          round(cap_rate, 1),
        "coc_return":        round(coc_return, 1),
        "noi_annual":        round(noi_annual, 0),

        # Hard money scenario
        "hml_total_cost":    round(hml_total_cost, 0),
        "hml_interest":      round(hml_interest, 0),
        "hml_points":        round(hml_points, 0),

        # Verdict
        "verdict": _brrrr_verdict(cash_out, all_in_cost, monthly_cf),
    }


def _brrrr_verdict(cash_out: float, all_in: float, monthly_cf: float) -> str:
    if cash_out >= all_in and monthly_cf > 0:
        return "PERFECT BRRRR — 100% capital recycled AND cash flows positive. Do it."
    elif cash_out >= all_in * 0.90 and monthly_cf > 0:
        return "EXCELLENT BRRRR — 90%+ capital recycled and positive cash flow."
    elif cash_out >= all_in * 0.75 and monthly_cf > 0:
        return "GOOD BRRRR — Gets most of your money back. Solid deal."
    elif cash_out > 0 and monthly_cf > 0:
        return "PARTIAL BRRRR — Doesn't fully recycle capital but cash flows. Acceptable."
    elif monthly_cf > 0:
        return "BUY & HOLD — Positive cash flow but won't recycle capital. Still works."
    else:
        return "DOESN'T WORK — Negative cash flow after refi. Find a cheaper property."


def brrrr_example() -> str:
    """Show a realistic example like Tranchi.ai's Detroit deals."""
    return """EXAMPLE: Detroit Tax Deed BRRRR

  Buy:     $6,500  (Wayne County tax deed)
  Rehab:   $18,000 (medium rehab — new roof, paint, floors)
  All-In:  $24,500

  ARV:     $65,000 (comparable sales in the area)
  Equity:  $40,500 created (62% below market!)

  REFINANCE at 75% LTV:
  Loan:    $48,750
  Cashout: $48,750 - $24,500 = +$24,250 BACK IN YOUR POCKET
  (You got ALL your money back + $24k extra to do next deal)

  POST-REFI CASH FLOW:
  Rent (Section 8): $1,050/mo
  Mortgage:           $340/mo
  Tax:                  $5/mo
  Insurance:            $2/mo
  Mgmt (8%):           $84/mo
  Net Cash Flow:      +$619/mo

  Result: FREE HOUSE that pays you $619/month."""
