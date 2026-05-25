"""
Creative Financing Calculator — subject-to, seller financing, seller credits,
DSCR loans, wrap mortgages, and lease options.
"""
from dataclasses import dataclass
from typing import Optional


# ── DSCR (Debt-Service Coverage Ratio) ───────────────────────────────────────

def calc_dscr(
    monthly_rent: float,
    monthly_mortgage: float,
    monthly_tax: float,
    monthly_insurance: float,
    monthly_hoa: float = 0,
    vacancy_rate: float = 0.08,
    mgmt_rate: float = 0.10,
) -> dict:
    """
    DSCR = Net Operating Income / Annual Debt Service
    Lenders typically require DSCR >= 1.25 for investment loans.
    DSCR loans don't use your personal income — only the property's cash flow.
    """
    effective_rent = monthly_rent * (1 - vacancy_rate)
    mgmt_fee = effective_rent * mgmt_rate
    operating_expenses = monthly_tax + monthly_insurance + monthly_hoa + mgmt_fee
    noi_monthly = effective_rent - operating_expenses
    noi_annual = noi_monthly * 12
    annual_debt = monthly_mortgage * 12

    dscr = noi_annual / annual_debt if annual_debt > 0 else 0

    # Lender requirements
    if dscr >= 1.35:
        loan_eligible = True
        lender_view = "Strong — most DSCR lenders approve"
        dscr_color = "green"
    elif dscr >= 1.25:
        loan_eligible = True
        lender_view = "Eligible — meets minimum for most DSCR lenders"
        dscr_color = "cyan"
    elif dscr >= 1.10:
        loan_eligible = False
        lender_view = "Borderline — some lenders may approve with higher down payment"
        dscr_color = "yellow"
    else:
        loan_eligible = False
        lender_view = "Below threshold — DSCR lenders will decline"
        dscr_color = "red"

    # What rent would be needed to hit 1.25 DSCR
    target_noi_annual = annual_debt * 1.25
    target_noi_monthly = target_noi_annual / 12
    target_eff_rent = (target_noi_monthly + operating_expenses) / (1 - vacancy_rate) if (1 - vacancy_rate) > 0 else 0
    rent_gap = max(0, target_eff_rent - monthly_rent)

    return {
        "dscr": round(dscr, 3),
        "noi_monthly": round(noi_monthly, 2),
        "noi_annual": round(noi_annual, 2),
        "annual_debt_service": round(annual_debt, 2),
        "effective_rent": round(effective_rent, 2),
        "loan_eligible": loan_eligible,
        "lender_view": lender_view,
        "dscr_color": dscr_color,
        "rent_needed_for_125": round(target_eff_rent, 2),
        "rent_gap_to_qualify": round(rent_gap, 2),
        "vacancy_loss": round(monthly_rent * vacancy_rate, 2),
        "mgmt_fee": round(mgmt_fee, 2),
    }


# ── Subject-To ────────────────────────────────────────────────────────────────

def calc_subject_to(
    existing_loan_balance: float,
    existing_monthly_payment: float,
    existing_rate: float,
    arv: float,
    your_purchase_price: float,
    wholesale_fee: float = 0,
    monthly_rent: float = 0,
) -> dict:
    """
    Subject-To: You take title to the property and the seller's existing
    mortgage stays in place. You make the seller's payments.
    Great when seller has low-rate mortgage you'd never qualify for today.
    """
    equity_at_purchase = arv - existing_loan_balance
    cash_to_seller = your_purchase_price - existing_loan_balance  # What you pay seller above loan
    cash_to_seller = max(0, cash_to_seller)

    monthly_cash_flow = monthly_rent - existing_monthly_payment if monthly_rent else 0
    annual_cash_flow = monthly_cash_flow * 12

    rate_savings = 0
    if existing_rate < 0.065:  # Below current market (~7%)
        market_payment = existing_loan_balance * (0.07 / 12) * (1.07 / 12) ** 360 / ((1.07 / 12) ** 360 - 1)
        rate_savings = (market_payment - existing_monthly_payment) * 12

    return {
        "strategy": "Subject-To",
        "existing_loan_balance": existing_loan_balance,
        "existing_monthly_payment": existing_monthly_payment,
        "existing_rate_pct": f"{existing_rate * 100:.2f}%",
        "cash_to_seller": cash_to_seller,
        "total_cash_needed": cash_to_seller + 3000,  # +closing costs
        "equity_at_purchase": equity_at_purchase,
        "arv": arv,
        "monthly_cash_flow": round(monthly_cash_flow, 2) if monthly_rent else "N/A",
        "annual_cash_flow": round(annual_cash_flow, 2) if monthly_rent else "N/A",
        "annual_rate_savings_vs_market": round(rate_savings, 0),
        "pros": [
            "Keep seller's below-market interest rate",
            "Little to no cash needed (just pay arrears + closing)",
            "No new loan qualification needed",
            "Fast close (7-14 days typical)",
        ],
        "risks": [
            "Due-on-sale clause — lender can call loan due (rarely enforced)",
            "Seller's credit still tied to property until you pay off or refinance",
            "Must maintain seller's payments perfectly",
        ],
        "best_for": "Sellers in pre-foreclosure with below-market rate (3-5%) who have little equity",
    }


# ── Seller Financing ─────────────────────────────────────────────────────────

def calc_seller_finance(
    purchase_price: float,
    down_payment: float,
    interest_rate: float,
    loan_years: int,
    balloon_years: Optional[int] = None,
    monthly_rent: float = 0,
) -> dict:
    """
    Seller acts as the bank. They carry the note.
    Buyer makes monthly payments directly to seller.
    """
    loan_amount = purchase_price - down_payment
    monthly_rate = interest_rate / 12
    n = loan_years * 12

    if monthly_rate > 0:
        payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
    else:
        payment = loan_amount / n

    balloon_balance = 0
    if balloon_years and balloon_years < loan_years:
        # Remaining balance after balloon_years
        n_paid = balloon_years * 12
        balloon_balance = loan_amount * ((1 + monthly_rate) ** n - (1 + monthly_rate) ** n_paid) / ((1 + monthly_rate) ** n - 1)

    monthly_cf = monthly_rent - payment if monthly_rent else 0
    total_interest = (payment * n) - loan_amount

    return {
        "strategy": "Seller Financing",
        "purchase_price": purchase_price,
        "down_payment": down_payment,
        "loan_amount": loan_amount,
        "interest_rate_pct": f"{interest_rate * 100:.2f}%",
        "loan_term_years": loan_years,
        "monthly_payment": round(payment, 2),
        "balloon_years": balloon_years,
        "balloon_balance": round(balloon_balance, 0) if balloon_balance else "None",
        "total_interest_paid": round(total_interest, 0),
        "monthly_cash_flow": round(monthly_cf, 2) if monthly_rent else "N/A",
        "pros": [
            "No bank qualification needed",
            "Flexible terms negotiated directly with seller",
            "Fast close, lower closing costs",
            "Creative structuring (interest-only, balloon, etc.)",
        ],
        "risks": [
            "Seller must agree to carry the note",
            "Works best when seller owns property free & clear",
            "Need balloon refinance plan if balloon term",
        ],
        "best_for": "Free & clear properties — seller needs income stream, not lump sum",
    }


# ── Seller Credits ────────────────────────────────────────────────────────────

def calc_seller_credits(
    purchase_price: float,
    repair_cost: float,
    credit_percent: float = 0.03,
    loan_type: str = "conventional",
) -> dict:
    """
    Seller credits: Seller pays closing costs or repairs at closing.
    Reduces cash buyer needs to bring, making your wholesale deal more attractive.
    Max credit limits vary by loan type.
    """
    max_credit_pct = {
        "conventional": 0.09,   # 3-9% depending on LTV
        "fha": 0.06,
        "va": 0.04,
        "usda": 0.06,
        "cash": 1.0,             # No limit for cash buyers
    }

    credit_amount = purchase_price * credit_percent
    max_allowed = purchase_price * max_credit_pct.get(loan_type.lower(), 0.03)
    credit_amount = min(credit_amount, max_allowed)

    # Effective purchase price after credit
    effective_price = purchase_price - credit_amount

    return {
        "purchase_price": purchase_price,
        "seller_credit_pct": f"{credit_percent * 100:.1f}%",
        "seller_credit_amount": round(credit_amount, 0),
        "max_allowed_pct": f"{max_credit_pct.get(loan_type.lower(), 0.03) * 100:.0f}%",
        "max_allowed_amount": round(max_allowed, 0),
        "effective_price_to_buyer": round(effective_price, 0),
        "loan_type": loan_type.upper(),
        "repair_cost": repair_cost,
        "covers_repairs_pct": f"{(credit_amount / repair_cost * 100):.0f}%" if repair_cost > 0 else "N/A",
        "benefit": f"Buyer brings {credit_amount:,.0f} less to closing — makes deal easier to sell to end buyer",
    }


# ── Lease Option ─────────────────────────────────────────────────────────────

def calc_lease_option(
    purchase_price: float,
    monthly_rent: float,
    option_term_years: int = 2,
    option_credit_pct: float = 0.15,
    option_fee: float = 5000,
) -> dict:
    """
    Lease-Option (Rent-to-Own): Control property with option to buy.
    Great when seller won't accept low cash offer but needs monthly income.
    """
    monthly_credit = monthly_rent * option_credit_pct
    total_rent_credit = monthly_credit * (option_term_years * 12)
    effective_purchase_price = purchase_price - total_rent_credit - option_fee

    return {
        "strategy": "Lease-Option",
        "option_price": purchase_price,
        "monthly_rent": monthly_rent,
        "option_fee": option_fee,
        "option_term_years": option_term_years,
        "monthly_rent_credit": round(monthly_credit, 2),
        "total_rent_credits": round(total_rent_credit, 0),
        "effective_purchase_price": round(effective_purchase_price, 0),
        "total_cash_in": round(option_fee + (monthly_rent * option_term_years * 12), 0),
        "pros": [
            "Control property with small option fee",
            "Lock in today's price in rising market",
            "Time to fix credit / secure financing",
            "Rent credits reduce purchase price",
        ],
        "risks": [
            "Lose option fee if you don't buy",
            "Seller can't sell to anyone else during term",
            "Need financing plan for when option expires",
        ],
        "best_for": "Properties that need time — seller wants income, investor needs time to fix credit",
    }


# ── Quick Strategy Picker ─────────────────────────────────────────────────────

def recommend_strategy(
    seller_equity_pct: float,
    seller_motivation: str,
    existing_rate: float = 0.07,
    is_distressed: bool = True,
    needs_cash_now: bool = False,
    is_behind_on_payments: bool = False,
) -> list:
    """
    Recommend the best deal structure based on seller's situation.
    Returns list of strategies in order of best fit.
    """
    recommendations = []

    motivation = seller_motivation.lower()

    # Pre-foreclosure / behind on payments
    if is_behind_on_payments or "foreclosure" in motivation or "behind" in motivation:
        if existing_rate < 0.055:
            recommendations.append({
                "strategy": "Subject-To",
                "reason": "Keep their below-market rate, cure arrears, fast close to stop foreclosure",
                "priority": 1,
            })
        recommendations.append({
            "strategy": "Cash Offer (Wholesale)",
            "reason": "Speed is everything in pre-foreclosure — cash closes in days",
            "priority": 2,
        })

    # High equity, motivated
    if seller_equity_pct >= 0.50 and not needs_cash_now:
        recommendations.append({
            "strategy": "Seller Financing",
            "reason": "High equity owner gets better monthly income than lump sum, you skip the bank",
            "priority": 1 if not is_behind_on_payments else 3,
        })

    # Low equity / distressed
    if seller_equity_pct < 0.20:
        recommendations.append({
            "strategy": "Short Sale",
            "reason": "Low equity — negotiate with lender to accept less than owed",
            "priority": 2,
        })

    # Standard wholesale
    recommendations.append({
        "strategy": "Assignment of Contract (Wholesale)",
        "reason": "Universal strategy — works on any motivated seller deal",
        "priority": 5,
    })

    # Lease option if seller needs income
    if "income" in motivation or "retire" in motivation or "cash flow" in motivation:
        recommendations.append({
            "strategy": "Lease-Option",
            "reason": "Seller gets monthly income + locked-in sale price",
            "priority": 3,
        })

    # Sort by priority
    recommendations.sort(key=lambda x: x["priority"])
    return recommendations
