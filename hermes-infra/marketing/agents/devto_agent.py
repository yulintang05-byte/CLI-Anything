"""Dev.to article agent for Hermes marketing.

Generates a first-person Rust/CLI developer article and, when
``config.DEVTO_API_KEY`` is set, publishes it automatically via the Dev.to
API.  If no API key is configured the article is saved to
``output/devto_{date}.md`` for manual posting.
"""
from __future__ import annotations

import json
import logging
import os
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any

import httpx

from .base import BaseAgent
from .. import config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEVTO_API_URL = "https://dev.to/api/articles"
_DEVTO_TAGS = ["rust", "cli", "ai", "productivity"]

_SYSTEM_PROMPT = (
    "You are a senior Rust developer writing authentically on Dev.to. "
    "Share real technical details, gotchas, and learnings. "
    "Include actual code. Developers smell marketing from a mile away."
)

# ---------------------------------------------------------------------------
# User prompt
# ---------------------------------------------------------------------------

_ARTICLE_PROMPT = f"""Write a complete Dev.to article about building Hermes — a Rust-based
terminal client for Claude AI.  Follow every instruction below exactly.

---

## Context about Hermes

- **What it is:** A commercial Claude AI terminal, written in Rust.  Sold on Whop.
- **Pricing:** Pro $12/mo, Ultra $29/mo.
- **Install:** `{config.INSTALL_CMD}`
- **Product page:** {config.WHOP_URL}
- **Tech stack (assume for the article):** Rust async runtime (tokio), crossterm for raw-mode
  TUI, streaming SSE over hyper/reqwest, a local SQLite session cache to enable prompt caching
  across invocations.

---

## Article requirements

**Word count:** 1 000–1 500 words of body copy (not counting the front-matter block).

**Tone:** First-person, personal story.  Write as the developer who built Hermes.  Describe
real obstacles — async streaming quirks, crossterm edge cases on Windows, making TUI rendering
feel smooth under backpressure.  Be honest about what didn't work the first time.

**Structure (use these Markdown headings exactly):**

```
# I built a Rust terminal for Claude AI — here's what I learned

## Why I built it
...

## The architecture
...

## The trickiest parts
...

## Live demo: installing and using Hermes
...

## Is it worth $12/mo?
...

## What's next
...
```

**Content requirements per section:**

- **Why I built it:** personal motivation; pain point with existing IDE extension approach;
  goal of a scriptable, pipeable, SSH-friendly AI terminal.
- **The architecture:** high-level diagram in ASCII art or described in prose; mention tokio,
  crossterm, SSE streaming, SQLite session cache.  Keep it accurate to Rust ecosystem norms.
- **The trickiest parts:** pick 2–3 real technical challenges:
  - Handling partial SSE frames that span TCP segments (give a code snippet).
  - Crossterm raw-mode cleanup on panic (give a code snippet using a Drop guard).
  - At least one other challenge of your choice.
  All code snippets must be in fenced Rust code blocks (```rust ... ```).
- **Live demo:** show the install one-liner in a bash code block, then show a realistic CLI
  interaction (fictional but plausible), then show piping Hermes output to another tool.
- **Is it worth $12/mo?:** honest cost-benefit; who it's for; who should stick with the free
  Claude web UI.  Mention Ultra at $29/mo for heavy users.  Link to {config.WHOP_URL}.
- **What's next:** 2–3 planned features; invite readers to try it and report bugs.

**Code blocks:** At least 3 fenced code blocks total (minimum 2 in ```rust, 1 in ```bash).

**Do NOT use:** marketing clichés, excessive adjectives, fake benchmarks without caveats,
or anything that reads like an ad.

---

Output only the article body as Markdown.  No preamble, no explanation.
Do NOT include YAML front-matter — the caller inserts that separately.
"""


class DevToAgent(BaseAgent):
    """Generates and optionally publishes a Dev.to article about Hermes."""

    def __init__(self, client: Any) -> None:  # client: anthropic.Anthropic
        super().__init__(name="DevTo", client=client)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def run(self) -> dict[str, Any]:
        """Generate the Dev.to article, then post or save it.

        Returns:
            A dict with keys:
              - ``agent``    – "DevTo"
              - ``platform`` – "dev.to"
              - ``status``   – "posted" | "saved_for_manual_post"
              - ``content``  – article title (str)
              - ``url``      – article URL if posted, else ``None``
              - ``file_path``– path to the saved .md file (always present)
        """
        # 1. Generate article body via Claude.
        body_markdown = await self.generate(
            prompt=_ARTICLE_PROMPT,
            system=_SYSTEM_PROMPT,
        )

        # 2. Derive metadata from the generated content.
        title = _extract_h1(body_markdown)
        slug = _slugify(title)
        canonical_url = f"{config.PRODUCT_URL}/blog/{slug}"
        date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

        # 3. Attempt to publish if an API key is available.
        if config.DEVTO_API_KEY:
            return await self._post_to_devto(
                title=title,
                body_markdown=body_markdown,
                canonical_url=canonical_url,
                date_str=date_str,
            )

        # 4. No API key — save to disk for manual posting.
        return self._save_locally(
            title=title,
            body_markdown=body_markdown,
            canonical_url=canonical_url,
            date_str=date_str,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _post_to_devto(
        self,
        title: str,
        body_markdown: str,
        canonical_url: str,
        date_str: str,
    ) -> dict[str, Any]:
        """POST the article to Dev.to via their public API.

        Uses ``httpx.AsyncClient`` for non-blocking I/O.  On any error
        (network or API) the method falls back to local save and includes
        error context in the returned dict.

        Args:
            title:          Article title extracted from the generated body.
            body_markdown:  Raw Markdown body (no front-matter).
            canonical_url:  Canonical URL to embed in the Dev.to metadata.
            date_str:       ISO date string used for fallback filenames.

        Returns:
            Result dict — see ``run()`` docstring for shape.
        """
        payload = {
            "article": {
                "title": title,
                "body_markdown": body_markdown,
                "published": True,
                "tags": _DEVTO_TAGS,
                "canonical_url": canonical_url,
            }
        }
        headers = {
            "api-key": config.DEVTO_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Always persist a local copy before attempting the network call.
        fallback_path = self._write_local_file(
            title=title,
            body_markdown=body_markdown,
            canonical_url=canonical_url,
            date_str=date_str,
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as http:
                response = await http.post(
                    _DEVTO_API_URL,
                    headers=headers,
                    content=json.dumps(payload),
                )
                response.raise_for_status()

            data = response.json()
            article_url: str = data.get("url", "")
            article_id: int | None = data.get("id")

            logger.info(
                "DevToAgent: article published — id=%s url=%s",
                article_id,
                article_url,
            )

            return {
                "agent": "DevTo",
                "platform": "dev.to",
                "status": "posted",
                "content": title,
                "url": article_url,
                "article_id": article_id,
                "file_path": fallback_path,
            }

        except httpx.HTTPStatusError as exc:
            # Dev.to returned a non-2xx status — include details for debugging.
            error_body = exc.response.text[:500]
            logger.error(
                "DevToAgent: HTTP %s from Dev.to API — %s",
                exc.response.status_code,
                error_body,
            )
            return {
                "agent": "DevTo",
                "platform": "dev.to",
                "status": "saved_for_manual_post",
                "content": title,
                "url": None,
                "file_path": fallback_path,
                "error": f"HTTP {exc.response.status_code}: {error_body}",
            }

        except httpx.RequestError as exc:
            # Network-level error (timeout, DNS failure, etc.).
            logger.error("DevToAgent: network error posting to Dev.to — %s", exc)
            return {
                "agent": "DevTo",
                "platform": "dev.to",
                "status": "saved_for_manual_post",
                "content": title,
                "url": None,
                "file_path": fallback_path,
                "error": str(exc),
            }

    def _save_locally(
        self,
        title: str,
        body_markdown: str,
        canonical_url: str,
        date_str: str,
    ) -> dict[str, Any]:
        """Save the article to disk when no Dev.to API key is configured.

        Args:
            title:          Article title.
            body_markdown:  Raw Markdown body.
            canonical_url:  Canonical URL for the article.
            date_str:       ISO date string used in the filename.

        Returns:
            Result dict with ``status="saved_for_manual_post"``.
        """
        file_path = self._write_local_file(
            title=title,
            body_markdown=body_markdown,
            canonical_url=canonical_url,
            date_str=date_str,
        )
        logger.info(
            "DevToAgent: no DEVTO_API_KEY configured — article saved to %s",
            file_path,
        )
        return {
            "agent": "DevTo",
            "platform": "dev.to",
            "status": "saved_for_manual_post",
            "content": title,
            "url": None,
            "file_path": file_path,
        }

    def _write_local_file(
        self,
        title: str,
        body_markdown: str,
        canonical_url: str,
        date_str: str,
    ) -> str:
        """Write the article body (with a minimal YAML front-matter header) to disk.

        The front-matter is included so the saved file can be posted manually
        to Dev.to or any other platform without further editing.

        Args:
            title:          Article title.
            body_markdown:  Raw Markdown body (no front-matter).
            canonical_url:  Canonical URL to embed in the front-matter.
            date_str:       ISO date string used in the filename.

        Returns:
            Absolute path of the file that was written.
        """
        front_matter = (
            f"---\n"
            f"title: {json.dumps(title)}\n"
            f"published: false\n"
            f"tags: {', '.join(_DEVTO_TAGS)}\n"
            f"canonical_url: {canonical_url}\n"
            f"---\n\n"
        )
        full_content = front_matter + body_markdown

        filename = f"devto_{date_str}.md"
        file_path = os.path.join(config.OUTPUT_DIR, filename)

        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(full_content)

        return file_path


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _extract_h1(markdown: str) -> str:
    """Return the text of the first H1 heading in *markdown*.

    Falls back to a default title if no H1 is found.
    """
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            return stripped[2:].strip()
    return "I built a Rust terminal for Claude AI — here's what I learned"


def _slugify(text: str) -> str:
    """Convert *text* to a URL-safe slug.

    Steps:
    1. Normalise Unicode to NFKD, drop non-ASCII characters.
    2. Lower-case.
    3. Replace any sequence of non-alphanumeric characters with a hyphen.
    4. Strip leading/trailing hyphens.
    5. Truncate to 80 characters to keep URLs reasonable.

    Args:
        text: Human-readable title string.

    Returns:
        A URL-safe slug string.
    """
    # Normalise unicode (e.g. accented chars → ASCII equivalents where possible).
    normalised = unicodedata.normalize("NFKD", text)
    ascii_text = normalised.encode("ascii", errors="ignore").decode("ascii")

    lower = ascii_text.lower()

    # Replace runs of non-word characters (anything not a-z, 0-9) with hyphens.
    slug = re.sub(r"[^a-z0-9]+", "-", lower)

    # Strip leading/trailing hyphens and truncate.
    slug = slug.strip("-")[:80].rstrip("-")

    return slug or "hermes-rust-claude-terminal"
