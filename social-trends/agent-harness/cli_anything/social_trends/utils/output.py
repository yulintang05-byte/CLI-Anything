"""Output formatting — JSON or human-readable tables."""

import json
import sys
from typing import Any


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def print_table(rows: list[dict], columns: list[str] | None = None) -> None:
    if not rows:
        print("(no data)")
        return
    cols = columns or list(rows[0].keys())
    widths = {c: max(len(c), max(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    header = "  ".join(c.upper().ljust(widths[c]) for c in cols)
    sep = "  ".join("-" * widths[c] for c in cols)
    print(header)
    print(sep)
    for r in rows:
        print("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols))


def print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title.upper()}")
    print(f"{'=' * 60}")


def print_list(items: list[str], indent: int = 2) -> None:
    pad = " " * indent
    for item in items:
        print(f"{pad}• {item}")
