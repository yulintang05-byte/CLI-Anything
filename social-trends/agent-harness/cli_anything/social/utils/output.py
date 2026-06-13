"""Formatted output helpers (rich tables, JSON, colored text)."""
import json
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text

console = Console()


def print_banner():
    console.print(
        Panel.fit(
            "[bold cyan]Social Trends CLI[/bold cyan]\n"
            "[dim]YouTube & TikTok viral trend scraper + account optimizer[/dim]",
            border_style="cyan",
        )
    )


def print_json(data: Any):
    console.print_json(json.dumps(data, indent=2, default=str))


def print_table(title: str, rows: List[Dict], columns: List[str], styles: Dict[str, str] = None):
    table = Table(title=title, box=box.ROUNDED, show_lines=True)
    for col in columns:
        style = (styles or {}).get(col, "")
        table.add_column(col, style=style, overflow="fold")
    for row in rows:
        table.add_row(*[str(row.get(c, "")) for c in columns])
    console.print(table)


def print_section(title: str, items: List[str], color: str = "green"):
    console.print(f"\n[bold {color}]{title}[/bold {color}]")
    for i, item in enumerate(items, 1):
        console.print(f"  [dim]{i:>2}.[/dim] {item}")


def print_success(msg: str):
    console.print(f"[bold green]✓[/bold green] {msg}")


def print_warning(msg: str):
    console.print(f"[bold yellow]⚠[/bold yellow]  {msg}")


def print_error(msg: str):
    console.print(f"[bold red]✗[/bold red] {msg}")


def print_info(msg: str):
    console.print(f"[bold blue]ℹ[/bold blue]  {msg}")
