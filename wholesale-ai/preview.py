#!/usr/bin/env python3
"""
Preview renderer — draws the key Wholesale AI screens to an SVG so you can
see the real TUI without running it interactively. Uses the actual display
functions and data from the app (no mock-ups).
"""
import main
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from modules.deal_browser import all_strategies_analysis, HOT_MARKETS
from modules.lender_directory import HARD_MONEY_LENDERS, DSCR_LENDERS

# record=True lets us export exactly what renders
con = Console(record=True, width=150)
main.console = con  # redirect the app's console into our recorder

con.print(main.BANNER)

# ── 1. Main menu panel (trimmed) ──────────────────────────────────────────────
con.rule("[bold cyan]MAIN MENU (Command Center)[/bold cyan]")
con.print(Panel(
    "  Profile: [green]Albert | Real Estate LLC[/green]   Agents: [dim]○ Idle[/dim]"
    "   Earned: [bold green]$0[/bold green]   Close Rate: [cyan]0%[/cyan]\n\n"
    "  [bold green]── FIND DEALS ──[/bold green]\n"
    "  [cyan][1][/cyan] Browse Gov & Distressed   [cyan][2][/cyan] Hot Markets   "
    "[cyan][23][/cyan] [bold]LIVE Lead Finder[/bold]   [cyan][24][/cyan] Luxury Wholesale\n"
    "  [bold green]── ANALYZE ──[/bold green]\n"
    "  [cyan][3][/cyan] [bold]Deal Card — ALL 4 Strategies[/bold]   [cyan][25][/cyan] Lender Directory\n"
    "  [bold green]── AI AGENTS (Goal: $10k-$30k/mo) ──[/bold green]\n"
    "  [cyan][26][/cyan] [bold]Run All Agents[/bold]   [cyan][27][/cyan] Agent Dashboard\n"
    "  [bold green]── CLOSE & SCALE ──[/bold green]\n"
    "  [cyan][12][/cyan] Pipeline/CRM   [cyan][14][/cyan] Section 8/VASH   [cyan][29][/cyan] Pre-Screen Tenants",
    title="[bold green]WHOLESALE AI[/bold green]", border_style="green",
))

# ── 2. The flagship: full deal card, all 4 strategies on a real Detroit deal ──
con.rule("[bold cyan]OPTION 3 — DEAL CARD (all 4 strategies, one screen)[/bold cyan]")
detroit = next(m for m in HOT_MARKETS if m["city"].lower() == "detroit")
data = all_strategies_analysis(
    price=detroit["avg_price"], arv=detroit["avg_price"] * 8,
    market_rent=detroit["avg_rent"], sqft=1000, bedrooms=3,
    state="MI", condition="medium", buyer_credit_score=730, buyer_cash=12000,
)
main.display_full_deal_card(data, address="Detroit, MI", badge="TAX DEED / LAND BANK")

# ── 3. Lender directory ───────────────────────────────────────────────────────
con.rule("[bold cyan]OPTION 25 — LENDER DIRECTORY (Hard Money)[/bold cyan]")
t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
for c in ("Lender", "Rates", "Min Credit", "Specialty"):
    t.add_column(c)
for L in HARD_MONEY_LENDERS[:6]:
    t.add_row(L["name"], L["rates"], str(L["min_credit"]), L["specialty"])
con.print(t)

# ── 4. Agent dashboard (empty/fresh state) ────────────────────────────────────
con.rule("[bold cyan]OPTION 27 — AGENT DASHBOARD[/bold cyan]")
con.print(Panel(
    "  Status: [dim]○ Idle[/dim]\n\n"
    "  Total Earned: [bold green]$0[/bold green]   Deals Won: [cyan]0[/cyan]  Lost: [red]0[/red]\n"
    "  Close Rate: [bold]0%[/bold]   Avg Assignment Fee: [green]$0[/green]\n\n"
    "  [dim]Run option 26 to have the agents scan, score, and queue deals.[/dim]",
    title="[bold green]AGENT PERFORMANCE[/bold green]", border_style="green",
))

con.save_svg("preview.svg", title="Wholesale AI — Preview")
print("Wrote preview.svg")
