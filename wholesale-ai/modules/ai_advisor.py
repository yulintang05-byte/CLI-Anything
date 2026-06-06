"""
AI Advisor — Claude-powered deal analysis, negotiation scripts, and offer generation.
Uses Anthropic API (get free credits at console.anthropic.com).
"""
import os
from typing import Optional
import anthropic


def get_client() -> Optional[anthropic.Anthropic]:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    return anthropic.Anthropic(api_key=key)


SYSTEM_PROMPT = """You are an expert real estate wholesaling advisor with 20+ years of experience.
You specialize in:
- Finding distressed, government-owned, and off-market properties below market value
- Wholesale deal analysis (MAO calculations, ARV estimation, repair scoping)
- Creative deal structures: assignment of contract, double closing, subject-to, seller financing
- Negotiating with motivated sellers (probate, tax liens, pre-foreclosure, estate sales)
- Building cash buyer lists and marketing wholesale deals
- Working with government property sources: HUD homes, GSA surplus, tax lien properties,
  USDA rural, Fannie Mae HomePath, Freddie Mac HomeSteps, US Marshals seized assets

Always be specific, practical, and actionable. Give real numbers and scripts when asked.
Be straight with the user about whether a deal works or not. Never sugarcoat bad numbers.
Format responses clearly with sections. Keep explanations concise but complete."""


def analyze_deal(
    address: str,
    asking_price: float,
    arv: float,
    repairs: float,
    property_type: str = "single family",
    bedrooms: int = 3,
    sqft: int = 1500,
    condition: str = "distressed",
    source: str = "unknown",
    notes: str = "",
) -> str:
    """Full AI deal analysis with strategy recommendations."""
    client = get_client()
    if not client:
        return "⚠️  ANTHROPIC_API_KEY not set. Add it to .env to unlock AI analysis.\n   Get a free key at: https://console.anthropic.com/"

    wholesale_fee = 10_000
    mao = (arv * 0.70) - repairs - wholesale_fee
    spread = arv - asking_price - repairs - wholesale_fee
    is_deal = asking_price <= mao

    prompt = f"""Analyze this wholesale real estate deal and give me your honest assessment:

PROPERTY: {address}
Type: {property_type} | {bedrooms}bd | {sqft} sqft | Condition: {condition}
Source: {source}

NUMBERS:
- Seller Asking Price: ${asking_price:,.0f}
- After Repair Value (ARV): ${arv:,.0f}
- Estimated Repairs: ${repairs:,.0f}
- Max Allowable Offer (MAO @ 70% − $10k fee): ${mao:,.0f}
- Equity Spread: ${spread:,.0f}
- Deal works at asking price: {"YES" if is_deal else "NO — needs ${:,.0f} price reduction".format(asking_price - mao)}

Additional notes: {notes if notes else "None"}

Please provide:
1. **Deal Grade** (A/B/C/F) with one-sentence verdict
2. **Key Numbers** — what the cash buyer gets, what I make, what seller gets
3. **Strategy** — best deal structure (assignment, double close, subject-to, etc.) and why
4. **Red Flags** — anything that could kill this deal
5. **Next Steps** — exactly what to do next (3 action items)
6. **Negotiation Approach** — how to get to my number if seller is above MAO"""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def generate_negotiation_script(
    seller_situation: str,
    asking_price: float,
    your_offer: float,
    property_address: str = "",
    seller_motivation: str = "",
) -> str:
    """Generate a tailored negotiation script for motivated sellers."""
    client = get_client()
    if not client:
        return "⚠️  ANTHROPIC_API_KEY not set. Add it to .env to unlock this feature."

    prompt = f"""Write me a complete negotiation phone/in-person script for this situation:

Property: {property_address or "the property"}
Seller Situation: {seller_situation}
Seller Asking: ${asking_price:,.0f}
My Target Offer: ${your_offer:,.0f}  (gap to close: ${asking_price - your_offer:,.0f})
Seller's Known Motivation: {seller_motivation or "unknown"}

Write a full word-for-word script including:
1. **Opening** — how to start the conversation and build rapport fast
2. **Discovery Questions** — to uncover their real motivation and timeline
3. **Pain Points** — how to gently surface their problem (repairs, taxes, etc.)
4. **Presenting the Offer** — exactly how to say the number without losing them
5. **Handling Objections** — responses to "that's too low", "I owe more", "I'll list it", "I need time"
6. **Closing** — getting them to sign or commit to next steps

Use natural, conversational language. Mark where to pause and listen with [LISTEN]."""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def generate_offer_letter(
    buyer_name: str,
    seller_name: str,
    property_address: str,
    offer_price: float,
    earnest_money: float = 1000,
    closing_days: int = 30,
    assignment_clause: bool = True,
    inspection_days: int = 14,
    extra_terms: str = "",
) -> str:
    """Generate a wholesale Letter of Intent / offer letter."""
    client = get_client()
    if not client:
        return "⚠️  ANTHROPIC_API_KEY not set. Add it to .env to unlock this feature."

    prompt = f"""Write a professional real estate wholesale Letter of Intent (LOI) / offer letter.

BUYER: {buyer_name}
SELLER: {seller_name}
PROPERTY: {property_address}
OFFER PRICE: ${offer_price:,.0f}
EARNEST MONEY DEPOSIT: ${earnest_money:,.0f}
INSPECTION PERIOD: {inspection_days} days
CLOSING TIMELINE: {closing_days} days from acceptance
ASSIGNMENT CLAUSE NEEDED: {"YES — buyer reserves right to assign contract" if assignment_clause else "NO"}
ADDITIONAL TERMS: {extra_terms or "Standard cash purchase, as-is, no repairs"}

Write a complete, professional LOI that:
1. States the offer clearly and confidently
2. Includes all standard protective clauses for the buyer
3. Has proper assignment language if needed (e.g., "Buyer and/or assigns")
4. Is firm but friendly in tone
5. Includes a signature block for both parties
6. Mentions the property will be purchased as-is, where-is
7. States earnest money is refundable during inspection period

Format it as an actual ready-to-use letter with today's date placeholder [DATE]."""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def explain_strategy(strategy: str) -> str:
    """Explain a wholesale strategy in plain language with step-by-step process."""
    client = get_client()
    if not client:
        return "⚠️  ANTHROPIC_API_KEY not set. Add it to .env to unlock this feature."

    strategies = {
        "assignment": "Assignment of Contract",
        "double close": "Double Closing / Simultaneous Close",
        "subject-to": "Subject-To (Taking Over Seller's Mortgage)",
        "seller finance": "Seller Financing",
        "tax lien": "Tax Lien Investing",
        "tax deed": "Tax Deed / Tax Sale Investing",
        "hud": "Buying HUD Homes (Government Foreclosures)",
        "pre-foreclosure": "Pre-Foreclosure / Notice of Default Investing",
        "probate": "Probate Real Estate Investing",
    }

    full_name = strategies.get(strategy.lower(), strategy)

    prompt = f"""Explain "{full_name}" as a real estate wholesale/investment strategy.

Cover:
1. **What it is** — plain English, 2 sentences max
2. **How it works** — step-by-step process (numbered list)
3. **Money needed** — realistic startup capital required
4. **Profit potential** — typical deals, timelines
5. **Pros** — top 3 advantages
6. **Cons / Risks** — top 3 risks and how to handle them
7. **Getting Started** — first 3 actions to take THIS WEEK for free
8. **Script to find these deals** — what to say to find sellers/properties

Be specific with real numbers. Skip the theory — make it actionable."""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def ask_advisor(question: str, context: str = "") -> str:
    """Free-form question to the wholesale AI advisor."""
    client = get_client()
    if not client:
        return "⚠️  ANTHROPIC_API_KEY not set. Add it to .env to unlock the AI advisor.\n   Get a free key at: https://console.anthropic.com/"

    prompt = question
    if context:
        prompt = f"Context: {context}\n\nQuestion: {question}"

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def find_cash_buyers_strategy(market: str, property_type: str = "single family") -> str:
    """Get a strategy for finding cash buyers in a specific market."""
    client = get_client()
    if not client:
        return "⚠️  ANTHROPIC_API_KEY not set."

    prompt = f"""Give me a complete cash buyer acquisition strategy for {market}.
Property type I'm wholesaling: {property_type}

Include:
1. **Top 5 Free Methods** to find cash buyers fast (with specific actions)
2. **Online Platforms** — which sites to post deals on and how
3. **Networking** — specific groups, events, meetups to attend
4. **Craigslist/Facebook** — exact ad copy to post to attract buyers
5. **Skip Tracing** — how to find investors who bought cash in last 12 months
6. **Script** — what to say when a buyer calls you
7. **How to vet buyers** — 3 questions to ask to confirm they can close

Give me real tactics, not theory."""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=900,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
