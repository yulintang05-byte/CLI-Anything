"""
Outreach Script Generator

One-click scripts for every seller type and every channel.
The moment a lead comes in, generate:
  - SMS (high response rate)
  - Cold call opener + full script
  - Voicemail (30 seconds)
  - Email
  - Door knock opener
  - Direct mail postcard text

Alberto's profile is auto-filled. Scripts are ready to copy and send.
"""
import os
from typing import Optional


SELLER_TYPES = {
    "tax_delinquent":    "Tax Delinquent Owner",
    "pre_foreclosure":   "Pre-Foreclosure / NOD",
    "probate":           "Probate / Inherited",
    "absentee":          "Absentee / Out-of-State Owner",
    "tired_landlord":    "Tired Landlord",
    "divorce":           "Divorce / Separation",
    "estate_sale":       "Estate / Inherited (listed)",
    "long_dom":          "Long Days on Market (listed, not selling)",
    "vacant":            "Vacant / Abandoned Property",
    "fsbo":              "For Sale By Owner (FSBO)",
    "fixer_upper":       "Fixer / As-Is Listed",
    "generic":           "Generic (unknown seller situation)",
}


def generate_sms(
    seller_type: str,
    property_address: str,
    seller_name: str = "",
    investor_name: str = "Alberto",
    investor_phone: str = "",
) -> str:
    """Short, punchy SMS. Under 160 chars. High response rate."""
    name_part = f" {seller_name}," if seller_name else ","
    scripts = {
        "tax_delinquent": (
            f"Hi{name_part} {investor_name} here. I saw the property at {property_address} "
            f"has a tax situation. I buy as-is, close in 2 weeks, handle the taxes. "
            f"Free to chat? {investor_phone}"
        ),
        "pre_foreclosure": (
            f"Hi{name_part} I'm {investor_name} — I help homeowners avoid foreclosure by "
            f"buying fast. {property_address} — still your place? I can make an offer this week. "
            f"{investor_phone}"
        ),
        "probate": (
            f"Hi{name_part} I'm {investor_name}. I understand you may have inherited a property "
            f"at {property_address}. I buy as-is, cash, close when you're ready. No pressure. "
            f"{investor_phone}"
        ),
        "absentee": (
            f"Hi{name_part} {investor_name} here. I noticed you own {property_address} — "
            f"would you consider an offer? I buy as-is, any condition, quick close. "
            f"{investor_phone}"
        ),
        "tired_landlord": (
            f"Hi{name_part} {investor_name} — I buy rental properties from landlords ready to "
            f"move on. {property_address} — interested in an offer? I close fast, no agents. "
            f"{investor_phone}"
        ),
        "divorce": (
            f"Hi{name_part} I'm {investor_name}. I can make a fast cash offer on {property_address} "
            f"to close quickly. Sometimes a clean break is the best move. No commission, no hassle. "
            f"{investor_phone}"
        ),
        "long_dom": (
            f"Hi{name_part} I saw {property_address} has been listed a while. "
            f"I'm a cash buyer — I can close in 2 weeks with no contingencies. "
            f"Worth a quick call? {investor_name} {investor_phone}"
        ),
        "fsbo": (
            f"Hi{name_part} I'm {investor_name}, cash buyer. Saw your FSBO at {property_address}. "
            f"I can close in 14 days, no agent fees, no repairs needed. Offer ready this week. "
            f"{investor_phone}"
        ),
        "fixer_upper": (
            f"Hi{name_part} {investor_name} here. I buy properties as-is — no repairs, no cleanup needed. "
            f"{property_address} — interested in a quick cash offer? {investor_phone}"
        ),
        "vacant": (
            f"Hi{name_part} I'm {investor_name}. I noticed {property_address} appears vacant. "
            f"I buy properties as-is with a quick close. Free to talk? {investor_phone}"
        ),
        "generic": (
            f"Hi{name_part} this is {investor_name}. I'm interested in buying {property_address} "
            f"— do you still own it? I pay cash and close fast. {investor_phone}"
        ),
    }
    return scripts.get(seller_type, scripts["generic"])


def generate_cold_call_script(
    seller_type: str,
    property_address: str,
    seller_name: str = "there",
    investor_name: str = "Alberto Soriano",
    investor_company: str = "",
    offer_price: float = 0,
) -> dict:
    """Full cold call script with opener, body, objections, and close."""

    openers = {
        "tax_delinquent": (
            f"Hi, is this {seller_name}? Great — my name is {investor_name}, "
            f"I'm a local real estate investor. I was looking at the county tax records "
            f"and saw that there's a property at {property_address} with some unpaid taxes. "
            f"I don't know your situation, but I buy properties in any condition and can "
            f"help with the tax situation. Is that something you'd want to talk about?"
        ),
        "pre_foreclosure": (
            f"Hi {seller_name}, this is {investor_name}. I work with homeowners who are "
            f"going through a tough time with their mortgage. I saw there may be some action "
            f"on {property_address} and I wanted to reach out before it gets further. "
            f"I can sometimes help people get out from under a property without going through "
            f"foreclosure. Is that something worth a conversation?"
        ),
        "probate": (
            f"Hi {seller_name}, my name is {investor_name}. I'm so sorry for your loss — "
            f"I know this is a difficult time. I'm a local investor who works with families "
            f"going through probate to take properties off their hands quickly for cash, "
            f"so you can focus on more important things. Is the property at {property_address} "
            f"something you'd consider selling?"
        ),
        "absentee": (
            f"Hi {seller_name}, this is {investor_name}. I'm a local real estate investor "
            f"and I was looking at properties in that area and noticed you own "
            f"{property_address}. I'm not sure if you're looking to sell or not, but I "
            f"buy properties as-is for cash and can close very quickly. Is that something "
            f"you'd be open to hearing more about?"
        ),
        "tired_landlord": (
            f"Hi {seller_name}, {investor_name} here. I work with landlords who are ready "
            f"to get out of the rental game — whether it's problem tenants, repairs, or just "
            f"ready to cash out. I saw you own {property_address} and I wanted to see if "
            f"you'd be open to a conversation about selling."
        ),
        "long_dom": (
            f"Hi {seller_name}, my name is {investor_name}. I saw {property_address} has "
            f"been on the market for a while and I wanted to reach out. I'm a cash buyer — "
            f"no agent commissions, no financing contingencies, I can close in two weeks. "
            f"Is that something that would work for you?"
        ),
        "fsbo": (
            f"Hi {seller_name}, {investor_name} here. I saw your For Sale By Owner sign "
            f"at {property_address}. I'm a local cash buyer — no real estate agents, "
            f"no commissions on your end. I can close in 14 days. Would you be open to "
            f"hearing my offer?"
        ),
        "generic": (
            f"Hi {seller_name}, this is {investor_name}. I'm a local real estate investor "
            f"and I'm looking to buy properties in the area. I saw {property_address} and "
            f"wanted to see if you'd be open to selling. I pay cash, buy as-is, and can "
            f"close quickly."
        ),
    }

    objections = {
        "I need to think about it": (
            "Totally understand. Can I ask — what's the main thing you'd be thinking about? "
            "I want to make sure if we do have a conversation, I can address your biggest concern."
        ),
        "I'm not interested": (
            "No problem at all. I get it — most people I call aren't actively thinking about selling. "
            "Can I ask — if the price was right, would you ever consider it? Or is there another "
            "reason it's not the right time?"
        ),
        "I already have an agent": (
            "That's great — agents are the right move for retail buyers. My situation is different — "
            "I'm a direct buyer, which means no showings, no 30-60 day escrow, no contingencies. "
            "I can close on your timeline. Does your agent have a cash buyer who can do that?"
        ),
        "I want full price / more money": (
            "I hear you — and that makes sense. The difference with me is convenience and certainty. "
            "No repairs, no commissions, no waiting for financing to fall through. Sometimes that "
            "certainty is worth a lot. What would you need to feel like you got a fair deal?"
        ),
        "I need to talk to my spouse / family": (
            "Absolutely — that's the right call on a decision this big. Can I set up a call with "
            "both of you this week? I want to make sure everyone's questions get answered."
        ),
        "How did you get my number?": (
            "Public county records — property ownership is public information. I look for properties "
            "where I might be able to help the owner. I'm sorry if it came out of nowhere."
        ),
    }

    close = (
        f"If I could make you an offer on {property_address} that worked for you — "
        f"cash, as-is, on your timeline — what would be the main thing that would make "
        f"you say yes? ... Great. Based on that, I'd like to set a time to walk the property "
        f"and make you a formal offer. Are you free this week?"
    )

    price_str = f"${offer_price:,.0f}" if offer_price > 0 else "a strong cash offer"

    return {
        "opener":         openers.get(seller_type, openers["generic"]),
        "value_prop": (
            f"Here's what I can offer: I'll pay {price_str}, buy the property as-is — no repairs, "
            f"no cleanup. I pay all closing costs. We close when you're ready, usually 2-3 weeks. "
            f"No real estate agent commissions on your end."
        ),
        "objections":     objections,
        "close":          close,
        "follow_up": (
            f"After the call: 1) Text them a summary with the address + your number. "
            f"2) Follow up in 3 days if no response. "
            f"3) Add to pipeline as 'Lead' and set a reminder."
        ),
    }


def generate_voicemail(
    seller_type: str,
    property_address: str,
    investor_name: str = "Alberto Soriano",
    investor_phone: str = "",
) -> str:
    """30-second voicemail script — leave this if they don't pick up."""
    scripts = {
        "tax_delinquent": (
            f"Hi, this message is for the owner of {property_address}. My name is {investor_name} "
            f"and I'm a local real estate investor. I understand there may be some unpaid taxes on "
            f"this property and I might be able to help. Please give me a call back at {investor_phone or 'my number'}. "
            f"No pressure at all — just a conversation. Thank you."
        ),
        "pre_foreclosure": (
            f"Hi, this is {investor_name} calling for the owner of {property_address}. "
            f"I work with homeowners to help them avoid foreclosure by buying their property quickly. "
            f"If you have a moment, please call me back at {investor_phone or 'my number'}. Thank you."
        ),
        "long_dom": (
            f"Hi, this is {investor_name} — I'm a cash buyer looking at {property_address}. "
            f"I can close in two weeks with no contingencies. Give me a call at {investor_phone or 'my number'} "
            f"and let's see if we can make this work for both of us. Thank you."
        ),
        "generic": (
            f"Hi, this is {investor_name} calling about the property at {property_address}. "
            f"I'm a local cash buyer — no repairs needed, I close fast. "
            f"Please call me back at {investor_phone or 'my number'} when you get a chance. Thank you."
        ),
    }
    return scripts.get(seller_type, scripts["generic"])


def generate_email(
    seller_type: str,
    property_address: str,
    seller_name: str = "Property Owner",
    investor_name: str = "Alberto Soriano",
    investor_company: str = "",
    investor_phone: str = "",
    investor_email: str = "",
    offer_price: float = 0,
    arv: float = 0,
) -> dict:
    """Complete email — subject line + body. Ready to send."""
    subjects = {
        "tax_delinquent":  f"Regarding {property_address} — I can help resolve the tax situation",
        "pre_foreclosure": f"Regarding {property_address} — Fast cash offer before deadline",
        "probate":         f"Regarding the property at {property_address} — Simple cash option",
        "absentee":        f"Cash offer on {property_address} — Quick close, any condition",
        "tired_landlord":  f"Ready to get out of the landlord game? {property_address}",
        "long_dom":        f"Cash offer on {property_address} — Close in 14 days",
        "fsbo":            f"Cash buyer for {property_address} — No commissions, fast close",
        "fixer_upper":     f"As-is offer on {property_address} — No repairs, close fast",
        "generic":         f"Cash offer inquiry — {property_address}",
    }

    price_str = f"${offer_price:,.0f}" if offer_price > 0 else "a fair cash offer"
    arv_str   = f" (ARV ${arv:,.0f})" if arv > 0 else ""

    bodies = {
        "tax_delinquent": f"""Dear {seller_name},

My name is {investor_name}{', with ' + investor_company if investor_company else ''} and I'm a local real estate investor.

I noticed the property at {property_address} has outstanding tax obligations and I wanted to reach out directly. I've helped other homeowners in similar situations get out cleanly — without the stress of a tax auction.

What I can offer:
  • Cash purchase at {price_str}{arv_str}
  • I handle the back taxes as part of the transaction
  • Close in 2–3 weeks on your timeline
  • No real estate commissions — you keep more

There's absolutely no obligation — just a conversation. If the situation has already been resolved, I apologize for bothering you.

Feel free to reach me at {investor_phone or 'reply to this email'}.

Respectfully,
{investor_name}
{investor_company}
{investor_phone}
{investor_email}""",

        "long_dom": f"""Dear {seller_name},

My name is {investor_name} and I'm a local cash buyer. I noticed {property_address} has been on the market and I'd love to make a direct offer.

What makes me different from a typical buyer:
  • I pay cash — no financing contingencies
  • I buy as-is — no repairs or cleanup required
  • I close in 14 days — no waiting for bank approvals
  • No agent commissions on your side

My offer: {price_str}

If this sounds like something worth exploring, I'd love to have a quick call. Reply here or text/call me at {investor_phone or 'number in signature'}.

Best,
{investor_name}
{investor_company}
{investor_phone}
{investor_email}""",

        "generic": f"""Dear {seller_name},

My name is {investor_name} and I'm a real estate investor looking to buy properties in the area.

I'm interested in {property_address} and would love to make you a cash offer.

My offer would be:
  • {price_str} cash{arv_str}
  • Purchase as-is — no repairs needed
  • Close in 2–3 weeks on your timeline
  • I cover closing costs

There's no obligation to respond, but if you're open to a quick conversation I'd love to connect.

Best regards,
{investor_name}
{investor_company}
{investor_phone}
{investor_email}""",
    }

    subject = subjects.get(seller_type, subjects["generic"])
    body    = bodies.get(seller_type, bodies["generic"])

    return {"subject": subject, "body": body}


def generate_direct_mail_postcard(
    seller_type: str,
    property_address: str,
    investor_name: str = "Alberto Soriano",
    investor_phone: str = "",
) -> str:
    """Postcard text (front + back). Under 100 words total. High open rate."""
    cards = {
        "tax_delinquent": (
            f"FRONT: 'Don't let taxes cost you your home.'\n\n"
            f"BACK: I buy properties with tax issues — fast, for cash. "
            f"I can help you close before the deadline. {property_address}. "
            f"Call/text {investor_name} at {investor_phone or '[your number]'}. No pressure. Quick response."
        ),
        "pre_foreclosure": (
            f"FRONT: 'Facing foreclosure? There IS another way.'\n\n"
            f"BACK: I buy homes fast for cash — before the bank takes it. "
            f"You walk away with money, your credit protected. {property_address}. "
            f"Call/text {investor_name}: {investor_phone or '[your number]'}."
        ),
        "absentee": (
            f"FRONT: 'WE BUY HOUSES — FAST, AS-IS, ANY CONDITION'\n\n"
            f"BACK: Own {property_address}? I pay cash, close in 2 weeks, buy in any shape. "
            f"No agents, no repairs. Call/text {investor_name}: {investor_phone or '[your number]'}."
        ),
        "tired_landlord": (
            f"FRONT: 'Tired of being a landlord? Cash out in 14 days.'\n\n"
            f"BACK: I buy rental properties AS-IS. No showings, no repairs, no agent fees. "
            f"Keep ALL your equity. Call {investor_name}: {investor_phone or '[your number]'}."
        ),
        "generic": (
            f"FRONT: 'WE BUY HOUSES — CASH, AS-IS, FAST'\n\n"
            f"BACK: Any condition, any situation. Close in 2 weeks. "
            f"Fair offer, no pressure, no repairs. "
            f"Call/text {investor_name}: {investor_phone or '[your number]'}."
        ),
    }
    return cards.get(seller_type, cards["generic"])


def generate_door_knock_script(
    seller_type: str,
    property_address: str,
    investor_name: str = "Alberto Soriano",
    investor_phone: str = "",
) -> str:
    """In-person door knock opener — first 30 seconds matter most."""
    scripts = {
        "vacant": (
            f"Hi, I'm {investor_name}. Sorry to bother you — I noticed this property at "
            f"{property_address} appears to be vacant. Are you the owner? "
            f"[If yes:] I'm a local real estate investor and I'd love to make you a cash offer "
            f"on this property. Do you have 5 minutes to chat? "
            f"[Leave card if no answer or no owner:] "
            f"Leave a handwritten note: 'Interested in buying this property for cash. "
            f"Call/text {investor_name}: {investor_phone}.'"
        ),
        "fixer_upper": (
            f"Hi, is this your home? I'm {investor_name}, a local investor. "
            f"I noticed the property and I'm interested in buying it as-is — no repairs needed, "
            f"quick cash close. I know that might sound random! "
            f"Would you be open to hearing an offer? I promise it's a quick conversation."
        ),
        "generic": (
            f"Hi there — sorry to knock! My name is {investor_name}. "
            f"I'm a local real estate investor looking to buy in this neighborhood. "
            f"I'm curious if you'd ever consider selling? I buy homes for cash in any condition. "
            f"No agents, no commissions, quick close. Is that something worth a conversation?"
        ),
    }
    return scripts.get(seller_type, scripts["generic"])


def get_all_scripts(
    seller_type: str,
    property_address: str,
    seller_name: str = "",
    investor_name: str = "Alberto Soriano",
    investor_phone: str = "",
    investor_email: str = "",
    offer_price: float = 0,
    arv: float = 0,
) -> dict:
    """Generate the complete outreach package for one lead — all channels ready."""
    return {
        "seller_type":    SELLER_TYPES.get(seller_type, seller_type),
        "address":        property_address,
        "sms":            generate_sms(seller_type, property_address, seller_name, investor_name, investor_phone),
        "voicemail":      generate_voicemail(seller_type, property_address, investor_name, investor_phone),
        "cold_call":      generate_cold_call_script(seller_type, property_address, seller_name or "there",
                                                     investor_name, "", offer_price),
        "email":          generate_email(seller_type, property_address, seller_name or "Property Owner",
                                          investor_name, "", investor_phone, investor_email, offer_price, arv),
        "direct_mail":    generate_direct_mail_postcard(seller_type, property_address, investor_name, investor_phone),
        "door_knock":     generate_door_knock_script(seller_type, property_address, investor_name, investor_phone),
        "follow_up_sequence": [
            "Day 1:  SMS + voicemail if no answer",
            "Day 3:  Call again — 7am or 6pm (highest pickup rates)",
            "Day 5:  Email",
            "Day 7:  Postcard in mail",
            "Day 14: Second call — reference the postcard",
            "Day 21: Final email — 'Last reach out before I move on'",
            "Day 30: If no response — add to drip campaign, re-contact in 3 months",
        ],
    }


def detect_seller_type_from_lead(lead: dict) -> str:
    """Auto-detect seller type from lead data and distress signals."""
    distress = " ".join(lead.get("distress_signals", [])).lower()
    raw_text  = (lead.get("raw_text", "") or "").lower()
    combined  = distress + " " + raw_text

    if "tax" in combined and ("delinquent" in combined or "lien" in combined):
        return "tax_delinquent"
    if "foreclosure" in combined or "bank owned" in combined or "reo" in combined:
        return "pre_foreclosure"
    if "probate" in combined or "estate" in combined:
        return "probate"
    if "divorce" in combined:
        return "divorce"
    if "vacant" in combined or "abandoned" in combined:
        return "vacant"
    if "as-is" in combined or "as is" in combined or "handyman" in combined or "fixer" in combined:
        return "fixer_upper"
    dom = lead.get("days_on_market") or 0
    if dom >= 90:
        return "long_dom"
    if "motivated" in combined or "must sell" in combined or "price reduced" in combined:
        return "absentee"
    return "generic"
