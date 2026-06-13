"""Base agent class for all Hermes marketing agents."""
from __future__ import annotations

import asyncio
import functools
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import anthropic

from .. import config


class BaseAgent(ABC):
    """Abstract base class for all marketing agents.

    Subclasses must implement ``run()`` and return a dict with at minimum the
    keys ``agent``, ``content``, ``platform``, and ``status``.
    """

    def __init__(self, name: str, client: anthropic.Anthropic) -> None:
        self.name = name
        self.client = client
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # ------------------------------------------------------------------
    # Core generation helper
    # ------------------------------------------------------------------

    async def generate(self, prompt: str, system: str = "") -> str:
        """Call the Claude API asynchronously (runs the blocking SDK call in a
        thread-pool executor so the event loop is never blocked).

        Uses the model and token budget from config, with prompt caching on
        the system prompt so repeated agent runs reuse cached prefix tokens.
        Falls back through MODEL_FALLBACKS if the primary model is rejected.

        Args:
            prompt: The user-turn prompt to send.
            system: Optional system prompt.

        Returns:
            The first text block from the response as a plain string.
        """
        loop = asyncio.get_event_loop()

        last_error: Exception | None = None
        for model in [config.MODEL, *config.MODEL_FALLBACKS]:
            create_kwargs: dict[str, Any] = {
                "model": model,
                "max_tokens": config.MAX_TOKENS,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system:
                # Cache the system prompt: agents reuse the same system text
                # across waves, so subsequent calls hit the prompt cache.
                create_kwargs["system"] = [
                    {
                        "type": "text",
                        "text": system,
                        "cache_control": {"type": "ephemeral"},
                    }
                ]

            partial = functools.partial(self.client.messages.create, **create_kwargs)
            try:
                response: anthropic.types.Message = await loop.run_in_executor(
                    None, partial
                )
            except anthropic.NotFoundError as exc:
                # Model not available on this account — try the next fallback.
                last_error = exc
                continue

            for block in response.content:
                if block.type == "text":
                    return block.text
            return ""

        raise RuntimeError(
            f"All models failed ({[config.MODEL, *config.MODEL_FALLBACKS]}): {last_error}"
        )

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    async def run(self) -> dict[str, Any]:
        """Execute the agent's primary task.

        Must return a dict with at least::

            {
                "agent":    self.name,       # str
                "content":  <generated str>, # str
                "platform": <platform name>, # str
                "status":   "generated",     # str
            }

        Agents that successfully post to a platform should set
        ``"status"`` to ``"posted"`` and may include additional keys
        (e.g. ``"url"``).
        """

    # ------------------------------------------------------------------
    # Output persistence
    # ------------------------------------------------------------------

    def save_output(self, filename: str, content: str) -> str:
        """Persist *content* to ``config.OUTPUT_DIR`` with a timestamp prefix.

        Args:
            filename: Base filename (e.g. ``"thread.txt"``).  A UTC timestamp
                is prepended automatically so files never collide.
            content: Text content to write.

        Returns:
            The absolute path of the file that was written.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        timestamped_name = f"{timestamp}_{filename}"
        path = os.path.join(config.OUTPUT_DIR, timestamped_name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        return path
