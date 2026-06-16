"""
DISPO BLAST — 2980 Baldwin St, Detroit, MI 48214

We are in BACKUP position. This emails every cash buyer on file the moment the
PSA converts to us. Two safety rails so it can't misfire:

  PREVIEW (default — safe, sends nothing; run this NOW to verify everything):
      cd ~/CLI-Anything/wholesale-ai && PYTHONPATH=. .venv/bin/python3 dispo_blast_baldwin.py

  FIRE FOR REAL (only after the PSA is signed in our name):
      cd ~/CLI-Anything/wholesale-ai && PYTHONPATH=. .venv/bin/python3 dispo_blast_baldwin.py --send

Preview mode renders the exact email, lists every buyer who would receive it,
and runs a preflight (provider configured, verified sender set, buyers loaded)
WITHOUT sending — so you confirm it works before the deal is even live.
"""
import sys
from pathlib import Path

from dotenv import load_dotenv

# Robust .env load: script-relative first (works on any machine), then the
# known Mac path as fallback. Either way the keys load.
_HERE = Path(__file__).resolve().parent
for _candidate in (_HERE / ".env", Path("/Users/albert/CLI-Anything/wholesale-ai/.env")):
    if _candidate.exists():
        load_dotenv(_candidate, override=True)
        break

from modules.cash_buyers import get_all_buyers, record_buyer_deal_sent
from modules.email_sender import send_outreach_email, email_status
from modules.user_profile import load_profile

# ── Reply-to / signature: sourced from profile so buyer replies land in the
# inbox you actually check. Override with DISPO_REPLY_TO env var if needed.
import os
_PROFILE = load_profile()
REPLY_TO = os.getenv("DISPO_REPLY_TO") or _PROFILE.get("email") or "albert143rd@gmail.com"
FROM_NAME = _PROFILE.get("name", "Alberto Soriano")
COMPANY = _PROFILE.get("company", "RisePoint Ventures")

# ── Deal terms (DO NOT change without re-verifying the contract) ──────────────
ALL_IN = 134_900
SUBJECT = "Off-market: 4/2 colonial, 2,731 sqft — Islandview/East Village 48214 — $134.9k all-in"

PITCH = f"""Under contract, assignable, one buyer only — first proof of funds takes it.

  2980 Baldwin St, Detroit 48214 (Islandview, walkable to Belle Isle / Indian Village)
  4 bed / 2 bath - 2,731 sqft - 1912 three-level colonial - VACANT
  Newer roof, updated baths + kitchens, mid multi-to-single conversion

  All-in to you: ${ALL_IN:,} (contract + assignment, one number, no surprises)
  ARV: $350k conservative (listing-stated) - renovated 48214 comps run $156-185/sqft
       (2493 Fischer $310k - 3456 Burns $349k - 1494 Bewick $324.9k)
  Rehab: budget a gut - $100k-150k depending on your crew
  Your margin at ARV $350k / $125k rehab: ~$90k spread on a $285k basis

  Terms: $5k non-refundable EMD on assignment, close in 14 days, walk it first.

Reply with proof of funds and your walkthrough window. First verified PoF locks it.

{FROM_NAME} — {COMPANY} — {REPLY_TO}
"""

SMS = (
    f"Off-market 48214 Islandview: 4/2 colonial 2,731sqft, vacant, newer roof. "
    f"${ALL_IN//1000}k all-in assignable, ARV $350k, comps $156-185/sqft. "
    f"$5k EMD, 14-day close. First PoF takes it. Want the full packet? — Alberto"
)


def _mi_buyers():
    return [b for b in get_all_buyers() if "MI" in " ".join(b.get("markets", []))]


def preflight() -> bool:
    """Verify everything needed to send. Returns True if good to fire."""
    ok = True
    es = email_status()
    print("PREFLIGHT")
    print(f"  Email provider : {es['provider']}" + ("" if es["configured"] else "  ✗ NOT CONFIGURED"))
    if not es["configured"]:
        print("    → set SENDGRID_API_KEY (and a SendGrid-verified EMAIL_FROM) in .env")
        ok = False
    from_email = os.getenv("EMAIL_FROM", "")
    print(f"  Verified sender: {from_email or '✗ EMAIL_FROM not set'}")
    if not from_email:
        print("    → SendGrid rejects sends without a verified EMAIL_FROM")
        ok = False
    print(f"  Replies go to  : {REPLY_TO}")
    mi = _mi_buyers()
    with_email = [b for b in mi if b.get("email")]
    print(f"  MI buyers      : {len(mi)} on file, {len(with_email)} emailable, {len(mi)-len(with_email)} phone-only")
    if not mi:
        print("    → no Detroit-metro buyers in CRM (option 31 to add, or load buyer bench)")
        ok = False
    print(f"  Status         : {'✓ READY TO FIRE' if ok else '✗ FIX ABOVE BEFORE FIRING'}")
    return ok


def main():
    send = "--send" in sys.argv
    mode = "LIVE SEND" if send else "PREVIEW (no emails sent)"
    print(f"\n=== DISPO BLAST — 2980 Baldwin St — {mode} ===\n")

    ready = preflight()

    print("\nEMAIL THAT GOES OUT")
    print(f"  SUBJECT: {SUBJECT}")
    print("  " + "-" * 58)
    for line in PITCH.splitlines():
        print(f"  {line}")
    print("  " + "-" * 58)

    mi = _mi_buyers()
    if not send:
        print(f"\nWOULD EMAIL {len([b for b in mi if b.get('email')])} buyer(s):")
        for b in mi:
            tag = b["email"] if b.get("email") else f"PHONE-ONLY ({b.get('phone','?')})"
            print(f"  • {b.get('name','?')[:30]:30} → {tag}")
        print("\nPHONE-ONLY one-tap SMS:")
        print(f"  {SMS}")
        print("\nThis was PREVIEW. Nothing was sent.")
        print("When the PSA is signed in our name, re-run with  --send")
        return

    if not ready:
        print("\n✗ ABORTED — preflight failed. Fix the items above, then re-run --send.")
        sys.exit(1)

    emailed, failed, manual = 0, 0, []
    for b in mi:
        if b.get("email"):
            if send_outreach_email(b["email"], SUBJECT, PITCH, from_name=FROM_NAME, reply_to=REPLY_TO):
                record_buyer_deal_sent(b["id"])
                emailed += 1
            else:
                failed += 1
                print(f"  ✗ send failed → {b['name']} <{b['email']}>")
        else:
            manual.append(b)

    print(f"\nRESULT: {emailed} emailed, {failed} failed, {len(manual)} phone-only")
    if failed:
        print("  ⚠ Some sends failed — check SendGrid key/credits and verified sender.")
    print("\n=== PHONE / FORM ONE-TAPS (copy-paste SMS) ===")
    for b in manual:
        print(f"\n→ {b['name']} — {b.get('phone') or '(see notes)'}\n  notes: {b.get('notes','')[:120]}")
    print(f"\nSMS TEXT:\n{SMS}")
    print("\nAlso post on CL /reo (free dispo) and reply to the "
          "'Who's Buying In Detroit??' wholesaler for a JV dispo assist.")


if __name__ == "__main__":
    main()
