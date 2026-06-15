"""Display helpers — formatted tables and pretty-print for CLI output."""

import click


def table(headers: list[str], rows: list[list[str]], max_col_width: int = 40) -> None:
    """Print an ASCII table."""
    all_rows = [headers] + [[_trunc(str(c), max_col_width) for c in row] for row in rows]
    widths = [max(len(r[i]) for r in all_rows if i < len(r)) for i in range(len(headers))]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    click.echo(sep)
    _print_row(headers, widths)
    click.echo(sep)
    for row in rows:
        _print_row([str(c) if i < len(row) else "" for i, c in enumerate(headers)], widths, row)
    click.echo(sep)


def _print_row(headers: list[str], widths: list[int], row: list = None) -> None:
    cells = row if row is not None else headers
    line = "|"
    for i, w in enumerate(widths):
        val = str(cells[i]) if i < len(cells) else ""
        val = _trunc(val, w)
        line += f" {val:<{w}} |"
    click.echo(line)


def _trunc(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 2] + ".."


def section(title: str) -> None:
    click.echo(f"\n{'='*60}")
    click.echo(f"  {title}")
    click.echo(f"{'='*60}")


def bullet_list(items: list[str], indent: int = 2) -> None:
    pad = " " * indent
    for item in items:
        click.echo(f"{pad}• {item}")


def kv_block(data: dict, indent: int = 2) -> None:
    pad = " " * indent
    for k, v in data.items():
        if isinstance(v, list):
            click.echo(f"{pad}{k}:")
            for item in v:
                click.echo(f"{pad}  - {item}")
        elif isinstance(v, dict):
            click.echo(f"{pad}{k}:")
            kv_block(v, indent + 2)
        else:
            click.echo(f"{pad}{k}: {v}")


def num(n: int) -> str:
    """Format large numbers with K/M suffixes."""
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)
