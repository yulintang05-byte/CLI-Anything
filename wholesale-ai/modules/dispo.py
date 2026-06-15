"""
Dispo Engine — turn ANY locked deal into a buyer blast in one command.

This generalizes the Baldwin one-off so every co-wholesale / off-market deal
you lock fires to your cash-buyer bench instantly. Dispo (finding the buyer)
is the part fully in our control and the fastest route to a check — so it's
the part we make bulletproof.

  build_pitch(deal)          -> {subject, body, sms}
  preflight(state)           -> {ok, provider, sender, buyers_total, emailable}
  fire_blast(deal, send)     -> {emailed, failed, manual, ...}
  save_deal(deal)/load_deals() -> persist deals to ~/.wholesale-ai/dispo_deals.json

A "deal" is a plain dict:
  {address, all_in, beds, baths, sqft, year, arv, comps, rehab_low, rehab_high,
   emd, close_days, state, highlights, notes}

Everything degrades safely: preview sends nothing; a real send aborts if the
email provider / verified sender / buyer bench isn't ready.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from .user_profile import load_profile

DISPO_FILE = Path.home() / ".wholesale-ai" / "dispo_deals.json"

# Baldwin is live (backup position) — seed it so it's one click from a blast
# even before the deals file exists on a given machine.
_SEED_DEALS = [
    {
        "id": "baldwin",
        "address": "2980 Baldwin St, Detroit, MI 48214",
        "all_in": 134900, "beds": 4, "baths": 2, "sqft": 2731, "year": "1912",
        "arv": 350000,
        "comps": "2493 Fischer $310k - 3456 Burns $349k - 1494 Bewick $324.9k",
        "rehab_low": 100000, "rehab_high": 150000, "emd": 5000, "close_days": 14,
        "state": "MI",
        "highlights": "Newer roof, updated baths + kitchens, mid multi-to-single conversion. VACANT.",
    },
]


# ── Persistence ───────────────────────────────────────────────────────────────

def load_deals() -> list:
    if not DISPO_FILE.exists():
        return list(_SEED_DEALS)
    try:
        return json.loads(DISPO_FILE.read_text())
    except Exception:
        return list(_SEED_DEALS)


def save_deal(deal: dict) -> dict:
    DISPO_FILE.parent.mkdir(parents=True, exist_ok=True)
    deals = load_deals()
    deal.setdefault("id", datetime.now().strftime("%Y%m%d%H%M%S"))
    deal.setdefault("saved_at", datetime.now().isoformat())
    deals = [d for d in deals if d.get("id") != deal["id"]] + [deal]
    DISPO_FILE.write_text(json.dumps(deals, indent=2, default=str))
    return deal


# ── Pitch builder ─────────────────────────────────────────────────────────────

def build_pitch(deal: dict, profile: Optional[dict] = None) -> dict:
    """Build the buyer-facing subject, email body, and SMS from deal numbers."""
    if profile is None:
        profile = load_profile()

    reply_to = os.getenv("DISPO_REPLY_TO") or profile.get("email", "")
    name     = profile.get("name", "Alberto Soriano")
    company  = profile.get("company", "RisePoint Ventures")

    addr   = deal.get("address", "Off-market deal")
    all_in = deal.get("all_in", 0)
    beds   = deal.get("beds", "?")
    baths  = deal.get("baths", "?")
    sqft   = deal.get("sqft", "?")
    year   = deal.get("year", "")
    arv    = deal.get("arv", 0)
    rehab_low  = deal.get("rehab_low", 0)
    rehab_high = deal.get("rehab_high", 0)
    emd    = deal.get("emd", 5000)
    close  = deal.get("close_days", 14)
    comps  = deal.get("comps", "")
    highlights = deal.get("highlights", "")

    sqft_n = sqft if isinstance(sqft, (int, float)) and sqft else 0
    spread = (arv - all_in - ((rehab_low + rehab_high) / 2 if rehab_high else rehab_low)) if arv else 0

    rehab_line = (
        f"  Rehab: budget ${rehab_low:,}-${rehab_high:,} depending on your crew\n"
        if rehab_high else
        (f"  Rehab: budget ~${rehab_low:,}\n" if rehab_low else "")
    )
    comps_line = f"       ({comps})\n" if comps else ""
    hl_line    = f"  {highlights}\n" if highlights else ""
    spread_line = (
        f"  Your margin at ARV ${arv:,}: ~${spread:,.0f} spread\n" if spread > 0 else ""
    )

    city_zip = ""
    parts = [p.strip() for p in addr.split(",")]
    if len(parts) >= 2:
        city_zip = parts[1] + (" " + parts[2] if len(parts) > 2 else "")

    subject = f"Off-market: {beds}/{baths} {sqft}sqft — {city_zip or addr} — ${all_in/1000:.0f}k all-in"

    body = f"""Under contract, assignable, one buyer only — first proof of funds takes it.

  {addr}
  {beds} bed / {baths} bath - {sqft} sqft{f' - {year}' if year else ''} - VACANT
{hl_line}  All-in to you: ${all_in:,} (contract + assignment, one number, no surprises)
  ARV: ${arv:,} conservative
{comps_line}{rehab_line}{spread_line}
  Terms: ${emd:,} non-refundable EMD on assignment, close in {close} days, walk it first.

Reply with proof of funds and your walkthrough window. First verified PoF locks it.

{name} — {company} — {reply_to}
""".rstrip()

    sms = (
        f"Off-market {city_zip or addr}: {beds}/{baths} {sqft}sqft, vacant. "
        f"${all_in//1000}k all-in assignable, ARV ${arv//1000}k. "
        f"${emd//1000 if emd>=1000 else emd}k EMD, {close}-day close. First PoF takes it. "
        f"Want the packet? — {name.split()[0]}"
    )

    return {"subject": subject, "body": body, "sms": sms, "reply_to": reply_to}


# ── Buyer targeting ───────────────────────────────────────────────────────────

def matched_buyers(deal: dict) -> list:
    """Buyers whose market covers the deal's state and whose price band fits."""
    from .cash_buyers import get_all_buyers
    state  = (deal.get("state") or "").upper()
    all_in = deal.get("all_in", 0)
    out = []
    for b in get_all_buyers():
        markets = " ".join(b.get("markets", [])).upper()
        if state and state not in markets:
            continue
        pmax = b.get("price_max", 0)
        pmin = b.get("price_min", 0)
        # all_in must fit the buyer's band (pmax 0 = no ceiling)
        if all_in and pmin and all_in < pmin:
            continue
        if all_in and pmax and all_in > pmax:
            continue
        out.append(b)
    return out


def preflight(deal: dict) -> dict:
    """Verify everything needed to fire. Returns a status dict."""
    from .email_sender import email_status
    es = email_status()
    from_email = os.getenv("EMAIL_FROM", "")
    buyers = matched_buyers(deal)
    emailable = [b for b in buyers if b.get("email")]
    ok = bool(es["configured"] and from_email and buyers)
    return {
        "ok":           ok,
        "provider":     es["provider"],
        "configured":   es["configured"],
        "sender":       from_email,
        "buyers_total": len(buyers),
        "emailable":    len(emailable),
        "phone_only":   len(buyers) - len(emailable),
    }


# ── Fire ──────────────────────────────────────────────────────────────────────

def fire_blast(deal: dict, send: bool = False, profile: Optional[dict] = None) -> dict:
    """
    Blast a deal to the matched buyer bench.

    send=False (default) returns the rendered pitch + who WOULD receive it,
    sending nothing. send=True actually emails (aborts if preflight fails).
    """
    if profile is None:
        profile = load_profile()

    pitch = build_pitch(deal, profile)
    pf    = preflight(deal)
    buyers = matched_buyers(deal)

    result = {
        "address":   deal.get("address", ""),
        "subject":   pitch["subject"],
        "body":      pitch["body"],
        "sms":       pitch["sms"],
        "preflight": pf,
        "would_email": [b for b in buyers if b.get("email")],
        "phone_only":  [b for b in buyers if not b.get("email")],
        "sent":      False,
        "emailed":   0,
        "failed":    0,
    }

    if not send:
        result["mode"] = "preview"
        return result

    if not pf["ok"]:
        result["mode"]  = "aborted"
        result["error"] = "preflight failed — fix provider / verified sender / buyer bench"
        return result

    from .email_sender import send_outreach_email
    from .cash_buyers import record_buyer_deal_sent

    name = profile.get("name", "Alberto Soriano")
    for b in buyers:
        if not b.get("email"):
            continue
        if send_outreach_email(b["email"], pitch["subject"], pitch["body"],
                               from_name=name, reply_to=pitch["reply_to"]):
            record_buyer_deal_sent(b["id"])
            result["emailed"] += 1
        else:
            result["failed"] += 1

    result["sent"] = True
    result["mode"] = "sent"
    return result
