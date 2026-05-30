"""
Closing Agent — "The Deal Maker"
Pre-fills contracts, generates offer packets, tracks deals to close.
Knows every contract type and automatically selects the right one.
You only have to sign.
"""
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import anthropic

from agents.memory import load_patterns, save_patterns, log_activity, record_deal_outcome

MODEL      = "claude-opus-4-8"
OUTPUT_DIR = Path.home() / ".wholesale-ai" / "contracts"

SYSTEM_PROMPT = """You are a real estate closing specialist. You prepare contracts,
offer packages, and closing documents for wholesale real estate deals.

You know every deal structure:
- Assignment of Contract (most common — no money needed)
- Double Close (simultaneous A→B + B→C closing)
- Subject-To (take over existing mortgage)
- Seller Financing (seller acts as bank)
- DSCR Loan Close (conventional investment loan)
- Lease Option (option to buy)

You think about what could kill the deal at closing:
- Title issues (liens, judgments, cloudy title)
- Inspection surprises after contract
- Buyer financing falling through
- Seller getting cold feet
- Assignment fee disputes

Your documents are complete, professional, and protect the investor.
Always include: assignment clause, inspection period, earnest money terms,
as-is clause, and contingency language.
"""


class ClosingAgent:
    def __init__(self, profile: Optional[dict] = None):
        self.name     = "ClosingAgent"
        self.profile  = profile or {}
        self.patterns = load_patterns(self.name)
        self.client   = None
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self._init_client()

    def _init_client(self):
        key = os.getenv("ANTHROPIC_API_KEY")
        if key:
            self.client = anthropic.Anthropic(api_key=key)

    def _require_client(self):
        if not self.client:
            raise RuntimeError("ANTHROPIC_API_KEY not set")

    # ── Contract selection ────────────────────────────────────────────────

    def select_contract_type(self, deal: dict) -> str:
        """Automatically select the best contract type for a deal."""
        strategy   = deal.get("strategy", "Wholesale")
        seller_eq  = deal.get("seller_equity_pct", 100)
        price      = deal.get("price", 0)

        if strategy in ("Wholesale", "Flip"):
            return "assignment"
        elif strategy == "BRRRR" and price < 50000:
            return "assignment"   # wholesale to yourself or cash buy
        elif "Subject-To" in strategy:
            return "subject_to"
        elif "Seller Finance" in strategy:
            return "seller_finance"
        elif "Lease Option" in strategy:
            return "lease_option"
        elif strategy in ("DSCR Rental", "Buy & Hold"):
            return "purchase_sale"
        else:
            return "assignment"

    # ── Contract generation ───────────────────────────────────────────────

    def generate_contract(
        self,
        contract_type: str,
        buyer_name: str,
        seller_name: str,
        address: str,
        purchase_price: float,
        emd: float = 1000,
        closing_days: int = 21,
        assignment_fee: float = 10000,
        inspection_days: int = 14,
        extra_terms: str = "",
        end_buyer_name: str = "",
    ) -> dict:
        """
        Generate a complete, fill-in-ready contract.
        Returns dict with: content (full text), filename, type, warnings.
        """
        self._require_client()

        generators = {
            "assignment":     self._gen_assignment,
            "purchase_sale":  self._gen_purchase_sale,
            "subject_to":     self._gen_subject_to,
            "seller_finance": self._gen_seller_finance,
            "lease_option":   self._gen_lease_option,
            "double_close":   self._gen_double_close,
        }

        gen_fn = generators.get(contract_type, self._gen_assignment)
        content = gen_fn(
            buyer_name=buyer_name, seller_name=seller_name,
            address=address, purchase_price=purchase_price,
            emd=emd, closing_days=closing_days,
            assignment_fee=assignment_fee,
            inspection_days=inspection_days,
            extra_terms=extra_terms,
            end_buyer_name=end_buyer_name,
        )

        safe_addr = re.sub(r'[^\w\s-]', '', address)[:40].replace(" ", "_")
        filename  = f"{contract_type}_{safe_addr}_{datetime.now().strftime('%Y%m%d')}.txt"
        filepath  = OUTPUT_DIR / filename
        filepath.write_text(content)

        log_activity(self.name, "contract_generated", f"{contract_type} — {address}")

        return {
            "content":       content,
            "filename":      str(filepath),
            "type":          contract_type,
            "generated_at":  datetime.now().isoformat(),
            "warnings":      self._get_warnings(contract_type),
        }

    def _gen_assignment(self, buyer_name, seller_name, address, purchase_price,
                         emd, closing_days, assignment_fee, inspection_days,
                         extra_terms="", **kwargs) -> str:
        close_date = (datetime.now() + timedelta(days=closing_days)).strftime("%B %d, %Y")
        return f"""
ASSIGNMENT OF REAL ESTATE PURCHASE CONTRACT

⚠  LEGAL DISCLAIMER: This is a template only. Have a real estate attorney
    review before signing. Requirements vary by state.

Date: {datetime.now().strftime("%B %d, %Y")}

PARTIES:
Assignor (Buyer/Wholesaler): {buyer_name}
Seller: {seller_name}
Property Address: {address}

PURCHASE PRICE: ${purchase_price:,.0f}
EARNEST MONEY DEPOSIT (EMD): ${emd:,.0f}
INSPECTION PERIOD: {inspection_days} days from acceptance

CLOSING DATE: On or before {close_date}

TERMS AND CONDITIONS:

1. PURCHASE AND SALE
   Seller agrees to sell and Assignor agrees to purchase the Property
   in "AS-IS" condition for ${purchase_price:,.0f}.

2. EARNEST MONEY
   Buyer shall deposit ${emd:,.0f} EMD within 3 business days of acceptance.
   EMD is fully refundable during inspection period.

3. INSPECTION PERIOD
   Buyer has {inspection_days} days to inspect. Buyer may cancel for any reason
   during this period and receive full EMD refund.

4. ASSIGNMENT CLAUSE (CRITICAL FOR WHOLESALE)
   Buyer reserves the right to assign this contract to any third party
   without Seller's consent. Seller agrees to close with Buyer's assignee.
   Assignment fee does NOT come from Seller.

5. AS-IS SALE
   Property sold in current condition. Seller makes no representations
   about condition. Buyer accepts full responsibility after inspection.

6. TITLE
   Seller warrants clear, marketable title free of undisclosed liens.
   Seller to provide title insurance at closing.

7. CLOSING COSTS
   Each party pays their own closing costs unless otherwise agreed.

8. DEFAULT
   If Seller defaults, Buyer entitled to specific performance or return of EMD.
   If Buyer defaults after inspection period, EMD is forfeited.

9. ENTIRE AGREEMENT
   This contract is the entire agreement. Modifications must be in writing.

{f"ADDITIONAL TERMS: {extra_terms}" if extra_terms else ""}

SIGNATURES:
Seller: _________________________ Date: __________
Print: {seller_name}

Buyer/Assignor: _________________________ Date: __________
Print: {buyer_name}

ASSIGNMENT ADDENDUM
(Complete when assigning to end buyer)

Assignor assigns all rights to: {kwargs.get('end_buyer_name', '[END BUYER NAME]')}
Assignment Fee: ${assignment_fee:,.0f} (paid at closing by end buyer)
Assignment Date: {datetime.now().strftime("%B %d, %Y")}

Assignee: _________________________ Date: __________
Assignor: _________________________ Date: __________
""".strip()

    def _gen_purchase_sale(self, buyer_name, seller_name, address, purchase_price,
                            emd, closing_days, inspection_days, extra_terms="", **kwargs) -> str:
        close_date = (datetime.now() + timedelta(days=closing_days)).strftime("%B %d, %Y")
        return f"""
RESIDENTIAL PURCHASE AND SALE AGREEMENT

⚠  LEGAL DISCLAIMER: Template only. Have an attorney review before use.

Date: {datetime.now().strftime("%B %d, %Y")}
Buyer: {buyer_name}
Seller: {seller_name}
Property: {address}
Purchase Price: ${purchase_price:,.0f}
EMD: ${emd:,.0f} (due within 3 days of acceptance)
Closing Date: On or before {close_date}
Inspection Period: {inspection_days} days

FINANCING: CASH (no financing contingency)
Property sold AS-IS. Buyer accepts property in current condition
after inspection period expires.

Seller warrants: Clear title, no undisclosed defects, possession at closing.

{f"ADDITIONAL TERMS: {extra_terms}" if extra_terms else ""}

Seller: _________________________ Date: __________
Buyer: _________________________ Date: __________
""".strip()

    def _gen_subject_to(self, buyer_name, seller_name, address, purchase_price,
                         emd, closing_days, extra_terms="", **kwargs) -> str:
        return f"""
SUBJECT-TO PURCHASE AGREEMENT

⚠  LEGAL DISCLAIMER: Subject-to deals are complex. MUST have attorney review.
    Due-on-sale clause risk. Consult a real estate attorney first.

Date: {datetime.now().strftime("%B %d, %Y")}
Buyer: {buyer_name}
Seller: {seller_name}
Property: {address}
Purchase Price (equity): ${purchase_price:,.0f}

SUBJECT-TO TERMS:
Buyer takes title SUBJECT TO existing mortgage(s) remaining in Seller's name.
Buyer agrees to make all mortgage payments on time.
Seller's credit at risk if Buyer defaults — Seller acknowledges this risk.

Existing Loan Balance: $[LOAN BALANCE]
Existing Monthly Payment: $[PAYMENT]
Lender: [LENDER NAME]
Loan Number: [LOAN NUMBER]

Buyer accepts full responsibility for property and loan payments.
Seller agrees to deed property to Buyer in exchange for: ${purchase_price:,.0f} equity.
{f"ADDITIONAL TERMS: {extra_terms}" if extra_terms else ""}

Seller: _________________________ Date: __________
Buyer: _________________________ Date: __________
""".strip()

    def _gen_seller_finance(self, buyer_name, seller_name, address, purchase_price,
                             emd, closing_days, extra_terms="", **kwargs) -> str:
        return f"""
SELLER FINANCING AGREEMENT / PROMISSORY NOTE

⚠  LEGAL DISCLAIMER: Template only. Attorney review required.

Date: {datetime.now().strftime("%B %d, %Y")}
Borrower (Buyer): {buyer_name}
Lender (Seller): {seller_name}
Property: {address}
Purchase Price: ${purchase_price:,.0f}
Down Payment: $[DOWN PAYMENT]
Financed Amount: $[LOAN AMOUNT]

LOAN TERMS:
Interest Rate: [RATE]%
Term: [YEARS] years
Monthly Payment: $[PAYMENT] (P&I)
Balloon Payment (if any): $[BALLOON] due [DATE]
First Payment Due: [DATE]

SECURITY: Seller holds first mortgage/deed of trust on property.
DEFAULT: Buyer has 30-day cure period before foreclosure proceedings.
PREPAYMENT: Allowed without penalty.

{f"ADDITIONAL TERMS: {extra_terms}" if extra_terms else ""}

Seller: _________________________ Date: __________
Buyer: _________________________ Date: __________
""".strip()

    def _gen_lease_option(self, buyer_name, seller_name, address, purchase_price,
                           emd, closing_days, extra_terms="", **kwargs) -> str:
        option_exp = (datetime.now() + timedelta(days=365)).strftime("%B %d, %Y")
        return f"""
LEASE OPTION AGREEMENT

⚠  LEGAL DISCLAIMER: Template only. Attorney review required.

Date: {datetime.now().strftime("%B %d, %Y")}
Optionee (Buyer): {buyer_name}
Optionor (Seller): {seller_name}
Property: {address}
Option Purchase Price: ${purchase_price:,.0f}
Option Fee: ${emd:,.0f} (non-refundable, applies to purchase price)
Option Period: {datetime.now().strftime("%B %d, %Y")} to {option_exp}
Monthly Rent: $[RENT] (portion credited to purchase: $[CREDIT]/mo)

TERMS:
Optionee has exclusive right to purchase at ${purchase_price:,.0f} during option period.
Option fee and rent credits applied to purchase price at closing.
Optionee responsible for maintenance during lease period.
Optionee may assign this option to any third party.

{f"ADDITIONAL TERMS: {extra_terms}" if extra_terms else ""}

Seller: _________________________ Date: __________
Buyer: _________________________ Date: __________
""".strip()

    def _gen_double_close(self, buyer_name, seller_name, address, purchase_price,
                           emd, closing_days, assignment_fee, end_buyer_name="", **kwargs) -> str:
        a_price = purchase_price
        b_price = purchase_price + assignment_fee
        close_date = (datetime.now() + timedelta(days=closing_days)).strftime("%B %d, %Y")
        return f"""
DOUBLE CLOSE — TWO-CONTRACT STRUCTURE

⚠  LEGAL DISCLAIMER: Double closes require a title company familiar with
    simultaneous closings. Attorney review essential.

=== CONTRACT A: SELLER → WHOLESALER ===
Seller: {seller_name}
Buyer (Wholesaler): {buyer_name}
Property: {address}
Price: ${a_price:,.0f}
Close Date: {close_date}
[Standard purchase agreement terms apply]

=== CONTRACT B: WHOLESALER → END BUYER ===
Seller (Wholesaler): {buyer_name}
Buyer: {end_buyer_name or '[END BUYER NAME]'}
Property: {address}
Price: ${b_price:,.0f}
Close Date: {close_date} (same day as Contract A)

Wholesaler Profit: ${assignment_fee:,.0f}

NOTE: Title company must close both simultaneously.
Wholesaler's A-close funds typically transacted using B-close proceeds.
Confirm title company accepts simultaneous close structure.

Seller (Contract A): _________________________ Date: __________
Wholesaler:          _________________________ Date: __________
End Buyer:           _________________________ Date: __________
""".strip()

    def _get_warnings(self, contract_type: str) -> list:
        base = [
            "This is a template — have a licensed real estate attorney review before signing",
            "Requirements vary significantly by state",
            "Consider title insurance for all transactions",
        ]
        extra = {
            "subject_to": ["Due-on-sale clause risk — lender can call loan due immediately", "Seller's credit at risk if you miss payments"],
            "double_close": ["Title company must be comfortable with simultaneous closings", "Some title companies refuse double closes — confirm first"],
            "seller_finance": ["Dodd-Frank Act restrictions may apply — consult attorney", "Need promissory note AND deed of trust/mortgage recorded"],
        }
        return base + extra.get(contract_type, [])

    # ── AI-powered deal packet ────────────────────────────────────────────

    def generate_offer_packet(self, deal: dict, profile: dict) -> str:
        """Generate a complete offer presentation for a seller."""
        self._require_client()

        prompt = (
            f"Generate a professional offer packet for this wholesale deal.\n\n"
            f"Buyer: {profile.get('name', 'Investor')} | {profile.get('company', '')}\n"
            f"Property: {deal.get('address', 'Unknown')}\n"
            f"Offer Price: ${deal.get('price', 0):,.0f}\n"
            f"ARV: ${deal.get('arv', 0):,.0f}\n"
            f"Strategy: {deal.get('strategy', 'Wholesale')}\n"
            f"EMD: ${profile.get('emd_amount', 1000):,}\n"
            f"Close in: {profile.get('closing_days', 21)} days\n"
            f"Seller situation: {deal.get('seller_situation', 'unknown')}\n\n"
            f"Include:\n"
            f"1. Executive summary (1 paragraph — what you're offering)\n"
            f"2. Why this offer makes sense for the seller\n"
            f"3. Your credentials and track record\n"
            f"4. Clear next steps\n"
            f"5. Call to action\n\n"
            f"Professional but conversational. Not legal — just the business case."
        )

        resp = self.client.messages.create(
            model=MODEL, max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        log_activity(self.name, "offer_packet", deal.get("address", ""))
        return resp.content[0].text

    # ── Self-improvement ──────────────────────────────────────────────────

    def learn(self, closed_deals: list):
        if not self.client or len(closed_deals) < 3:
            return
        won = [d for d in closed_deals if d.get("outcome") == "won"]

        try:
            import json
            prompt = (
                f"From {len(won)} successful closings, what patterns emerge?\n"
                f"Deals: {str([(d.get('contract_type'), d.get('days_to_close'), d.get('what_worked')) for d in won[:10]])}\n\n"
                f"Respond with JSON: {{fastest_close_strategy, avg_contract_accept_days, best_emd_amount, insights: []}}"
            )
            resp = self.client.messages.create(
                model=MODEL, max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            m = re.search(r'\{.*\}', resp.content[0].text, re.DOTALL)
            if m:
                new = json.loads(m.group())
                current = load_patterns(self.name)
                current.update(new)
                save_patterns(self.name, current)
        except Exception:
            pass
