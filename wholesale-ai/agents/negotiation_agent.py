"""
Negotiation Agent — "The Negotiator"
Handles all seller communication intelligently.
Generates custom scripts, handles objections, knows when to walk away.
Learns which tactics get accepted offers.
"""
import os
import re
from typing import Optional

import anthropic

from agents.memory import load_patterns, save_patterns, log_activity

MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = """You are a master real estate negotiator working on behalf of a wholesale investor.

Your principles:
1. EMPATHY FIRST — understand the seller's real problem, then solve it
2. NEVER lead with price — lead with solutions (speed, certainty, as-is)
3. The seller's REAL motivation is never just money — find the why
4. Silence is power — let them fill it after you make an offer
5. Objections are requests for more information, not rejections
6. Always have a walkaway number and mean it
7. Every counteroffer is a YES in disguise — they're still talking

You think critically: Is this seller genuinely motivated? Are the numbers real?
What's the most likely way this deal falls apart, and how do I prevent it?

Your scripts are conversational, not salesy. Real humans talking to humans.
"""


class NegotiationAgent:
    def __init__(self, profile: Optional[dict] = None):
        self.name     = "NegotiationAgent"
        self.profile  = profile or {}
        self.patterns = load_patterns(self.name)
        self.client   = None
        self._init_client()

    def _init_client(self):
        key = os.getenv("ANTHROPIC_API_KEY")
        if key:
            self.client = anthropic.Anthropic(api_key=key)

    def _require_client(self):
        if not self.client:
            raise RuntimeError("ANTHROPIC_API_KEY not set")

    # ── Initial outreach script ───────────────────────────────────────────

    def generate_opening_script(
        self,
        seller_name: str,
        address: str,
        asking_price: float,
        your_target: float,
        seller_situation: str = "",
        contact_method: str = "phone",
    ) -> str:
        self._require_client()

        insights = "\n".join(self.patterns.get("insights", [])[:5]) or "No prior data yet."

        prompt = (
            f"Generate a {'phone call script' if contact_method == 'phone' else 'text/email'} "
            f"for first contact with a motivated seller.\n\n"
            f"Seller: {seller_name}\n"
            f"Property: {address}\n"
            f"Their asking price: ${asking_price:,.0f}\n"
            f"My target offer: ${your_target:,.0f}\n"
            f"Known situation: {seller_situation or 'unknown — probe gently'}\n\n"
            f"Learned patterns from past deals:\n{insights}\n\n"
            f"Write the complete opening script with:\n"
            f"1. Opening (30 seconds — earn the right to ask questions)\n"
            f"2. Discovery questions (find their real motivation)\n"
            f"3. Bridge to offer (transition naturally)\n"
            f"4. Offer delivery (present price with confidence)\n"
            f"5. Handle the 3 most likely objections\n"
            f"6. Close / next step\n\n"
            f"Write in natural conversational language. No salesy phrases."
        )

        resp = self.client.messages.create(
            model=MODEL, max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        script = resp.content[0].text
        log_activity(self.name, "script_generated", address)
        return script

    # ── Counter-offer response ────────────────────────────────────────────

    def generate_counter_response(
        self,
        seller_counter: float,
        your_mao: float,
        your_current_offer: float,
        conversation_context: str = "",
    ) -> str:
        self._require_client()

        gap     = seller_counter - your_mao
        closing = your_current_offer < your_mao

        prompt = (
            f"Seller countered at ${seller_counter:,.0f}.\n"
            f"My max (MAO): ${your_mao:,.0f}\n"
            f"My current offer: ${your_current_offer:,.0f}\n"
            f"Gap from MAO: ${gap:,.0f}\n"
            f"Context: {conversation_context or 'standard negotiation'}\n\n"
            f"Generate my response. Think step by step:\n"
            f"1. Is this gap bridgeable or should I walk?\n"
            f"2. What's my counter-strategy?\n"
            f"3. Write the actual response (what I say/write to the seller)\n"
            f"4. What's my fallback if they say no?\n\n"
            f"If the gap > $15,000 above MAO, recommend walking away clearly."
        )

        resp = self.client.messages.create(
            model=MODEL, max_tokens=1200,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        log_activity(self.name, "counter_generated", f"Their: ${seller_counter:,} | MAO: ${your_mao:,}")
        return resp.content[0].text

    # ── Objection handler ─────────────────────────────────────────────────

    def handle_objection(self, objection: str, deal_context: str = "") -> str:
        self._require_client()

        prompt = (
            f"Seller objection: \"{objection}\"\n"
            f"Deal context: {deal_context or 'wholesale deal, cash close, as-is'}\n\n"
            f"Generate a thoughtful response that:\n"
            f"1. Acknowledges their concern genuinely\n"
            f"2. Reframes the objection\n"
            f"3. Moves the conversation forward\n"
            f"4. Does NOT sound scripted or pushy\n\n"
            f"Also assess: Is this a real objection or a stall? How motivated is this seller?"
        )

        resp = self.client.messages.create(
            model=MODEL, max_tokens=800,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text

    # ── Walk-away assessment ──────────────────────────────────────────────

    def should_walk(
        self,
        asking: float,
        mao: float,
        conversations: int = 1,
        seller_motivation: str = "unknown",
    ) -> dict:
        self._require_client()

        gap_pct = ((asking - mao) / mao * 100) if mao > 0 else 100

        prompt = (
            f"Should I walk away from this deal?\n\n"
            f"Seller asking: ${asking:,.0f}\n"
            f"My MAO: ${mao:,.0f}\n"
            f"Gap: ${asking - mao:,.0f} ({gap_pct:.0f}% above MAO)\n"
            f"Conversations so far: {conversations}\n"
            f"Seller motivation level: {seller_motivation}\n\n"
            f"Reason through: time cost, probability of acceptance, "
            f"opportunity cost of chasing this vs finding a new deal.\n"
            f"Respond with:\n"
            f"DECISION: [WALK / STAY / ONE MORE TRY]\n"
            f"REASONING: [2-3 sentences]\n"
            f"IF STAYING: [What specifically to say or offer next]"
        )

        resp = self.client.messages.create(
            model=MODEL, max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text
        m = re.search(r"DECISION:\s*(\w[\w\s]*)", text)
        decision = m.group(1).strip() if m else "STAY"
        return {"decision": decision, "full_analysis": text}

    # ── Self-improvement ──────────────────────────────────────────────────

    def learn(self, closed_deals: list):
        if not self.client or len(closed_deals) < 3:
            return
        won  = [d for d in closed_deals if d.get("outcome") == "won"]
        lost = [d for d in closed_deals if d.get("outcome") == "lost"]

        prompt = (
            f"Analyze {len(won)} won and {len(lost)} lost negotiations.\n"
            f"Won: {str([(d.get('seller_situation'), d.get('what_worked')) for d in won[:8]])}\n"
            f"Lost: {str([(d.get('seller_situation'), d.get('what_failed')) for d in lost[:8]])}\n\n"
            f"What negotiation patterns lead to accepted offers? "
            f"What objections killed deals? "
            f"Respond with JSON: {{best_opener, best_close_rate_condition, "
            f"avoid_tactics: [], winning_scripts: [], insights: []}}"
        )

        try:
            resp = self.client.messages.create(
                model=MODEL, max_tokens=800,
                messages=[{"role": "user", "content": prompt}],
            )
            import json
            m = re.search(r'\{.*\}', resp.content[0].text, re.DOTALL)
            if m:
                new = json.loads(m.group())
                current = load_patterns(self.name)
                current.update(new)
                save_patterns(self.name, current)
                log_activity(self.name, "learned", f"Updated from {len(closed_deals)} deals")
        except Exception:
            pass
