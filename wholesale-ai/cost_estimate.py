#!/usr/bin/env python3
"""
Cost estimator for Wholesale AI.

Counts the ACTUAL Claude calls each feature makes and prices them at current
Claude Opus 4.x rates. Everything else in the app (scraping, scoring, the
4-strategy deal cards, contracts, lender matching, tenant scoring, pipeline)
is pure Python and costs $0.

Opus 4.x pricing: $15 / million input tokens, $75 / million output tokens.
Verify current rates at https://www.anthropic.com/pricing
"""
IN_RATE  = 15 / 1_000_000   # $ per input token
OUT_RATE = 75 / 1_000_000   # $ per output token

def cost(in_tok, out_tok):
    return in_tok * IN_RATE + out_tok * OUT_RATE

# (label, input tokens [system+prompt], typical output tokens, is it Opus?)
CALLS = {
    "Lead AI scoring (per scan, scores top 5)":   (900, 700),
    "Negotiation opening script":                  (600, 1400),
    "Counter-offer response":                      (450, 800),
    "Objection handler":                           (350, 500),
    "Walk-away assessment":                        (350, 450),
    "AI offer packet (seller presentation)":       (450, 1100),
    "AI deal analyzer (grade + red flags)":        (500, 900),
    "Ask the AI Advisor (one question)":           (150, 700),
    "Self-improvement learn (×3 agents)":          (4500, 1800),
}

print("=" * 72)
print("  PER-ACTION COST  (Claude Opus 4.x — the only thing that costs money)")
print("=" * 72)
for label, (i, o) in CALLS.items():
    print(f"  {label:48} ${cost(i, o):.3f}")

print("\n  FREE (pure Python — $0 forever):")
for f in ["Browse gov/distressed sources", "Hot markets + all 4-strategy deal cards",
          "Live lead scraping & scoring", "Lender directory + deal matching",
          "Luxury deal math", "Tenant pre-screen scoring", "ALL contracts (templates)",
          "Pipeline/CRM", "DSCR/BRRRR/cash-flow calculators", "Agent dashboard & memory"]:
    print(f"    • {f}")

# ── Monthly scenarios ─────────────────────────────────────────────────────────
def month(name, usage):
    total = 0.0
    print(f"\n{'─'*72}\n  {name}\n{'─'*72}")
    for label, n in usage.items():
        i, o = CALLS[label]
        c = cost(i, o) * n
        total += c
        print(f"  {n:>4}×  {label:46} ${c:6.2f}")
    print(f"  {'':>4}   {'TOTAL / MONTH':46} ${total:6.2f}")
    return total

month("LIGHT — learning the tool, a few deals", {
    "Lead AI scoring (per scan, scores top 5)": 20,
    "AI deal analyzer (grade + red flags)":     10,
    "Negotiation opening script":               10,
    "AI offer packet (seller presentation)":     8,
    "Ask the AI Advisor (one question)":        20,
})

month("ACTIVE — background agents daily + working real deals", {
    "Lead AI scoring (per scan, scores top 5)": 30,   # daily background scan
    "AI deal analyzer (grade + red flags)":     40,
    "Negotiation opening script":               30,
    "Counter-offer response":                   30,
    "Walk-away assessment":                     20,
    "AI offer packet (seller presentation)":    30,
    "Ask the AI Advisor (one question)":        50,
    "Self-improvement learn (×3 agents)":        3,
})

month("HEAVY — high volume, scaling to $10k-30k/mo", {
    "Lead AI scoring (per scan, scores top 5)":  60,
    "AI deal analyzer (grade + red flags)":     150,
    "Negotiation opening script":               120,
    "Counter-offer response":                   120,
    "Objection handler":                         80,
    "Walk-away assessment":                      80,
    "AI offer packet (seller presentation)":    100,
    "Ask the AI Advisor (one question)":        100,
    "Self-improvement learn (×3 agents)":         6,
})

print(f"\n{'='*72}")
print("  COST-SAVER: route the high-frequency Lead AI scoring to Haiku 4.5")
print("  ($1/$5 per M tok = ~15× cheaper). It's triage, not deep reasoning.")
haiku = (900*1 + 700*5) / 1_000_000
print(f"    Lead scoring on Opus:  ${cost(900,700):.3f}   on Haiku: ${haiku:.4f}")
print(f"    30 daily scans/mo:     ${cost(900,700)*30:.2f}  ->  ${haiku*30:.2f}")
print("=" * 72)
