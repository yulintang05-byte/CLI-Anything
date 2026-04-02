"""Twitter/X social agent for Hermes marketing.

Generates five fully-fledged Twitter threads per run, rotates through five
distinct content angles, optionally posts them via the Tweepy v2 client, and
persists every thread to disk.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from typing import Any

import anthropic

from ..config import (
    OUTPUT_DIR,
    PRODUCT_NAME,
    WHOP_URL,
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_SECRET,
)
from .base import BaseAgent

try:
    import tweepy  # optional dependency
    _TWEEPY_AVAILABLE = True
except ImportError:
    _TWEEPY_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a developer advocate who tweets authentically about CLI tools. "
    "No hype, just real value. Write tweets that developers actually want to share."
)

# Each angle has a name and a detailed instruction that is embedded in the user
# prompt so Claude knows exactly what to produce.
THREAD_ANGLES = [
    {
        "name": "speed",
        "label": "Speed thread",
        "instruction": (
            "Write a Twitter/X thread comparing Hermes vs Claude Code on performance. "
            "Focus on concrete benchmarks: startup time (Hermes ~80 ms cold start vs "
            "Claude Code ~1.4 s), response latency (streaming begins in <200 ms), "
            "memory footprint (Rust binary ~12 MB RSS vs Electron-based alternative). "
            "Include methodology notes so readers trust the numbers. "
            "Tone: developer-to-developer, no marketing fluff."
        ),
    },
    {
        "name": "price",
        "label": "Price thread",
        "instruction": (
            "Write a Twitter/X thread breaking down the cost of Hermes vs Claude Pro. "
            "Compare: Claude Pro $20/mo (web only, shared infrastructure, no API key "
            "control) vs Hermes Free (your own API key, pay per token), Hermes Pro "
            "$12/mo (unlimited sessions, priority routing, offline grace period), "
            "Hermes Ultra $29/mo (team features, priority support, advanced model "
            "access). Show actual math: a developer doing 50 k tokens/day costs ~$4.50 "
            "at claude-3-5-haiku rates. Hermes Pro at $12 covers the tooling; the API "
            "bill is separate and transparent. Tone: honest, show the trade-offs."
        ),
    },
    {
        "name": "feature",
        "label": "Feature thread",
        "instruction": (
            "Write a Twitter/X thread showcasing Hermes features. Cover: (1) the "
            "native Rust TUI — ratatui-powered, zero-latency keystrokes, works over "
            "SSH; (2) offline grace period — keeps working for 7 days if you lose "
            "internet; (3) multi-tier licensing — Free, Pro ($12/mo), Ultra ($29/mo), "
            "each unlocking additional capabilities without changing the binary; "
            "(4) bring-your-own-API-key model so you always control your data and "
            "spending; (5) plugin/tool calling hooks baked into the CLI. "
            "Tone: feature-focused but grounded, each tweet = one feature."
        ),
    },
    {
        "name": "demo",
        "label": "Demo thread",
        "instruction": (
            "Write a Twitter/X thread walking through installing Hermes and running a "
            "first query. Step 1: one-liner install "
            "`curl -fsSL https://hermes.sh/install.sh | bash`. "
            "Step 2: set ANTHROPIC_API_KEY. "
            "Step 3: run `hermes` to launch TUI. "
            "Step 4: ask it to scaffold a Rust project. "
            "Step 5: show the streamed response appearing in the terminal. "
            "Step 6: show how to switch models with a keybind. "
            "Make each tweet feel like a live demo narration with inline code snippets "
            "where appropriate (backticks in tweets). Tone: excited but practical."
        ),
    },
    {
        "name": "story",
        "label": "Story thread",
        "instruction": (
            "Write an authentic origin-story Twitter/X thread about why Hermes was "
            "built. The arc: developer loved Claude but was frustrated by the web "
            "interface breaking their flow; tried Claude Code but found the startup "
            "time and resource usage too heavy for their old ThinkPad; decided to "
            "build a lightweight Rust terminal client on a weekend; it grew into "
            "something others wanted; now it's a real product at whop.com/hermes. "
            "Include real emotional beats — the frustration, the 2 am build session, "
            "the first time a stranger used it. Tone: personal, vulnerable, human."
        ),
    },
]

# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------


def _build_thread_prompt(angle: dict[str, str], thread_number: int, total: int) -> str:
    """Return the user-turn prompt for generating a single thread."""
    return (
        f"Generate thread {thread_number} of {total}: **{angle['label']}**.\n\n"
        f"{angle['instruction']}\n\n"
        "Requirements:\n"
        "- Exactly 7 tweets (numbered 1/7 through 7/7).\n"
        "- Each tweet MUST be ≤280 characters INCLUDING the numbering prefix.\n"
        "- The final tweet (7/7) must include a call-to-action and the URL "
        f"{WHOP_URL}\n"
        "- Do NOT add hashtags beyond one or two per tweet — developers hate spam.\n"
        "- Return ONLY a JSON array of 7 strings, nothing else. Example format:\n"
        '["1/7 First tweet text", "2/7 Second tweet text", ..., "7/7 Last tweet with CTA"]'
    )


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------


class SocialAgent(BaseAgent):
    """Marketing agent that generates and optionally posts Twitter/X threads."""

    THREAD_ANGLES = THREAD_ANGLES  # expose for testing

    def __init__(self, client: anthropic.Anthropic) -> None:
        super().__init__(name="Social", client=client)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_tweets(self, raw: str) -> list[str]:
        """Extract the JSON array of tweet strings from the model response.

        The model is instructed to return only a JSON array, but may occasionally
        wrap it in markdown fences.  We strip those before parsing.
        """
        text = raw.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.splitlines()
            # Drop first line (``` or ```json) and last line (```)
            inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
            text = "\n".join(inner).strip()
        try:
            tweets = json.loads(text)
            if isinstance(tweets, list) and all(isinstance(t, str) for t in tweets):
                return tweets
        except json.JSONDecodeError:
            pass
        # Fallback: split on numbered lines like "1/7 …"
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        pattern = re.compile(r"^\d+/\d+\s")
        tweets = [ln for ln in lines if pattern.match(ln)]
        return tweets if tweets else lines  # last-resort: every non-empty line

    def _validate_tweets(self, tweets: list[str]) -> list[str]:
        """Truncate any tweet that exceeds 280 characters (Twitter's hard limit)."""
        validated: list[str] = []
        for tweet in tweets:
            if len(tweet) > 280:
                tweet = tweet[:277] + "…"
            validated.append(tweet)
        return validated

    async def _generate_thread(self, angle: dict[str, str], idx: int) -> list[str]:
        """Call Claude to produce one thread and return the parsed tweet list."""
        prompt = _build_thread_prompt(angle, idx + 1, len(THREAD_ANGLES))
        raw = await self.generate(prompt=prompt, system=SYSTEM_PROMPT)
        tweets = self._parse_tweets(raw)
        return self._validate_tweets(tweets)

    def _post_thread_to_twitter(self, tweets: list[str]) -> str | None:
        """Post the tweet chain via Tweepy if credentials are present.

        Returns the URL of the first tweet on success, or None if posting is
        skipped or fails.
        """
        if not _TWEEPY_AVAILABLE:
            return None
        if not all([
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_SECRET,
        ]):
            return None

        try:
            client = tweepy.Client(
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_SECRET,
            )

            response = client.create_tweet(text=tweets[0])
            first_id: str = str(response.data["id"])
            parent_id: str = first_id

            for tweet in tweets[1:]:
                response = client.create_tweet(
                    text=tweet,
                    in_reply_to_tweet_id=parent_id,
                )
                parent_id = str(response.data["id"])

            # Build a best-effort URL (requires username; omit if unavailable)
            return f"https://twitter.com/i/web/status/{first_id}"
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[SocialAgent] Twitter posting failed: {exc}")
            return None

    @staticmethod
    def _format_thread_markdown(angle: dict[str, str], tweets: list[str]) -> str:
        """Format a single thread into a readable Markdown section."""
        lines = [f"## {angle['label']}\n"]
        for i, tweet in enumerate(tweets, start=1):
            lines.append(f"### Tweet {i}")
            lines.append(f"{tweet}\n")
            lines.append(f"*Characters: {len(tweet)}/280*\n")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def run(self) -> dict[str, Any]:
        """Generate all five threads, optionally post the first, save to disk."""
        date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

        all_threads: list[list[str]] = []
        for idx, angle in enumerate(THREAD_ANGLES):
            tweets = await self._generate_thread(angle, idx)
            all_threads.append(tweets)

        # ------------------------------------------------------------------
        # Attempt to post the first thread (Speed thread) to Twitter/X
        # ------------------------------------------------------------------
        posted_url: str | None = None
        post_status = "generated"

        if all_threads:
            posted_url = self._post_thread_to_twitter(all_threads[0])
            if posted_url:
                post_status = "posted"

        # ------------------------------------------------------------------
        # Persist all threads to disk
        # ------------------------------------------------------------------
        sections: list[str] = [
            f"# {PRODUCT_NAME} Twitter/X Threads — {date_str}\n",
            f"> Generated by SocialAgent | {datetime.now(tz=timezone.utc).isoformat()}\n",
        ]
        for angle, tweets in zip(THREAD_ANGLES, all_threads):
            sections.append(self._format_thread_markdown(angle, tweets))

        full_content = "\n---\n\n".join(sections)
        saved_path = self.save_output(f"twitter_threads_{date_str}.md", full_content)
        print(f"[SocialAgent] Saved threads to {saved_path}")

        # ------------------------------------------------------------------
        # Return summary dict
        # ------------------------------------------------------------------
        first_tweet = all_threads[0][0] if all_threads and all_threads[0] else ""

        result: dict[str, Any] = {
            "agent": self.name,
            "platform": "twitter",
            "status": post_status,
            "content": first_tweet,
            "threads_generated": len(all_threads),
            "output_file": saved_path,
        }
        if posted_url:
            result["posted_url"] = posted_url

        return result
