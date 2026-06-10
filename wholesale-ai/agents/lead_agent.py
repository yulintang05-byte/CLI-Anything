"""
Lead Agent — "The Hunter"
Proactively finds distressed properties every day.
Scores every lead, flags HIGH MARGIN deals, queues them for DealAgent.
Gets smarter as it learns which sources and distress signals actually close.
"""
import os
import re
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
from modules import rentcast
from modules.deal_browser import all_strategies_analysis, HOT_MARKETS

# Deep-reasoning model for self-improvement / pattern learning (Opus)
MODEL = "claude-opus-4-8"
# Fast triage model for high-frequency lead scoring — ~15× cheaper than Opus
# Override with env var WHOLESALE_AI_SCORING_MODEL if you want Opus quality here
SCORING_MODEL = os.getenv("WHOLESALE_AI_SCORING_MODEL", "claude-haiku-4-5-20251001")

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

# Text that betrays a vacant lot / land parcel in any lead, regardless of
# which source it came from. Backstop for the RentCast source-level filter.
_LAND_TEXT_FLAGS = [
    "vacant lot", "vacant land", "infill", "buildable lot", "build your",
    "land bank", "dlba", "side lot", "lots totaling", "sold as a bundle",
    "new construction loan", "construction plans",
]
_LAND_TYPE_FLAGS = ("land", "lot", "vacant")

# Text that identifies a DLBA-owned house (real structure, but deed bars
# assignment). Backstop for the RentCast source-level is_link_only flag —
# catches any DLBA house that reaches enrichment from a non-RentCast source.
_DLBA_TEXT_FLAGS = [
    "detroit land bank", "building detroit", "own it now",
    "dlba", "land bank authority", "buildingdetroit",
]

# Addresses confirmed (via manual web verification) to be DLBA-owned even
# though the listing feed carries no DLBA markers. RentCast syndicates these
# with a normal agent name, so text/agent detection can't catch them.
# Extend via ~/.wholesale-ai/blocklist.json — one address substring per entry.
_KNOWN_DLBA_ADDRESSES = [
    "3240 glynn ct",
    "3758 rochester st",
]

_BLOCKLIST_FILE = os.path.join(
    os.path.expanduser("~"), ".wholesale-ai", "blocklist.json"
)


def _address_blocklist() -> list:
    """Built-in known-DLBA addresses + user-extendable blocklist file."""
    entries = list(_KNOWN_DLBA_ADDRESSES)
    try:
        import json
        with open(_BLOCKLIST_FILE) as f:
            entries += [str(a).lower() for a in json.load(f)]
    except Exception:
        pass
    return entries


def _looks_like_land(lead: dict) -> bool:
    """True if a lead is a vacant lot / land parcel rather than a structure."""
    ptype = str(lead.get("property_type", "")).strip().lower()
    if ptype and any(f in ptype for f in _LAND_TYPE_FLAGS):
        return True

    blob = " ".join(str(lead.get(f, "")) for f in
                    ("title", "description", "raw_text")).lower()
    if any(flag in blob for flag in _LAND_TEXT_FLAGS):
        return True

    # No structure signature: zero beds AND baths AND sqft.
    beds = lead.get("bedrooms") or 0
    baths = lead.get("bathrooms") or 0
    sqft = lead.get("sqft") or 0
    if beds == 0 and baths == 0 and sqft == 0 and lead.get("source", "").startswith("RentCast"):
        return True

    return False


def _is_dlba_house(lead: dict) -> bool:
    """True if this real house is owned/sold by the Detroit Land Bank Authority."""
    if lead.get("is_link_only") and "dlba" in str(lead.get("data_warning", "")).lower():
        return True  # already flagged upstream by rentcast module
    # Hard blocklist: addresses verified DLBA-owned but listed without markers
    addr = str(lead.get("title", "")).lower()
    if any(blocked in addr for blocked in _address_blocklist()):
        return True
    blob = " ".join(str(lead.get(f, "")) for f in
                    ("title", "description", "raw_text", "source")).lower()
    return any(flag in blob for flag in _DLBA_TEXT_FLAGS)


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

        # ── Source 0: RentCast LIVE listings (the real feed) ──────────
        # When a RENTCAST_API_KEY is set, this returns actual for-sale
        # houses with real prices, beds/baths, sqft, and days-on-market.
        # This is the source that lets Alberto "only sign."
        if rentcast.has_api_key():
            for market_str in markets:
                parts = market_str.split()
                if not parts:
                    continue
                city  = " ".join(parts[:-1]) if len(parts) > 1 else parts[0]
                state = parts[-1] if len(parts) > 1 else ""
                live = rentcast.search_sale_listings(
                    city=city, state=state, max_price=max_price, limit=50,
                )
                all_raw.extend(live)
            log_activity(self.name, "rentcast_pull", f"{len(all_raw)} live listings")

        # ── Source 1: Craigslist FSBO ─────────────────────────────────
        for market_str in markets:
            parts = market_str.split()
            if not parts:                      # empty / whitespace-only entry
                continue
            city = parts[0]
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
                min_score     = self.patterns.get("min_lead_score", 6.0)
                raw["status"] = "new" if raw["score"] >= min_score else "low_score"

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

        # Backstop: if a vacant lot / land parcel slipped past the source
        # filter (e.g. from a non-RentCast feed), refuse to analyze it. There's
        # no structure to flip or rent — any ARV/rent would be fabricated.
        if _looks_like_land(lead):
            lead["status"]       = "skip_land"
            lead["data_warning"] = "Vacant land / lot — no structure to rehab or rent"
            lead["high_margin"]  = False
            lead["score"]        = 0
            return lead

        # Backstop: DLBA-owned houses have real structures but their deeds bar
        # assignment. Surface as research link, never as a wholesale deal.
        if _is_dlba_house(lead):
            lead["status"]       = "link_only"
            lead["is_link_only"] = True
            lead["data_warning"] = (
                "Detroit Land Bank (DLBA) — buy direct at buildingdetroit.org. "
                "Deed bars assignment; not wholesaleable."
            )
            lead["high_margin"]  = False
            lead["score"]        = 0
            return lead

        # Sub-$30k Detroit listings are overwhelmingly DLBA inventory that
        # RentCast syndicates WITHOUT any DLBA markers (verified twice:
        # 3240 Glynn Ct, 3758 Rochester St). Don't block — but force a
        # verification warning so no outreach fires before a human/web check.
        city_l = str(lead.get("city", "")).lower()
        if "detroit" in city_l and 0 < price < 30000 and not lead.get("data_warning"):
            lead["data_warning"] = (
                "Sub-$30k Detroit listing — HIGH DLBA RISK. Verify owner is not "
                "Detroit Land Bank at buildingdetroit.org BEFORE any outreach."
            )

        # Estimate ARV from hot market data
        city  = lead.get("city", "Detroit")
        state = lead.get("state", "MI")
        arv_mult = self.patterns.get("min_arv_multiple", 6.0)

        # Prefer REAL RentCast AVM data over any estimate.
        if rentcast.has_api_key() and lead.get("source", "").startswith("RentCast"):
            lead = rentcast.enrich_with_avm(lead)

        if lead.get("arv_real"):
            arv = lead["arv_real"]
        else:
            hot_market = next((m for m in HOT_MARKETS if m["city"].lower() == city.lower()), None)
            arv = hot_market["avg_price"] * 8 if hot_market else price * arv_mult

        if lead.get("rent_real"):
            rent = lead["rent_real"]
        else:
            hot_market = next((m for m in HOT_MARKETS if m["city"].lower() == city.lower()), None)
            rent = hot_market["avg_rent"] if hot_market else 950

        # Sanity-check the AVM rent against ARV. A gross yield above ~25% is not
        # a real Detroit rental — it's a broken estimate (almost always a lot
        # valued as a house). Discard the bad rent, fall back to market rent,
        # and tag the lead so it can never be marked HIGH MARGIN on bad data.
        if arv and rent and (rent * 12 / arv) > rentcast.MAX_REALISTIC_GROSS_YIELD:
            hot_market = next((m for m in HOT_MARKETS if m["city"].lower() == city.lower()), None)
            fallback_rent = hot_market["avg_rent"] if hot_market else 950
            lead["data_warning"] = (
                f"AVM rent ${rent:,.0f}/mo implied a {rent*12/arv*100:.0f}% yield on "
                f"${arv:,.0f} ARV — unrealistic. Reverted to market rent ${fallback_rent:,.0f}. "
                f"Verify rent before offering."
            )
            lead.pop("rent_real", None)
            rent = fallback_rent

        # ARV sanity: an AVM ARV more than 5× the asking price is almost always
        # the ZIP-wide median bleeding into a rough sub-neighborhood (verified:
        # 4317 11th Ave N — AVM said $202k, Kingston's actual median is $73k).
        # Don't block, but force comp verification before anyone quotes it.
        if price > 0 and arv / price > 5 and not lead.get("data_warning"):
            lead["data_warning"] = (
                f"AVM ARV ${arv:,.0f} is {arv/price:.1f}× the ${price:,.0f} ask — "
                f"likely ZIP-median bleed into a cheaper micro-neighborhood. "
                f"Run comps (option 35) before quoting ARV to anyone."
            )

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

        except Exception as e:
            # Don't crash the whole run on one bad lead, but leave a trail so a
            # real analysis bug isn't silently swallowed.
            log_activity(self.name, "enrich_failed", f"{lead.get('title','?')}: {e}")

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
                model=SCORING_MODEL,
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
                m = re.search(rf"Lead {i}:\s*([\d.]+)/10[^\n]*?[—-]\s*([^\n]+)", text)
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
