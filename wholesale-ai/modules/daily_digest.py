"""
Daily Deal Digest — Morning automated scan summary.

Reads from the agent memory (deals scored/found) and
produces a clean morning briefing: what the agents found overnight,
which deals are hot, what you need to do today.

Run at startup or on demand. No extra API calls — reads local state.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from agents.memory import get_stats, get_leads, get_deal_outcomes


DIGEST_DIR  = Path.home() / ".wholesale-ai"
DIGEST_FILE = DIGEST_DIR / "digests.json"


def _load_digests() -> list:
    DIGEST_DIR.mkdir(exist_ok=True)
    if not DIGEST_FILE.exists():
        return []
    try:
        return json.loads(DIGEST_FILE.read_text())
    except Exception:
        return []


def _save_digest(digest: dict):
    digests = _load_digests()
    digests.append(digest)
    # Keep last 30 days only
    digests = digests[-30:]
    DIGEST_FILE.write_text(json.dumps(digests, indent=2))


def generate_morning_digest(markets: list = None) -> dict:
    """
    Compile the morning briefing from local agent memory.
    Returns structured digest with action items.
    """
    stats   = get_stats()
    leads   = get_leads()

    # Pull recent leads from memory
    yesterday  = datetime.now() - timedelta(days=1)
    new_leads  = []
    for lead in leads:
        try:
            ts = datetime.fromisoformat(lead.get("last_seen", "2000-01-01"))
            if ts >= yesterday:
                new_leads.append(lead)
        except Exception:
            pass

    high_margin = [l for l in new_leads if l.get("high_margin") or l.get("score", 0) >= 8.0]
    hot_deals   = sorted(new_leads, key=lambda x: x.get("score", 0), reverse=True)[:5]

    # Pipeline status from pipeline.json
    pipeline_file = DIGEST_DIR / "pipeline.json"
    pipeline_deals = []
    if pipeline_file.exists():
        try:
            pipeline_deals = json.loads(pipeline_file.read_text())
        except Exception:
            pass

    active_pipeline  = [d for d in pipeline_deals if d.get("stage") not in ("Closed", "Dead")]
    under_contract   = [d for d in pipeline_deals if d.get("stage") == "Under Contract"]
    offer_out        = [d for d in pipeline_deals if d.get("stage") == "Offer Sent"]
    marketing        = [d for d in pipeline_deals if d.get("stage") == "Marketing"]

    # Build action items
    action_items = []
    if high_margin:
        action_items.append(f"⭐ Review {len(high_margin)} HIGH MARGIN deal(s) — run the deal card (option 3)")
    if under_contract:
        action_items.append(f"📝 {len(under_contract)} deal(s) Under Contract — follow up on inspection / closing")
    if offer_out:
        action_items.append(f"📞 {len(offer_out)} offer(s) sent — follow up if no response in 48 hours")
    if marketing:
        action_items.append(f"🔍 {len(marketing)} deal(s) being marketed — push to buyer list")
    if not new_leads:
        action_items.append("🔎 Run agents (option 26) to find today's deals")
    if stats.get("won", 0) == 0:
        action_items.append("💡 No closed deals yet — focus on locking up one contract this week")

    # Motivation
    earned   = stats.get("total_earned", 0)
    target   = 15000
    to_go    = max(0, target - earned)
    goal_pct = min(100, round(earned / target * 100)) if target > 0 else 0

    digest = {
        "date":            datetime.now().strftime("%A, %B %d %Y"),
        "generated_at":    datetime.now().isoformat(),
        "markets_scanned": markets or [],
        "new_leads_24h":   len(new_leads),
        "high_margin_24h": len(high_margin),
        "hot_deals":       hot_deals,
        "pipeline": {
            "active":         len(active_pipeline),
            "under_contract": len(under_contract),
            "offer_sent":     len(offer_out),
            "marketing":      len(marketing),
        },
        "stats": {
            "total_earned":  earned,
            "target":        target,
            "to_go":         to_go,
            "goal_pct":      goal_pct,
            "deals_won":     stats.get("won", 0),
            "close_rate":    stats.get("close_rate", 0),
            "avg_fee":       stats.get("avg_fee", 0),
        },
        "action_items": action_items,
    }

    _save_digest(digest)
    return digest


def get_last_digest() -> Optional[dict]:
    digests = _load_digests()
    return digests[-1] if digests else None


def get_pipeline_health() -> dict:
    """Quick pipeline health check — what stage has the most deals, what's stale."""
    pipeline_file = DIGEST_DIR / "pipeline.json"
    if not pipeline_file.exists():
        return {"total": 0, "stale": [], "urgent": []}

    try:
        deals = json.loads(pipeline_file.read_text())
    except Exception:
        return {"total": 0, "stale": [], "urgent": []}

    now   = datetime.now()
    stale = []
    urgent = []

    for d in deals:
        if d.get("stage") in ("Closed", "Dead"):
            continue
        try:
            updated = datetime.fromisoformat(d.get("updated_at", now.isoformat()))
            days_idle = (now - updated).days
            if days_idle >= 14:
                stale.append({"id": d.get("id"), "address": d.get("address",""), "days_idle": days_idle, "stage": d.get("stage","")})
            if d.get("stage") == "Under Contract":
                urgent.append({"id": d.get("id"), "address": d.get("address",""), "stage": "Under Contract — CHECK DEADLINE"})
        except Exception:
            pass

    return {
        "total":  len([d for d in deals if d.get("stage") not in ("Closed", "Dead")]),
        "stale":  sorted(stale, key=lambda x: x["days_idle"], reverse=True),
        "urgent": urgent,
    }
