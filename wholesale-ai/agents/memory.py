"""
Agent Memory & Self-Improvement System.

Every deal outcome (win/loss) is recorded. After enough data,
Claude analyzes patterns and each agent updates its decision criteria.
Goal: agents that get measurably better with every deal closed.
"""
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

MEM_DIR = Path.home() / ".wholesale-ai" / "agents"
LEADS_FILE    = MEM_DIR / "leads.json"
DEALS_FILE    = MEM_DIR / "deals.json"
LEARNED_FILE  = MEM_DIR / "learned.json"
AGENT_LOG     = MEM_DIR / "agent_log.json"


def _ensure_dir():
    MEM_DIR.mkdir(parents=True, exist_ok=True)


def _read(path: Path, default) -> any:
    _ensure_dir()
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def _write(path: Path, data: any):
    _ensure_dir()
    path.write_text(json.dumps(data, indent=2, default=str))


# ── Lead Storage ─────────────────────────────────────────────────────────────

def save_lead(lead: dict) -> str:
    """Save a new lead. Returns lead_id."""
    leads = _read(LEADS_FILE, [])
    lead_id = f"L{int(time.time() * 1000) % 1000000:06d}"
    lead["id"]         = lead_id
    lead["created_at"] = datetime.now().isoformat()
    lead["status"]     = lead.get("status", "new")
    leads.append(lead)
    _write(LEADS_FILE, leads)
    return lead_id


def get_leads(status: str = None, min_score: float = 0) -> list:
    leads = _read(LEADS_FILE, [])
    if status:
        leads = [l for l in leads if l.get("status") == status]
    if min_score:
        leads = [l for l in leads if l.get("score", 0) >= min_score]
    return sorted(leads, key=lambda l: l.get("score", 0), reverse=True)


def update_lead(lead_id: str, **kwargs):
    leads = _read(LEADS_FILE, [])
    for lead in leads:
        if lead.get("id") == lead_id:
            lead.update(kwargs)
            lead["updated_at"] = datetime.now().isoformat()
    _write(LEADS_FILE, leads)


def count_leads(status: str = "new") -> int:
    return len([l for l in _read(LEADS_FILE, []) if l.get("status") == status])


# ── Deal Outcome Recording ────────────────────────────────────────────────────

def record_deal_outcome(deal: dict):
    """
    Record a completed deal for self-improvement analysis.
    deal should include: address, price, arv, strategy, outcome (won/lost/dead),
    fee_earned, days_to_close, market, condition, seller_situation,
    what_worked, what_failed.
    """
    deals = _read(DEALS_FILE, [])
    deal["recorded_at"] = datetime.now().isoformat()
    deals.append(deal)
    _write(DEALS_FILE, deals)
    _trigger_learning_if_ready(deals)


def get_deal_outcomes() -> list:
    return _read(DEALS_FILE, [])


def get_stats() -> dict:
    deals  = get_deal_outcomes()
    leads  = _read(LEADS_FILE, [])  # read once; derive all lead counts below
    won    = [d for d in deals if d.get("outcome") == "won"]
    total  = len(deals)
    earned = sum(d.get("fee_earned", 0) for d in won)
    avg_days = sum(d.get("days_to_close", 30) for d in won) / max(len(won), 1)
    active = len([l for l in leads if l.get("status") in ("new", "analyzing")])
    return {
        "total_deals":        total,
        "won":                len(won),
        "lost":               total - len(won),
        "close_rate":         round(len(won) / max(total, 1) * 100, 1),
        "total_earned":       earned,
        "avg_fee":            round(earned / max(len(won), 1), 0),
        "avg_days_to_close":  round(avg_days, 0),
        "active_leads":       active,
        "pipeline_leads":     len(leads),
    }


# ── Learned Patterns ─────────────────────────────────────────────────────────

def load_patterns(agent_name: str) -> dict:
    """
    Load this agent's learned patterns, merged onto the defaults so a saved
    dict that's missing a key (older file, partial learn() update, or a newly
    added default) never KeyErrors at the call site.
    """
    learned  = _read(LEARNED_FILE, {})
    patterns = _default_patterns(agent_name)
    saved    = learned.get(agent_name)
    if isinstance(saved, dict):
        patterns.update(saved)
    return patterns


def save_patterns(agent_name: str, patterns: dict):
    learned = _read(LEARNED_FILE, {})
    learned[agent_name] = patterns
    learned["last_updated"] = datetime.now().isoformat()
    _write(LEARNED_FILE, learned)


def _default_patterns(agent_name: str) -> dict:
    """Starting patterns before any learning has occurred."""
    base = {
        "min_lead_score":     6.0,
        "min_below_market":   40.0,
        "best_markets":       ["Detroit MI", "Birmingham AL", "Memphis TN"],
        "avoid_conditions":   ["gut"],
        "best_strategies":    ["BRRRR", "Flip", "Section 8"],
        "max_price":          80000,
        "min_arv_multiple":   4.0,
        "deals_analyzed":     0,
        "insights":           [],
    }
    if agent_name == "NegotiationAgent":
        base.update({
            "best_opener": "price_cut_request",
            "best_close_rate_condition": "motivated_seller",
            "avoid_tactics": [],
            "winning_scripts": [],
        })
    elif agent_name == "LeadAgent":
        base.update({
            "best_sources": ["Detroit DLBA", "Tax Deed", "Craigslist FSBO"],
            "distress_signals_that_close": ["estate sale", "motivated", "as-is"],
        })
    elif agent_name == "ClosingAgent":
        base.update({
            "fastest_close_strategy":  "Wholesale Assignment",
            "avg_contract_accept_days": 7,
            "best_emd_amount": 1000,
        })
    return base


# ── Self-Improvement Trigger ──────────────────────────────────────────────────

def _trigger_learning_if_ready(deals: list):
    """After every 5 won deals, trigger a learning analysis."""
    won = [d for d in deals if d.get("outcome") == "won"]
    if len(won) > 0 and len(won) % 5 == 0:
        _flag_for_learning()


def _flag_for_learning():
    flag = MEM_DIR / ".needs_learning"
    flag.touch()


def needs_learning() -> bool:
    flag = MEM_DIR / ".needs_learning"
    return flag.exists()


def mark_learning_done():
    flag = MEM_DIR / ".needs_learning"
    if flag.exists():
        flag.unlink()


# ── Agent Activity Log ────────────────────────────────────────────────────────

def log_activity(agent: str, action: str, detail: str = "", result: str = ""):
    log = _read(AGENT_LOG, [])
    log.append({
        "ts":     datetime.now().isoformat(),
        "agent":  agent,
        "action": action,
        "detail": detail,
        "result": result,
    })
    # Keep last 500 entries
    if len(log) > 500:
        log = log[-500:]
    _write(AGENT_LOG, log)


def get_recent_activity(n: int = 20) -> list:
    log = _read(AGENT_LOG, [])
    return log[-n:]
