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

        Args:
            prompt: The user-turn prompt to send.
            system: Optional system prompt.

        Returns:
            The first text block from the response as a plain string.
        """
        loop = asyncio.get_event_loop()

        create_kwargs: dict[str, Any] = {
            "model": "claude-opus-4-6",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            create_kwargs["system"] = system

        partial = functools.partial(self.client.messages.create, **create_kwargs)

        response: anthropic.types.Message = await loop.run_in_executor(None, partial)

        # Extract the first text block; fall back to empty string if none.
        for block in response.content:
            if block.type == "text":
                return block.text
        return ""

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
