"""Hacker News "Show HN" post agent for Hermes marketing.

Generates an authentic HN Show HN post with title, body, anticipated Q&A,
and a Reddit r/programming crosspost variant.  Output is written to
``output/hn_{date}.md``.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from .base import BaseAgent
from .. import config

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are a seasoned Hacker News contributor. "
    "Write authentic technical posts that start real discussions. "
    "Never sound like marketing. Focus on what's technically interesting."
)

# ---------------------------------------------------------------------------
# User prompt
# ---------------------------------------------------------------------------

_HN_PROMPT = f"""Write a complete Hacker News "Show HN" submission for Hermes, a commercial
Claude-powered terminal product.  Follow every instruction below exactly.

---

## Context about Hermes

- **What it is:** A terminal client for Claude AI, written in Rust, sold on Whop.
- **Pricing:** Pro plan $12/mo, Ultra plan $29/mo.  No free tier (be upfront about this).
- **Value proposition:** Faster response streaming and lower effective cost than running Claude
  Code directly, because Hermes batches/caches requests and uses a purpose-built Rust TUI.
- **How it differs from claude-code CLI:** claude-code runs inside editors (VS Code, JetBrains).
  Hermes is a standalone terminal — you can pipe it, script it, SSH into it, run it in tmux.
- **Install:** `{config.INSTALL_CMD}`
- **Purchase/info:** {config.WHOP_URL}

---

## Output format

Produce the following sections **in this exact Markdown structure**:

```
# Show HN: Hermes – <subtitle max 60 chars total including "Show HN: ">
```

> (The title including "Show HN: " prefix must be ≤ 60 characters total.
> It should be technically descriptive, not salesy.)

---

## HN Post Body (300–500 words)

Write the body text as if you are the founder posting on news.ycombinator.com.
Requirements:
- Start with **what the problem is** (a technical pain point, not marketing copy).
- Explain **why Rust** — be specific: latency budget, zero-cost streaming, no GC pauses.
- Describe **how it differs from claude-code** — be fair, acknowledge what claude-code does well.
- Mention pricing honestly and early; developers hate surprise paywalls.
- Include the install one-liner naturally in the flow.
- Do NOT use bullet points in this section — write in natural paragraphs as a founder would.
- Keep jargon accurate; HN readers will call out anything wrong.

---

## Anticipated HN Comments & Pre-Written Responses

Write exactly **5 realistic HN comments** that the community would likely post (sceptical,
technical, price-sensitive, or curious), followed by a concise founder response to each.

Format each as:

### Comment 1
**HN commenter:** <the comment text, 1–3 sentences, reads like a real HN user>

**Founder response:** <honest, technical reply, no defensiveness, 2–4 sentences>

(Repeat for Comments 2–5)

---

## Reddit r/programming Crosspost Version

Write a **separate version** of the post adapted for Reddit r/programming.  Reddit culture
differs: titles can be longer, the body can be slightly less terse, and Markdown lists are
more accepted.  Requirements:
- Title: ≤ 300 chars (Reddit limit), but keep it informative.
- Body: 200–350 words.  Can use Markdown lists.  Still honest about pricing.
- End with the install one-liner in a code block.

---

Output only the Markdown document.  No preamble, no explanation.
"""


class HNAgent(BaseAgent):
    """Generates an authentic Hacker News Show HN post (and Reddit crosspost) for Hermes."""

    def __init__(self, client: Any) -> None:  # client: anthropic.Anthropic
        super().__init__(name="HN", client=client)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def run(self) -> dict[str, Any]:
        """Generate the HN post content and persist it to disk.

        Returns:
            A dict with keys ``agent``, ``platform``, ``status``, ``content``
            (the HN post title), and ``file_path``.
        """
        content = await self.generate(prompt=_HN_PROMPT, system=_SYSTEM_PROMPT)

        # Extract the title from the first heading line for the return value.
        title = _extract_title(content)

        date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        filename = f"hn_{date_str}.md"
        file_path = os.path.join(config.OUTPUT_DIR, filename)

        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(content)

        return {
            "agent": "HN",
            "platform": "hackernews",
            "status": "generated",
            "content": title,
            "file_path": file_path,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_title(markdown: str) -> str:
    """Return the text of the first H1 heading found in *markdown*.

    Falls back to the first 100 characters of the content if no heading is
    found (should not happen in practice given the prompt structure).
    """
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    # Fallback: return the beginning of whatever was generated.
    return markdown[:100].strip()
