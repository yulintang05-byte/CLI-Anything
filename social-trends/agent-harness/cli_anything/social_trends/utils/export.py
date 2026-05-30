#!/usr/bin/env python3
"""Export utilities — write trend reports and analysis to JSON, CSV, or Markdown."""

import csv
import io
import json
from datetime import datetime
from typing import Any


def to_json(data: Any, pretty: bool = True) -> str:
    """Serialize data to JSON string."""
    return json.dumps(data, indent=2 if pretty else None, default=str)


def to_csv(data: list[dict], headers: list[str] | None = None) -> str:
    """Convert a list of dicts to CSV string."""
    if not data:
        return ""
    if headers is None:
        headers = list(data[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(data)
    return buf.getvalue()


def to_markdown(data: dict, title: str = "Trend Report") -> str:
    """Convert trend/analysis data to a human-readable Markdown report."""
    lines = [f"# {title}", f"", f"*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*", ""]

    def _render_value(v, depth=0):
        indent = "  " * depth
        if isinstance(v, dict):
            parts = []
            for k2, v2 in v.items():
                parts.append(f"{indent}**{k2}**: {_render_value(v2, depth + 1)}")
            return "\n" + "\n".join(parts)
        if isinstance(v, list):
            if not v:
                return "*(empty)*"
            if all(isinstance(i, (str, int, float, bool)) for i in v):
                return ", ".join(str(i) for i in v)
            parts = []
            for item in v:
                if isinstance(item, dict):
                    parts.append(f"{indent}- " + ", ".join(f"**{k}**: {v_}" for k, v_ in item.items()))
                else:
                    parts.append(f"{indent}- {item}")
            return "\n" + "\n".join(parts)
        return str(v)

    for section_key, section_val in data.items():
        if section_key in ("generated_at", "metadata"):
            continue
        heading = section_key.replace("_", " ").title()
        lines.append(f"## {heading}")
        lines.append("")
        if isinstance(section_val, list):
            if section_val and isinstance(section_val[0], dict):
                # Table for list of dicts
                cols = list(section_val[0].keys())
                lines.append("| " + " | ".join(cols) + " |")
                lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
                for row in section_val[:30]:
                    cells = [str(row.get(c, "")) for c in cols]
                    lines.append("| " + " | ".join(cells) + " |")
            else:
                for item in section_val:
                    lines.append(f"- {item}")
        elif isinstance(section_val, dict):
            for k, v in section_val.items():
                lines.append(f"**{k}**: {_render_value(v)}")
                lines.append("")
        else:
            lines.append(str(section_val))
        lines.append("")

    return "\n".join(lines)


def save_to_file(data: Any, path: str, fmt: str = "json") -> str:
    """Save data to a file in the given format.

    Args:
        data: Data to export
        path: Output file path
        fmt: json | csv | markdown

    Returns:
        Absolute path of the written file
    """
    if fmt == "json":
        content = to_json(data)
    elif fmt == "csv":
        if isinstance(data, list):
            content = to_csv(data)
        elif isinstance(data, dict):
            # Try to find a primary list key
            for key in ["videos", "hashtags", "sounds", "recommendations", "music_tracks"]:
                if key in data and isinstance(data[key], list):
                    content = to_csv(data[key])
                    break
            else:
                content = to_csv([data])
        else:
            content = str(data)
    elif fmt == "markdown":
        title = "Social Trends Report"
        if isinstance(data, dict):
            title = data.get("title", title)
        content = to_markdown(data if isinstance(data, dict) else {"data": data}, title)
    else:
        raise ValueError(f"Unknown format: {fmt}. Use json, csv, or markdown.")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return path
