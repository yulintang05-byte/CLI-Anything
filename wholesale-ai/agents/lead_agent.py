"""
Lead Agent — "The Hunter"
Proactively finds distressed properties every day.
Scores every lead, flags HIGH MARGIN deals, queues them for DealAgent.
Gets smarter as it learns which sources and distress signals actually close.
"""
import os
from datetime import datetime
from typing import Optional

import anthropic

from agents.memory import (
    save_lead, get_leads, update_lead, load_patterns,
    save_patterns, log_activity, needs_learning,
)
from modules.web_scraper import (
    scrape_craigslist_fsbo, get_dlba_listings,
    get_tax_deed_listings, get_hud_listings_url,
    score_raw_lead, CRAIGSLIST_CITIES,
)
from modules.deal_browser import all_strategies_analysis, HOT_MARKETS

MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = """You are the Lead Agent for a real estate wholesale operation.
Your ONLY job is to find and score potential deals.

You think critically about every lead:
- Is the price genuinely below market, or is it priced low due to serious defects?
- What distress signals suggest a motivated seller?
- Which strategy (flip, BRRRR, wholesale, Section 8) fits best?
- What's the realistic ARV based on the market?

You are PROACTIVE — you don't wait to be asked. You scan sources daily,
flag high-margin opportunities, and queue them for the deal analyst.

Be skeptical. A $5,000 house that needs $80,000 in repairs is NOT a deal.
A $5,000 house that needs $20,000 and can rent for $950/mo IS a deal.

Score leads 1-10. Only queue scores 7+.
"""


class LeadAgent:
    def __init__(self, profile: Optional[dict] = None):
        self.name     = "LeadAgent"
        self.profile  = profile or {}
        self.patterns = load_patterns(self.name)
        self.client   = None
        self._init_client()

    def _init_client(self):
        key = os.getenv("ANTHROPIC_API_KEY")
        if key:
            self.client = anthropic.Anthropic(api_key=key)

    # ── Main proactive run ────────────────────────────────────────────────

    def run(self, markets: list = None, max_price: int = 80000) -> dict:
        """
        Full lead generation cycle. Call this daily.
        Returns summary dict with counts and top leads.
        """
        markets = markets or self.patterns.get("best_markets", ["Detroit MI", "Birmingham AL", "Memphis TN"])
        log_activity(self.name, "run_start", f"Markets: {markets}")

        all_raw  = []
        new_leads = 0
        high_margin = 0

        # ── Source 1: Craigslist FSBO ─────────────────────────────────
        for market_str in markets:
            city = market_str.split()[0]
            if city in CRAIGSLIST_CITIES:
                raw = scrape_craigslist_fsbo(city=city, max_price=max_price)
                all_raw.extend(raw)

        # ── Source 2: Detroit DLBA ────────────────────────────────────
        all_raw.extend(get_dlba_listings())

        # ── Source 3: Tax deed links ──────────────────────────────────
        for market_str in markets:
            state = market_str.split()[-1] if len(market_str.split()) > 1 else "MI"
            all_raw.extend(get_tax_deed_listings(state=state))

        # ── Source 4: HUD HomeStore links ─────────────────────────────
        for market_str in markets:
            state = market_str.split()[-1] if len(market_str.split()) > 1 else "MI"
            hud = get_hud_listings_url(state=state, max_price=max_price)
            all_raw.append({
                "title": hud["desc"], "url": hud["url"],
                "price": 0, "source": "HUD HomeStore",
                "state": state, "city": "",
            })

        # ── Score and save each raw lead ──────────────────────────────
        for raw in all_raw:
            if raw.get("is_link_only"):
                # Save as a research link, not a scored lead
                raw["status"] = "link_only"
                raw["score"]  = 0
            else:
                raw["score"]  = score_raw_lead(raw)
                raw["status"] = "new" if raw["score"] >= self.patterns["min_lead_score"] else "low_score"

            # Run full strategy analysis on priced leads
            if raw.get("price", 0) > 0 and raw.get("score", 0) >= 6:
                raw = self._enrich_lead(raw)
                if raw.get("high_margin"):
                    high_margin += 1

            lead_id = save_lead(raw)
            raw["id"] = lead_id
            new_leads += 1

        # ── AI-enhanced scoring of top leads ─────────────────────────
        top = sorted(
            [l for l in all_raw if l.get("score", 0) >= 7],
            key=lambda x: x.get("score", 0), reverse=True
        )[:5]

        if top and self.client:
            top = self._ai_score_batch(top)

        log_activity(self.name, "run_complete",
                     f"Found {new_leads} leads, {high_margin} HIGH MARGIN",
                     f"Top score: {top[0]['score'] if top else 0:.1f}")

        return {
            "total_raw":     len(all_raw),
            "new_leads":     new_leads,
            "high_margin":   high_margin,
            "top_leads":     top[:5],
            "queued_for_analysis": len([l for l in all_raw if l.get("score", 0) >= 7]),
        }

    # ── Lead enrichment ───────────────────────────────────────────────────

    def _enrich_lead(self, lead: dict) -> dict:
        """Run all_strategies_analysis on a priced lead."""
        price = lead.get("price", 0)
        if price <= 0:
            return lead

        # Estimate ARV from hot market data
        city  = lead.get("city", "Detroit")
        state = lead.get("state", "MI")
        arv_mult = self.patterns.get("min_arv_multiple", 6.0)

        hot_market = next((m for m in HOT_MARKETS if m["city"].lower() == city.lower()), None)
        if hot_market:
            arv  = hot_market["avg_price"] * 8
            rent = hot_market["avg_rent"]
        else:
            arv  = price * arv_mult
            rent = 950

        try:
            credit = self.profile.get("credit_score", 730)
            cash   = self.profile.get("available_cash", 12000)
            analysis = all_strategies_analysis(
                price=price, arv=arv, market_rent=rent,
                state=state, condition="medium",
                buyer_credit_score=credit, buyer_cash=cash,
            )
            lead["analysis"]      = analysis
            lead["arv_est"]       = arv
            lead["rent_est"]      = rent
            lead["high_margin"]   = analysis.get("high_margin", False)
            lead["best_strategy"] = analysis.get("best_strategy", "Wholesale")
            lead["flip_profit"]   = analysis.get("flip", {}).get("profit", 0)
            lead["brrrr_verdict"] = analysis.get("brrrr", {}).get("verdict", "")
            lead["dscr_ratio"]    = analysis.get("dscr", {}).get("ratio", 0)
            lead["sec8_cf"]       = analysis.get("section8", {}).get("monthly_cf", 0)

            # Boost score for high-margin deals
            if analysis.get("high_margin"):
                lead["score"] = min(10.0, lead["score"] + 2.0)

        except Exception:
            pass

        return lead

    # ── AI scoring ───────────────────────────────────────────────────────

    def _ai_score_batch(self, leads: list) -> list:
        """Use Claude to critically score and reason about top leads."""
        if not self.client:
            return leads

        prompt_lines = []
        for i, l in enumerate(leads, 1):
            prompt_lines.append(
                f"Lead {i}: {l.get('title','?')}\n"
                f"  Price: ${l.get('price',0):,} | City: {l.get('city','?')}, {l.get('state','?')}\n"
                f"  Source: {l.get('source','?')} | Distress signals: {l.get('distress_signals',[])}\n"
                f"  ARV est: ${l.get('arv_est',0):,} | Rent est: ${l.get('rent_est',0):,}/mo\n"
                f"  Best strategy: {l.get('best_strategy','?')} | Current score: {l.get('score',0):.1f}/10\n"
            )

        try:
            resp = self.client.messages.create(
                model=MODEL,
                max_tokens=1500,
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": (
                        "Critically evaluate these leads. For each, reason through: "
                        "Is this genuinely below market? What could go wrong? "
                        "Assign a final score 1-10 and ONE sentence of reasoning.\n\n"
                        + "\n".join(prompt_lines)
                        + "\n\nRespond in this exact format:\n"
                        "Lead 1: [score]/10 — [one sentence reasoning]\n"
                        "Lead 2: [score]/10 — [one sentence reasoning]\n..."
                    ),
                }],
            )
            text = resp.content[0].text
            for i, lead in enumerate(leads, 1):
                # Lazy match up to the dash, then capture the rest of the line as
                # reasoning. A greedy [^\n]* before (.+) would leave only 1 char.
                m = __import__("re").search(rf"Lead {i}:\s*([\d.]+)/10[^\n]*?[—-]\s*([^\n]+)", text)
                if m:
                    lead["ai_score"]     = float(m.group(1))
                    lead["ai_reasoning"] = m.group(2).strip()
                    lead["score"]        = max(lead["score"], lead["ai_score"])
        except Exception:
            pass

        return leads

    # ── Self-improvement ─────────────────────────────────────────────────

    def learn(self, closed_deals: list):
        """
        Analyze closed deal outcomes and update scoring patterns.
        Called automatically after 5 wins.
        """
        if not self.client or len(closed_deals) < 3:
            return

        won  = [d for d in closed_deals if d.get("outcome") == "won"]
        lost = [d for d in closed_deals if d.get("outcome") != "won"]

        prompt = (
            f"You are analyzing {len(closed_deals)} real estate wholesale deals "
            f"({len(won)} won, {len(lost)} lost) to improve future lead scoring.\n\n"
            f"WON DEALS:\n{json_summary(won[:10])}\n\n"
            f"LOST DEALS:\n{json_summary(lost[:10])}\n\n"
            "Identify patterns. What do the won deals have in common? "
            "What should the Lead Agent look for? "
            "Respond with a JSON object with these keys: "
            "best_markets (list), min_below_market (number), "
            "best_strategies (list), avoid_conditions (list), "
            "distress_signals_that_close (list), insights (list of strings)."
        )

        try:
            resp = self.client.messages.create(
                model=MODEL,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            import json, re
            m = re.search(r'\{.*\}', resp.content[0].text, re.DOTALL)
            if m:
                new_patterns = json.loads(m.group())
                current = load_patterns(self.name)
                current.update(new_patterns)
                current["deals_analyzed"] = len(closed_deals)
                save_patterns(self.name, current)
                log_activity(self.name, "learned", f"Updated patterns from {len(closed_deals)} deals")
        except Exception:
            pass


def json_summary(deals: list) -> str:
    import json
    safe = [{k: v for k, v in d.items() if k not in ("analysis",)} for d in deals]
    return json.dumps(safe, indent=2, default=str)[:3000]
