#!/usr/bin/env python3
"""
Wholesale AI — Real Estate Wholesale + Gov Property Finder
Free alternative to Tranchi.ai built on public gov data + Claude AI.

Usage: python main.py
"""
import os
import sys
from pathlib import Path
from typing import Optional

# Load .env before anything else
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, FloatPrompt, IntPrompt
from rich.text import Text
from rich.columns import Columns
from rich import box
from rich.rule import Rule
from rich.markdown import Markdown

from modules.deal_calculator import (
    calculate_deal, DealInputs, estimate_repairs,
    quick_mao, cash_flow_analysis,
)
from modules.hud_search import (
    get_fair_market_rents, build_hud_homestore_url,
    build_foreclosure_search_url, get_gsa_properties_url,
    get_tax_lien_resources,
)
from modules.ai_advisor import (
    analyze_deal, generate_negotiation_script,
    generate_offer_letter, explain_strategy,
    ask_advisor, find_cash_buyers_strategy,
)
from modules.market_data import (
    get_zip_info, estimate_arv_by_market, get_repair_cost_guide,
    get_wholesale_checklist, get_motivated_seller_sources,
)

console = Console()


# ── Branding ─────────────────────────────────────────────────────────────────

BANNER = """[bold green]
 ██╗    ██╗██╗  ██╗ ██████╗ ██╗     ███████╗███████╗ █████╗ ██╗     ███████╗
 ██║    ██║██║  ██║██╔═══██╗██║     ██╔════╝██╔════╝██╔══██╗██║     ██╔════╝
 ██║ █╗ ██║███████║██║   ██║██║     █████╗  ███████╗███████║██║     █████╗
 ██║███╗██║██╔══██║██║   ██║██║     ██╔══╝  ╚════██║██╔══██║██║     ██╔══╝
 ╚███╔███╔╝██║  ██║╚██████╔╝███████╗███████╗███████║██║  ██║███████╗███████╗
  ╚══╝╚══╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝[/bold green]
[bold yellow]          AI-Powered Real Estate Wholesale + Gov Property Finder[/bold yellow]
[dim]          Find gov-owned & distressed properties under market value[/dim]
"""


def show_banner():
    console.print(BANNER)
    ai_status = "[green]✓ Active[/green]" if os.getenv("ANTHROPIC_API_KEY") else "[red]✗ Not set (add to .env)[/red]"
    hud_status = "[green]✓ Active[/green]" if os.getenv("HUD_API_TOKEN") else "[yellow]○ Optional (huduser.gov)[/yellow]"
    console.print(f"  AI Advisor: {ai_status}   HUD FMR API: {hud_status}\n")


# ── Helpers ───────────────────────────────────────────────────────────────────

def currency(v: float) -> str:
    return f"${v:,.0f}"


def pct(v: float) -> str:
    return f"{v:.1f}%"


def grade_color(g: str) -> str:
    return {"A": "green", "B": "cyan", "C": "yellow", "F": "red"}.get(g, "white")


def press_enter():
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def section(title: str):
    console.print()
    console.rule(f"[bold cyan]{title}[/bold cyan]")
    console.print()


# ── Menus ────────────────────────────────────────────────────────────────────

def main_menu():
    while True:
        show_banner()
        console.print(Panel(
            "\n"
            "  [bold cyan][1][/bold cyan]  Deal Calculator (MAO / ARV / ROI)\n"
            "  [bold cyan][2][/bold cyan]  Find Gov & Distressed Properties\n"
            "  [bold cyan][3][/bold cyan]  AI Deal Analyzer\n"
            "  [bold cyan][4][/bold cyan]  Generate Negotiation Script\n"
            "  [bold cyan][5][/bold cyan]  Generate Offer Letter / LOI\n"
            "  [bold cyan][6][/bold cyan]  HUD Fair Market Rents Lookup\n"
            "  [bold cyan][7][/bold cyan]  Wholesale Strategy Guide\n"
            "  [bold cyan][8][/bold cyan]  Find Cash Buyers Strategy\n"
            "  [bold cyan][9][/bold cyan]  Repair Cost Guide\n"
            "  [bold cyan][10][/bold cyan] Ask the AI Advisor Anything\n"
            "  [bold cyan][11][/bold cyan] Setup & API Keys\n"
            "  [bold cyan][0][/bold cyan]  Exit\n",
            title="[bold green]MAIN MENU[/bold green]",
            border_style="green",
        ))

        choice = Prompt.ask("[bold]Select[/bold]", choices=["0","1","2","3","4","5","6","7","8","9","10","11"])

        if choice == "0":
            console.print("\n[bold green]Go get that bag. 💰[/bold green]\n")
            sys.exit(0)
        elif choice == "1":
            menu_deal_calculator()
        elif choice == "2":
            menu_property_search()
        elif choice == "3":
            menu_ai_deal_analyzer()
        elif choice == "4":
            menu_negotiation_script()
        elif choice == "5":
            menu_offer_letter()
        elif choice == "6":
            menu_hud_fmr()
        elif choice == "7":
            menu_strategy_guide()
        elif choice == "8":
            menu_cash_buyers()
        elif choice == "9":
            menu_repair_guide()
        elif choice == "10":
            menu_ask_advisor()
        elif choice == "11":
            menu_setup()


# ── 1. Deal Calculator ────────────────────────────────────────────────────────

def menu_deal_calculator():
    section("DEAL CALCULATOR")
    console.print("[dim]Run the numbers on any potential deal using the 70% Rule.[/dim]\n")

    sub = Prompt.ask(
        "What do you want to calculate?",
        choices=["mao", "cashflow", "repair"],
        default="mao",
    )

    if sub == "mao":
        _calc_mao()
    elif sub == "cashflow":
        _calc_cashflow()
    elif sub == "repair":
        _calc_repair()


def _calc_mao():
    console.print("\n[bold]Enter deal details[/bold] (press Enter to skip optional fields)\n")

    arv = FloatPrompt.ask("After Repair Value (ARV) — what similar fixed-up homes sell for")
    repairs = FloatPrompt.ask("Estimated repair cost")
    asking = FloatPrompt.ask("Seller's asking price")
    fee = FloatPrompt.ask("Your wholesale fee target", default=10000)
    discount = FloatPrompt.ask("ARV discount % (70 = standard, 65 = stricter)", default=70) / 100

    inputs = DealInputs(
        arv=arv,
        repair_cost=repairs,
        purchase_price=asking,
        wholesale_fee=fee,
        arv_discount=discount,
    )
    result = calculate_deal(inputs)
    _display_deal_result(result, asking)


def _display_deal_result(result, asking_price: float):
    console.print()
    grade_c = grade_color(result.grade)

    # Main panel
    grade_text = f"[bold {grade_c}]GRADE: {result.grade}[/bold {grade_c}]"
    deal_text = "[bold green]✓ IT'S A DEAL[/bold green]" if result.is_deal else "[bold red]✗ NOT A DEAL AT ASKING PRICE[/bold red]"

    console.print(Panel(
        f"{grade_text}  {deal_text}",
        border_style=grade_c,
    ))

    # Numbers table
    t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    t.add_column("Metric", style="bold")
    t.add_column("Amount", justify="right")
    t.add_column("Notes")

    t.add_row("ARV (Fixed-up value)", currency(result.arv), "Pull real comps!")
    t.add_row("Repair Estimate", currency(result.repair_cost), "Get contractor bids")
    t.add_row("Seller Asking", currency(asking_price), "")
    t.add_row("─" * 20, "─" * 10, "")
    t.add_row("[bold]Max Allowable Offer (MAO)[/bold]", f"[bold green]{currency(result.mao)}[/bold green]", "Most you can pay seller")
    t.add_row("Suggested Opening Offer", currency(result.suggested_offer), "~12% below MAO (room to negotiate)")
    t.add_row("─" * 20, "─" * 10, "")
    t.add_row("Max End Buyer Price", currency(result.max_end_buyer_price), "MAO + your fee")
    t.add_row("[bold yellow]Your Wholesale Fee[/bold yellow]", f"[bold yellow]{currency(result.profit_at_mao)}[/bold yellow]", "If you pay MAO")
    t.add_row("Your Cash Needed (EMD)", currency(result.cash_in_deal), "Earnest money only")
    t.add_row("Equity Spread", currency(result.equity_spread), "ARV - (price + repairs)")

    console.print(t)

    if not result.is_deal:
        gap = asking_price - result.mao
        console.print(f"\n[bold red]Seller needs to come down {currency(gap)} to make this work.[/bold red]")
        console.print(f"[yellow]Negotiate from your opening offer of {currency(result.suggested_offer)}.[/yellow]")

    if result.notes:
        console.print("\n[bold]Notes:[/bold]")
        for note in result.notes:
            console.print(f"  • {note}")

    press_enter()


def _calc_cashflow():
    console.print("\n[bold]Buy-and-Hold Cash Flow Analysis[/bold]\n")

    purchase = FloatPrompt.ask("Purchase price")
    rent = FloatPrompt.ask("Expected monthly rent")
    down_pct = FloatPrompt.ask("Down payment %", default=20) / 100
    rate = FloatPrompt.ask("Interest rate %", default=7.0) / 100
    tax = FloatPrompt.ask("Monthly property tax estimate", default=250)
    insurance = FloatPrompt.ask("Monthly insurance estimate", default=120)

    result = cash_flow_analysis(
        purchase_price=purchase,
        monthly_rent=rent,
        down_pct=down_pct,
        interest_rate=rate,
        tax_monthly=tax,
        insurance_monthly=insurance,
    )

    t = Table(show_header=False, box=box.ROUNDED)
    t.add_column("Metric", style="bold")
    t.add_column("Value", justify="right")

    t.add_row("Down Payment", currency(result["down_payment"]))
    t.add_row("Monthly Mortgage (P&I)", currency(result["monthly_payment"]))
    t.add_row("Gross Monthly Income", currency(result["gross_income"]))
    t.add_row("Effective Income (8% vacancy)", currency(result["effective_income"]))
    t.add_row("Total Monthly Expenses", currency(result["total_expenses"]))
    t.add_row("─" * 25, "─" * 12)
    cf = result["monthly_cash_flow"]
    cf_color = "green" if cf > 0 else "red"
    t.add_row(f"[bold {cf_color}]Monthly Cash Flow[/bold {cf_color}]", f"[bold {cf_color}]{currency(cf)}[/bold {cf_color}]")
    t.add_row("Annual Cash Flow", currency(result["annual_cash_flow"]))
    t.add_row("Cap Rate", pct(result["cap_rate"]))
    t.add_row("Cash-on-Cash Return", pct(result["cash_on_cash"]))

    console.print(t)
    press_enter()


def _calc_repair():
    console.print("\n[bold]Repair Cost Estimator[/bold]\n")
    sqft = FloatPrompt.ask("Property square footage")
    condition = Prompt.ask("Condition", choices=["light", "medium", "heavy", "gut"], default="medium")
    est = estimate_repairs(sqft, condition)

    console.print(f"\n[bold green]Estimated Repair Cost: {currency(est)}[/bold green]")
    console.print(f"[dim]Based on {condition} condition at ~${int(est/sqft)}/sqft for {sqft:,.0f} sqft[/dim]")
    console.print("[yellow]⚠  Always get real contractor bids before making an offer[/yellow]")
    press_enter()


# ── 2. Property Search ───────────────────────────────────────────────────────

def menu_property_search():
    section("FIND GOV & DISTRESSED PROPERTIES")
    console.print("[dim]All sources below are free. Click the links or copy to your browser.[/dim]\n")

    state = Prompt.ask("State abbreviation (e.g. TX, FL, GA)", default="").upper()
    zip_code = Prompt.ask("Zip code (optional)", default="")
    max_price = 0
    if Confirm.ask("Filter by max price?", default=False):
        max_price = int(FloatPrompt.ask("Max price"))

    # ZIP info
    if zip_code:
        info = get_zip_info(zip_code)
        if "city" in info:
            console.print(f"\n[green]📍 {info['city']}, {info['state']} ({info.get('county', '')} County)[/green]")

    # Foreclosure / REO search links
    foreclosure_urls = build_foreclosure_search_url(state=state, zip_code=zip_code, max_price=max_price)

    console.print("\n[bold cyan]── GOVERNMENT-OWNED PROPERTIES (Below Market) ──[/bold cyan]")
    gov_keys = ["HUD Home Store (Gov Owned)", "HomePath (Fannie Mae Gov)", "HomeSteps (Freddie Mac Gov)",
                "USDA Rural Properties (Gov)", "GSA Property Auctions"]
    _print_url_table("Source", foreclosure_urls, highlight_keys=gov_keys)

    console.print("\n[bold cyan]── FORECLOSURES & BANK-OWNED (REO) ──[/bold cyan]")
    reo_keys = ["Foreclosure.com (Free)", "Auction.com (REO/Bank Owned)", "Hubzu (Bank Owned)"]
    _print_url_table("Source", {k: v for k, v in foreclosure_urls.items() if k in reo_keys})

    # GSA & federal
    console.print("\n[bold cyan]── FEDERAL / SEIZED ASSET AUCTIONS ──[/bold cyan]")
    gsa = get_gsa_properties_url()
    _print_url_table("Agency", gsa)

    # Tax liens
    console.print("\n[bold cyan]── TAX LIEN & TAX DEED SALES ──[/bold cyan]")
    liens = get_tax_lien_resources(state=state)
    _print_url_table("Resource", liens)

    # Motivated seller sources
    console.print("\n[bold cyan]── FREE MOTIVATED SELLER SOURCES ──[/bold cyan]")
    sources = get_motivated_seller_sources()
    for category, items in sources.items():
        console.print(f"\n[bold yellow]{category}[/bold yellow]")
        for name, info in items.items():
            console.print(f"  • [bold]{name}:[/bold] {info}")

    press_enter()


def _print_url_table(col1: str, data: dict, highlight_keys: list = None):
    t = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
    t.add_column(col1, style="bold", min_width=30)
    t.add_column("URL / Instructions")

    for k, v in data.items():
        style = "green" if (highlight_keys and k in highlight_keys) else "white"
        t.add_row(f"[{style}]{k}[/{style}]", v)
    console.print(t)


# ── 3. AI Deal Analyzer ──────────────────────────────────────────────────────

def menu_ai_deal_analyzer():
    section("AI DEAL ANALYZER")
    _check_ai_key()

    console.print("[dim]Get a full AI analysis of any deal — grade, strategy, red flags, next steps.[/dim]\n")

    address = Prompt.ask("Property address (or description)", default="123 Main St, Atlanta GA")
    arv = FloatPrompt.ask("After Repair Value (ARV)")
    repairs = FloatPrompt.ask("Estimated repairs")
    asking = FloatPrompt.ask("Seller asking price")
    prop_type = Prompt.ask("Property type", default="single family")
    bedrooms = IntPrompt.ask("Bedrooms", default=3)
    sqft = IntPrompt.ask("Square footage", default=1500)
    condition = Prompt.ask("Condition", choices=["light", "medium", "heavy", "gut"], default="medium")
    source = Prompt.ask("Where'd you find it?", default="HUD homestore")
    notes = Prompt.ask("Any extra notes (motivation, liens, etc.)", default="")

    console.print("\n[dim]Analyzing deal...[/dim]")
    result = analyze_deal(
        address=address,
        asking_price=asking,
        arv=arv,
        repairs=repairs,
        property_type=prop_type,
        bedrooms=bedrooms,
        sqft=sqft,
        condition=condition,
        source=source,
        notes=notes,
    )

    console.print(Panel(Markdown(result), title="[bold green]AI Deal Analysis[/bold green]", border_style="green"))
    press_enter()


# ── 4. Negotiation Script ─────────────────────────────────────────────────────

def menu_negotiation_script():
    section("NEGOTIATION SCRIPT GENERATOR")
    _check_ai_key()

    console.print("[dim]Get a word-for-word script tailored to your seller's situation.[/dim]\n")

    situation = Prompt.ask(
        "Seller situation",
        default="behind on mortgage, property needs major repairs, wants to avoid foreclosure",
    )
    asking = FloatPrompt.ask("Seller's asking price")
    your_offer = FloatPrompt.ask("Your target offer")
    address = Prompt.ask("Property address (optional)", default="")
    motivation = Prompt.ask("Known seller motivation (financial stress, divorce, inheritance, etc.)", default="")

    console.print("\n[dim]Generating script...[/dim]")
    script = generate_negotiation_script(
        seller_situation=situation,
        asking_price=asking,
        your_offer=your_offer,
        property_address=address,
        seller_motivation=motivation,
    )

    console.print(Panel(Markdown(script), title="[bold cyan]Negotiation Script[/bold cyan]", border_style="cyan"))
    press_enter()


# ── 5. Offer Letter ───────────────────────────────────────────────────────────

def menu_offer_letter():
    section("OFFER LETTER / LOI GENERATOR")
    _check_ai_key()

    console.print("[dim]Generate a professional Letter of Intent ready to send to the seller.[/dim]\n")

    buyer = Prompt.ask("Your name (or company name)")
    seller = Prompt.ask("Seller's name")
    address = Prompt.ask("Property address")
    offer = FloatPrompt.ask("Offer price")
    emd = FloatPrompt.ask("Earnest money deposit", default=1000)
    closing = IntPrompt.ask("Closing days from acceptance", default=21)
    inspection = IntPrompt.ask("Inspection period days", default=14)
    assignment = Confirm.ask("Include assignment clause? (needed for wholesale)", default=True)
    extra = Prompt.ask("Any extra terms or conditions?", default="")

    console.print("\n[dim]Drafting offer letter...[/dim]")
    letter = generate_offer_letter(
        buyer_name=buyer,
        seller_name=seller,
        property_address=address,
        offer_price=offer,
        earnest_money=emd,
        closing_days=closing,
        assignment_clause=assignment,
        inspection_days=inspection,
        extra_terms=extra,
    )

    console.print(Panel(Markdown(letter), title="[bold yellow]Offer Letter / LOI[/bold yellow]", border_style="yellow"))

    if Confirm.ask("\nSave to file?", default=True):
        safe_addr = address.replace(" ", "_").replace(",", "").replace("/", "")[:40]
        filename = f"LOI_{safe_addr}.txt"
        Path(filename).write_text(letter)
        console.print(f"[green]Saved to {filename}[/green]")

    press_enter()


# ── 6. HUD Fair Market Rents ─────────────────────────────────────────────────

def menu_hud_fmr():
    section("HUD FAIR MARKET RENTS")
    console.print("[dim]Official HUD rent data by state/county — use to verify rental comps.[/dim]\n")

    state = Prompt.ask("State abbreviation (e.g. GA, TX, FL)").upper()

    if not os.getenv("HUD_API_TOKEN"):
        console.print(Panel(
            "[yellow]HUD_API_TOKEN not set.[/yellow]\n\n"
            "Get your [bold]free[/bold] token at:\n"
            "  [cyan]https://www.huduser.gov/portal/dataset/api.html[/cyan]\n\n"
            "Then add to your [bold].env[/bold] file:\n"
            "  HUD_API_TOKEN=your-token-here\n\n"
            "Meanwhile, check rent data manually:\n"
            "  [cyan]https://www.huduser.gov/portal/datasets/fmr.html[/cyan]",
            title="HUD API Token Needed",
            border_style="yellow",
        ))
        press_enter()
        return

    console.print(f"\n[dim]Fetching HUD Fair Market Rents for {state}...[/dim]")
    data = get_fair_market_rents(state)

    if "error" in data:
        console.print(f"[red]Error: {data['error']}[/red]")
        if "signup_url" in data:
            console.print(f"[cyan]Get token at: {data['signup_url']}[/cyan]")
        press_enter()
        return

    records = data.get("data", [])
    if not records:
        console.print("[yellow]No FMR data returned for that state.[/yellow]")
        press_enter()
        return

    t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    t.add_column("County")
    t.add_column("State")
    t.add_column("Year")
    t.add_column("0BR", justify="right")
    t.add_column("1BR", justify="right")
    t.add_column("2BR", justify="right")
    t.add_column("3BR", justify="right")
    t.add_column("4BR", justify="right")

    for r in records:
        t.add_row(
            r.get("county", ""),
            r.get("state", ""),
            str(r.get("year", "")),
            currency(r.get("rent_0br", 0)),
            currency(r.get("rent_1br", 0)),
            currency(r.get("rent_2br", 0)),
            currency(r.get("rent_3br", 0)),
            currency(r.get("rent_4br", 0)),
        )

    console.print(t)
    console.print("[dim]Source: HUD USER API — official government data[/dim]")
    press_enter()


# ── 7. Strategy Guide ────────────────────────────────────────────────────────

def menu_strategy_guide():
    section("WHOLESALE STRATEGY GUIDE")

    strategies = {
        "1": ("assignment", "Assignment of Contract (most common)"),
        "2": ("double close", "Double Closing / Simultaneous Close"),
        "3": ("subject-to", "Subject-To (take over mortgage)"),
        "4": ("seller finance", "Seller Financing"),
        "5": ("tax lien", "Tax Lien Investing"),
        "6": ("tax deed", "Tax Deed / Tax Sale"),
        "7": ("hud", "Buying HUD Homes"),
        "8": ("pre-foreclosure", "Pre-Foreclosure / NOD"),
        "9": ("probate", "Probate Real Estate"),
    }

    console.print("[bold]Choose a strategy to learn:[/bold]\n")
    for k, (_, label) in strategies.items():
        console.print(f"  [{k}] {label}")
    console.print()

    choice = Prompt.ask("Select", choices=list(strategies.keys()))
    strategy_key, strategy_label = strategies[choice]

    if os.getenv("ANTHROPIC_API_KEY"):
        console.print(f"\n[dim]Loading AI guide for {strategy_label}...[/dim]")
        result = explain_strategy(strategy_key)
        console.print(Panel(Markdown(result), title=f"[bold green]{strategy_label}[/bold green]", border_style="green"))
    else:
        _show_wholesale_checklist()

    press_enter()


def _show_wholesale_checklist():
    console.print("\n[bold cyan]WHOLESALE DEAL CHECKLIST[/bold cyan]\n")
    for step in get_wholesale_checklist():
        console.print(f"  {step}")
    console.print(
        "\n[yellow]Tip: Add ANTHROPIC_API_KEY to .env for detailed AI strategy guides.[/yellow]\n"
        "[dim]Free key at: https://console.anthropic.com/[/dim]"
    )


# ── 8. Cash Buyers ───────────────────────────────────────────────────────────

def menu_cash_buyers():
    section("FIND CASH BUYERS")
    _check_ai_key()

    market = Prompt.ask("Your target market (city, state, or metro area)", default="Atlanta, GA")
    prop_type = Prompt.ask("Property type you're wholesaling", default="single family")

    console.print(f"\n[dim]Building cash buyer strategy for {market}...[/dim]")
    strategy = find_cash_buyers_strategy(market=market, property_type=prop_type)

    console.print(Panel(Markdown(strategy), title="[bold cyan]Cash Buyer Strategy[/bold cyan]", border_style="cyan"))
    press_enter()


# ── 9. Repair Guide ──────────────────────────────────────────────────────────

def menu_repair_guide():
    section("REPAIR COST REFERENCE GUIDE")
    guide = get_repair_cost_guide()

    console.print(f"[bold red]⚠  {guide['disclaimer']}[/bold red]\n")

    for category, items in guide.items():
        if category == "disclaimer":
            continue
        console.print(f"\n[bold cyan]{category.replace('_', ' ').title()}[/bold cyan]")
        t = Table(show_header=False, box=box.SIMPLE)
        t.add_column("Item", style="bold")
        t.add_column("Cost Range", justify="right", style="green")
        for item, cost in items.items():
            t.add_row(item, cost)
        console.print(t)

    press_enter()


# ── 10. Ask Advisor ──────────────────────────────────────────────────────────

def menu_ask_advisor():
    section("ASK THE AI ADVISOR")
    _check_ai_key()

    console.print("[dim]Ask anything about wholesaling, deal structures, finding deals, contracts, etc.[/dim]\n")

    while True:
        question = Prompt.ask("[bold cyan]Your question[/bold cyan]")
        if question.lower() in ("exit", "quit", "back", "q"):
            break

        console.print("\n[dim]Thinking...[/dim]")
        answer = ask_advisor(question)
        console.print(Panel(Markdown(answer), border_style="green"))
        console.print()

        if not Confirm.ask("Ask another question?", default=True):
            break


# ── 11. Setup ────────────────────────────────────────────────────────────────

def menu_setup():
    section("SETUP & API KEYS")

    ai_key = os.getenv("ANTHROPIC_API_KEY", "")
    hud_key = os.getenv("HUD_API_TOKEN", "")

    console.print(Panel(
        f"[bold]Current Configuration:[/bold]\n\n"
        f"  ANTHROPIC_API_KEY: {'[green]✓ Set[/green]' if ai_key else '[red]✗ Not set[/red]'}\n"
        f"  HUD_API_TOKEN:     {'[green]✓ Set[/green]' if hud_key else '[yellow]○ Not set (optional)[/yellow]'}\n\n"
        f"[bold]How to set up:[/bold]\n\n"
        f"  1. Copy [bold].env.example[/bold] → [bold].env[/bold]\n"
        f"  2. Add your keys to [bold].env[/bold]\n"
        f"  3. Restart the app\n\n"
        f"[bold]Get free API keys:[/bold]\n\n"
        f"  [cyan]Claude AI (AI Advisor):[/cyan]\n"
        f"    https://console.anthropic.com/\n"
        f"    → Create account → API Keys → Create Key\n"
        f"    → Free $5 credit to start\n\n"
        f"  [cyan]HUD API (Fair Market Rents):[/cyan]\n"
        f"    https://www.huduser.gov/portal/dataset/api.html\n"
        f"    → Register → Request token → Free forever\n\n"
        f"[bold]Cost comparison:[/bold]\n\n"
        f"  Tranchi.ai: $$$$/month subscription\n"
        f"  This tool:  ~$0.01-0.05 per AI analysis (pay only for what you use)\n"
        f"              Typical month of heavy use: under $5",
        title="[bold green]SETUP[/bold green]",
        border_style="green",
    ))

    if Confirm.ask("\nCreate .env file from template?", default=True):
        env_path = Path(__file__).parent / ".env"
        template_path = Path(__file__).parent / ".env.example"
        if env_path.exists():
            console.print("[yellow].env already exists — edit it directly[/yellow]")
        elif template_path.exists():
            env_path.write_text(template_path.read_text())
            console.print(f"[green]Created .env — open it and add your API keys[/green]")
        else:
            env_path.write_text(
                "ANTHROPIC_API_KEY=sk-ant-your-key-here\n"
                "HUD_API_TOKEN=your-hud-token-here\n"
            )
            console.print(f"[green]Created .env — open it and add your keys[/green]")

    press_enter()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _check_ai_key():
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print(Panel(
            "[yellow]AI features require ANTHROPIC_API_KEY[/yellow]\n\n"
            "Get a free key (includes $5 credit) at:\n"
            "  [cyan]https://console.anthropic.com/[/cyan]\n\n"
            "Add to [bold].env[/bold]:\n"
            "  ANTHROPIC_API_KEY=sk-ant-your-key-here\n\n"
            "This tool costs ~$0.01-0.05 per AI call.\n"
            "A full month of heavy use is typically under $5.\n"
            "[bold green]That's 99% cheaper than Tranchi.ai.[/bold green]",
            title="⚠  AI Key Needed",
            border_style="yellow",
        ))


# ── Entry Point ───────────────────────────────────────────────────────────────

@click.command()
@click.option("--mao", is_flag=True, help="Quick MAO calculation (non-interactive)")
@click.option("--arv", type=float, help="After Repair Value for quick MAO")
@click.option("--repairs", type=float, help="Repair cost for quick MAO")
@click.option("--fee", type=float, default=10000, help="Wholesale fee")
def cli(mao, arv, repairs, fee):
    """Wholesale AI — Real Estate Wholesale + Gov Property Finder"""
    if mao and arv and repairs:
        result = quick_mao(arv, repairs, fee)
        console.print(f"\n[bold green]MAO: {currency(result)}[/bold green]")
        console.print(f"[dim]Formula: (${arv:,.0f} × 70%) - ${repairs:,.0f} repairs - ${fee:,.0f} fee[/dim]\n")
        return

    main_menu()


if __name__ == "__main__":
    cli()
