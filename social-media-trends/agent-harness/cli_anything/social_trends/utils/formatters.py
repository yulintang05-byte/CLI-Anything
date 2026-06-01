#!/usr/bin/env python3
"""Output formatters for the social trends CLI."""


def fmt_table(rows: list[dict], columns: list[str] = None) -> str:
    """Format a list of dicts as a text table."""
    if not rows:
        return "(no data)"
    cols = columns or list(rows[0].keys())
    widths = {c: max(len(c), max(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    header = "  ".join(c.ljust(widths[c]) for c in cols)
    sep = "  ".join("-" * widths[c] for c in cols)
    body = "\n".join(
        "  ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols) for r in rows
    )
    return f"{header}\n{sep}\n{body}"


def fmt_list(items: list, bullet: str = "•") -> str:
    """Format a list with bullet points."""
    return "\n".join(f"  {bullet} {item}" for item in items)
