"""
Tenant Pre-Screener — qualification questions, scoring, and screening resources.
Use before showing a property to filter serious applicants.
Section 8 / VASH tenants have their own qualification track.
"""

SCREENING_QUESTIONS = [
    # Income & Employment
    {"id": "income",       "q": "Monthly gross income?",                           "type": "number",  "weight": 25},
    {"id": "employed",     "q": "Employment status?",                              "type": "choice",  "weight": 15,
     "options": ["Full-time employed", "Part-time", "Self-employed", "Retired", "Benefits/SSI", "Voucher (Sec8/VASH)"]},
    {"id": "job_length",   "q": "How long at current job/income source?",          "type": "choice",  "weight": 5,
     "options": ["Less than 6 months", "6–12 months", "1–2 years", "2+ years"]},

    # Rental History
    {"id": "evictions",    "q": "Any evictions in the past 5 years?",              "type": "yesno",   "weight": 20},
    {"id": "prev_rent",    "q": "Current/previous monthly rent paid?",             "type": "number",  "weight": 5},
    {"id": "notice_given", "q": "Did you give proper notice to previous landlord?","type": "yesno",   "weight": 5},
    {"id": "move_reason",  "q": "Reason for moving?",                              "type": "text",    "weight": 0},

    # Household
    {"id": "occupants",    "q": "Total number of occupants?",                      "type": "number",  "weight": 5},
    {"id": "pets",         "q": "Do you have pets?",                               "type": "yesno",   "weight": 5},
    {"id": "smoke",        "q": "Does anyone in the household smoke?",             "type": "yesno",   "weight": 5},

    # Move-in
    {"id": "move_date",    "q": "Target move-in date?",                            "type": "text",    "weight": 0},
    {"id": "lease_term",   "q": "Preferred lease length?",                         "type": "choice",  "weight": 5,
     "options": ["Month-to-month", "6 months", "1 year", "2+ years"]},
    {"id": "credit_range", "q": "Approximate credit score range?",                 "type": "choice",  "weight": 10,
     "options": ["Below 550", "550–600", "600–650", "650–700", "700+"]},
]

CREDIT_SCORES = {
    "Below 550": 0, "550–600": 30, "600–650": 55,
    "650–700": 75, "700+": 100,
}

SCREENING_SERVICES = {
    "TransUnion SmartMove":  {"url": "https://www.mysmartmove.com/",      "cost": "$25–45/applicant", "checks": "Credit, criminal, eviction, income insights"},
    "RentSpree":             {"url": "https://www.rentspree.com/",        "cost": "$30–40/applicant", "checks": "Credit, background, eviction — tenant or landlord pays"},
    "Cozy / Apartments.com": {"url": "https://www.apartments.com/tools/","cost": "Free",              "checks": "Basic credit + background, tenant pays $29"},
    "Avail":                 {"url": "https://www.avail.co/",             "cost": "Free tier",        "checks": "Full screening, tenant pays $30, free for landlord"},
    "TurboTenant":           {"url": "https://www.turbotenant.com/",      "cost": "Free",             "checks": "Credit, criminal, eviction — tenant-paid screening"},
    "National Tenant Network":{"url": "https://www.ntnonline.com/",       "cost": "$15–35/applicant", "checks": "Nationwide eviction database — best eviction check"},
}

SECTION8_SCREENING = {
    "what_changes": [
        "Housing Authority verifies income (they do the work for you)",
        "HUD inspects the unit — they screen the tenant's rental history",
        "Tenant's voucher is conditional on good behavior — they won't risk losing it",
        "Government sends rent directly to you regardless of tenant situation",
    ],
    "what_you_still_check": [
        "Number of occupants vs unit size (HUD has max occupancy rules)",
        "Pets (your choice — not covered by voucher program)",
        "Lease term compatibility with HUD's HAP contract schedule",
        "Criminal history — you CAN screen for this even with vouchers",
    ],
    "process": [
        "1. List property on GoSection8.com and your local PHA wait list",
        "2. Tenant contacts you with their voucher number",
        "3. Verify voucher is current with HUD/PHA",
        "4. Run criminal background check only (rest done by HUD)",
        "5. HUD inspector visits — usually approves within 2 weeks",
        "6. Sign HAP contract — gov pays you directly every month",
    ],
    "gosection8": "https://www.gosection8.com/",
    "find_tenants": "https://www.affordablehousingonline.com/",
}

VASH_SCREENING = {
    "what_is_vash": (
        "VASH (Veterans Affairs Supportive Housing) is Section 8 exclusively for veterans. "
        "The VA case manager pre-screens the veteran's stability, mental health, and rental readiness. "
        "These are among the most vetted tenants in any program."
    ),
    "va_case_manager": "Every VASH tenant has a VA case manager who stays involved — built-in support system.",
    "find_vash_tenants": [
        "1. Contact your local VA Medical Center's HUD-VASH coordinator",
        "2. List on the VA housing portal: https://www.va.gov/find-locations/",
        "3. List on GoSection8 with VASH filter",
        "4. Contact local homeless veteran organizations",
    ],
    "va_contact": "https://www.va.gov/homeless/hchv.asp",
    "gosection8": "https://www.gosection8.com/",
}


def score_tenant(answers: dict, rent_amount: float) -> dict:
    """
    Score a tenant applicant on 0–100 scale.
    Returns score, recommendation, and red flags.
    """
    score = 0
    red_flags = []
    positives = []

    # Guard against a 0 rent (no default on the prompt) so the income-ratio
    # f-strings below never divide by zero.
    if rent_amount <= 0:
        rent_amount = 1

    # Income check: standard is 3x monthly rent
    income = answers.get("income", 0)
    if income >= rent_amount * 3:
        score += 25
        positives.append(f"Income {income/rent_amount:.1f}x rent (need 3x) ✓")
    elif income >= rent_amount * 2.5:
        score += 15
        positives.append(f"Income {income/rent_amount:.1f}x rent — slightly below 3x standard")
    elif income >= rent_amount * 2:
        score += 5
        red_flags.append(f"Income only {income/rent_amount:.1f}x rent — risk of non-payment")
    else:
        red_flags.append(f"Income {income/rent_amount:.1f}x rent — does NOT meet standard (need 3x)")

    # Employment
    emp = answers.get("employed", "")
    if emp in ("Full-time employed", "Retired", "Voucher (Sec8/VASH)"):
        score += 15
        positives.append(f"{emp} — stable income source ✓")
    elif emp == "Self-employed":
        score += 10
        positives.append("Self-employed — verify with bank statements")
    else:
        score += 5

    # Job length
    jl = answers.get("job_length", "")
    if jl == "2+ years":
        score += 5
        positives.append("2+ years at current job ✓")
    elif jl == "Less than 6 months":
        red_flags.append("Less than 6 months at job — stability concern")

    # Evictions — hardest red flag
    if answers.get("evictions") is True:
        red_flags.append("EVICTION HISTORY — high risk, verify details before proceeding")
    else:
        score += 20
        positives.append("No eviction history ✓")

    # Notice given
    if answers.get("notice_given") is True:
        score += 5
        positives.append("Gave proper notice to previous landlord ✓")
    elif answers.get("notice_given") is False:
        red_flags.append("Did NOT give proper notice — may indicate conflict with landlord")

    # Pets
    if answers.get("pets"):
        positives.append("Has pets — collect pet deposit, verify breed restrictions for insurance")

    # Smoking
    if answers.get("smoke"):
        red_flags.append("Smoker — specify no-smoking clause in lease, adds turnover cost")

    # Credit
    credit_map = {"Below 550": 0, "550–600": 3, "600–650": 7, "650–700": 9, "700+": 10}
    credit_range = answers.get("credit_range", "600–650")
    score += credit_map.get(credit_range, 7)
    if credit_range in ("700+", "650–700"):
        positives.append(f"Credit score {credit_range} ✓")
    elif credit_range == "Below 550":
        red_flags.append("Credit below 550 — require larger deposit or co-signer")

    # Lease term
    if answers.get("lease_term") == "1 year":
        score += 5
        positives.append("1-year lease term ✓")
    elif answers.get("lease_term") == "2+ years":
        score += 5
        positives.append("2+ year lease — excellent stability")

    # Recommendation
    if score >= 75 and not any("EVICTION" in f for f in red_flags):
        recommendation = "APPROVE — strong applicant"
        rec_color = "green"
    elif score >= 55 and not any("EVICTION" in f for f in red_flags):
        recommendation = "CONDITIONAL — run full screening, verify income"
        rec_color = "yellow"
    elif any("EVICTION" in f for f in red_flags):
        recommendation = "DECLINE — eviction history"
        rec_color = "red"
    else:
        recommendation = "DECLINE — does not meet standards"
        rec_color = "red"

    return {
        "score":          score,
        "max_score":      100,
        "recommendation": recommendation,
        "rec_color":      rec_color,
        "red_flags":      red_flags,
        "positives":      positives,
        "income_ratio":   round(income / rent_amount, 2) if rent_amount > 0 else 0,
    }
