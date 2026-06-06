"""
title_company.py — Title company directory and transaction cost calculator
for real estate wholesalers. No external dependencies.
"""

# ---------------------------------------------------------------------------
# Title company directory
# ---------------------------------------------------------------------------

TITLE_COMPANIES = {
    "old_republic": {
        "name": "Old Republic Title",
        "type": "national",
        "website": "oldrepublictitle.com",
        "notes": "Investor-friendly, bulk discounts available for high-volume wholesalers and flippers. Strong relationships with REI communities.",
        "states_strong": ["IL", "FL", "CA", "TX", "AZ", "OH", "MI", "GA", "CO", "WI"],
    },
    "first_american": {
        "name": "First American Title",
        "type": "national",
        "website": "firstam.com",
        "notes": "One of the largest title companies in the US. Investor accounts available with dedicated reps. Good for multi-state portfolios.",
        "states_strong": ["CA", "TX", "FL", "NY", "AZ", "NV", "WA", "OR", "CO", "IL"],
    },
    "fidelity_national": {
        "name": "Fidelity National Title",
        "type": "national",
        "website": "fnf.com",
        "notes": "Good for Detroit/Midwest markets. Strong track record clearing distressed titles and tax deeds. Part of FNF Group which also owns Chicago Title and Lawyers Title.",
        "states_strong": ["MI", "OH", "IN", "IL", "WI", "MN", "MO", "KY", "PA", "NY"],
    },
    "stewart_title": {
        "name": "Stewart Title",
        "type": "national",
        "website": "stewart.com",
        "notes": "Known for fast closings and investor pricing programs. Good tech infrastructure for remote/dry closings. Strong commercial and residential presence.",
        "states_strong": ["TX", "FL", "GA", "CO", "AZ", "CA", "OH", "TN", "AL", "SC"],
    },
    "attorneys_title": {
        "name": "Attorney's Title",
        "type": "regional",
        "website": "N/A — local offices",
        "notes": "Common in MI, OH, GA — often cheaper than national companies because the attorney handles both title and closing. Preferred by many investors in attorney-closing states.",
        "states_strong": ["MI", "OH", "GA", "IN", "KY", "TN"],
    },
    "independence_title": {
        "name": "Independence Title",
        "type": "regional",
        "website": "independencetitle.com",
        "notes": "Texas-based, known for fast closings in the DFW, Houston, San Antonio, and Austin markets. Investor-friendly staff familiar with assignments and double closes.",
        "states_strong": ["TX"],
    },
    "land_title_guarantee": {
        "name": "Land Title Guarantee Company",
        "type": "regional",
        "website": "ltgc.com",
        "notes": "Dominant in Colorado and active in Utah. Well-regarded by local investors and wholesalers in the Denver metro and mountain states.",
        "states_strong": ["CO", "UT"],
    },
    "chicago_title": {
        "name": "Chicago Title",
        "type": "national",
        "website": "ctt.com",
        "notes": "Chicago and Midwest focus but operates nationally. Part of FNF Group. Strong in Cook County and surrounding Illinois counties. Good for distressed and REO properties.",
        "states_strong": ["IL", "MI", "OH", "IN", "WI", "MO", "MN", "KY", "PA", "NJ"],
    },
}

# ---------------------------------------------------------------------------
# Closing costs by state
# ---------------------------------------------------------------------------

CLOSING_COSTS_BY_STATE = {
    "MI": {
        "state": "Michigan",
        "title_insurance_pct": 0.005,
        "transfer_tax_pct": 0.0075,
        "recording_fee": 100,
        "typical_total_pct": 0.02,
        "notes": "Michigan has both state and county transfer taxes. Title is typically seller-paid. Attorney closing optional but common in metro Detroit.",
        "attorney_required": False,
    },
    "AL": {
        "state": "Alabama",
        "title_insurance_pct": 0.003,
        "transfer_tax_pct": 0.001,
        "recording_fee": 50,
        "typical_total_pct": 0.015,
        "notes": "Alabama has one of the lowest transfer tax rates in the South. Closing attorneys common but not required. Good investor closing environment.",
        "attorney_required": False,
    },
    "TN": {
        "state": "Tennessee",
        "title_insurance_pct": 0.004,
        "transfer_tax_pct": 0.0037,
        "recording_fee": 60,
        "typical_total_pct": 0.018,
        "notes": "Tennessee transfer tax is called 'realty transfer tax'. No state income tax makes TN a popular investor market. Closing attorneys handle most transactions.",
        "attorney_required": False,
    },
    "TX": {
        "state": "Texas",
        "title_insurance_pct": 0.005,
        "transfer_tax_pct": 0.0,
        "recording_fee": 75,
        "typical_total_pct": 0.015,
        "notes": "Texas has NO real estate transfer tax — a major investor advantage. Title company handles closings (no attorney required). Promulgated title rates are state-regulated.",
        "attorney_required": False,
    },
    "FL": {
        "state": "Florida",
        "title_insurance_pct": 0.004,
        "transfer_tax_pct": 0.007,
        "recording_fee": 80,
        "typical_total_pct": 0.02,
        "notes": "Florida documentary stamp tax applies to both deeds (0.7%) and mortgages (0.35%). Seller typically pays title in most FL counties. Fast closing environment.",
        "attorney_required": False,
    },
    "GA": {
        "state": "Georgia",
        "title_insurance_pct": 0.003,
        "transfer_tax_pct": 0.001,
        "recording_fee": 60,
        "typical_total_pct": 0.015,
        "notes": "Georgia has a low transfer tax rate. Closing attorneys required by law for real estate transactions. Many investor-friendly attorneys in Atlanta metro.",
        "attorney_required": True,
    },
    "OH": {
        "state": "Ohio",
        "title_insurance_pct": 0.004,
        "transfer_tax_pct": 0.001,
        "recording_fee": 60,
        "typical_total_pct": 0.015,
        "notes": "Ohio conveyance fee is set per county and varies. Some counties charge more. Title companies handle most closings. Good inventory of distressed properties.",
        "attorney_required": False,
    },
    "IN": {
        "state": "Indiana",
        "title_insurance_pct": 0.003,
        "transfer_tax_pct": 0.002,
        "recording_fee": 55,
        "typical_total_pct": 0.015,
        "notes": "Indiana has low closing costs overall. No attorney required. Good wholesale market, especially Indianapolis and Fort Wayne. Title companies handle everything.",
        "attorney_required": False,
    },
}

# ---------------------------------------------------------------------------
# Educational content
# ---------------------------------------------------------------------------

WHAT_TITLE_DOES = [
    "Title insurance protects you (and your lender) if someone later claims ownership of the property you purchased.",
    "A title search reviews public records going back decades to find liens, judgments, unpaid taxes, easements, or competing ownership claims.",
    "Owner's title insurance is a one-time premium paid at closing — it protects you for as long as you or your heirs own the property.",
    "Lender's title insurance (required by most lenders) only protects the bank, not you — always buy owner's coverage too.",
    "Common title defects: mechanic's liens, IRS tax liens, HOA liens, child support liens, old mortgages not properly released, forged deeds, and probate issues.",
    "In wholesale deals with distressed sellers, title issues are extremely common — always order a title search before you assign or close.",
    "Title companies also handle the closing: they collect funds, pay off liens, record the new deed, and disburse proceeds.",
    "A 'clear title' means the title search found no unresolved defects. You want this confirmed before closing any deal.",
    "For double closes, title companies coordinate both the A-B and B-C closings — some require you to fund the A-B leg first.",
    "Title insurance does NOT cover issues you knew about before closing or physical defects in the property itself.",
]

INVESTOR_TITLE_TIPS = [
    "Order a title search (or preliminary title report) as early as possible — title issues can kill deals and take weeks to cure.",
    "Build a relationship with one investor-friendly title company or closing attorney who understands assignments and double closes.",
    "Ask the title company upfront: 'Do you work with wholesalers and assignment closings?' Not all will.",
    "A 'dry closing' means the documents are signed before funds arrive — useful when your end buyer's funds are wiring the same day.",
    "Assignment closing: the cheapest option. You assign your contract to the end buyer and collect your fee at closing. One set of closing costs.",
    "Double close (simultaneous close): you actually buy the property (A-B) and immediately resell it (B-C). Two sets of closing costs but hides your profit margin from both seller and buyer.",
    "For double closes, confirm the title company will use 'transactional funding' or your end buyer's funds to close the A-B leg — some title companies require you to have funds in advance.",
    "Always get a title commitment (the title company's promise to insure) before releasing your earnest money or assigning the contract.",
    "In attorney-closing states (GA, SC, MA, NY, CT, DE), find a real estate attorney who does investor deals — they'll be much more flexible than a standard residential attorney.",
    "Negotiate a discounted 'reissue rate' on title insurance if the property was last sold within 3-10 years — you may get 30-40% off.",
    "Keep a list of 2-3 investor-friendly title reps in each market you work. A good title rep can often flag problems before they become emergencies.",
    "If a property has a complex title issue (heirs, lost deed, tax sale), ask your title company if they can 'quiet title' — it costs money but may be worth it on the right deal.",
]

# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def calc_closing_costs(purchase_price, state, is_assignment=True, wholesale_fee=0):
    """
    Calculate estimated closing costs for a wholesale transaction.

    Parameters
    ----------
    purchase_price : float — the purchase price of the property
    state          : str   — two-letter state code (MI, TX, FL, etc.)
    is_assignment  : bool  — True for assignment close, False for double close
    wholesale_fee  : float — wholesale/assignment fee (used only for double close B-C pricing)

    Returns
    -------
    dict with all line items and total closing costs
    """
    state = state.upper().strip()

    if state not in CLOSING_COSTS_BY_STATE:
        return {
            "error": f"State '{state}' not in database. Supported states: {list(CLOSING_COSTS_BY_STATE.keys())}",
            "supported_states": list(CLOSING_COSTS_BY_STATE.keys()),
        }

    costs = CLOSING_COSTS_BY_STATE[state]

    title_insurance = round(purchase_price * costs["title_insurance_pct"], 2)
    transfer_tax    = round(purchase_price * costs["transfer_tax_pct"], 2)
    recording_fee   = costs["recording_fee"]
    escrow_fee      = round(purchase_price * 0.003, 2)
    title_search    = 250.0
    attorney_fee    = 750.0 if costs["attorney_required"] else 0.0

    subtotal_hard_costs = round(
        title_insurance + transfer_tax + recording_fee + escrow_fee + title_search + attorney_fee, 2
    )

    double_close_extra = 0.0

    if is_assignment:
        close_type_label = "Assignment Closing"
        close_type_note  = (
            "Assignment closing: you assign your equitable interest to the end buyer. "
            "You do NOT take title. One set of closing costs. Cheapest option."
        )
    else:
        close_type_label = "Double Close (Simultaneous)"
        bc_price = purchase_price + wholesale_fee
        double_close_extra = round(
            bc_price * costs["title_insurance_pct"]
            + bc_price * costs["transfer_tax_pct"]
            + recording_fee
            + round(bc_price * 0.003, 2)
            + title_search
            + attorney_fee,
            2,
        )
        close_type_note = (
            "Double close: you purchase (A-B) and immediately resell (B-C). "
            "Two sets of title and transfer costs but your fee is not visible to either party."
        )

    total = round(subtotal_hard_costs + double_close_extra, 2)

    return {
        "state":               state,
        "state_name":          costs["state"],
        "purchase_price":      purchase_price,
        "close_type":          close_type_label,
        "close_type_note":     close_type_note,
        "wholesale_fee":       wholesale_fee,
        "line_items": {
            "title_insurance":       title_insurance,
            "transfer_tax":          transfer_tax,
            "recording_fee":         recording_fee,
            "escrow_settlement_fee": escrow_fee,
            "title_search_exam":     title_search,
            "attorney_fee":          attorney_fee,
            "double_close_bc_leg":   double_close_extra,
        },
        "subtotal_ab_closing": subtotal_hard_costs,
        "total_closing_costs": total,
        "typical_pct_of_purchase": costs["typical_total_pct"],
        "state_notes":         costs["notes"],
        "attorney_required":   costs["attorney_required"],
    }


def get_title_companies_for_state(state):
    """
    Return a list of title companies well-suited for a given state.

    Parameters
    ----------
    state : str — two-letter state code

    Returns
    -------
    dict with 'state', 'companies' list, and optional 'note'
    """
    state = state.upper().strip()
    matches = []

    for key, company in TITLE_COMPANIES.items():
        if state in company.get("states_strong", []):
            entry = dict(company)
            entry["key"] = key
            matches.append(entry)

    # Regional companies first — tend to be more locally investor-friendly
    matches.sort(key=lambda c: (0 if c["type"] == "regional" else 1, c["name"]))

    if not matches:
        nationals = [
            dict(c, key=k)
            for k, c in TITLE_COMPANIES.items()
            if c["type"] == "national"
        ]
        nationals.sort(key=lambda c: c["name"])
        return {
            "state": state,
            "note": (
                f"No state-specific matches found for '{state}'. "
                "Returning all national companies — they operate in every state."
            ),
            "companies": nationals,
            "count": len(nationals),
        }

    return {
        "state": state,
        "companies": matches,
        "count": len(matches),
    }


def get_hud1_settlement_guide():
    """
    Return a plain-English explanation of key HUD-1 settlement statement line items.

    Returns
    -------
    dict with 'overview' and 'line_items' keys
    """
    return {
        "overview": (
            "The HUD-1 Settlement Statement (now largely replaced by the Closing Disclosure for consumer loans, "
            "but still used in cash and commercial deals) lists every dollar that changes hands at closing. "
            "It has two columns: buyer (borrower) and seller."
        ),
        "line_items": {
            "100 — Gross Amount Due From Borrower": (
                "The total the buyer owes at closing before their credits. Includes purchase price, "
                "prepaid items (insurance, taxes), and settlement charges."
            ),
            "200 — Amounts Paid By or On Behalf of Borrower": (
                "Credits to the buyer: earnest money deposit, loan amount, seller concessions, "
                "and any other credits. Reduces what the buyer must bring to the table."
            ),
            "300 — Cash at Settlement From/To Borrower": (
                "Line 103 minus Line 303: the net cash the buyer must wire or bring to closing (or receive back)."
            ),
            "400 — Gross Amount Due To Seller": (
                "Total the seller is owed: purchase price plus any credits running in their favor."
            ),
            "500 — Reductions in Amount Due To Seller": (
                "Seller's debits: existing mortgage payoffs, seller-paid closing costs, unpaid taxes, "
                "HOA dues, commissions, and other liens being paid at closing."
            ),
            "600 — Cash at Settlement To/From Seller": (
                "The seller's net proceeds: Line 420 minus Line 520. This is what the seller walks away with."
            ),
            "700 — Real Estate Broker Commissions": (
                "Total agent commissions paid out of the seller's proceeds. Usually 5-6% of sales price, "
                "split between listing and buyer's agent."
            ),
            "800 — Items Payable in Connection With Loan": (
                "Loan origination fees, discount points, appraisal fee, credit report fee, and lender charges. "
                "Cash deals have minimal entries here."
            ),
            "900 — Items Required By Lender to Be Paid in Advance": (
                "Prepaid interest (from closing date to end of month), homeowner's insurance premium, "
                "and mortgage insurance premium if applicable."
            ),
            "1000 — Reserves Deposited With Lender (Escrow)": (
                "Escrow impounds: months of insurance and property taxes the lender requires upfront "
                "to fund your escrow account. Cash deals have no entry here."
            ),
            "1100 — Title Charges": (
                "Title search fee, title examination, title insurance binder, attorney fee (if applicable), "
                "and owner's and lender's title insurance premiums."
            ),
            "1200 — Government Recording and Transfer Charges": (
                "Deed recording fees, mortgage recording fees, city/county/state transfer taxes and stamps."
            ),
            "1300 — Additional Settlement Charges": (
                "Survey, pest inspection, home warranty, and any other charges not covered above."
            ),
            "wholesale_specific": (
                "On assignment closings, the wholesaler's fee often appears as a line item in the 1300s "
                "or as an addendum. On double closes, it shows up as the difference between the A-B and B-C "
                "purchase prices and appears on two separate HUD-1s."
            ),
        },
    }


def find_title_company_tips():
    """
    Return a list of tips for finding investor-friendly title companies locally.

    Returns
    -------
    list of str
    """
    return [
        "Ask your local REIA (Real Estate Investor Association) for referrals — members share who actually works with investors.",
        "Call title companies and directly ask: 'Do you handle assignment closings and double closes?' If they hesitate or say no, move on.",
        "Ask local wholesalers and flippers who they use — word of mouth is the fastest way to find investor-friendly closers.",
        "Search Facebook groups for your target market and search 'title company' or 'who does your closings' — investors share this freely.",
        "BiggerPockets forums have threads for almost every major metro with title company recommendations from active investors.",
        "In attorney-closing states (GA, SC, MA, NY, CT, DE), look for real estate attorneys who specialize in investor transactions, not just retail buyers.",
        "Once you find a good title rep, protect that relationship — refer other investors to them and they'll prioritize your deals.",
        "Test a new title company with a simple deal before sending them a complex double close — you want to know their competence before it matters.",
        "National companies (First American, Fidelity, Old Republic) often have local branches with investor specialists — call the branch, not the national 800 number.",
        "Ask if the title company has experience with tax deed and probate properties — these require extra expertise to clear title.",
        "Confirm the title company will close on your timeline — some are slow and that kills your holding costs on flips.",
        "Get a fee sheet in advance. Investor-friendly title companies are transparent about fees and don't add junk charges at the last minute.",
        "If you're doing deals in multiple states, consider using a national company that can assign you a dedicated rep across markets.",
        "Some title companies offer 'bulk pricing' if you commit to a minimum number of closings per month — worth asking if you're doing volume.",
    ]
