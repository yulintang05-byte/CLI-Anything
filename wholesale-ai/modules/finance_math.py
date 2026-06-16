"""
Shared amortization math.

One place for the standard fixed-rate mortgage formulas so the same loan
payment isn't copy-pasted (and silently drifting) across every calculator.
"""


def monthly_payment(loan_amount: float, annual_rate: float, years: float) -> float:
    """
    Standard fully-amortizing monthly payment (principal + interest).

    annual_rate is a decimal (0.06 = 6%). Handles the 0% case (straight-line)
    and guards a 0-year term so callers never divide by zero.
    """
    n = max(int(round(years * 12)), 1)
    monthly_rate = annual_rate / 12
    if monthly_rate > 0:
        return loan_amount * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
    return loan_amount / n


def remaining_balance(
    loan_amount: float,
    annual_rate: float,
    years: float,
    years_elapsed: float,
) -> float:
    """
    Outstanding principal after `years_elapsed` of payments on a fully-
    amortizing loan — i.e. the balloon balance if the note is called early.

    Returns 0 at a 0% rate (straight-line payoff leaves nothing extra) and
    when the elapsed term meets or exceeds the full term.
    """
    n = max(int(round(years * 12)), 1)
    n_paid = max(int(round(years_elapsed * 12)), 0)
    if n_paid >= n:
        return 0.0
    monthly_rate = annual_rate / 12
    if monthly_rate <= 0:
        # Straight-line: balance is simply the unpaid fraction of principal.
        return loan_amount * (n - n_paid) / n
    return loan_amount * ((1 + monthly_rate) ** n - (1 + monthly_rate) ** n_paid) / \
        ((1 + monthly_rate) ** n - 1)
