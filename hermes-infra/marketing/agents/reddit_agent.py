"""Reddit marketing agent for Hermes.

Cycles through a schedule of subreddits, generates a culture-appropriate post
for each, optionally submits via PRAW, and persists the content to disk.
The schedule position is tracked in a lightweight JSON state file so successive
runs always target a fresh subreddit.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

import anthropic

from ..config import (
    OUTPUT_DIR,
    PRODUCT_NAME,
    PRODUCT_TAGLINE,
    WHOP_URL,
    INSTALL_CMD,
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USERNAME,
    REDDIT_PASSWORD,
)
from .base import BaseAgent

try:
    import praw  # optional dependency
    _PRAW_AVAILABLE = True
except ImportError:
    _PRAW_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a genuine Rust developer sharing a project you built. "
    "Each subreddit has different culture. Match the tone perfectly. "
    "Never sound like spam. Add real technical value."
)

# Schedule of subreddits to cycle through, in order.
SUBREDDITS = [
    {"sub": "rust",             "type": "technical",   "flair": "Projects"},
    {"sub": "commandline",      "type": "showcase",    "flair": None},
    {"sub": "devops",           "type": "tool",        "flair": None},
    {"sub": "MachineLearning",  "type": "application", "flair": "Project"},
    {"sub": "programming",      "type": "blog",        "flair": None},
    {"sub": "SideProject",      "type": "launch",      "flair": None},
    {"sub": "AIToolsAndUsecases","type": "tool",       "flair": None},
]

# State file persists the schedule index across agent runs.
_STATE_FILE = os.path.join(OUTPUT_DIR, ".reddit_state.json")

# ---------------------------------------------------------------------------
# Per-subreddit prompt templates
# ---------------------------------------------------------------------------

_SUBREDDIT_PROMPTS: dict[str, str] = {
    "rust": (
        "Write a Reddit post for r/rust about Hermes — a terminal Claude AI client "
        "written entirely in Rust. This is a technical audience that cares deeply "
        "about implementation quality, idiomatic Rust, and crate choices.\n\n"
        "Cover:\n"
        "- Why Rust was chosen (low latency, low memory, single-binary distribution)\n"
        "- Key crates used: ratatui for the TUI, tokio for async I/O, reqwest for "
        "  the Anthropic API, serde/serde_json for config and responses, "
        "  crossterm for cross-platform terminal control\n"
        "- Interesting engineering challenges: streaming SSE responses into ratatui "
        "  without blocking the render loop, cross-platform binary packaging, "
        "  implementing a graceful offline mode by caching tokens locally\n"
        "- Honest reflection on where the code is rough and what's next\n\n"
        "Do NOT lead with pricing or marketing language. r/rust readers will "
        "immediately close a post that smells like an ad. Lead with the engineering.\n\n"
        "Format: Reddit markdown. Title on first line prefixed with 'TITLE: '. "
        "Blank line. Then the body. Body should be 400-600 words."
    ),

    "commandline": (
        "Write a Reddit showcase post for r/commandline about Hermes — a fast Rust "
        "terminal client for Claude AI.\n\n"
        "This subreddit loves: terminal screenshots (describe what they'd see in "
        "plain text using code blocks), install one-liners, keybind tables, and "
        "anything that makes the shell feel more powerful.\n\n"
        "Include:\n"
        f"- Install one-liner: `{INSTALL_CMD}`\n"
        "- ASCII art or code-block mockup of the TUI (approximate it in text)\n"
        "- Keybinds table (Ctrl+L clear, Ctrl+N new session, Tab model switch, etc.)\n"
        "- What makes it different from just using the Claude web app or API directly\n"
        "- A short demo: user types a prompt, streaming response appears line by line\n\n"
        "Tone: enthusiastic but grounded. r/commandline loves real demos, not pitches.\n\n"
        "Format: Reddit markdown. Title on first line prefixed with 'TITLE: '. "
        "Blank line. Then the body. Body 350-500 words."
    ),

    "devops": (
        "Write a Reddit post for r/devops about Hermes — a terminal Claude AI client "
        "that fits naturally into DevOps workflows.\n\n"
        "Angle: DevOps engineers spend their lives in terminals, SSH sessions, and "
        "automation scripts. A lightweight AI assistant that runs anywhere a shell "
        "runs is genuinely useful.\n\n"
        "Cover:\n"
        "- Using Hermes over SSH (no browser needed, connects to existing API key)\n"
        "- Piping output: `hermes 'explain this error' < stderr.log`\n"
        "- Using it in CI for log analysis or runbook generation\n"
        "- The offline grace period (7-day cache) for air-gapped or flaky-network "
        "  environments\n"
        "- Resource footprint: ~12 MB RSS, starts in <100 ms — relevant for "
        "  constrained VMs or containers\n\n"
        "Tone: peer-to-peer, practical, skip the fluff. r/devops will call out "
        "any vague claims.\n\n"
        "Format: Reddit markdown. Title on first line prefixed with 'TITLE: '. "
        "Blank line. Then the body. Body 350-500 words."
    ),

    "MachineLearning": (
        "Write a Reddit post for r/MachineLearning about Hermes as an application "
        "of the Claude API.\n\n"
        "This is a research-adjacent audience. They care about model capabilities, "
        "prompt engineering, context windows, and practical tooling for ML work.\n\n"
        "Cover:\n"
        "- How Hermes exposes the full Claude API (model selection, system prompts, "
        "  temperature, context window management) from the terminal\n"
        "- Using Hermes for quick experiments: testing prompts, comparing model "
        "  outputs, scripting evals via the CLI flags\n"
        "- Context-window awareness: the TUI shows live token count so you know "
        "  when you're approaching limits\n"
        "- The bring-your-own-key model: relevant for researchers who already have "
        "  Anthropic API access and don't want another subscription layer obscuring "
        "  their usage\n\n"
        "Tone: technically precise. Avoid overselling capabilities. r/MachineLearning "
        "readers will cross-examine any benchmarks.\n\n"
        "Format: Reddit markdown. Title on first line prefixed with 'TITLE: '. "
        "Blank line. Then the body. Body 400-550 words."
    ),

    "programming": (
        "Write a Reddit blog-style post for r/programming about building a terminal "
        "AI client in Rust.\n\n"
        "r/programming likes thoughtful technical writing — the kind of post "
        "programmers bookmark and share. Write it as a dev blog entry, not a "
        "product announcement.\n\n"
        "Narrative arc:\n"
        "1. The problem: web-based AI clients break terminal flow and feel slow\n"
        "2. The choice to use Rust: single binary, memory safety, native speed\n"
        "3. The hardest part: rendering streaming SSE into a ratatui TUI without "
        "   jank\n"
        "4. What you learned about building CLI products that people actually use\n"
        "5. Where it is now: Hermes, free + paid tiers, real users\n\n"
        "Include code snippets where they add value (tokio + reqwest async streaming, "
        "ratatui render loop). Keep snippets short.\n\n"
        "Tone: first-person, reflective, honest about mistakes. No bulleted feature "
        "lists — this is prose.\n\n"
        "Format: Reddit markdown. Title on first line prefixed with 'TITLE: '. "
        "Blank line. Then the body. Body 500-700 words."
    ),

    "SideProject": (
        "Write a Reddit launch post for r/SideProject about Hermes.\n\n"
        "r/SideProject values: honesty about metrics, authentic origin stories, "
        "real pricing transparency, and builders talking to builders.\n\n"
        "Include:\n"
        "- What it is (one sentence)\n"
        "- Why you built it (honest personal motivation)\n"
        "- Current metrics: launched X weeks ago, N users, revenue if comfortable "
        "  sharing (or 'early but growing')\n"
        "- Pricing: Free (BYOK), Pro $12/mo, Ultra $29/mo — sold at "
        f"  {WHOP_URL}\n"
        "- Biggest technical win\n"
        "- Biggest mistake so far\n"
        "- What's next\n"
        "- Ask for feedback, not upvotes\n\n"
        "Tone: builder-to-builder. Vulnerable and direct. No PR speak.\n\n"
        "Format: Reddit markdown. Title on first line prefixed with 'TITLE: '. "
        "Blank line. Then the body. Body 300-450 words."
    ),

    "AIToolsAndUsecases": (
        "Write a Reddit tool-showcase post for r/AIToolsAndUsecases about Hermes.\n\n"
        "This subreddit is friendly to tool announcements if they're genuinely "
        "useful. Readers want to know: what does it do, who is it for, how do I "
        "try it?\n\n"
        "Cover:\n"
        f"- What: {PRODUCT_NAME} — {PRODUCT_TAGLINE} Terminal client for Claude AI\n"
        "- Who: developers who live in the terminal and want AI assistance without "
        "  leaving it\n"
        "- How to try it: install one-liner, runs in seconds\n"
        "- Key features: Rust-based speed, ratatui TUI, BYOK, offline grace period, "
        "  Pro/Ultra tiers\n"
        "- Pricing: Free with your own API key; Pro $12/mo, Ultra $29/mo for extras\n"
        f"- Link: {WHOP_URL}\n\n"
        "Keep it concise. This sub doesn't need a wall of text, just enough to "
        "make readers click through.\n\n"
        "Format: Reddit markdown. Title on first line prefixed with 'TITLE: '. "
        "Blank line. Then the body. Body 200-350 words."
    ),
}

# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------


def _load_state() -> dict[str, Any]:
    """Load schedule state from disk, or return a fresh state dict."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if os.path.exists(_STATE_FILE):
        try:
            with open(_STATE_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    return {"index": 0}


def _save_state(state: dict[str, Any]) -> None:
    """Persist schedule state to disk."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(_STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)


def _next_subreddit(state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (target_subreddit_entry, updated_state) without mutating state."""
    idx = state.get("index", 0) % len(SUBREDDITS)
    target = SUBREDDITS[idx]
    new_state = {"index": (idx + 1) % len(SUBREDDITS)}
    return target, new_state

# ---------------------------------------------------------------------------
# Content parsing
# ---------------------------------------------------------------------------


def _parse_title_and_body(raw: str) -> tuple[str, str]:
    """Split the model response into (title, body).

    The model is instructed to prefix the title with 'TITLE: ' on the first
    non-empty line.  Everything after the blank line separator is the body.
    """
    lines = raw.strip().splitlines()
    title = ""
    body_lines: list[str] = []
    found_title = False
    past_blank = False

    for line in lines:
        stripped = line.strip()
        if not found_title:
            if stripped.upper().startswith("TITLE:"):
                title = stripped[6:].strip()
                found_title = True
            elif stripped:
                # Model didn't follow format; treat first line as title
                title = stripped
                found_title = True
        else:
            if not past_blank and stripped == "":
                past_blank = True
                continue
            body_lines.append(line)

    body = "\n".join(body_lines).strip()
    return title, body


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------


class RedditAgent(BaseAgent):
    """Marketing agent that generates and optionally posts Reddit content."""

    SUBREDDITS = SUBREDDITS  # expose for testing

    def __init__(self, client: anthropic.Anthropic) -> None:
        super().__init__(name="Reddit", client=client)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_prompt_for_sub(self, sub_entry: dict[str, Any]) -> str:
        """Return the generation prompt for the given subreddit entry."""
        sub_name: str = sub_entry["sub"]
        prompt = _SUBREDDIT_PROMPTS.get(sub_name)
        if prompt:
            return prompt
        # Fallback: generic prompt for any unlisted subreddit
        return (
            f"Write a Reddit post for r/{sub_name} about Hermes — a fast, Rust-based "
            f"terminal client for Claude AI. Pricing: Free (BYOK), Pro $12/mo, "
            f"Ultra $29/mo. Sold at {WHOP_URL}. "
            f"Match the subreddit culture for r/{sub_name}. "
            "Format: Reddit markdown. Title on first line prefixed with 'TITLE: '. "
            "Blank line. Then the body (300-500 words)."
        )

    def _post_to_reddit(
        self,
        sub_name: str,
        title: str,
        body: str,
        flair: str | None,
    ) -> str | None:
        """Submit the post via PRAW if credentials are present.

        Returns the post URL on success, or None if posting is skipped or fails.
        """
        if not _PRAW_AVAILABLE:
            return None
        if not all([
            REDDIT_CLIENT_ID,
            REDDIT_CLIENT_SECRET,
            REDDIT_USERNAME,
            REDDIT_PASSWORD,
        ]):
            return None

        try:
            reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                username=REDDIT_USERNAME,
                password=REDDIT_PASSWORD,
                user_agent="hermes-bot/1.0",
            )
            subreddit = reddit.subreddit(sub_name)
            submit_kwargs: dict[str, Any] = {
                "title": title,
                "selftext": body,
            }
            if flair:
                # Attempt to find and apply the flair by display name
                try:
                    for template in subreddit.flair.link_templates:
                        if template["text"].lower() == flair.lower():
                            submit_kwargs["flair_id"] = template["id"]
                            break
                except Exception:  # pylint: disable=broad-except
                    pass  # Flair is optional; continue without it

            post = subreddit.submit(**submit_kwargs)
            return f"https://www.reddit.com{post.permalink}"
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[RedditAgent] Reddit posting failed: {exc}")
            return None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def run(self) -> dict[str, Any]:
        """Pick the next subreddit, generate a post, optionally submit, save."""
        date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

        # ---- Advance schedule ------------------------------------------
        state = _load_state()
        sub_entry, new_state = _next_subreddit(state)
        sub_name: str = sub_entry["sub"]
        sub_type: str = sub_entry["type"]
        sub_flair: str | None = sub_entry["flair"]

        # ---- Generate content ------------------------------------------
        prompt = self._get_prompt_for_sub(sub_entry)
        raw = await self.generate(prompt=prompt, system=SYSTEM_PROMPT)
        title, body = _parse_title_and_body(raw)

        # ---- Optionally post -------------------------------------------
        post_url: str | None = self._post_to_reddit(sub_name, title, body, sub_flair)
        post_status = "posted" if post_url else "generated"

        # ---- Persist state only after generation succeeds --------------
        _save_state(new_state)

        # ---- Save to disk ----------------------------------------------
        md_content = (
            f"# r/{sub_name} — {title}\n\n"
            f"> **Type:** {sub_type} | **Flair:** {sub_flair or 'none'} | "
            f"**Date:** {date_str} | **Status:** {post_status}\n"
        )
        if post_url:
            md_content += f"> **Posted:** {post_url}\n"
        md_content += f"\n---\n\n{body}\n"

        saved_path = self.save_output(f"reddit_{sub_name}_{date_str}.md", md_content)
        print(f"[RedditAgent] Saved post to {saved_path}")

        # ---- Return summary --------------------------------------------
        result: dict[str, Any] = {
            "agent": self.name,
            "platform": f"reddit/{sub_name}",
            "status": post_status,
            "title": title,
            "output_file": saved_path,
        }
        if post_url:
            result["url"] = post_url
        else:
            result["url"] = None

        return result
