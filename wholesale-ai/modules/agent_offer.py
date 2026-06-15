"""
Agent Offer Engine — the LEGAL, low-touch outreach path to deal #1.

Contacting the LISTING AGENT with a written cash offer is normal, legal
business contact. (Cold-texting/robo-calling a homeowner is TCPA-restricted
— $500–$1,500 per message. This module never does that.)

For every real, below-market, HIGH-MARGIN listing the scan finds, this builds
a professional cash Letter of Intent with "and/or assigns" language and sends
it to the listing agent. The agent presents it to the seller. If accepted,
Alberto signs the assignable contract and assigns it to a cash buyer.

  build_cash_offer_loi(...)  -> {subject, body, opening_offer, walk_away}
  send_agent_offer(...)      -> {sent, saved_to, to_email, opening_offer, ...}

Both degrade gracefully: if no agent email or no email provider is configured,
the LOI is still written to disk so Alberto can send it in one paste.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from .user_profile import load_profile

OFFER_DIR = Path.home() / ".wholesale-ai" / "offers"


def _round_offer(amount: float) -> int:
    """Round an offer to the nearest $500 so it reads like a real offer."""
    if amount <= 0:
        return 0
    return int(round(amount / 500.0) * 500)


def build_cash_offer_loi(
    address: str,
    mao: float,
    agent_name: str = "",
    list_price: float = 0,
    profile: Optional[dict] = None,
    opening_pct: float = 0.90,
) -> dict:
    """
    Compose a cash Letter of Intent to the listing agent.

    Opens below MAO (default 90%) to leave negotiation room; MAO is the
    walk-away ceiling so the assignment fee is always protected.
    """
    if profile is None:
        profile = load_profile()

    name    = profile.get("name", "Alberto Soriano")
    company = profile.get("company", "")
    email   = profile.get("email", "")
    phone   = profile.get("phone", "")
    emd     = profile.get("emd_amount", 1000)
    closing = profile.get("closing_days", 21)
    entity  = profile.get("purchasing_entity") or company or name

    walk_away    = _round_offer(mao)
    opening_offer = _round_offer(mao * opening_pct)
    if opening_offer <= 0:
        opening_offer = walk_away

    greeting = f"Hi {agent_name.split()[0]}," if agent_name else "Hello,"
    list_line = (
        f"I'm reaching out about your listing at {address} (listed at ${list_price:,.0f})."
        if list_price > 0 else
        f"I'm reaching out about your listing at {address}."
    )

    subject = f"Cash Offer — {address}"

    body = f"""{greeting}

{list_line} I'm a cash buyer and I'd like to submit the following offer for your seller's consideration:

  • Purchase price:   ${opening_offer:,.0f}
  • Terms:            All cash — no financing or appraisal contingency
  • Buyer:            {entity}, and/or assigns
  • Earnest money:    ${emd:,.0f}, deposited within 48 hours of acceptance
  • Closing:          On or before {closing} days from acceptance
  • Inspection:       Short due-diligence period; property purchased as-is
  • Proof of funds:   Available on request

I can move quickly and close on your seller's timeline. If the number needs to
work differently, I'm open to discussing — please send a counter and I'll
respond same day.

You can reach me at {phone or email}{' or ' + email if (phone and email) else ''}.

Best regards,
{name}
{company}
{phone}
{email}""".rstrip()

    return {
        "subject":       subject,
        "body":          body,
        "opening_offer": opening_offer,
        "walk_away":     walk_away,
    }


def send_agent_offer(
    lead: dict,
    mao: float,
    profile: Optional[dict] = None,
    auto_send: bool = True,
) -> dict:
    """
    Build the LOI for a lead and send it to the listing agent (if an email and
    an email provider are configured). Always saves the LOI to disk.

    Returns a status dict describing what happened so the caller can show it.
    """
    if profile is None:
        profile = load_profile()

    address     = lead.get("title") or lead.get("address") or "Unknown"
    agent_name  = lead.get("agent_name", "") or lead.get("seller_name", "")
    agent_email = lead.get("agent_email", "") or lead.get("seller_email", "")
    list_price  = lead.get("price", 0)

    loi = build_cash_offer_loi(
        address=address, mao=mao, agent_name=agent_name,
        list_price=list_price, profile=profile,
    )

    # Always save the LOI to disk — even if we can't auto-send it.
    OFFER_DIR.mkdir(parents=True, exist_ok=True)
    safe  = "".join(c if c.isalnum() else "_" for c in address)[:40]
    stamp = datetime.now().strftime("%Y%m%d")
    saved = OFFER_DIR / f"offer_{safe}_{stamp}.txt"
    saved.write_text(
        f"TO: {agent_name or 'Listing Agent'} <{agent_email or 'NO EMAIL ON FILE'}>\n"
        f"SUBJECT: {loi['subject']}\n"
        f"OPENING OFFER: ${loi['opening_offer']:,.0f}  |  WALK-AWAY (MAO): ${loi['walk_away']:,.0f}\n"
        f"{'-'*60}\n{loi['body']}\n"
    )

    result = {
        "address":       address,
        "to_name":       agent_name,
        "to_email":      agent_email,
        "opening_offer": loi["opening_offer"],
        "walk_away":     loi["walk_away"],
        "subject":       loi["subject"],
        "body":          loi["body"],
        "saved_to":      str(saved),
        "sent":          False,
        "reason":        "",
    }

    if not auto_send:
        result["reason"] = "auto_send disabled"
        return result

    if not agent_email or "@" not in agent_email:
        result["reason"] = "no listing-agent email on this listing"
        return result

    # Lazy import so the module loads even if email_sender has heavy deps.
    from .email_sender import send_outreach_email, email_status
    if not email_status()["configured"]:
        result["reason"] = "no email provider configured (set SENDGRID_API_KEY or SMTP)"
        return result

    sent = send_outreach_email(
        to_email  = agent_email,
        subject   = loi["subject"],
        body      = loi["body"],
        from_name = profile.get("name", "Alberto Soriano"),
        reply_to  = profile.get("email", ""),
    )
    result["sent"] = bool(sent)
    if not sent:
        result["reason"] = "email provider rejected the send (check key/credits)"
    return result
