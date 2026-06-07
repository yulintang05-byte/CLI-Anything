"""
Agent Runner — Orchestrates all 4 agents.
Runs the full pipeline: Find → Analyze → Negotiate → Close.
Can run proactively on a schedule or on-demand.
Goal: $10k-$30k/month with minimal human input.

Human only needs to: review top leads, approve offers, sign contracts.
"""
import os
import time
import threading
from datetime import datetime
from typing import Optional

from agents.memory import (
    get_leads, get_stats, get_recent_activity,
    needs_learning, mark_learning_done, get_deal_outcomes,
    log_activity,
)
from agents.lead_agent        import LeadAgent
from agents.negotiation_agent import NegotiationAgent
from agents.closing_agent     import ClosingAgent
from modules.deal_browser     import all_strategies_analysis
from modules.user_profile     import load_profile


class AgentRunner:
    """
    Orchestrates the full wholesale pipeline.
    Each agent specializes, communicates through shared memory.
    """

    def __init__(self):
        self.profile     = load_profile()
        self.lead_agent  = LeadAgent(profile=self.profile)
        self.neg_agent   = NegotiationAgent(profile=self.profile)
        self.close_agent = ClosingAgent(profile=self.profile)
        self._running    = False
        self._thread     = None

    # ── Full pipeline run (on-demand) ─────────────────────────────────────

    def run_full_pipeline(
        self,
        markets: list = None,
        max_price: int = 80000,
        console=None,
    ) -> dict:
        """
        Run the complete pipeline once:
        1. Find leads (LeadAgent)
        2. Analyze top leads (deal analysis)
        3. Queue high-margin for offers (ClosingAgent)
        4. Trigger learning if needed
        """
        results = {
            "started_at": datetime.now().isoformat(),
            "steps": [],
        }

        def log(msg):
            results["steps"].append({"ts": datetime.now().isoformat(), "msg": msg})
            if console:
                console.print(f"  [dim]{msg}[/dim]")
            log_activity("Runner", "step", msg)

        # ── Step 1: Find leads ────────────────────────────────────────
        log("LeadAgent scanning sources...")
        try:
            lead_result = self.lead_agent.run(markets=markets, max_price=max_price)
            results["lead_result"] = lead_result
            log(f"Found {lead_result['new_leads']} leads, {lead_result['high_margin']} HIGH MARGIN")
        except Exception as e:
            log(f"LeadAgent error: {e}")
            lead_result = {"new_leads": 0, "high_margin": 0, "top_leads": []}
            results["lead_result"] = lead_result

        # ── Step 2: Analyze top leads ─────────────────────────────────
        top_leads = lead_result.get("top_leads", [])
        analyzed  = []

        for lead in top_leads[:5]:
            price = lead.get("price", 0)
            if price <= 0:
                continue
            try:
                # LeadAgent._enrich_lead already ran all_strategies_analysis on
                # priced leads. Reuse it so we don't double-compute with a
                # divergent ARV formula (the two used to disagree, drifting the
                # high_margin flag). Only compute here if the lead wasn't enriched.
                data = lead.get("analysis")
                if not data:
                    data = all_strategies_analysis(
                        price=price, arv=lead.get("arv_est") or price * 6,
                        market_rent=lead.get("rent_est") or 950,
                        state=lead.get("state", "MI"), condition="medium",
                        sqft=lead.get("sqft", 1000),
                        buyer_credit_score=self.profile.get("credit_score", 730),
                        buyer_cash=self.profile.get("available_cash", 12000),
                    )
                lead["full_analysis"] = data
                lead["status"]        = "analyzed"
                analyzed.append(lead)
                log(f"Analyzed: {lead.get('title','')[:50]} → {data.get('best_strategy','?')}")
            except Exception:
                pass

        results["analyzed_leads"] = analyzed

        # ── Step 3: Flag for human review ────────────────────────────
        high_margin_ready = [
            l for l in analyzed
            if l.get("full_analysis", {}).get("high_margin", False)
        ]
        results["ready_for_review"] = high_margin_ready
        log(f"{len(high_margin_ready)} deals ready for your review and offer")

        # ── Step 4: Self-improvement check ───────────────────────────
        if needs_learning():
            log("Running self-improvement analysis...")
            try:
                deals = get_deal_outcomes()
                self.lead_agent.learn(deals)
                self.neg_agent.learn(deals)
                self.close_agent.learn(deals)
                mark_learning_done()
                log("Agents updated from deal history")
            except Exception as e:
                log(f"Learning error (non-critical): {e}")

        results["completed_at"] = datetime.now().isoformat()
        results["stats"]        = get_stats()
        return results

    # ── Background scheduling ─────────────────────────────────────────────

    def start_background(self, interval_hours: int = 24, markets: list = None):
        """
        Start agents running in background every N hours.
        Agents proactively find and score leads without being asked.
        """
        if self._running:
            return "Already running"

        # Guard against interval_hours <= 0 — range(0*60) is empty, which would
        # spin run_full_pipeline() with no sleep and run away with API spend.
        interval_hours = max(1, int(interval_hours))

        self._running = True

        def _loop():
            while self._running:
                try:
                    log_activity("Runner", "scheduled_run", f"Interval: {interval_hours}h")
                    self.run_full_pipeline(markets=markets)
                except Exception as e:
                    log_activity("Runner", "scheduled_error", str(e))
                # Sleep in 60-second chunks so we can stop cleanly
                for _ in range(interval_hours * 60):
                    if not self._running:
                        break
                    time.sleep(60)

        self._thread = threading.Thread(target=_loop, daemon=True, name="AgentRunner")
        self._thread.start()
        log_activity("Runner", "background_started", f"Every {interval_hours} hours")
        return f"Agents running every {interval_hours} hours in background"

    def stop_background(self):
        self._running = False
        log_activity("Runner", "background_stopped")
        return "Background agents stopped"

    def is_running(self) -> bool:
        return self._running and (self._thread is not None) and self._thread.is_alive()

    # ── Negotiation pipeline ──────────────────────────────────────────────

    def run_negotiation(
        self,
        address: str,
        seller_name: str,
        asking_price: float,
        mao: float,
        seller_situation: str = "",
    ) -> dict:
        """Full negotiation run — script + counter + walk-away assessment."""
        profile = self.profile

        target = mao * 0.88  # Open 12% below MAO

        script   = self.neg_agent.generate_opening_script(
            seller_name=seller_name,
            address=address,
            asking_price=asking_price,
            your_target=target,
            seller_situation=seller_situation,
        )

        walk_rec = self.neg_agent.should_walk(
            asking=asking_price, mao=mao,
            seller_motivation=seller_situation,
        )

        return {
            "opening_script":  script,
            "your_target":     round(target, 0),
            "mao":             mao,
            "walk_assessment": walk_rec,
        }

    # ── Closing pipeline ──────────────────────────────────────────────────

    def prepare_close(
        self,
        deal: dict,
        contract_type: str = None,
        include_offer_packet: bool = True,
    ) -> dict:
        """
        Auto-select contract, generate it, and (optionally) an AI offer packet.
        Returns everything ready for human signature.

        The contract itself is a free template. The offer packet is a live
        Claude call, so pass include_offer_packet=False when the caller only
        needs the contract (saves an Opus call / API spend).
        """
        if not contract_type:
            contract_type = self.close_agent.select_contract_type(deal)

        contract = self.close_agent.generate_contract(
            contract_type=contract_type,
            buyer_name=self.profile.get("purchasing_entity") or self.profile.get("name", "Buyer"),
            seller_name=deal.get("seller_name", "[SELLER NAME]"),
            address=deal.get("address", "[ADDRESS]"),
            purchase_price=deal.get("price", 0),
            emd=self.profile.get("emd_amount", 1000),
            closing_days=self.profile.get("closing_days", 21),
            assignment_fee=deal.get("wholesale_fee", 10000),
            inspection_days=14,
        )

        offer_packet = None
        if include_offer_packet:
            offer_packet = self.close_agent.generate_offer_packet(deal, self.profile)

        return {
            "contract_type":  contract_type,
            "contract":       contract,
            "offer_packet":   offer_packet,
            "ready_to_sign":  True,
            "warnings":       contract.get("warnings", []),
        }

    # ── Status dashboard ──────────────────────────────────────────────────

    def dashboard(self) -> dict:
        stats    = get_stats()
        activity = get_recent_activity(10)
        new_leads = get_leads(status="new", min_score=7)[:5]
        high_margin = [l for l in get_leads(min_score=8) if l.get("high_margin")][:3]

        return {
            "running":       self.is_running(),
            "stats":         stats,
            "recent":        activity,
            "new_leads":     new_leads,
            "high_margin":   high_margin,
            "learned_patterns": {
                "lead":     self.lead_agent.patterns,
                "neg":      self.neg_agent.patterns,
                "closing":  self.close_agent.patterns,
            },
        }
