"""
Deal Pipeline / CRM — save, track, and manage deals through stages.
Stored locally in ~/.wholesale-ai/pipeline.json (no cloud needed).
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


PIPELINE_DIR = Path.home() / ".wholesale-ai"
PIPELINE_FILE = PIPELINE_DIR / "pipeline.json"

STAGES = [
    "Lead",           # Found property, not yet analyzed
    "Analyzing",      # Running numbers
    "Offer Sent",     # LOI / offer submitted to seller
    "Under Contract", # Seller accepted, in inspection period
    "Marketing",      # Actively marketing to cash buyers
    "Closed",         # Deal done, assignment fee collected
    "Dead",           # Deal fell apart
]

STAGE_COLORS = {
    "Lead":           "dim white",
    "Analyzing":      "yellow",
    "Offer Sent":     "cyan",
    "Under Contract": "blue",
    "Marketing":      "magenta",
    "Closed":         "bold green",
    "Dead":           "red",
}


def _load() -> list:
    PIPELINE_DIR.mkdir(exist_ok=True)
    if not PIPELINE_FILE.exists():
        return []
    try:
        return json.loads(PIPELINE_FILE.read_text())
    except Exception:
        return []


def _save(deals: list):
    PIPELINE_DIR.mkdir(exist_ok=True)
    PIPELINE_FILE.write_text(json.dumps(deals, indent=2))


def add_deal(
    address: str,
    asking_price: float = 0,
    arv: float = 0,
    repairs: float = 0,
    mao: float = 0,
    wholesale_fee: float = 10000,
    source: str = "",
    notes: str = "",
    stage: str = "Lead",
) -> dict:
    """Add a new deal to the pipeline."""
    deals = _load()
    deal = {
        "id": str(uuid.uuid4())[:8],
        "address": address,
        "asking_price": asking_price,
        "arv": arv,
        "repairs": repairs,
        "mao": mao,
        "wholesale_fee": wholesale_fee,
        "source": source,
        "notes": notes,
        "stage": stage,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "history": [{"stage": stage, "date": datetime.now().isoformat(), "note": "Deal added"}],
    }
    deals.append(deal)
    _save(deals)
    return deal


def get_all_deals(stage_filter: Optional[str] = None) -> list:
    """Get all deals, optionally filtered by stage."""
    deals = _load()
    if stage_filter:
        deals = [d for d in deals if d.get("stage", "").lower() == stage_filter.lower()]
    return sorted(deals, key=lambda d: d.get("updated_at", ""), reverse=True)


def get_deal(deal_id: str) -> Optional[dict]:
    """Get a single deal by ID."""
    for deal in _load():
        if deal.get("id") == deal_id:
            return deal
    return None


def update_deal(deal_id: str, **kwargs) -> Optional[dict]:
    """Update fields on a deal."""
    deals = _load()
    for i, deal in enumerate(deals):
        if deal.get("id") == deal_id:
            old_stage = deal.get("stage")
            deals[i].update(kwargs)
            deals[i]["updated_at"] = datetime.now().isoformat()
            # Log stage changes
            if "stage" in kwargs and kwargs["stage"] != old_stage:
                history = deals[i].get("history", [])
                history.append({
                    "stage": kwargs["stage"],
                    "date": datetime.now().isoformat(),
                    "note": kwargs.get("notes", f"Moved from {old_stage}"),
                })
                deals[i]["history"] = history
            _save(deals)
            return deals[i]
    return None


def advance_stage(deal_id: str, note: str = "") -> Optional[dict]:
    """Move deal to next stage."""
    deal = get_deal(deal_id)
    if not deal:
        return None
    current = deal.get("stage", "Lead")
    if current in STAGES:
        idx = STAGES.index(current)
        if idx < len(STAGES) - 1:
            next_stage = STAGES[idx + 1]
            return update_deal(deal_id, stage=next_stage, notes=note or f"Advanced to {next_stage}")
    return deal


def delete_deal(deal_id: str) -> bool:
    """Remove a deal from the pipeline."""
    deals = _load()
    original_len = len(deals)
    deals = [d for d in deals if d.get("id") != deal_id]
    if len(deals) < original_len:
        _save(deals)
        return True
    return False


def pipeline_summary() -> dict:
    """Get stage counts and totals."""
    deals = _load()
    summary = {stage: 0 for stage in STAGES}
    total_potential = 0
    closed_fees = 0

    for deal in deals:
        stage = deal.get("stage", "Lead")
        if stage in summary:
            summary[stage] += 1
        fee = deal.get("wholesale_fee", 0)
        if stage not in ("Dead",):
            total_potential += fee
        if stage == "Closed":
            closed_fees += fee

    return {
        "by_stage": summary,
        "total_deals": len(deals),
        "total_potential_fees": total_potential,
        "closed_fees": closed_fees,
        "active_deals": len([d for d in deals if d.get("stage") not in ("Closed", "Dead")]),
    }
