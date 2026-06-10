"""
Auto Offer System — generates and batches offer emails like Tranchi.ai's
"Slide to Place Offer" feature. Builds professional offer emails using
the investor's profile + property details.
"""
import os
from typing import Optional
import anthropic
from .user_profile import load_profile


FINANCING_DETAILS = {
    "DSCR Loan": "DSCR Loan (80% LTV, 20% Down Payment)",
    "Seller Finance": "Seller Financing (terms to be negotiated)",
    "Hard Money": "Hard Money Loan (65% ARV)",
    "Cash": "All Cash — no financing contingency",
    "Conventional": "Conventional Loan (20% Down)",
    "FHA": "FHA Loan (3.5% Down)",
    "$5K Down": "Creative Financing — $5,000 Down Payment",
}


def generate_offer_email(
    seller_name: str,
    seller_email: str,
    seller_phone: str,
    property_address: str,
    list_price: float,
    offer_price: float,
    financing_type: str = "DSCR Loan",
    profile: Optional[dict] = None,
    custom_notes: str = "",
) -> dict:
    """
    Generate a complete offer email using the user's profile.
    Returns dict with subject, body, recipient info.
    Matches Tranchi.ai's exact offer email format.
    """
    if profile is None:
        profile = load_profile()

    name = profile.get("name", "Investor")
    company = profile.get("company", "")
    portfolio = profile.get("portfolio_size", 0)
    years = profile.get("years_experience", 1)
    emd = profile.get("emd_amount", 1000)
    closing = profile.get("closing_days", 30)
    credit_pct = profile.get("seller_credit_pct", 3)
    entity = profile.get("purchasing_entity", company)
    bio = profile.get("bio_line", "")

    down_pct = 0.20
    down_amount = offer_price * down_pct
    credit_amount = offer_price * (credit_pct / 100)
    financing_str = FINANCING_DETAILS.get(financing_type, financing_type)

    subject = f"Purchase Offer – {property_address}"

    body = f"""Hello,

I hope this message finds you well. My name is {name} with {company} and I am writing to express my strong interest in purchasing the property located at {property_address}, currently listed at ${list_price:,.0f}.

I am a serious, qualified buyer ready to move quickly. Here is a summary of my offer:

- Offer Price: ${offer_price:,.0f}
- Financing: {financing_str} ({int(down_pct*100)}% Down Payment of ${down_amount:,.0f})
- Purchasing Entity: {entity}
- Closing Timeline: {closing} days from acceptance
- Seller Credit Requested: {credit_pct}% toward buyer closing costs (${credit_amount:,.0f})
- Earnest Money Deposit: ${emd:,.0f} — ready to submit upon acceptance

About me: {bio or f"I have {portfolio} investment properties in my current portfolio and {years} year{'s' if years == 1 else 's'} of real estate investing experience."} I am committed to a smooth, professional transaction and can provide any documentation upon request.{chr(10) + chr(10) + custom_notes if custom_notes else ""}

I look forward to discussing this further. Please feel free to reach me at {profile.get('email', '')} or {profile.get('phone', '')}.

Best regards,
{name}
{company}
{profile.get('phone', '')}
{profile.get('email', '')}"""

    return {
        "to_name": seller_name,
        "to_email": seller_email,
        "to_phone": seller_phone,
        "subject": subject,
        "body": body,
        "offer_price": offer_price,
        "property_address": property_address,
        "financing_type": financing_type,
    }


def generate_ai_offer_email(
    property_data: dict,
    offer_price: float,
    strategy: str = "buy_hold",
    profile: Optional[dict] = None,
) -> str:
    """
    Claude-enhanced offer email — AI personalizes based on property and seller situation.
    """
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        # Fall back to template version
        result = generate_offer_email(
            seller_name=property_data.get("contact_name", "Property Owner"),
            seller_email=property_data.get("contact_email", ""),
            seller_phone=property_data.get("contact_phone", ""),
            property_address=property_data.get("address", ""),
            list_price=property_data.get("price", offer_price),
            offer_price=offer_price,
            financing_type=property_data.get("financing_type", "DSCR Loan"),
            profile=profile,
        )
        return result["body"]

    if profile is None:
        profile = load_profile()

    client = anthropic.Anthropic(api_key=key)

    prop_type = property_data.get("category", "Tax Deed")
    address = property_data.get("address", "")
    ask = property_data.get("price", offer_price)
    arv = property_data.get("arv", 0)
    rent = property_data.get("est_rent", 0)
    cf = property_data.get("cash_flow", 0)

    prompt = f"""Write a professional real estate offer email for this specific property:

PROPERTY: {address}
Type: {prop_type}
List Price: ${ask:,.0f}
My Offer: ${offer_price:,.0f}
ARV: ${arv:,.0f}
Est. Rent: ${rent:,.0f}/mo
Est. Cash Flow: ${cf:,.0f}/mo
Strategy: {"Buy & Hold" if strategy == "buy_hold" else "Contract Flip / Wholesale"}

MY PROFILE:
Name: {profile.get("name", "Investor")}
Company: {profile.get("company", "")}
Portfolio: {profile.get("portfolio_size", 0)} properties
Experience: {profile.get("years_experience", 1)} years
EMD: ${profile.get("emd_amount", 1000):,.0f}
Closing: {profile.get("closing_days", 30)} days

Write a confident, professional offer email. Include:
- Offer price clearly stated
- Financing method ({profile.get("preferred_financing", "DSCR Loan")})
- 3% seller credit request toward closing costs
- EMD amount
- Closing timeline
- Brief credibility statement (portfolio size + experience)
- Friendly, professional tone — not aggressive

Keep it concise — under 250 words. No fluff. Ready to copy and send."""

    try:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        print(f"  [auto_offer] AI email generation failed: {e}")
        fallback = generate_offer_email(
            seller_name=property_data.get("contact_name", "Property Owner"),
            seller_email=property_data.get("contact_email", ""),
            seller_phone=property_data.get("contact_phone", ""),
            property_address=property_data.get("address", ""),
            list_price=property_data.get("price", offer_price),
            offer_price=offer_price,
            financing_type=property_data.get("financing_type", "DSCR Loan"),
            profile=profile,
        )
        return fallback["body"]


def batch_generate_offers(
    properties: list,
    offer_discount: float = 0.0,
    financing_type: Optional[str] = None,
    profile: Optional[dict] = None,
) -> list:
    """
    Generate offer emails for a list of properties at once.
    offer_discount: % below asking (0.0 = at asking, 0.10 = 10% below)
    Returns list of offer email dicts.
    """
    if profile is None:
        profile = load_profile()

    offers = []
    for prop in properties:
        ask = prop.get("price", 0)
        offer_price = ask * (1 - offer_discount)
        ft = financing_type or prop.get("financing_type", profile.get("preferred_financing", "DSCR Loan"))

        offer = generate_offer_email(
            seller_name=prop.get("contact_name", "Property Owner"),
            seller_email=prop.get("contact_email", ""),
            seller_phone=prop.get("contact_phone", ""),
            property_address=prop.get("address", ""),
            list_price=ask,
            offer_price=offer_price,
            financing_type=ft,
            profile=profile,
        )
        offers.append({**offer, "property": prop})

    return offers


def get_facebook_buyer_groups() -> list:
    """
    Facebook investor groups for finding cash buyers and flipping contracts.
    Same groups Tranchi.ai recommends in their videos.
    """
    return [
        {"name": "DFW Real Estate Investors", "market": "Dallas-Fort Worth, TX", "url": "https://www.facebook.com/groups/dfwrealestateinvestors"},
        {"name": "Chicago Real Estate Investors & Contractors", "market": "Chicago, IL", "url": "https://www.facebook.com/groups/chicagorealestateinvestors"},
        {"name": "717 Investors Group (Justin Robitaille)", "market": "National", "url": "https://www.facebook.com/groups/717investorsgroup"},
        {"name": "Detroit Real Estate Investors", "market": "Detroit, MI", "url": "https://www.facebook.com/groups/detroitrealestate"},
        {"name": "Atlanta Real Estate Investors Alliance", "market": "Atlanta, GA", "url": "https://www.facebook.com/groups/atlantarealestateinvestors"},
        {"name": "Houston Real Estate Investment", "market": "Houston, TX", "url": "https://www.facebook.com/groups/houstonrealestateinvestment"},
        {"name": "Memphis Real Estate Investors", "market": "Memphis, TN", "url": "https://www.facebook.com/groups/memphisrei"},
        {"name": "Birmingham AL Real Estate Investors", "market": "Birmingham, AL", "url": "https://www.facebook.com/groups/birminghamalrei"},
        {"name": "US Real Estate Investors", "market": "National", "url": "https://www.facebook.com/groups/usrealestateinvestors"},
        {"name": "Wholesale Real Estate Nation", "market": "National", "url": "https://www.facebook.com/groups/wholesalerealestatenetwork"},
        {"name": "Section 8 Landlords Network", "market": "National", "url": "https://www.facebook.com/groups/section8landlords"},
        {"name": "Cash Buyers Network Real Estate", "market": "National", "url": "https://www.facebook.com/groups/cashbuyersnetwork"},
    ]
