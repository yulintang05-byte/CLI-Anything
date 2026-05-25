"""
Deal Calculator — MAO, ARV, ROI, cash flow, and wholesale fee math.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DealInputs:
    arv: float                    # After Repair Value
    repair_cost: float            # Estimated repairs
    purchase_price: float         # What seller wants (or your offer)
    wholesale_fee: float = 10000  # Your assignment fee
    closing_costs: float = 3000   # Buyer's closing costs estimate
    holding_months: int = 0       # Months holding (0 = no hold)
    monthly_holding: float = 800  # Insurance, taxes, utilities per month
    arv_discount: float = 0.70    # Conservative 70% rule (use 0.65 for tighter)


@dataclass
class DealResult:
    mao: float                    # Max Allowable Offer (what you pay seller)
    max_end_buyer_price: float    # What you sell to cash buyer
    suggested_offer: float        # Your opening offer (MAO - negotiation room)
    profit_at_mao: float          # Wholesale profit if you pay MAO
    profit_at_offer: float        # Profit if seller accepts opening offer
    equity_spread: float          # ARV - (purchase + repairs)
    roi_percent: float            # Return as % of money in deal
    cash_in_deal: float           # Your actual cash needed (typically $0 for pure wholesale)
    arv: float
    repair_cost: float
    is_deal: bool                 # True if profitable at MAO
    grade: str                    # A/B/C/F rating
    notes: list = field(default_factory=list)


def calculate_deal(inputs: DealInputs) -> DealResult:
    """Run the full wholesale deal analysis."""
    # MAO Formula: (ARV × discount%) - repairs - closing - holding - wholesale fee
    holding_cost = inputs.holding_months * inputs.monthly_holding
    mao = (inputs.arv * inputs.arv_discount) - inputs.repair_cost - inputs.closing_costs - holding_cost

    # What you list the contract for to end buyers (MAO + your fee)
    max_end_buyer_price = mao + inputs.wholesale_fee

    # Suggested opening offer: 10-15% below MAO for negotiating room
    suggested_offer = mao * 0.88

    # Equity spread from seller's asking price
    equity_spread = inputs.arv - (inputs.purchase_price + inputs.repair_cost)

    # Profit scenarios
    profit_at_mao = inputs.wholesale_fee
    profit_at_offer = mao - suggested_offer + inputs.wholesale_fee

    # ROI (on EMD/earnest money — typically ~$1k-2k for wholesalers)
    emd_estimate = max(1000, mao * 0.01)
    roi_percent = (inputs.wholesale_fee / emd_estimate) * 100

    # Cash wholesalers actually need in deal (just EMD)
    cash_in_deal = emd_estimate

    # Is it a deal?
    is_deal = mao > 0 and (inputs.purchase_price <= mao)
    spread_ok = equity_spread >= 30000

    # Grade the deal
    notes = []
    if inputs.purchase_price > mao:
        gap = inputs.purchase_price - mao
        notes.append(f"Seller asking ${gap:,.0f} too much — needs price reduction")
    if inputs.repair_cost > inputs.arv * 0.25:
        notes.append("Heavy rehab — end buyers will expect a steeper discount")
    if inputs.wholesale_fee < 5000:
        notes.append("Wholesale fee under $5k — consider if your time is worth it")
    if inputs.wholesale_fee > 20000:
        notes.append("Fee over $20k may scare off buyers — consider $10-15k range")
    if not is_deal:
        notes.append("Numbers don't work at seller's price — must negotiate down")
    if spread_ok and is_deal:
        notes.append("Strong equity spread — attractive to cash buyers")

    if is_deal and equity_spread >= 50000:
        grade = "A"
    elif is_deal and equity_spread >= 30000:
        grade = "B"
    elif is_deal and equity_spread >= 15000:
        grade = "C"
    else:
        grade = "F"

    return DealResult(
        mao=max(0, mao),
        max_end_buyer_price=max(0, max_end_buyer_price),
        suggested_offer=max(0, suggested_offer),
        profit_at_mao=profit_at_mao,
        profit_at_offer=profit_at_offer,
        equity_spread=equity_spread,
        roi_percent=roi_percent,
        cash_in_deal=cash_in_deal,
        arv=inputs.arv,
        repair_cost=inputs.repair_cost,
        is_deal=is_deal,
        grade=grade,
        notes=notes,
    )


def quick_mao(arv: float, repairs: float, wholesale_fee: float = 10000, discount: float = 0.70) -> float:
    """Quick MAO calculation."""
    return (arv * discount) - repairs - wholesale_fee


def estimate_repairs(sqft: float, condition: str) -> float:
    """
    Rough repair estimate by condition.
    condition: 'light' | 'medium' | 'heavy' | 'gut'
    """
    rates = {"light": 15, "medium": 30, "heavy": 50, "gut": 75}
    rate = rates.get(condition.lower(), 30)
    return sqft * rate


def estimate_arv(price_per_sqft: float, sqft: float) -> float:
    """Rough ARV from comps per sqft."""
    return price_per_sqft * sqft


def cash_flow_analysis(
    purchase_price: float,
    monthly_rent: float,
    down_pct: float = 0.20,
    interest_rate: float = 0.07,
    loan_years: int = 30,
    tax_monthly: float = 250,
    insurance_monthly: float = 120,
    vacancy_rate: float = 0.08,
    mgmt_rate: float = 0.08,
    maintenance_monthly: float = 150,
) -> dict:
    """Full buy-and-hold cash flow analysis."""
    down = purchase_price * down_pct
    loan = purchase_price - down
    monthly_rate = interest_rate / 12
    n = loan_years * 12
    # Mortgage payment (P&I)
    if monthly_rate > 0:
        pmt = loan * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
    else:
        pmt = loan / n

    gross_monthly = monthly_rent
    vacancy_loss = gross_monthly * vacancy_rate
    mgmt_fee = gross_monthly * mgmt_rate
    eff_income = gross_monthly - vacancy_loss

    total_expenses = pmt + tax_monthly + insurance_monthly + mgmt_fee + maintenance_monthly
    noi = eff_income - (tax_monthly + insurance_monthly + mgmt_fee + maintenance_monthly)
    cash_flow = eff_income - total_expenses
    cap_rate = (noi * 12 / purchase_price) * 100
    coc = (cash_flow * 12 / down) * 100 if down > 0 else 0

    return {
        "monthly_payment": round(pmt, 2),
        "gross_income": round(gross_monthly, 2),
        "effective_income": round(eff_income, 2),
        "total_expenses": round(total_expenses, 2),
        "monthly_cash_flow": round(cash_flow, 2),
        "annual_cash_flow": round(cash_flow * 12, 2),
        "noi": round(noi * 12, 2),
        "cap_rate": round(cap_rate, 2),
        "cash_on_cash": round(coc, 2),
        "down_payment": round(down, 2),
        "is_positive": cash_flow > 0,
    }
