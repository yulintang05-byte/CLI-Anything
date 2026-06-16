"""
Background Scheduler — runs the full agent pipeline on a daily or N-hour schedule.

Stores config in ~/.wholesale-ai/scheduler.json.
Writes scan results to ~/.wholesale-ai/last_scan.json after every run.
Can be started as a daemon thread from main.py — no external dependencies.
"""
import json
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


WHOLESALE_DIR = Path.home() / ".wholesale-ai"
SCHEDULER_CONFIG_FILE = WHOLESALE_DIR / "scheduler.json"
LAST_SCAN_FILE = WHOLESALE_DIR / "last_scan.json"

# ── Global thread state ───────────────────────────────────────────────────────

_scheduler_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()
_last_run: Optional[str] = None          # ISO timestamp of last completed run
_last_scan_summary: Optional[dict] = None


# ── Config dataclass ──────────────────────────────────────────────────────────

@dataclass
class SchedulerConfig:
    run_time: str = "06:00"               # "HH:MM" — used for daily mode
    interval_hours: Optional[int] = None  # If set, overrides run_time; run every N hours
    markets: list = field(default_factory=list)
    max_price: int = 80000
    enabled: bool = True


def _config_from_dict(d: dict) -> SchedulerConfig:
    return SchedulerConfig(
        run_time=d.get("run_time", "06:00"),
        interval_hours=d.get("interval_hours"),
        markets=d.get("markets", []),
        max_price=d.get("max_price", 80000),
        enabled=d.get("enabled", True),
    )


# ── Persistence ───────────────────────────────────────────────────────────────

def load_scheduler_config() -> SchedulerConfig:
    """Read ~/.wholesale-ai/scheduler.json; return defaults if missing."""
    WHOLESALE_DIR.mkdir(exist_ok=True)
    if not SCHEDULER_CONFIG_FILE.exists():
        return SchedulerConfig()
    try:
        data = json.loads(SCHEDULER_CONFIG_FILE.read_text())
        return _config_from_dict(data)
    except Exception:
        return SchedulerConfig()


def save_scheduler_config(config: SchedulerConfig) -> None:
    """Write config to ~/.wholesale-ai/scheduler.json."""
    WHOLESALE_DIR.mkdir(exist_ok=True)
    SCHEDULER_CONFIG_FILE.write_text(json.dumps(asdict(config), indent=2))


def _save_last_scan(summary: dict) -> None:
    """Persist scan result to ~/.wholesale-ai/last_scan.json."""
    WHOLESALE_DIR.mkdir(exist_ok=True)
    LAST_SCAN_FILE.write_text(json.dumps(summary, indent=2))


def _load_last_scan() -> Optional[dict]:
    if not LAST_SCAN_FILE.exists():
        return None
    try:
        return json.loads(LAST_SCAN_FILE.read_text())
    except Exception:
        return None


# ── Scheduling math ───────────────────────────────────────────────────────────

def get_next_run_time(config: SchedulerConfig) -> datetime:
    """
    Return the next datetime the scheduler should fire.

    Interval mode  (interval_hours is set): now + N hours.
    Daily mode (run_time like "06:00"):     next occurrence of that wall-clock time.
    """
    now = datetime.now()

    if config.interval_hours:
        hours = max(1, int(config.interval_hours))
        return now + timedelta(hours=hours)

    # Daily mode — parse "HH:MM"
    try:
        hh, mm = [int(x) for x in config.run_time.split(":")]
    except Exception:
        hh, mm = 6, 0

    candidate = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate


# ── Core scan ─────────────────────────────────────────────────────────────────

def _run_scan(markets: list, max_price: int) -> dict:
    """
    Lazily import AgentRunner, run the full pipeline, and return a summary dict.
    Importing here avoids circular-import issues at module load time.
    """
    # Lazy import — do NOT move to the top of this file.
    from agents.runner import AgentRunner  # noqa: PLC0415

    runner = AgentRunner()
    pipeline_result = runner.run_full_pipeline(markets=markets, max_price=max_price)

    lead_result = pipeline_result.get("lead_result", {})
    analyzed = pipeline_result.get("analyzed_leads", [])
    ready = pipeline_result.get("ready_for_review", [])

    hot_deals = []
    for lead in ready[:10]:
        hot_deals.append({
            "title":        lead.get("title", ""),
            "price":        lead.get("price", 0),
            "arv_est":      lead.get("arv_est", 0),
            "score":        lead.get("score", 0),
            "high_margin":  lead.get("high_margin", False),
            "url":          lead.get("url", ""),
            "market":       lead.get("market", ""),
        })

    summary = {
        "scanned_at":   datetime.now().isoformat(),
        "markets":      markets or [],
        "max_price":    max_price,
        "new_leads":    lead_result.get("new_leads", 0),
        "high_margin":  lead_result.get("high_margin", 0),
        "analyzed":     len(analyzed),
        "ready_for_review": len(ready),
        "hot_deals":    hot_deals,
        "pipeline_stats": pipeline_result.get("stats", {}),
    }
    return summary


# ── Digest helper ─────────────────────────────────────────────────────────────

def _save_morning_digest(summary: dict) -> None:
    """
    Append a digest entry to ~/.wholesale-ai/digests.json (reuses daily_digest format).
    Imported lazily to avoid issues if daily_digest has its own heavy imports.
    """
    try:
        from modules.daily_digest import generate_morning_digest  # noqa: PLC0415
        digest = generate_morning_digest(markets=summary.get("markets"))
        # Merge scheduler scan data into the digest so it's richer
        digest["scheduler_scan"] = {
            "new_leads":    summary.get("new_leads", 0),
            "high_margin":  summary.get("high_margin", 0),
            "hot_deals":    summary.get("hot_deals", []),
        }
    except Exception as e:
        # Daily digest is non-critical — last_scan.json is authoritative.
        print(f"  [scheduler] digest generation skipped: {e}")


# ── Background thread ─────────────────────────────────────────────────────────

def _scheduler_loop(config: SchedulerConfig) -> None:
    """
    Long-running background thread body.

    1. Calculate next_run.
    2. Sleep in 30-second ticks until next_run (or stop_event fires).
    3. Run the scan; write last_scan.json; save morning digest.
    4. For interval mode recalculate next_run as now + N hours.
       For daily mode recalculate as next occurrence of run_time.
    5. Repeat until _stop_event is set.
    """
    global _last_run, _last_scan_summary

    next_run = get_next_run_time(config)

    while not _stop_event.is_set():
        now = datetime.now()

        if now >= next_run:
            # ── Run the scan ──────────────────────────────────────────
            try:
                summary = _run_scan(config.markets, config.max_price)
            except Exception as exc:
                summary = {
                    "scanned_at":   datetime.now().isoformat(),
                    "error":        str(exc),
                    "new_leads":    0,
                    "high_margin":  0,
                    "hot_deals":    [],
                }

            _last_run = datetime.now().isoformat()
            _last_scan_summary = summary

            _save_last_scan(summary)
            _save_morning_digest(summary)

            # ── Compute next run ──────────────────────────────────────
            if config.interval_hours:
                hours = max(1, int(config.interval_hours))
                next_run = datetime.now() + timedelta(hours=hours)
            else:
                # Daily mode — schedule same wall-clock time tomorrow
                try:
                    hh, mm = [int(x) for x in config.run_time.split(":")]
                except Exception:
                    hh, mm = 6, 0
                next_run = (datetime.now() + timedelta(days=1)).replace(
                    hour=hh, minute=mm, second=0, microsecond=0
                )

        # Sleep in small ticks so stop_event is checked frequently
        _stop_event.wait(timeout=30)


# ── Public API ────────────────────────────────────────────────────────────────

def start_scheduler(config: Optional[SchedulerConfig] = None) -> str:
    """
    Start the background scheduler daemon thread.
    Returns a human-readable status string with the next scheduled run time.
    If the scheduler is already running returns an informative message instead
    of starting a second thread.
    """
    global _scheduler_thread, _stop_event

    if is_scheduler_running():
        next_run = get_next_run_time(config or load_scheduler_config())
        return f"Scheduler already running. Next run: {next_run.strftime('%Y-%m-%d %H:%M')}"

    if config is None:
        config = load_scheduler_config()

    if not config.enabled:
        return "Scheduler is disabled in config (enabled=False). Update config and retry."

    _stop_event.clear()

    _scheduler_thread = threading.Thread(
        target=_scheduler_loop,
        args=(config,),
        daemon=True,
        name="WholesaleScheduler",
    )
    _scheduler_thread.start()

    next_run = get_next_run_time(config)

    if config.interval_hours:
        mode = f"every {config.interval_hours}h"
    else:
        mode = f"daily at {config.run_time}"

    return (
        f"Scheduler started ({mode}). "
        f"Next run: {next_run.strftime('%Y-%m-%d %H:%M')}"
    )


def stop_scheduler() -> str:
    """Signal the background thread to stop and wait up to 5 seconds for it."""
    global _scheduler_thread

    if not is_scheduler_running():
        return "Scheduler is not running."

    _stop_event.set()
    if _scheduler_thread is not None:
        _scheduler_thread.join(timeout=5)

    return "Scheduler stopped."


def is_scheduler_running() -> bool:
    """Return True if the background scheduler thread is alive."""
    return (
        _scheduler_thread is not None
        and _scheduler_thread.is_alive()
        and not _stop_event.is_set()
    )


def get_scheduler_status() -> dict:
    """
    Return a status dict suitable for display in a CLI dashboard.

    Keys:
        running         bool
        next_run        str  ISO datetime (or None)
        last_run        str  ISO datetime (or None)
        last_scan_summary  dict (or None)
    """
    config = load_scheduler_config()
    running = is_scheduler_running()

    next_run_dt = get_next_run_time(config) if running else None
    next_run_str = next_run_dt.isoformat() if next_run_dt else None

    # Fall back to persisted scan if the in-memory summary was lost (e.g. restart)
    scan_summary = _last_scan_summary or _load_last_scan()

    return {
        "running":           running,
        "next_run":          next_run_str,
        "last_run":          _last_run,
        "last_scan_summary": scan_summary,
        "config": {
            "run_time":       config.run_time,
            "interval_hours": config.interval_hours,
            "markets":        config.markets,
            "max_price":      config.max_price,
            "enabled":        config.enabled,
        },
    }
