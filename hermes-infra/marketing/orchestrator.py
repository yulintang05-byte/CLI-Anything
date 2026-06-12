"""Hermes Marketing Swarm — persistent orchestrator.

Runs all marketing agents on a schedule, forever.  Never crashes: every
per-agent exception is caught, logged as a warning, and the swarm continues.

Schedule
--------
* Every  4 h  — SocialAgent  (Twitter / X threads)
* Every 12 h  — RedditAgent, SEOAgent, VideoAgent
* Every 24 h  — DevToAgent
* Every 72 h  — HNAgent

Each "tick" is one hour.  The orchestrator sleeps 3 600 s between ticks and
checks which agents are due to run.
"""
from __future__ import annotations

import asyncio
import traceback
from datetime import datetime, timezone
from typing import Any

import anthropic

from . import config
from .agents.seo import SEOAgent
from .agents.social import SocialAgent
from .agents.reddit import RedditAgent
from .agents.devto import DevToAgent
from .agents.video import VideoAgent
from .agents.hn import HNAgent

# ---------------------------------------------------------------------------
# ASCII banner
# ---------------------------------------------------------------------------

BANNER = r"""
██╗  ██╗███████╗██████╗ ███╗   ███╗███████╗███████╗
██║  ██║██╔════╝██╔══██╗████╗ ████║██╔════╝██╔════╝
███████║█████╗  ██████╔╝██╔████╔██║█████╗  ███████╗
██╔══██║██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══╝  ╚════██║
██║  ██║███████╗██║  ██║██║ ╚═╝ ██║███████╗███████║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝
MARKETING SWARM v1.0 — agents never sleep 🚀
"""

# ---------------------------------------------------------------------------
# Wave runner
# ---------------------------------------------------------------------------


async def run_wave(agents: list[Any]) -> list[dict[str, Any]]:
    """Run all *agents* concurrently.

    Exceptions from individual agents are captured and returned as error dicts
    so that one bad agent never aborts the rest.

    Args:
        agents: List of agent instances whose ``run()`` coroutine will be
            gathered concurrently.

    Returns:
        A list of result dicts, one per agent.  Failed agents produce::

            {"agent": <name>, "platform": "unknown", "status": "error",
             "content": "<traceback>"}
    """
    coros = [a.run() for a in agents]
    raw_results = await asyncio.gather(*coros, return_exceptions=True)

    results: list[dict[str, Any]] = []
    for agent, result in zip(agents, raw_results):
        if isinstance(result, Exception):
            tb = "".join(traceback.format_exception(type(result), result, result.__traceback__))
            print(f"  [WARNING] {agent.name} raised an exception:\n{tb}")
            results.append(
                {
                    "agent": agent.name,
                    "platform": getattr(agent, "platform", "unknown"),
                    "status": "error",
                    "content": str(result),
                }
            )
        else:
            results.append(result)
    return results


# ---------------------------------------------------------------------------
# Status table printer
# ---------------------------------------------------------------------------


def _truncate(text: str, width: int = 50) -> str:
    """Return *text* truncated to *width* characters with an ellipsis."""
    text = text.replace("\n", " ").strip()
    if len(text) <= width:
        return text
    return text[: width - 1] + "…"


def print_status_table(results: list[dict[str, Any]]) -> None:
    """Print a fixed-width status table to stdout.

    Columns: Agent | Platform | Status | Preview (50 chars)
    """
    col_agent    = 18
    col_platform = 14
    col_status   = 10
    col_preview  = 52   # 50 chars + 2 padding

    sep = (
        "+" + "-" * (col_agent + 2)
        + "+" + "-" * (col_platform + 2)
        + "+" + "-" * (col_status + 2)
        + "+" + "-" * col_preview
        + "+"
    )
    header = (
        f"| {'Agent':<{col_agent}} "
        f"| {'Platform':<{col_platform}} "
        f"| {'Status':<{col_status}} "
        f"| {'Content Preview (50 chars)':<{col_preview - 2}} |"
    )

    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"\n  Wave completed at {now}")
    print(sep)
    print(header)
    print(sep)

    for r in results:
        agent_name = _truncate(str(r.get("agent", "")),    col_agent)
        platform   = _truncate(str(r.get("platform", "")), col_platform)
        status     = _truncate(str(r.get("status", "")),   col_status)
        preview    = _truncate(str(r.get("content", "")),  50)

        print(
            f"| {agent_name:<{col_agent}} "
            f"| {platform:<{col_platform}} "
            f"| {status:<{col_status}} "
            f"| {preview:<{col_preview - 2}} |"
        )

    print(sep)
    print()


# ---------------------------------------------------------------------------
# Schedule definition
# ---------------------------------------------------------------------------

# Interval in hours for each agent class.
AGENT_INTERVALS: dict[str, int] = {
    "SocialAgent":  4,   # max safe cadence — X tolerates frequent threads
    "RedditAgent":  12,  # kept at 12h: faster gets accounts shadowbanned
    "SEOAgent":     12,  # doubled — more long-tail pages, more search surface
    "DevToAgent":   24,  # Dev.to rate-limits aggressive publishing
    "VideoAgent":   12,  # doubled — daily Shorts + long-form scripts
    "HNAgent":      72,  # kept: reposting HN faster guarantees a ban
}


def _build_agents(client: anthropic.Anthropic) -> list[Any]:
    """Instantiate one instance of every agent class."""
    return [
        SEOAgent("SEOAgent", client),
        SocialAgent("SocialAgent", client),
        RedditAgent("RedditAgent", client),
        DevToAgent("DevToAgent", client),
        VideoAgent("VideoAgent", client),
        HNAgent("HNAgent", client),
    ]


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


async def main_loop() -> None:  # pragma: no cover
    """Persistent scheduling loop — runs forever.

    Each iteration is one "tick" (one hour).  On every tick we check, for each
    agent class, whether enough hours have elapsed since that agent last ran.
    If so, we fire it.
    """
    print(BANNER)

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    agents = _build_agents(client)

    # Map agent name → hours since last run (start at interval so every agent
    # fires immediately on the first tick).
    hours_since_last_run: dict[str, int] = {
        agent.name: AGENT_INTERVALS[agent.name]
        for agent in agents
    }

    tick = 0
    while True:
        tick += 1
        now_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        print(f"[Tick {tick:06d}] {now_str} — checking schedule …")

        # Determine which agents are due this tick.
        due_agents = [
            agent
            for agent in agents
            if hours_since_last_run[agent.name] >= AGENT_INTERVALS[agent.name]
        ]

        if due_agents:
            due_names = ", ".join(a.name for a in due_agents)
            print(f"  Running wave: [{due_names}]")
            try:
                results = await run_wave(due_agents)
                print_status_table(results)
            except Exception:  # belt-and-suspenders; run_wave already guards
                print("  [ERROR] Unexpected failure in run_wave:")
                traceback.print_exc()

            # Reset counters for agents that just ran.
            for agent in due_agents:
                hours_since_last_run[agent.name] = 0
        else:
            print("  No agents due this tick.")

        # Increment hour counters for all agents.
        for agent in agents:
            hours_since_last_run[agent.name] += 1

        # Sleep one hour until the next tick.
        await asyncio.sleep(3600)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main_loop())
