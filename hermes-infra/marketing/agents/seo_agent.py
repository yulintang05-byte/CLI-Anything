"""SEO blog post agent for Hermes marketing.

Generates a full SEO-optimised blog post targeting developer-focused keywords,
plus 10 long-tail keyword ideas and 5 backlink target sites with pitch angles.
Output is written to ``output/seo_{date}.md``.
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
    "You are an expert SEO copywriter specialising in developer tools and CLI products. "
    "Write content that ranks on Google and converts developers to paying customers. "
    "Be direct, technical, and honest."
)

# ---------------------------------------------------------------------------
# User prompt template
# ---------------------------------------------------------------------------

_BLOG_PROMPT = f"""Write a complete, production-ready SEO blog post for Hermes — a commercial
Claude-powered terminal product. Follow every instruction below exactly.

---

## Blog post requirements

**Target keywords (use naturally throughout the post):**
- "claude terminal"
- "AI coding CLI"
- "claude code alternative"
- "terminal AI assistant"

**Focus keyword:** "claude terminal" (aim for ~1.5% density)

**Word count:** 800–1 200 words of body copy (not counting the meta description block)

**Structure (use exactly these Markdown headings):**

```
## Meta description
<150-character meta description. Must include "claude terminal"
and a clear benefit.>

# <Title — include "claude terminal" near the front, ≤ 65 characters>

## Introduction
...

## What Is Hermes?
...

## Why a Dedicated CLI Beats an IDE Extension
...

## Hermes vs Claude Code: Pricing and Performance
...

## Getting Started in One Line
...

## Conclusion
...
```

**Content checklist — every section must cover:**

- **Introduction:** hook (pain point), mention "claude terminal" naturally, preview of article.
- **What Is Hermes?:** product description, built-in Rust for speed, sold on Whop, Pro $12/mo /
  Ultra $29/mo. Explain what "faster/cheaper Claude Code" means in concrete terms.
- **Why a Dedicated CLI Beats an IDE Extension:** latency argument, no GUI overhead, scriptable /
  pipeable, works over SSH, pairs with tmux/zellij. Be honest and specific.
- **Hermes vs Claude Code: Pricing and Performance:** comparison table (Markdown table):
  | | Hermes Pro | Hermes Ultra | Claude Code |
  Use real approximate numbers where known; be honest about unknowns.
- **Getting Started in One Line:** show the install command in a fenced code block:
  ```bash
  {config.INSTALL_CMD}
  ```
  Then show a minimal usage example (fictional but plausible CLI invocation).
- **Conclusion:** summarise benefits, include a CTA linking to {config.WHOP_URL} using anchor
  text "try Hermes free".

**Formatting rules:**
- Use `##` for H2 sections and `###` for any H3 subsections.
- Include at least one Markdown code block.
- Do NOT add any promotional padding or marketing-speak clichés ("game-changer", "revolutionise",
  "cutting-edge", etc.).

---

## Long-tail keyword ideas

After the blog post, on a new line, add a section exactly like this:

## 10 Long-Tail Keyword Ideas

List exactly 10 long-tail keyword phrases (one per line, each ≤ 60 chars) that a developer
interested in AI-assisted coding might search for. Focus on commercial/informational intent.
Format as a numbered Markdown list.

---

## Backlink targets

After the keyword ideas, add:

## 5 Backlink Target Sites

For each site provide:
1. **Site name** and URL
2. **Why it's a good fit** (1 sentence)
3. **Pitch angle** (1–2 sentences: what you'd offer them)

Choose real, authoritative developer-focused sites (e.g. dev blogs, newsletters, podcasts,
OSS aggregators). Do NOT invent fake sites.

---

Output only the Markdown document. No preamble, no explanation.
"""


class SEOAgent(BaseAgent):
    """Generates an SEO blog post, keyword list, and backlink targets for Hermes."""

    def __init__(self, client: Any) -> None:  # client: anthropic.Anthropic
        super().__init__(name="SEO", client=client)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def run(self) -> dict[str, Any]:
        """Generate all SEO content and persist it to disk.

        Returns:
            A dict with keys ``agent``, ``platform``, ``status``, ``content``,
            ``file_path``, and ``word_count``.
        """
        content = await self.generate(prompt=_BLOG_PROMPT, system=_SYSTEM_PROMPT)

        date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        filename = f"seo_{date_str}.md"
        file_path = os.path.join(config.OUTPUT_DIR, filename)

        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(content)

        # Rough word count for observability.
        word_count = len(content.split())

        return {
            "agent": "SEO",
            "platform": "blog",
            "status": "generated",
            "content": content[:100],
            "file_path": file_path,
            "word_count": word_count,
        }
