# CLAUDE.md — Wholesale AI Session Instructions

> Read this file at the start of EVERY session. No exceptions.
> Alberto does not re-explain context. You pick up where you left off.

---

## Who Alberto Is

Real estate wholesaler. Runs the Midwest + growing nationally.
**Alberto's only job: read the deal and sign the contract.**
Everything else — finding deals, running numbers, writing outreach, drafting contracts, matching buyers, setting up lenders — is your job.

---

## How to Start Every Session

1. Check `git log --oneline -5` to see what was last committed
2. Check `wholesale-ai/modules/pipeline.py` for active deals in the pipeline
3. If Alberto pastes app output, analyze it immediately — don't ask what he wants
4. If a deal shows `HIGH MARGIN`, verify it's not a phantom before generating outreach

---

## The Workflow (Never Deviate)

```
SCAN [23]  →  verify deal is real  →  generate close package
→  Alberto sends SMS (one tap)  →  negotiation scripts on reply
→  contract drafted  →  Alberto signs  →  assign to buyer  →  collect fee
```

Alberto never types scripts. You write them word-for-word, copy-paste ready.
Alberto never runs numbers. You run them with 4 strategies (Flip/BRRRR/DSCR/Section 8).
Alberto never cold calls. ElevenLabs speaks the script. (See voice module below.)

---

## API Keys — SECURITY PROTOCOL

Keys are stored in Alberto's Mem.ai notes app.
**NEVER ask Alberto to paste a key in chat.**
**NEVER commit a key to git.**

To get a key, use the Mem.ai MCP tool:
```python
mcp__d85c7d0c-7b5f-43fa-8677-93a396cd23be__search_notes(query="rentcast api key")
mcp__d85c7d0c-7b5f-43fa-8677-93a396cd23be__search_notes(query="anthropic api key")
mcp__d85c7d0c-7b5f-43fa-8677-93a396cd23be__search_notes(query="elevenlabs api key")
mcp__d85c7d0c-7b5f-43fa-8677-93a396cd23be__search_notes(query="email smtp password")
```

Write retrieved keys to `wholesale-ai/.env` only. `.env` is gitignored.

---

## Connected Services

| Service | Purpose | Key location | Module |
|---------|---------|--------------|--------|
| Anthropic Claude | AI deal analysis | Mem.ai notes | `modules/ai_advisor.py` |
| RentCast | Live listings + ARV + rent | Mem.ai notes | `modules/rentcast.py` |
| ElevenLabs | Voice outreach (voicemails + calls) | Mem.ai notes | `modules/elevenlabs_voice.py` |
| Email (SMTP/SendGrid) | Automated outreach emails | Mem.ai notes | `modules/email_sender.py` |
| Obsidian | Deal notes vault sync | Vault path in .env | `modules/obsidian_sync.py` |
| HUD API | Fair Market Rent data | Mem.ai notes | `modules/hud_search.py` |
| ATTOM | Deep property data | Mem.ai notes | (optional enrichment) |

---

## ElevenLabs Voice Integration

When a close package is generated, also produce audio:

```python
from modules.elevenlabs_voice import speak_script
speak_script(script_text, output_path="voicemail_3240_Glynn.mp3")
```

ElevenLabs speaks the voicemail script in a professional male voice.
Alberto plays the MP3 when the seller picks up, or drops it as a voicemail.
Key env var: `ELEVENLABS_API_KEY`
Voice ID env var: `ELEVENLABS_VOICE_ID` (default: Adam — professional US male)

---

## Email Integration

When a close package is generated, queue the outreach email automatically:

```python
from modules.email_sender import send_outreach_email
send_outreach_email(to_email, subject, body, from_name="Alberto Soriano")
```

Env vars needed: `EMAIL_FROM`, `EMAIL_PASSWORD`, `EMAIL_SMTP_HOST`, `EMAIL_SMTP_PORT`
OR: `SENDGRID_API_KEY` (preferred — no SMTP config needed)

---

## Obsidian Vault Sync

Every deal card and pipeline entry gets exported as a markdown note:

```python
from modules.obsidian_sync import export_deal_to_obsidian
export_deal_to_obsidian(deal_data, address)
```

Files land in: `$OBSIDIAN_VAULT_PATH/Wholesale Deals/YYYY-MM/address.md`
Alberto opens Obsidian and sees every deal in his vault automatically.
Env var: `OBSIDIAN_VAULT_PATH` (e.g. `/Users/albertosoriano/Documents/Obsidian/Main`)

---

## Phantom Deal Filters — Never Remove These

Three layers stop bad data from reaching Alberto:

| Layer | File | What it stops |
|-------|------|---------------|
| Source | `modules/rentcast.py` | Vacant lots (0 beds/0 sqft), DLBA infill parcels |
| Source | `modules/rentcast.py` | DLBA-owned houses (`_is_land_bank_listing`) → `is_link_only` |
| Agent | `agents/lead_agent.py` | `_looks_like_land()` backstop, `_is_dlba_house()` backstop |
| Agent | `agents/lead_agent.py` | AVM yield > 25% gross → revert to market rent |
| Display | `main.py` | Yellow `⚠ VERIFY BEFORE YOU ACT` panel on any `data_warning` |
| Portal | `modules/web_scraper.py` | DLBA portal entries → `is_link_only=True, price=0` |

**Never** generate outreach for a lead with `is_link_only=True` or `status=link_only`.

---

## Current Branch

```
git branch: claude/real-estate-wholesale-ai-mHOW0
git push target: origin claude/real-estate-wholesale-ai-mHOW0
```

Always develop and push to this branch. Never push to main without Alberto's permission.

---

## How to Run the App

```bash
cd ~/CLI-Anything/wholesale-ai
python3 main.py
```

Key menu options:
- **23** — Live Lead Scan (the main event — run this daily)
- **26** — Pipeline manager (active deals)
- **35** — Comp validator (verify ARV before sending offer)
- **37** — Rehab estimator (real repair numbers)
- **41** — Property management finder
- **42** — BRRRR HML auto-trigger

---

## When a Deal Comes Up — Your Checklist

1. **Is it real?** — WebSearch the address. Confirm beds/baths/photos exist. Not a DLBA listing.
2. **Are the numbers right?** — ARV via option [35]. Rehab via option [37]. Don't use flat $20k default.
3. **Generate the package** — SMS + call script + email + voicemail MP3 + buyer pitch
4. **Export to Obsidian** — so Alberto has it in his vault
5. **Hand Alberto one action** — "Send this SMS:" followed by the exact text. Nothing else.

---

## Things You Never Do

- Never tell Alberto to "check the numbers" — you check them
- Never generate outreach for a DLBA / link_only lead
- Never commit `.env` or any file containing real API keys
- Never push to a branch other than the one above without asking
- Never ask Alberto to explain context — read this file instead
