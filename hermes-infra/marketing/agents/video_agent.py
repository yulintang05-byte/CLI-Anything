"""Video content agent for Hermes.

Generates a complete video content package per run:
  - 90-second word-for-word demo script with on-screen action cues
  - YouTube metadata (A/B title options, description, tags, thumbnail concepts)
  - YouTube Shorts script (60-second vertical format)
  - TikTok/Instagram Reels opening hooks (5 × 3-second hooks)

All content is saved to a single Markdown file in the output directory.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import anthropic

from ..config import (
    OUTPUT_DIR,
    PRODUCT_NAME,
    PRODUCT_TAGLINE,
    WHOP_URL,
    INSTALL_CMD,
)
from .base import BaseAgent

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a developer content creator who makes viral programming videos. "
    "Hook in 3 seconds or lose them. Show don't tell. "
    "Real terminal output beats any animation."
)

# ---------------------------------------------------------------------------
# Prompt builders
# The agent fires five targeted prompts and stitches the results together.
# This is more reliable than a single mega-prompt and gives us cleaner sections.
# ---------------------------------------------------------------------------

_DEMO_SCRIPT_PROMPT = f"""
Write a word-for-word 90-second demo video script for {PRODUCT_NAME} — {PRODUCT_TAGLINE}
{PRODUCT_NAME} is a fast, Rust-based terminal client for Claude AI.
Pricing: Free (BYOK), Pro $12/mo, Ultra $29/mo. Sold at {WHOP_URL}.
Install: `{INSTALL_CMD}`

The script must follow this exact structure.  Use [ACTION] tags for on-screen
cues and (narrator) for the spoken words.  Be word-for-word precise — a
presenter should be able to read this verbatim.

Timestamps and required beats:
  0–10s  OPENING HOOK
         - Hook line: "What if your terminal could think?"
         - Establish the problem: web AI breaks your flow, IDE plugins are heavy
         - Promise: this changes in 90 seconds

  10–30s INSTALL DEMO
         - Run the install one-liner: `{INSTALL_CMD}`
         - Show the progress output in the terminal
         - Binary is ready in seconds; contrast with npm-based tools

  30–60s FIRST QUERY
         - Launch {PRODUCT_NAME} with `hermes`
         - Show the ratatui TUI loading
         - Type an impressive query: "scaffold a Rust CLI that parses TOML config"
         - Show the streaming response appearing line by line in the TUI
         - Highlight the token counter updating in real time

  60–75s PRICING REVEAL
         - "Free tier — your API key, your cost, no subscription"
         - "Pro at $12/mo — priority routing, offline grace period"
         - "Ultra at $29/mo — team features, advanced model access"
         - "You control the spend.  No black-box billing."

  75–90s CTA
         - "Get {PRODUCT_NAME} now at {WHOP_URL}"
         - Show the URL on screen
         - End on the terminal with {PRODUCT_NAME} still running

Format the output as a proper two-column script:
| Time  | Narration + [ACTION CUES] |
Use markdown table format.  Every second matters — keep it tight.
""".strip()

_YOUTUBE_METADATA_PROMPT = f"""
Generate complete YouTube metadata for a {PRODUCT_NAME} demo video.
{PRODUCT_NAME} is a fast, Rust-based terminal client for Claude AI.
Pricing: Free (BYOK), Pro $12/mo, Ultra $29/mo. Sold at {WHOP_URL}.

Return ALL of the following, clearly labelled with markdown headers:

## Title Options (A/B/C test)
Three distinct title options.  Each must be:
- Under 60 characters
- Include a strong keyword (Claude, terminal, Rust, AI CLI, etc.)
- Different hook angle each: speed, transformation, curiosity

## Description
Write a 500-word keyword-rich YouTube description.  Include:
- First 2 lines are the hook (these show before "Show more")
- What {PRODUCT_NAME} is and who it's for
- Timestamp chapters (00:00 Intro, 00:10 Install, 00:30 First Query, etc.)
- Feature list with emoji bullets
- Pricing section
- Links section: {WHOP_URL} , install command
- Relevant keywords naturally woven into prose (not stuffed)
- Call to action: subscribe, like, comment

## Tags
List exactly 30 YouTube tags, comma-separated.  Mix short-tail and long-tail.
Cover: Claude AI, Rust CLI, terminal productivity, AI coding assistant, etc.

## Thumbnail Concepts
Three distinct thumbnail concepts described for a designer.
Each concept: background, foreground element, text overlay, color palette, mood.
Make them click-worthy without being misleading.
""".strip()

_SHORTS_SCRIPT_PROMPT = f"""
Write a 60-second YouTube Shorts script for {PRODUCT_NAME}.
{PRODUCT_NAME} is a fast, Rust-based terminal client for Claude AI.
{WHOP_URL}

YouTube Shorts rules:
- Vertical format (9:16) — mention "on my screen" rather than "on the left/right"
- First 2 seconds MUST be the hook — no intro, no "hey guys"
- Fast cuts, punchy sentences, max 8-10 words per spoken line
- Show the terminal filling the frame
- End with a verbal CTA and on-screen URL

Structure (use timestamps):
  0-2s   Hook: the most provocative claim you can make about {PRODUCT_NAME}
  2-15s  Pain: show the messy alternative (browser switching, slow tools)
  15-40s Payoff: install + first query in real time, no cuts
  40-55s Benefits flash: 3 bullet points, spoken fast
  55-60s CTA: "{WHOP_URL} — link in bio"

Format as a numbered shot list with SPOKEN TEXT in quotes and [action] in brackets.
""".strip()

_REELS_HOOKS_PROMPT = f"""
Write 5 different 3-second opening hooks for TikTok and Instagram Reels promoting
{PRODUCT_NAME} — a fast Rust terminal client for Claude AI.

Each hook is the VERY FIRST thing the viewer sees and hears.  You have exactly
3 seconds before they scroll.  Make them feel something: curiosity, FOMO, surprise.

For each hook provide:
- Hook number and a short label (e.g. "Hook 1: The Comparison")
- SPOKEN line (≤12 words, punchy, no filler)
- ON-SCREEN TEXT overlay (≤6 words, large font)
- Visual setup (what's on screen in these 3 seconds)

Target angles, one per hook:
  1. Speed comparison (before/after feel)
  2. Developer identity ("if you still use the web app…")
  3. Price shock ("this is cheaper than your coffee subscription")
  4. The terminal takeover ("your terminal is about to get smarter")
  5. Curiosity gap ("I hid something in this terminal — watch closely")

Format each hook clearly separated with a horizontal rule.
""".strip()

# ---------------------------------------------------------------------------
# Section header templates
# ---------------------------------------------------------------------------

_SECTION_TITLES = {
    "demo_script":       "90-Second Demo Script",
    "youtube_metadata":  "YouTube Metadata",
    "shorts_script":     "YouTube Shorts Script (60s)",
    "reels_hooks":       "TikTok / Instagram Reels Hooks",
}

# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------


class VideoAgent(BaseAgent):
    """Marketing agent that generates a complete video content package."""

    def __init__(self, client: anthropic.Anthropic) -> None:
        super().__init__(name="Video", client=client)

    # ------------------------------------------------------------------
    # Section generators
    # ------------------------------------------------------------------

    async def _gen_demo_script(self) -> str:
        """Generate the 90-second word-for-word demo script."""
        return await self.generate(
            prompt=_DEMO_SCRIPT_PROMPT,
            system=SYSTEM_PROMPT,
        )

    async def _gen_youtube_metadata(self) -> str:
        """Generate YouTube title, description, tags, and thumbnail concepts."""
        return await self.generate(
            prompt=_YOUTUBE_METADATA_PROMPT,
            system=SYSTEM_PROMPT,
        )

    async def _gen_shorts_script(self) -> str:
        """Generate the 60-second YouTube Shorts script."""
        return await self.generate(
            prompt=_SHORTS_SCRIPT_PROMPT,
            system=SYSTEM_PROMPT,
        )

    async def _gen_reels_hooks(self) -> str:
        """Generate 5 three-second TikTok/Instagram Reels opening hooks."""
        return await self.generate(
            prompt=_REELS_HOOKS_PROMPT,
            system=SYSTEM_PROMPT,
        )

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    @staticmethod
    def _wrap_section(title: str, content: str) -> str:
        """Wrap a content block in a clearly delineated Markdown section."""
        divider = "=" * 72
        return (
            f"<!-- {divider} -->\n"
            f"## {title}\n\n"
            f"{content.strip()}\n"
        )

    def _build_package(
        self,
        date_str: str,
        demo_script: str,
        youtube_metadata: str,
        shorts_script: str,
        reels_hooks: str,
    ) -> str:
        """Assemble all sections into a single Markdown document."""
        now_iso = datetime.now(tz=timezone.utc).isoformat()
        header = (
            f"# {PRODUCT_NAME} Video Content Package\n\n"
            f"> **Generated:** {now_iso}  \n"
            f"> **Agent:** VideoAgent  \n"
            f"> **Product:** {PRODUCT_NAME} — {PRODUCT_TAGLINE}  \n"
            f"> **Buy:** {WHOP_URL}  \n\n"
            "---\n\n"
        )

        sections = [
            self._wrap_section(_SECTION_TITLES["demo_script"],      demo_script),
            self._wrap_section(_SECTION_TITLES["youtube_metadata"],  youtube_metadata),
            self._wrap_section(_SECTION_TITLES["shorts_script"],     shorts_script),
            self._wrap_section(_SECTION_TITLES["reels_hooks"],       reels_hooks),
        ]

        return header + "\n\n---\n\n".join(sections) + "\n"

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def run(self) -> dict[str, Any]:
        """Generate the full video content package and save it to disk."""
        date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

        # Run the four generation tasks.  They are intentionally sequential
        # rather than gathered with asyncio.gather because each call consumes
        # significant tokens and we want clear, ordered progress logging.
        print(f"[VideoAgent] Generating 90-second demo script…")
        demo_script = await self._gen_demo_script()

        print(f"[VideoAgent] Generating YouTube metadata…")
        youtube_metadata = await self._gen_youtube_metadata()

        print(f"[VideoAgent] Generating YouTube Shorts script…")
        shorts_script = await self._gen_shorts_script()

        print(f"[VideoAgent] Generating TikTok/Reels hooks…")
        reels_hooks = await self._gen_reels_hooks()

        # Assemble and persist
        package = self._build_package(
            date_str,
            demo_script,
            youtube_metadata,
            shorts_script,
            reels_hooks,
        )

        saved_path = self.save_output(f"video_package_{date_str}.md", package)
        print(f"[VideoAgent] Saved video package to {saved_path}")

        return {
            "agent": self.name,
            "platform": "youtube",
            "status": "generated",
            "content": "Video package ready",
            "output_file": saved_path,
            "sections": list(_SECTION_TITLES.values()),
        }
