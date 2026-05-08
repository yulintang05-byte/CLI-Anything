"""Output formatting utilities for trend-scout CLI."""

import json
from typing import Any


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def print_section(title: str, content: Any, as_json: bool = False) -> None:
    if as_json:
        print_json({title: content})
        return
    print(f"\n{'='*60}")
    print(f"  {title.upper()}")
    print(f"{'='*60}")
    if isinstance(content, list):
        for i, item in enumerate(content, 1):
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"  [{i}] {k}: {v}")
                print()
            else:
                print(f"  {i}. {item}")
    elif isinstance(content, dict):
        _print_dict(content, indent=2)
    else:
        print(f"  {content}")


def _print_dict(d: dict, indent: int = 0) -> None:
    for k, v in d.items():
        prefix = " " * indent
        if isinstance(v, dict):
            print(f"{prefix}{k}:")
            _print_dict(v, indent + 2)
        elif isinstance(v, list):
            print(f"{prefix}{k}:")
            for item in v:
                if isinstance(item, dict):
                    for ik, iv in item.items():
                        print(f"{prefix}  - {ik}: {iv}")
                else:
                    print(f"{prefix}  - {item}")
        else:
            print(f"{prefix}{k}: {v}")


def print_hashtag_list(hashtags: list[dict], label: str = "Trending Hashtags") -> None:
    print(f"\n  {label}:")
    for h in hashtags:
        tag = h.get("hashtag", "")
        score = h.get("trending_score", h.get("frequency_in_trending", ""))
        score_str = f"  (score: {score})" if score else ""
        print(f"    {tag}{score_str}")


def print_account_summary(accounts: list[dict]) -> None:
    if not accounts:
        print("  No accounts configured. Use: trend-scout account add")
        return
    print(f"\n  Accounts ({len(accounts)} total):")
    for a in accounts:
        print(f"    [{a.get('platform', '?').upper()}] @{a.get('username', '?')} — {a.get('niche', '?')} niche — {a.get('followers', 0):,} followers")


def truncate(text: str, max_len: int = 60) -> str:
    return text[:max_len] + "..." if len(text) > max_len else text
