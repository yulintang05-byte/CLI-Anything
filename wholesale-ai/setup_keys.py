#!/usr/bin/env python3
"""
setup_keys.py — One-command live setup.

Run this on your Mac:  python setup_keys.py

Walks you through pasting each API key, writes them to .env, then tests
each connection so you KNOW it's live before you start hunting deals.
"""
import os
import sys
from pathlib import Path

ENV_FILE = Path(__file__).parent / ".env"

KEYS = [
    {
        "name": "ANTHROPIC_API_KEY",
        "label": "AI brain (negotiation scripts, deal analysis, advisor)",
        "where": "https://console.anthropic.com/  →  Settings → API Keys",
        "cost": "~$0.01–0.05 per call. A heavy month is under $5.",
        "starts": "sk-ant-",
        "required_for": "AI Deal Analyzer, Negotiation Scripts, Ask the Advisor",
        "optional": True,
    },
    {
        "name": "RENTCAST_API_KEY",
        "label": "LIVE listings feed (real for-sale houses + ARV + rent)",
        "where": "https://app.rentcast.io/app/api  →  free tier = 50 calls/mo",
        "cost": "FREE up to 50 calls/month. This is THE deal feed.",
        "starts": "",
        "required_for": "LIVE Lead Finder, agent deal hunting, real comps",
        "optional": True,
    },
    {
        "name": "HUD_API_TOKEN",
        "label": "HUD Fair Market Rents (Section 8 rent ceilings)",
        "where": "https://www.huduser.gov/portal/dataset/api.html  (free token)",
        "cost": "FREE.",
        "starts": "",
        "required_for": "HUD FMR lookups, accurate Section 8 numbers",
        "optional": True,
    },
    {
        "name": "ELEVENLABS_API_KEY",
        "label": "ElevenLabs — voice outreach (voicemail MP3s + call audio)",
        "where": "https://elevenlabs.io  →  Profile → API Key",
        "cost": "Free tier = 10,000 chars/mo (~15 voicemails). Starter $5/mo.",
        "starts": "",
        "required_for": "Auto-generate voicemail audio for every deal",
        "optional": True,
    },
    {
        "name": "ELEVENLABS_VOICE_ID",
        "label": "ElevenLabs Voice ID (which voice speaks your scripts)",
        "where": "Leave blank for default (Adam — professional US male). Find IDs at elevenlabs.io/voice-library",
        "cost": "N/A",
        "starts": "",
        "required_for": "ElevenLabs voice selection",
        "optional": True,
    },
    {
        "name": "OBSIDIAN_VAULT_PATH",
        "label": "Obsidian vault path (deal notes auto-synced here)",
        "where": "Open Obsidian → Settings → About → Vault path (e.g. /Users/alberto/Documents/Obsidian/Main)",
        "cost": "FREE — Obsidian is free.",
        "starts": "/",
        "required_for": "Auto-export deal cards to your Obsidian vault",
        "optional": True,
    },
    {
        "name": "SENDGRID_API_KEY",
        "label": "SendGrid — auto-send outreach emails (preferred over SMTP)",
        "where": "https://app.sendgrid.com/  →  Settings → API Keys → Create API Key",
        "cost": "FREE up to 100 emails/day. More than enough for deals.",
        "starts": "SG.",
        "required_for": "Auto-email sellers when close package is built",
        "optional": True,
    },
    {
        "name": "EMAIL_FROM",
        "label": "Your sender email address (used if no SendGrid key)",
        "where": "Your business email address, e.g. alberto@yourdomain.com",
        "cost": "N/A",
        "starts": "",
        "required_for": "SMTP fallback email sending",
        "optional": True,
    },
]


def read_existing() -> dict:
    vals = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                vals[k.strip()] = v.strip()
    return vals


def is_real(val: str) -> bool:
    """A real key, not a placeholder."""
    if not val:
        return False
    placeholders = ("your-key", "your-hud", "your-key-here", "sk-ant-your")
    return not any(p in val.lower() for p in placeholders)


def write_env(vals: dict):
    lines = [
        "# ─── AI Analysis (console.anthropic.com) ───────────────────────────────",
        f"ANTHROPIC_API_KEY={vals.get('ANTHROPIC_API_KEY','')}",
        "",
        "# ─── RentCast — LIVE listings + real ARV/rent (the deal feed) ──────────",
        "# Free tier = 50 calls/mo. Key: https://app.rentcast.io/app/api",
        f"RENTCAST_API_KEY={vals.get('RENTCAST_API_KEY','')}",
        "",
        "# ─── HUD USER API (huduser.gov/portal/dataset/api.html) ────────────────",
        f"HUD_API_TOKEN={vals.get('HUD_API_TOKEN','')}",
        "",
        "# ─── Optional: ATTOM Data API (attomdata.com) ──────────────────────────",
        f"ATTOM_API_KEY={vals.get('ATTOM_API_KEY','')}",
        "",
        "# ─── ElevenLabs — voice outreach MP3s (elevenlabs.io) ──────────────────",
        f"ELEVENLABS_API_KEY={vals.get('ELEVENLABS_API_KEY','')}",
        f"ELEVENLABS_VOICE_ID={vals.get('ELEVENLABS_VOICE_ID','')}",
        "",
        "# ─── Obsidian vault — deal notes auto-sync ──────────────────────────────",
        f"OBSIDIAN_VAULT_PATH={vals.get('OBSIDIAN_VAULT_PATH','')}",
        "",
        "# ─── Email outreach — SendGrid (preferred) or SMTP ─────────────────────",
        f"SENDGRID_API_KEY={vals.get('SENDGRID_API_KEY','')}",
        f"EMAIL_FROM={vals.get('EMAIL_FROM','')}",
        f"EMAIL_PASSWORD={vals.get('EMAIL_PASSWORD','')}",
        f"EMAIL_SMTP_HOST={vals.get('EMAIL_SMTP_HOST','')}",
        f"EMAIL_SMTP_PORT={vals.get('EMAIL_SMTP_PORT','587')}",
        "",
    ]
    ENV_FILE.write_text("\n".join(lines))


def prompt_keys():
    print("\n" + "=" * 70)
    print("  WHOLESALE AI — LIVE SETUP")
    print("  Paste each key when asked. Press Enter to skip / keep current.")
    print("=" * 70)

    existing = read_existing()
    vals = dict(existing)

    for k in KEYS:
        name = k["name"]
        current = existing.get(name, "")
        have = is_real(current)
        status = f"✓ already set ({current[:10]}...)" if have else "✗ not set"

        print(f"\n── {k['label']}")
        print(f"   Status:   {status}")
        print(f"   Get it:   {k['where']}")
        print(f"   Cost:     {k['cost']}")
        print(f"   Powers:   {k['required_for']}")

        entry = input(f"   Paste {name} (Enter to keep current): ").strip()
        if entry:
            if k["starts"] and not entry.startswith(k["starts"]):
                print(f"   ⚠  Warning: expected key to start with '{k['starts']}'. Saving anyway.")
            vals[name] = entry
        elif not have:
            print("   → skipped (feature stays in sample mode)")

    write_env(vals)
    print(f"\n✓ Saved to {ENV_FILE}")
    return vals


def test_connections(vals: dict):
    print("\n" + "=" * 70)
    print("  TESTING CONNECTIONS")
    print("=" * 70)

    # Load into env for the test
    for k, v in vals.items():
        if v:
            os.environ[k] = v

    # --- Anthropic ---
    ak = vals.get("ANTHROPIC_API_KEY", "")
    if is_real(ak):
        try:
            import urllib.request
            import json
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json.dumps({
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "hi"}],
                }).encode(),
                headers={
                    "x-api-key": ak,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
            )
            urllib.request.urlopen(req, timeout=15)
            print("  ANTHROPIC_API_KEY:  ✓ LIVE — AI features active")
        except Exception as e:
            msg = str(e)[:60]
            print(f"  ANTHROPIC_API_KEY:  ✗ failed — {msg}")
            print("     (check the key, or your network blocks outbound HTTPS)")
    else:
        print("  ANTHROPIC_API_KEY:  ○ not set — AI features in sample mode")

    # --- RentCast ---
    rk = vals.get("RENTCAST_API_KEY", "")
    if is_real(rk):
        try:
            from modules import rentcast
            diag = rentcast.diagnose()
            if diag["ok"]:
                print("  RENTCAST_API_KEY:   ✓ LIVE — real listings feed active")
            else:
                print(f"  RENTCAST_API_KEY:   ✗ {diag.get('reason','')} — {diag.get('fix','')}")
        except Exception as e:
            print(f"  RENTCAST_API_KEY:   ✗ error — {str(e)[:60]}")
    else:
        print("  RENTCAST_API_KEY:   ○ not set — listings in sample mode")

    # --- HUD ---
    hk = vals.get("HUD_API_TOKEN", "")
    print(f"  HUD_API_TOKEN:      {'✓ set' if is_real(hk) else '○ not set (optional)'}")

    print("\n" + "=" * 70)
    live = is_real(vals.get("ANTHROPIC_API_KEY","")) or is_real(vals.get("RENTCAST_API_KEY",""))
    if live:
        print("  🎉 You're LIVE. Run:  python main.py")
        print("     Then hit [36] to schedule the daily scan, or [23] to hunt now.")
    else:
        print("  Still in sample mode — no keys saved. The tool works on built-in")
        print("  data, but won't pull real listings until you add a RentCast key.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        vals = prompt_keys()
        test_connections(vals)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled. Nothing saved this run.\n")
        sys.exit(0)
