"""
DISPO BLAST — 2980 Baldwin St, Detroit, MI 48214
FIRE THIS THE MOMENT THE PSA IS SIGNED. Do not run before — we are backup position.

  cd ~/CLI-Anything/wholesale-ai && PYTHONPATH=. .venv/bin/python3 dispo_blast_baldwin.py

Emails every buyer on file that has an email (SendGrid, verified sender),
prints copy-paste SMS for phone-only buyers, and logs sends to the buyer CRM.
"""
from dotenv import load_dotenv

load_dotenv("/Users/albert/CLI-Anything/wholesale-ai/.env", override=True)

from modules.cash_buyers import get_all_buyers, record_buyer_deal_sent
from modules.email_sender import send_outreach_email

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

Alberto Soriano — RisePoint Ventures — yulintang05@gmail.com
"""

SMS = (
    f"Off-market 48214 Islandview: 4/2 colonial 2,731sqft, vacant, newer roof. "
    f"${ALL_IN//1000}k all-in assignable, ARV $350k, comps $156-185/sqft. "
    f"$5k EMD, 14-day close. First PoF takes it. Want the full packet? — Alberto"
)

if __name__ == "__main__":
    emailed, manual = 0, []
    for b in get_all_buyers():
        if "MI" not in " ".join(b.get("markets", [])):
            continue
        if b.get("email"):
            if send_outreach_email(b["email"], SUBJECT, PITCH, from_name="Alberto Soriano",
                                   reply_to="yulintang05@gmail.com"):
                record_buyer_deal_sent(b["id"])
                emailed += 1
        else:
            manual.append(b)

    print(f"\nemailed: {emailed}")
    print("\n=== PHONE / FORM ONE-TAPS (copy-paste SMS below) ===")
    for b in manual:
        contact = b.get("phone") or "(see notes)"
        print(f"\n→ {b['name']} — {contact}\n  notes: {b['notes'][:120]}")
    print(f"\nSMS TEXT:\n{SMS}")
    print("\nAlso post the deal on CL /reo (free dispo) and reply to the "
          "'Who's Buying In Detroit??' wholesaler for a JV dispo assist.")
