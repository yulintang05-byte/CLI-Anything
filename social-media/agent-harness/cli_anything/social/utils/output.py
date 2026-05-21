"""JSON and table output helpers."""
import json
from typing import Any, List, Dict, Optional


def as_json(data: Any, indent: int = 2) -> str:
    return json.dumps(data, indent=indent, ensure_ascii=False)


def as_table(rows: List[Dict], columns: List[str], max_col: int = 32) -> str:
    """Render a list of dicts as a plain-text table."""
    if not rows:
        return "(no results)"
    widths = {c: max(len(c), max(len(str(r.get(c, ""))[:max_col]) for r in rows)) for c in columns}
    sep = "+" + "+".join("-" * (widths[c] + 2) for c in columns) + "+"
    header = "|" + "|".join(f" {c:<{widths[c]}} " for c in columns) + "|"
    lines = [sep, header, sep]
    for r in rows:
        lines.append("|" + "|".join(f" {str(r.get(c,''))[:max_col]:<{widths[c]}} " for c in columns) + "|")
    lines.append(sep)
    return "\n".join(lines)


def emit(data: Any, fmt: str, columns: Optional[List[str]] = None) -> str:
    """Return formatted string for `data`. fmt is 'json' or 'table'."""
    if fmt == "json":
        return as_json(data)
    rows = data if isinstance(data, list) else [data]
    cols = columns or (list(rows[0].keys()) if rows else [])
    return as_table(rows, cols)
