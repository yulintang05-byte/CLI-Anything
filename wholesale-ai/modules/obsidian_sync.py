"""
Obsidian Vault Sync — writes every deal card as a Markdown note.

Every time a close package is built or a lead is marked high-margin,
this module drops a formatted .md file into Alberto's Obsidian vault.
Open Obsidian and the deal is already there — no copy-paste needed.

Env var:
  OBSIDIAN_VAULT_PATH  — absolute path to your vault root
  e.g. /Users/albertosoriano/Documents/Obsidian/Main

Notes land at:
  $OBSIDIAN_VAULT_PATH/Wholesale Deals/YYYY-MM/Address.md

Tags applied: #wholesale #deal #<city> #<status>
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def _vault() -> Optional[Path]:
    v = os.getenv("OBSIDIAN_VAULT_PATH", "").strip()
    if not v:
        return None
    return Path(v)


def _deals_folder() -> Optional[Path]:
    vault = _vault()
    if not vault:
        return None
    month = datetime.now().strftime("%Y-%m")
    folder = vault / "Wholesale Deals" / month
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _safe_filename(address: str) -> str:
    return (
        address.replace("/", "-").replace("\\", "-")
               .replace(":", "").replace("*", "")
               .replace("?", "").replace('"', "")
               .replace("<", "").replace(">", "")
               .replace("|", "")[:80]
    ) + ".md"


def export_deal_to_obsidian(
    deal_data:  dict,
    address:    str,
    status:     str = "active",
    sms_script: str = "",
    email_body: str = "",
    notes:      str = "",
) -> Optional[str]:
    """
    Write a formatted deal card to Obsidian vault.
    Returns the file path written, or None if vault not configured.
    """
    folder = _deals_folder()
    if not folder:
        return None

    now   = datetime.now()
    price = deal_data.get("purchase_price", deal_data.get("price", 0))
    arv   = deal_data.get("arv", 0)
    rehab = deal_data.get("repair_estimate", deal_data.get("estimated_rehab", 0))
    spread = deal_data.get("wholesale_spread", arv - price - rehab if arv else 0)
    rent  = deal_data.get("monthly_rent", 0)
    city  = deal_data.get("city", "")
    state = deal_data.get("state", "")
    source = deal_data.get("source", "")

    # Frontmatter (Obsidian dataview-compatible)
    lines = [
        "---",
        f"address: \"{address}\"",
        f"city: {city}",
        f"state: {state}",
        f"status: {status}",
        f"price: {price:,.0f}" if price else "price: unknown",
        f"arv: {arv:,.0f}" if arv else "arv: unknown",
        f"rehab: {rehab:,.0f}" if rehab else "rehab: unknown",
        f"spread: {spread:,.0f}" if spread else "spread: unknown",
        f"rent: {rent:,.0f}" if rent else "rent: unknown",
        f"source: \"{source}\"",
        f"date_added: {now.strftime('%Y-%m-%d')}",
        f"tags: [wholesale, deal, {city.lower().replace(' ', '-')}, {status}]",
        "---",
        "",
        f"# {address}",
        f"> Added {now.strftime('%B %d, %Y at %I:%M %p')} · Source: {source}",
        "",
    ]

    # Deal snapshot
    lines += [
        "## Deal Snapshot",
        "",
        f"| | |",
        f"|---|---|",
        f"| **Purchase Price** | ${price:,.0f} |" if price else "| **Purchase Price** | Unknown |",
        f"| **ARV** | ${arv:,.0f} |" if arv else "| **ARV** | Unknown |",
        f"| **Est. Rehab** | ${rehab:,.0f} |" if rehab else "| **Est. Rehab** | Unknown |",
        f"| **Wholesale Spread** | ${spread:,.0f} |" if spread else "| **Wholesale Spread** | TBD |",
        f"| **Monthly Rent** | ${rent:,.0f}/mo |" if rent else "| **Monthly Rent** | TBD |",
        "",
    ]

    # Strategy results if present
    strategies = deal_data.get("strategies", {})
    if strategies:
        lines += ["## Strategy Analysis", ""]
        for name, s in strategies.items():
            lines.append(f"### {name}")
            for k, v in s.items():
                if isinstance(v, float):
                    lines.append(f"- **{k}**: {v:,.2f}")
                elif isinstance(v, int):
                    lines.append(f"- **{k}**: {v:,}")
                else:
                    lines.append(f"- **{k}**: {v}")
            lines.append("")

    # Outreach scripts
    if sms_script:
        lines += [
            "## SMS (send first)",
            "",
            "```",
            sms_script.strip(),
            "```",
            "",
        ]
    if email_body:
        lines += [
            "## Email Body",
            "",
            "```",
            email_body.strip(),
            "```",
            "",
        ]

    # Notes
    if notes:
        lines += ["## Notes", "", notes, ""]

    # Action checklist
    lines += [
        "## Checklist",
        "",
        "- [ ] Verify address on Zillow/Redfin (photos, beds/baths confirmed)",
        "- [ ] Run comps — option 35",
        "- [ ] Get real rehab estimate — option 37",
        "- [ ] Send SMS to seller",
        "- [ ] Seller responded",
        "- [ ] Negotiation script run",
        "- [ ] Purchase contract signed",
        "- [ ] Buyer matched",
        "- [ ] Assignment contract signed",
        "- [ ] Assignment fee collected",
        "",
    ]

    content = "\n".join(lines)
    out_path = folder / _safe_filename(address)
    out_path.write_text(content, encoding="utf-8")
    print(f"  [obsidian] ✓ Deal note saved: {out_path}")
    return str(out_path)


def export_pipeline_digest_to_obsidian(pipeline_deals: list) -> Optional[str]:
    """
    Write a daily digest of all active pipeline deals to Obsidian.
    One file per day: $VAULT/Wholesale Deals/Daily Digest/YYYY-MM-DD.md
    """
    vault = _vault()
    if not vault:
        return None

    folder = vault / "Wholesale Deals" / "Daily Digest"
    folder.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        "---",
        f"date: {today}",
        "tags: [wholesale, digest, daily]",
        "---",
        "",
        f"# Wholesale Pipeline — {today}",
        f"> {len(pipeline_deals)} active deal(s)",
        "",
        "| Address | Price | ARV | Spread | Status |",
        "|---------|-------|-----|--------|--------|",
    ]

    for d in pipeline_deals:
        addr   = d.get("address", d.get("title", "Unknown"))[:40]
        price  = f"${d.get('price', 0):,.0f}"
        arv    = f"${d.get('arv', 0):,.0f}" if d.get("arv") else "TBD"
        spread = f"${d.get('spread', 0):,.0f}" if d.get("spread") else "TBD"
        status = d.get("status", "active")
        lines.append(f"| {addr} | {price} | {arv} | {spread} | {status} |")

    lines += ["", "---", "Generated by Wholesale AI"]

    out_path = folder / f"{today}.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  [obsidian] ✓ Digest saved: {out_path}")
    return str(out_path)


def vault_status() -> dict:
    """Return vault configuration status for display in the app."""
    vault = _vault()
    if not vault:
        return {"configured": False, "path": None, "deal_count": 0}

    deal_folder = vault / "Wholesale Deals"
    count = 0
    if deal_folder.exists():
        count = sum(1 for f in deal_folder.rglob("*.md") if f.name != "Daily Digest")

    return {
        "configured": True,
        "path":       str(vault),
        "deal_count": count,
    }
