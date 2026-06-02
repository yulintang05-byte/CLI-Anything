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
from modules.pipeline import (
    add_deal, get_all_deals, update_deal, advance_stage,
    delete_deal, pipeline_summary, STAGES, STAGE_COLORS,
)
from modules.neighborhood import (
    get_city_crime_data, get_neighborhood_links,
    estimate_property_tax, estimate_insurance, get_property_records_urls,
)
from modules.creative_financing import (
    calc_dscr, calc_subject_to, calc_seller_finance,
    calc_seller_credits, calc_lease_option, recommend_strategy,
)
from modules.user_profile import load_profile, save_profile, is_profile_complete
from modules.auto_offer import (
    generate_offer_email, generate_ai_offer_email,
    batch_generate_offers, get_facebook_buyer_groups,
)
from modules.deal_browser import (
    GOV_SOURCES, DEAL_CATEGORIES, HOT_MARKETS,
    get_sources_by_category, analyze_deal_card,
    all_strategies_analysis,
    get_section8_guide, get_llc_formation_guide,
)
from modules.brrrr        import calc_brrrr, brrrr_example
from modules.lender_directory import (
    HARD_MONEY_LENDERS, DSCR_LENDERS,
    get_hml_for_deal, get_dscr_for_deal, get_lender_summary,
)
from modules.tenant_screener  import (
    SCREENING_QUESTIONS, SCREENING_SERVICES, SECTION8_SCREENING,
    VASH_SCREENING, score_tenant,
)
from modules.luxury_wholesale import (
    LUXURY_MARKETS, LUXURY_DEAL_SOURCES, LUXURY_DEVELOPER_BUYERS,
    LUXURY_DEAL_ANALYSIS, calc_luxury_deal,
)
from modules.owner_finance import (
    OWNER_FINANCE_SOURCES, MOTIVATION_SIGNALS, IDEAL_SELLER_PROFILE,
    NEGOTIATION_PITCH, calc_owner_finance_entry,
)
from modules.web_scraper      import (
    scrape_craigslist_fsbo, get_dlba_listings,
    get_tax_deed_listings, get_hud_listings_url,
    CRAIGSLIST_CITIES,
)
from agents.runner import AgentRunner
from agents.memory import get_stats as agent_stats

# Global agent runner (started once, shared across menus)
_runner: Optional[AgentRunner] = None

def get_runner() -> AgentRunner:
    global _runner
    if _runner is None:
        _runner = AgentRunner()
    return _runner


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
    summary = pipeline_summary()
    pipe_status = f"[cyan]{summary['active_deals']} active deals | ${summary['closed_fees']:,.0f} closed[/cyan]"
    console.print(f"  AI Advisor: {ai_status}   HUD FMR API: {hud_status}   Pipeline: {pipe_status}\n")


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
        profile = load_profile()
        runner  = get_runner()
        agent_status = "[bold green]● RUNNING[/bold green]" if runner.is_running() else "[dim]○ Idle[/dim]"
        profile_status = (
            f"[green]{profile['name']} | {profile['company']}[/green]"
            if is_profile_complete(profile)
            else "[yellow]⚠ Set profile first — option 28![/yellow]"
        )
        # Header only needs earned + close rate — use the cheap stats accessor,
        # not the full dashboard() (which does ~6 JSON reads) on every redraw.
        stats = agent_stats()

        console.print(Panel(
            f"\n  Profile: {profile_status}   Agents: {agent_status}"
            f"   Earned: [bold green]${stats['total_earned']:,.0f}[/bold green]"
            f"   Close Rate: [cyan]{stats['close_rate']}%[/cyan]\n\n"

            "  [bold green]── FIND DEALS ──────────────────────────────────────────────[/bold green]\n"
            "  [bold cyan][1][/bold cyan]  Browse Gov & Distressed Properties\n"
            "  [bold cyan][2][/bold cyan]  Hot Markets Guide ($4k-$20k)\n"
            "  [bold cyan][23][/bold cyan] [bold]LIVE Lead Finder[/bold] — Scrape & Score Properties Now\n"
            "  [bold cyan][24][/bold cyan] Luxury Wholesale + Developer Buyers ($500k+)\n\n"

            "  [bold green]── ANALYZE ─────────────────────────────────────────────────[/bold green]\n"
            "  [bold cyan][3][/bold cyan]  [bold]Deal Card — ALL 4 Strategies[/bold] (Flip │ BRRRR │ DSCR │ Sec8)\n"
            "  [bold cyan][4][/bold cyan]  AI Deal Analyzer (full grade + red flags)\n"
            "  [bold cyan][5][/bold cyan]  Neighborhood & Crime Score\n"
            "  [bold cyan][6][/bold cyan]  DSCR Calculator\n"
            "  [bold cyan][7][/bold cyan]  Property Tax & Insurance Estimates\n"
            "  [bold cyan][8][/bold cyan]  BRRRR Calculator\n"
            "  [bold cyan][25][/bold cyan] Lender Directory (Hard Money + DSCR Loans)\n\n"

            "  [bold green]── MAKE OFFERS ─────────────────────────────────────────────[/bold green]\n"
            "  [bold cyan][9][/bold cyan]  [bold]AUTO OFFER[/bold] — Generate & Send Offer Emails\n"
            "  [bold cyan][10][/bold cyan] AI Negotiation Script + Counter Strategy\n"
            "  [bold cyan][11][/bold cyan] Generate Contract (Assignment │ Sub-To │ Seller Finance │ More)\n\n"

            "  [bold green]── AI AGENTS (Proactive — Goal: $10k-$30k/mo) ──────────────[/bold green]\n"
            "  [bold cyan][26][/bold cyan] [bold]Run All Agents[/bold] — Find → Analyze → Offer pipeline\n"
            "  [bold cyan][27][/bold cyan] Agent Dashboard — Leads queue, activity, learned patterns\n\n"

            "  [bold green]── CLOSE & SCALE ────────────────────────────────────────────[/bold green]\n"
            "  [bold cyan][12][/bold cyan] Deal Pipeline / CRM\n"
            "  [bold cyan][30][/bold cyan] [bold]Owner-Financing Finder[/bold] — Low Entry, Motivated Sellers\n"
            "  [bold cyan][13][/bold cyan] Creative Financing\n"
            "  [bold cyan][14][/bold cyan] Section 8 / VASH Tenant Guide\n"
            "  [bold cyan][15][/bold cyan] Find Cash Buyers, Developers & Motivated Sellers\n"
            "  [bold cyan][16][/bold cyan] LLC Formation Guide\n"
            "  [bold cyan][29][/bold cyan] Pre-Screen Tenants\n\n"

            "  [bold green]── SETTINGS ────────────────────────────────────────────────[/bold green]\n"
            "  [bold cyan][28][/bold cyan] My Investor Profile (credit score, cash, targets)\n"
            "  [bold cyan][17][/bold cyan] Wholesale Strategy Guide\n"
            "  [bold cyan][18][/bold cyan] Repair Cost Guide\n"
            "  [bold cyan][19][/bold cyan] Ask the AI Advisor Anything\n"
            "  [bold cyan][20][/bold cyan] HUD Fair Market Rents\n"
            "  [bold cyan][21][/bold cyan] Setup & API Keys\n"
            "  [bold cyan][0][/bold cyan]  Exit\n",
            title="[bold green]WHOLESALE AI — COMMAND CENTER[/bold green]",
            border_style="green",
        ))

        valid = [str(i) for i in range(22)] + ["23","24","25","26","27","28","29","30"]
        choice = Prompt.ask("[bold]Select[/bold]", choices=valid)

        if choice == "0":
            console.print("\n[bold green]Go get that bag.[/bold green]\n")
            sys.exit(0)
        elif choice == "1":
            menu_browse_deals()
        elif choice == "2":
            menu_hot_markets()
        elif choice == "3":
            menu_deal_calculator()
        elif choice == "4":
            menu_ai_deal_analyzer()
        elif choice == "5":
            menu_neighborhood()
        elif choice == "6":
            menu_dscr()
        elif choice == "7":
            menu_tax_insurance()
        elif choice == "8":
            menu_brrrr()
        elif choice == "9":
            menu_auto_offer()
        elif choice == "10":
            menu_negotiation_script()
        elif choice == "11":
            menu_offer_letter()
        elif choice == "12":
            menu_pipeline()
        elif choice == "13":
            menu_creative_financing()
        elif choice == "14":
            menu_section8()
        elif choice == "15":
            menu_cash_buyers()
        elif choice == "16":
            menu_llc_guide()
        elif choice == "17":
            menu_strategy_guide()
        elif choice == "18":
            menu_repair_guide()
        elif choice == "19":
            menu_ask_advisor()
        elif choice == "20":
            menu_hud_fmr()
        elif choice == "21":
            menu_setup()
        elif choice == "23":
            menu_live_leads()
        elif choice == "24":
            menu_luxury()
        elif choice == "25":
            menu_lenders()
        elif choice == "26":
            menu_run_agents()
        elif choice == "27":
            menu_agent_dashboard()
        elif choice == "28":
            menu_investor_profile()
        elif choice == "29":
            menu_tenant_screener()
        elif choice == "30":
            menu_owner_finance()


# ── 1. Browse Deals ──────────────────────────────────────────────────────────

def menu_browse_deals():
    section("BROWSE GOV & DISTRESSED PROPERTIES")
    console.print("[dim]Filter by deal type — same categories as Tranchi.ai's Browse Deals page.[/dim]\n")

    console.print("[bold]Deal Categories:[/bold]\n")
    for i, cat in enumerate(DEAL_CATEGORIES, 1):
        console.print(f"  [{i:2}] {cat}")
    console.print()

    choice = Prompt.ask("Select category (number)", default="1")
    try:
        idx = int(choice) - 1
        category = DEAL_CATEGORIES[idx] if 0 <= idx < len(DEAL_CATEGORIES) else "All Deals"
    except (ValueError, IndexError):
        category = "All Deals"

    sources = get_sources_by_category(category) if category != "All Deals" else GOV_SOURCES

    console.print(f"\n[bold green]Sources for: {category}[/bold green]\n")
    for group, items in sources.items():
        console.print(f"[bold yellow]{group}[/bold yellow]")
        for name, url in items.items():
            console.print(f"  • [bold]{name}[/bold]\n    {url}")
        console.print()

    if Confirm.ask("Save a deal you found to your pipeline?", default=False):
        _pipeline_add()

    press_enter()


def display_full_deal_card(data: dict, address: str = "", badge: str = ""):
    """
    Render a Tranchi.ai-style deal card with all 4 strategies pre-calculated.
    Shows Flip, BRRRR, DSCR, and Section 8 side by side on one screen.
    """
    flip  = data["flip"]
    brrrr = data["brrrr"]
    dscr  = data["dscr"]
    sec8  = data["section8"]
    buyer = data["buyer"]

    high_margin_badge = "  [bold white on green] ⭐ HIGH MARGIN [/bold white on green]" if data["high_margin"] else ""
    badge_str = f"  [bold magenta]{badge}[/bold magenta]" if badge else ""
    header = (
        f"  [bold]{address or 'Property Analysis'}[/bold]{badge_str}{high_margin_badge}\n\n"
        f"  Ask: [bold yellow]{currency(data['price'])}[/bold yellow]"
        f"  │  ARV: [bold cyan]{currency(data['arv'])}[/bold cyan]"
        f"  │  [yellow]{data['below_market_pct']}% Below Market[/yellow]"
        f"  │  Repairs: {currency(data['repairs'])}"
        f"  │  All-In: [bold]{currency(data['all_in'])}[/bold]"
        f"  │  Rent Est: [green]{currency(data['market_rent'])}/mo[/green]"
    )
    console.print(Panel(header, border_style="bright_white", title="[bold white]DEAL CARD[/bold white]"))

    # ── Strategy panels ──────────────────────────────────────────────────
    flip_color = "green" if flip["verdict"] in ("STRONG FLIP", "GOOD FLIP") else (
        "yellow" if flip["verdict"] == "MARGINAL" else "red"
    )
    flip_panel = Panel(
        f"[bold]MAO:[/bold] [cyan]{currency(flip['mao'])}[/cyan]\n"
        f"[bold]Repairs:[/bold] {currency(flip['repairs'])}\n"
        f"[bold]Profit:[/bold] [bold green]{currency(flip['profit'])}[/bold green]\n"
        f"[bold]ROI:[/bold] {flip['roi']}%\n"
        f"[bold]Wholesale Fee:[/bold] [yellow]{currency(flip['wholesale_fee'])}[/yellow]\n"
        f"[bold]Timeline:[/bold] {flip['timeline']}\n\n"
        f"[bold {flip_color}]{flip['verdict']}[/bold {flip_color}]",
        title="[bold yellow]🔨 FIX & FLIP[/bold yellow]",
        border_style=flip_color,
    )

    cash_back = brrrr["cash_back"]
    brrrr_color = (
        "green"  if "PERFECT" in brrrr["verdict"] or "EXCELLENT" in brrrr["verdict"]
        else "cyan"   if "GOOD" in brrrr["verdict"]
        else "yellow" if "PARTIAL" in brrrr["verdict"]
        else "red"
    )
    cash_back_str = (
        f"[bold green]+{currency(cash_back)} BACK 💰[/bold green]" if cash_back > 0
        else f"[red]{currency(cash_back)} left in[/red]"
    )
    cf2_color = "green" if brrrr["monthly_cf"] > 0 else "red"
    brrrr_panel = Panel(
        f"[bold]All-In:[/bold] {currency(brrrr['all_in'])}\n"
        f"[bold]Refi @ 75% ARV:[/bold] {currency(brrrr['refi_loan'])}\n"
        f"[bold]Cash Back:[/bold] {cash_back_str}\n"
        f"[bold]Capital Recycled:[/bold] {brrrr['capital_recycled']}%\n"
        f"[bold]Refi Pmt:[/bold] {currency(brrrr['refi_payment'])}/mo\n"
        f"[bold]Cash Flow:[/bold] [{cf2_color}]{currency(brrrr['monthly_cf'])}/mo[/{cf2_color}]\n\n"
        f"[bold {brrrr_color}]{brrrr['verdict']}[/bold {brrrr_color}]",
        title="[bold cyan]🔄 BRRRR / REFI[/bold cyan]",
        border_style=brrrr_color,
    )

    dscr_color = "green" if dscr["qualifies"] else "red"
    dscr_status = (
        f"[bold green]✓ QUALIFIES ({dscr['ratio']}x)[/bold green]" if dscr["qualifies"]
        else f"[bold red]✗ {dscr['ratio']}x (need 1.25x)[/bold red]"
    )
    dcf_color = "green" if dscr["monthly_cf"] > 0 else "red"
    dscr_panel = Panel(
        f"[bold]DSCR:[/bold] {dscr_status}\n"
        f"[bold]Credit:[/bold] Need 680 │ Yours: [green]{dscr['credit_score']}[/green] [green]✓[/green]\n"
        f"[bold]Cash In:[/bold] {currency(dscr['down_payment'])}\n"
        f"[bold]Mortgage:[/bold] {currency(dscr['monthly_payment'])}/mo\n"
        f"[bold]Cash Flow:[/bold] [{dcf_color}]{currency(dscr['monthly_cf'])}/mo[/{dcf_color}]\n"
        f"[bold]CoC Return:[/bold] {dscr['coc_return']}%\n\n"
        f"[bold {'green' if dscr['can_do'] else 'red'}]{'✓ QUALIFIED' if dscr['can_do'] else '✗ Need more cash'}[/bold {'green' if dscr['can_do'] else 'red'}]",
        title="[bold blue]🏦 DSCR LOAN[/bold blue]",
        border_style=dscr_color,
    )

    s8_cf_color = "green" if sec8["monthly_cf"] > 0 else "red"
    sec8_panel = Panel(
        f"[bold]FMR Rent:[/bold] [bold green]{currency(sec8['fmr_est'])}/mo[/bold green]\n"
        f"[bold]Market Rent:[/bold] {currency(sec8['market_rent'])}/mo\n"
        f"[bold]Gov Pays:[/bold] [green]{sec8['gov_pays']}[/green]\n"
        f"[bold]Cash Flow:[/bold] [{s8_cf_color}]{currency(sec8['monthly_cf'])}/mo[/{s8_cf_color}]\n"
        f"[bold]Annual:[/bold] {currency(sec8['annual_income'])} guaranteed\n"
        f"[bold]CoC Return:[/bold] {sec8['coc_return']}%\n\n"
        f"[bold green]Vacancy Risk: {sec8['vacancy_risk']}[/bold green]",
        title="[bold magenta]🏛️ SECTION 8[/bold magenta]",
        border_style="magenta",
    )

    console.print(Columns([flip_panel, brrrr_panel, dscr_panel, sec8_panel], equal=True, expand=True))

    # ── Buyer position + recommendation ─────────────────────────────────
    brrrr_status = (
        "[green]✓ YES (cash)[/green]" if buyer["can_brrrr"]
        else f"[yellow]✓ w/ Hard Money (need ~{currency(data['brrrr']['hml_cash_needed'])})[/yellow]"
    )
    position_line = (
        f"  Cash: [bold yellow]{currency(buyer['cash'])}[/bold yellow]  │  "
        f"Credit: [bold yellow]{buyer['credit']}[/bold yellow]  │  "
        f"Wholesale: [green]✓[/green]  │  "
        f"BRRRR: {brrrr_status}  │  "
        f"DSCR Loan: {'[green]✓ QUALIFIED[/green]' if buyer['can_dscr'] else '[red]✗ Below threshold[/red]'}"
    )
    console.print(Panel(
        f"{position_line}\n\n"
        f"  [bold green]★  BEST STRATEGY: {data['best_strategy']}[/bold green]\n"
        f"  {data['best_reason']}",
        title="[bold green]YOUR POSITION[/bold green]",
        border_style="green",
    ))


def menu_hot_markets():
    section("HOT MARKETS — $4K-$20K HOMES")
    console.print(
        "[dim]Same markets Tranchi.ai shows. Each card displays all 4 exit strategies "
        "calculated for average-priced properties in that market.[/dim]\n"
    )

    profile = load_profile()
    credit  = profile.get("credit_score", 730)
    cash    = profile.get("available_cash", 12000)

    for i, m in enumerate(HOT_MARKETS, 1):
        arv_est = m["avg_price"] * 8  # typical ARV is 6-10x purchase for these markets
        data = all_strategies_analysis(
            price=m["avg_price"],
            arv=arv_est,
            market_rent=m["avg_rent"],
            sqft=1000,
            bedrooms=3,
            state=m["state"],
            condition="medium",
            buyer_credit_score=credit,
            buyer_cash=cash,
        )
        display_full_deal_card(
            data,
            address=f"{m['city']}, {m['state']}",
            badge="TAX DEED / LAND BANK",
        )
        console.print(f"  [dim]Source: {m['url']}[/dim]\n")

        if i < len(HOT_MARKETS) and not Confirm.ask("See next market?", default=True):
            break

    if Confirm.ask("\nSave a deal to your pipeline?", default=False):
        _pipeline_add()
    press_enter()


# ── 3. Deal Calculator ────────────────────────────────────────────────────────

def menu_deal_calculator():
    section("DEAL CALCULATOR — ALL STRATEGIES")
    console.print(
        "[dim]Enter a property's basic numbers and see ALL 4 exit strategies calculated\n"
        "simultaneously: Fix & Flip, BRRRR, DSCR Rental Loan, and Section 8.\n"
        "Your cash ($12k) and credit (730) are shown on every card.[/dim]\n"
    )

    sub = Prompt.ask(
        "Calculate",
        choices=["full", "mao", "cashflow", "repair"],
        default="full",
    )

    if sub == "full":
        _calc_full_deal_card()
    elif sub == "mao":
        _calc_mao()
    elif sub == "cashflow":
        _calc_cashflow()
    elif sub == "repair":
        _calc_repair()


def _calc_full_deal_card():
    """Full Tranchi.ai-style deal card — all 4 strategies at once."""
    console.print("\n[bold]Enter property details[/bold]\n")

    address = Prompt.ask("Address or description (optional)", default="")
    price   = FloatPrompt.ask("Asking / purchase price")
    arv     = FloatPrompt.ask("ARV — what it's worth fixed up (pull comps!)")
    rent    = FloatPrompt.ask("Estimated monthly rent")
    sqft    = FloatPrompt.ask("Square footage (approx)", default=1000)
    beds    = IntPrompt.ask("Bedrooms", default=3)
    state   = Prompt.ask("State abbreviation (e.g. MI, AL, TN)", default="MI").upper()
    condition = Prompt.ask(
        "Condition",
        choices=["light", "medium", "heavy", "gut"],
        default="medium",
    )
    repair_known = Confirm.ask("Do you have a specific repair estimate?", default=False)
    repair_override = FloatPrompt.ask("Repair cost") if repair_known else None

    profile = load_profile()
    credit  = profile.get("credit_score", 730)
    cash    = profile.get("available_cash", 12000)

    with console.status("[bold green]Calculating all strategies...[/bold green]"):
        data = all_strategies_analysis(
            price=price,
            arv=arv,
            market_rent=rent,
            sqft=sqft,
            bedrooms=beds,
            state=state,
            condition=condition,
            repair_override=repair_override,
            buyer_credit_score=credit,
            buyer_cash=cash,
        )

    display_full_deal_card(data, address=address, badge=condition.upper())

    # Offer to add to pipeline
    if Confirm.ask("\nAdd this deal to your pipeline?", default=False):
        stage = Prompt.ask(
            "Stage",
            choices=["Lead", "Analyzing", "Offer Sent", "Under Contract", "Marketing", "Closed", "Dead"],
            default="Lead",
        )
        notes = Prompt.ask("Notes", default=f"Best strategy: {data['best_strategy']}")
        add_deal(
            address=address or "Unknown address",
            price=price,
            arv=arv,
            repairs=data["repairs"],
            rent=rent,
            strategy=data["best_strategy"],
            stage=stage,
            notes=notes,
        )
        console.print("[green]✓ Added to pipeline.[/green]")

    press_enter()


def _calc_mao():
    console.print("\n[bold]MAO — Maximum Allowable Offer[/bold]\n")

    arv      = FloatPrompt.ask("ARV (what it's worth fully fixed up)")
    repairs  = FloatPrompt.ask("Estimated repair cost")
    asking   = FloatPrompt.ask("Seller's asking price")
    fee      = FloatPrompt.ask("Your wholesale fee target", default=10000)
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
    grade_c   = grade_color(result.grade)
    grade_txt = f"[bold {grade_c}]GRADE: {result.grade}[/bold {grade_c}]"
    deal_txt  = "[bold green]✓ IT'S A DEAL[/bold green]" if result.is_deal else "[bold red]✗ NOT A DEAL AT ASKING PRICE[/bold red]"

    console.print(Panel(f"{grade_txt}  {deal_txt}", border_style=grade_c))

    t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    t.add_column("Metric", style="bold")
    t.add_column("Amount", justify="right")
    t.add_column("Notes")

    t.add_row("ARV (Fixed-up value)",        currency(result.arv),               "Pull real comps!")
    t.add_row("Repair Estimate",             currency(result.repair_cost),        "Get contractor bids")
    t.add_row("Seller Asking",               currency(asking_price),              "")
    t.add_row("─" * 20, "─" * 10, "")
    t.add_row("[bold]Max Allowable Offer (MAO)[/bold]",
              f"[bold green]{currency(result.mao)}[/bold green]",                 "Most you can pay")
    t.add_row("Suggested Opening Offer",     currency(result.suggested_offer),    "~12% below MAO")
    t.add_row("─" * 20, "─" * 10, "")
    t.add_row("Max End Buyer Price",         currency(result.max_end_buyer_price),"MAO + your fee")
    t.add_row("[bold yellow]Your Wholesale Fee[/bold yellow]",
              f"[bold yellow]{currency(result.profit_at_mao)}[/bold yellow]",     "At MAO")
    t.add_row("Your Cash Needed (EMD)",      currency(result.cash_in_deal),       "Earnest money only")
    t.add_row("Equity Spread",               currency(result.equity_spread),      "ARV − (price + repairs)")

    console.print(t)

    if not result.is_deal:
        gap = asking_price - result.mao
        console.print(f"\n[bold red]Seller needs to drop {currency(gap)} to make this work.[/bold red]")
        console.print(f"[yellow]Open at {currency(result.suggested_offer)} and negotiate up.[/yellow]")

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
    section("FIND CASH BUYERS, DEVELOPERS & MOTIVATED SELLERS")
    _check_ai_key()

    console.print(
        "  [1] Find Cash Buyers in my market\n"
        "  [2] Find Local Developers & Flippers\n"
        "  [3] Find Motivated Sellers\n"
        "  [4] Show Facebook Investor Groups\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3","4"], default="1")

    if sub == "0":
        return

    market    = Prompt.ask("Target market (city and state)", default="Detroit, MI")
    prop_type = Prompt.ask("Property type", default="single family")

    if sub == "1":
        console.print(f"\n[dim]Building cash buyer strategy for {market}...[/dim]")
        strategy = find_cash_buyers_strategy(market=market, property_type=prop_type)
        console.print(Panel(Markdown(strategy), title="[bold cyan]Cash Buyer Strategy[/bold cyan]", border_style="cyan"))

    elif sub == "2":
        console.print(f"\n[dim]Finding developers and active flippers in {market}...[/dim]")
        result = ask_advisor(
            f"I'm a real estate wholesaler in {market} with {prop_type} properties. "
            f"Give me a complete step-by-step guide to find: "
            f"(1) Local developers actively buying and building in this market, "
            f"(2) Active fix-and-flip investors who buy volume, "
            f"(3) Landlords who own 5+ properties and keep buying, "
            f"(4) Property management companies that might have investor clients. "
            f"Include specific ways to find them: county records, LinkedIn, PropStream, "
            f"local REIA groups, BiggerPockets, and in-person strategies. "
            f"Give me exact search terms and outreach scripts."
        )
        console.print(Panel(Markdown(result), title=f"[bold cyan]Developers & Flippers — {market}[/bold cyan]", border_style="cyan"))

    elif sub == "3":
        console.print(f"\n[dim]Finding motivated sellers in {market}...[/dim]")
        result = ask_advisor(
            f"I'm wholesaling {prop_type} properties in {market}. "
            f"Give me the complete playbook for finding motivated sellers: "
            f"(1) Free public record sources — tax delinquent lists, probate, divorce, pre-foreclosure, "
            f"(2) Driving for dollars — what to look for and how to track, "
            f"(3) Direct mail — best lists, message templates, response rates, "
            f"(4) Online methods — Facebook Marketplace, Craigslist, Google ads strategy, "
            f"(5) Bandit signs — best placement, what to write, local rules, "
            f"(6) Cold calling — best lists to call, opener scripts. "
            f"Be specific about free vs paid options and expected response rates."
        )
        console.print(Panel(Markdown(result), title=f"[bold cyan]Motivated Sellers — {market}[/bold cyan]", border_style="cyan"))

    elif sub == "4":
        groups = get_facebook_buyer_groups()
        console.print(Panel(
            Markdown(groups),
            title="[bold cyan]Facebook Investor Groups[/bold cyan]",
            border_style="cyan",
        ))

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


# ── 9. Auto Offer ────────────────────────────────────────────────────────────

def menu_auto_offer():
    section("AUTO OFFER SYSTEM")
    profile = load_profile()

    if not is_profile_complete(profile):
        console.print(Panel(
            "[yellow]Set up your Investor Profile first (menu option 28).[/yellow]\n"
            "Your profile feeds into every offer email automatically.",
            border_style="yellow",
        ))
        if Confirm.ask("Set up profile now?", default=True):
            menu_investor_profile()
            profile = load_profile()
        else:
            press_enter()
            return

    console.print(Panel(
        f"  Sending as: [bold]{profile['name']}[/bold] | {profile['company']}\n"
        f"  Financing:  {profile['preferred_financing']}\n"
        f"  EMD: ${profile['emd_amount']:,}  |  Closing: {profile['closing_days']} days  |  Seller Credit: {profile['seller_credit_pct']}%",
        title="[bold green]Your Offer Profile[/bold green]",
        border_style="green",
    ))

    console.print("\n  [1] Generate single offer email\n  [2] Batch offers (multiple properties)\n  [3] View Facebook buyer groups\n")
    sub = Prompt.ask("Select", choices=["1", "2", "3"])

    if sub == "1":
        _auto_offer_single(profile)
    elif sub == "2":
        _auto_offer_batch(profile)
    elif sub == "3":
        _show_fb_groups()


def _auto_offer_single(profile: dict):
    console.print("\n[bold]Property & Seller Details[/bold]\n")
    address = Prompt.ask("Property address")
    list_price = FloatPrompt.ask("List / asking price")
    offer_price = FloatPrompt.ask("Your offer price", default=list_price)
    seller_name = Prompt.ask("Seller / agent name", default="Property Owner")
    seller_email = Prompt.ask("Seller email", default="")
    seller_phone = Prompt.ask("Seller phone", default="")
    financing = Prompt.ask(
        "Financing type",
        choices=["DSCR Loan", "Seller Finance", "Hard Money", "Cash", "$5K Down", "Conventional"],
        default=profile.get("preferred_financing", "DSCR Loan"),
    )
    notes = Prompt.ask("Custom note to add (optional)", default="")

    use_ai = bool(os.getenv("ANTHROPIC_API_KEY")) and Confirm.ask("Use AI to personalize this email?", default=True)

    if use_ai:
        console.print("\n[dim]Generating AI-personalized offer...[/dim]")
        body = generate_ai_offer_email(
            property_data={"address": address, "price": list_price, "financing_type": financing},
            offer_price=offer_price,
            profile=profile,
        )
        subject = f"Purchase Offer – {address}"
        to_email = seller_email
        to_name = seller_name
    else:
        result = generate_offer_email(
            seller_name=seller_name,
            seller_email=seller_email,
            seller_phone=seller_phone,
            property_address=address,
            list_price=list_price,
            offer_price=offer_price,
            financing_type=financing,
            profile=profile,
            custom_notes=notes,
        )
        body = result["body"]
        subject = result["subject"]
        to_email = result["to_email"]
        to_name = result["to_name"]

    console.print(Panel(
        f"[bold]TO:[/bold]      {to_name}  {seller_phone}\n"
        f"[bold]EMAIL:[/bold]   {to_email}\n"
        f"[bold]SUBJECT:[/bold] {subject}\n\n"
        f"[bold]BODY:[/bold]\n\n{body}",
        title="[bold yellow]OFFER EMAIL — READY TO SEND[/bold yellow]",
        border_style="yellow",
    ))

    if Confirm.ask("\nSave to file?", default=True):
        safe = address.replace(" ", "_").replace(",", "")[:40]
        fname = f"offer_{safe}.txt"
        Path(fname).write_text(f"TO: {to_name}\nEMAIL: {to_email}\nSUBJECT: {subject}\n\n{body}")
        console.print(f"[green]✓ Saved to {fname}[/green]")

    # Add to pipeline
    if Confirm.ask("Add to Deal Pipeline?", default=True):
        add_deal(address=address, asking_price=list_price, source="manual", stage="Offer Sent")
        console.print("[green]✓ Added to pipeline as 'Offer Sent'[/green]")

    press_enter()


def _auto_offer_batch(profile: dict):
    console.print("\n[bold]Batch Offer Generator[/bold]")
    console.print("[dim]Enter multiple properties. Empty address = done.[/dim]\n")

    properties = []
    while True:
        address = Prompt.ask(f"Property #{len(properties)+1} address (Enter to finish)", default="")
        if not address:
            break
        price = FloatPrompt.ask("  Asking price")
        email = Prompt.ask("  Seller email (optional)", default="")
        phone = Prompt.ask("  Seller phone (optional)", default="")
        properties.append({"address": address, "price": price, "contact_email": email, "contact_phone": phone})

    if not properties:
        press_enter()
        return

    discount = FloatPrompt.ask(f"\nOffer % below asking (0 = at asking, 5 = 5% below)", default=0) / 100
    offers = batch_generate_offers(properties, offer_discount=discount, profile=profile)

    console.print(f"\n[bold green]Generated {len(offers)} offer emails:[/bold green]\n")

    for i, offer in enumerate(offers, 1):
        console.print(f"[bold cyan]Offer #{i}:[/bold cyan] {offer['property_address']}")
        console.print(f"  Offer: {currency(offer['offer_price'])}  |  To: {offer['to_email'] or 'no email'}")
        console.print()

    if Confirm.ask("Save all to files?", default=True):
        for i, offer in enumerate(offers, 1):
            safe = offer["property_address"].replace(" ", "_").replace(",", "")[:30]
            fname = f"offer_{i:02}_{safe}.txt"
            Path(fname).write_text(f"TO: {offer['to_name']}\nEMAIL: {offer['to_email']}\nSUBJECT: {offer['subject']}\n\n{offer['body']}")
        console.print(f"[green]✓ Saved {len(offers)} offer files[/green]")
        for i, offer in enumerate(offers, 1):
            add_deal(address=offer["property_address"], asking_price=offer.get("property", {}).get("price", 0), stage="Offer Sent")
        console.print(f"[green]✓ Added {len(offers)} deals to pipeline[/green]")

    press_enter()


def _show_fb_groups():
    section("FACEBOOK BUYER & INVESTOR GROUPS")
    console.print("[dim]Same groups Tranchi.ai recommends for finding cash buyers and flipping contracts.[/dim]\n")

    groups = get_facebook_buyer_groups()
    t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    t.add_column("Group Name", style="bold")
    t.add_column("Market")
    t.add_column("URL")

    for g in groups:
        t.add_row(g["name"], g["market"], g["url"])

    console.print(t)
    console.print("\n[bold yellow]How to use:[/bold yellow]")
    console.print("  1. Join 5-10 groups in your target market")
    console.print("  2. Post: 'Looking for cash buyers for [city] — got [beds/baths/sqft] at $[price]. DM me.'")
    console.print("  3. When buyers respond, collect their criteria (zip, price range, beds)")
    console.print("  4. Build your list — these become your repeat buyers for every deal")
    press_enter()


# ── 8. BRRRR Calculator ──────────────────────────────────────────────────────

def menu_brrrr():
    section("BRRRR CALCULATOR")
    console.print("[dim]Buy, Rehab, Rent, Refinance, Repeat — the strategy to build a portfolio with recycled capital.[/dim]\n")

    console.print(Panel(brrrr_example(), title="[bold cyan]Example Deal[/bold cyan]", border_style="cyan"))

    if not Confirm.ask("\nRun your own BRRRR numbers?", default=True):
        press_enter()
        return

    console.print()
    purchase = FloatPrompt.ask("Purchase price")
    repairs = FloatPrompt.ask("Estimated rehab cost")
    arv = FloatPrompt.ask("After Repair Value (ARV)")
    rent = FloatPrompt.ask("Expected monthly rent")
    ltv = FloatPrompt.ask("Refinance LTV % (75% standard, 80% aggressive)", default=75) / 100
    rate = FloatPrompt.ask("Refinance interest rate %", default=7.5) / 100

    state = Prompt.ask("State (for tax estimate, optional)", default="")
    if state:
        tax_data = estimate_property_tax(state, arv)
        monthly_tax = tax_data["monthly_estimate"]
        ins_data = estimate_insurance(arv, state)
        monthly_ins = ins_data["landlord_monthly"]
        console.print(f"[dim]Auto-estimated: tax ${monthly_tax}/mo, insurance ${monthly_ins}/mo[/dim]")
    else:
        monthly_tax = FloatPrompt.ask("Monthly property tax estimate", default=100)
        monthly_ins = FloatPrompt.ask("Monthly insurance estimate", default=80)

    result = calc_brrrr(
        purchase_price=purchase,
        repair_cost=repairs,
        arv=arv,
        monthly_rent=rent,
        refinance_ltv=ltv,
        refinance_rate=rate,
        monthly_tax=monthly_tax,
        monthly_insurance=monthly_ins,
    )

    # Verdict color
    verdict = result["verdict"]
    v_color = "green" if "PERFECT" in verdict or "EXCELLENT" in verdict else \
              "cyan" if "GOOD" in verdict else \
              "yellow" if "PARTIAL" in verdict or "BUY" in verdict else "red"

    console.print(Panel(
        f"  [{v_color}][bold]{verdict}[/bold][/{v_color}]\n\n"
        f"  All-In Cost:           {currency(result['all_in_cost'])}\n"
        f"  ARV:                   {currency(result['arv'])}\n"
        f"  Equity Created:        [green]{currency(result['equity_created'])} ({result['equity_pct']}% below market)[/green]\n\n"
        f"  Refinance Loan ({result['refi_ltv_pct']} LTV):  {currency(result['refi_loan_amount'])}\n"
        f"  [bold]Cash Returned:         {'[green]+' if result['cash_returned'] > 0 else '[red]'}{currency(result['cash_returned'])}{'[/green]' if result['cash_returned'] > 0 else '[/red]'}[/bold]\n"
        f"  Cash Still In Deal:    {currency(result['cash_left_in'])}\n"
        f"  Capital Recycled:      {result['capital_recycled_pct']}%\n\n"
        f"  Monthly Cash Flow:     [{'green' if result['monthly_cash_flow'] > 0 else 'red'}]{currency(result['monthly_cash_flow'])}/mo[/{'green' if result['monthly_cash_flow'] > 0 else 'red'}]\n"
        f"  Annual Cash Flow:      {currency(result['annual_cash_flow'])}\n"
        f"  Cap Rate:              {result['cap_rate']}%\n"
        f"  Cash-on-Cash Return:   {result['coc_return']}%",
        title="[bold]BRRRR Analysis[/bold]",
        border_style=v_color,
    ))

    press_enter()


# ── 14. Section 8 Guide ──────────────────────────────────────────────────────

def menu_section8():
    section("SECTION 8 / GOVERNMENT TENANT GUIDE")
    guide = get_section8_guide()
    vash  = guide["vash_program"]

    console.print(Panel(guide["what_it_is"], title="What is Section 8?", border_style="blue"))
    console.print(f"\n[bold yellow]Pro Tip:[/bold yellow] {guide['pro_tip']}\n")

    console.print("[bold green]Benefits:[/bold green]")
    for b in guide["benefits"]:
        console.print(f"  ✓ {b}")

    console.print("\n[bold cyan]How to Become a Section 8 Landlord:[/bold cyan]")
    for step in guide["how_to_apply"]:
        console.print(f"  {step}")

    console.print("\n[bold]Key Links:[/bold]")
    console.print(f"  Find your local HUD/PHA:  {guide['find_your_pha']}")
    console.print(f"  HUD Fair Market Rents:    {guide['fmr_lookup']}")
    console.print(f"  Section 8 Info:           {guide['section8_apply']}")
    console.print(f"  Find Section 8 Tenants:   {guide['tenant_finder']}")
    console.print(f"  Affordable Housing:       {guide['rental_rates']}")

    # VASH — Veterans Affairs Supportive Housing
    console.print()
    console.print(Panel(
        f"[bold]{vash['what']}[/bold]\n\n"
        f"[bold cyan]How to Get VASH Tenants:[/bold cyan]\n"
        f"  {vash['how_to_list']}\n\n"
        f"[bold yellow]Pro Tip:[/bold yellow] {vash['pro_tip']}\n\n"
        f"[bold]VASH Links:[/bold]\n"
        f"  VA Housing Coordinator: {vash['va_contact']}\n"
        f"  List your property:     {vash['gosection8']}\n"
        f"  VASH Program details:   {vash['vash_detail']}",
        title="[bold yellow]🎖️  VASH — Veterans Affairs Supportive Housing (Section 8 for Vets)[/bold yellow]",
        border_style="yellow",
    ))

    # AI tenant finder tip
    if os.getenv("ANTHROPIC_API_KEY"):
        if Confirm.ask("\nGet AI help finding the right tenant strategy for your property?", default=False):
            address = Prompt.ask("Property address or market")
            beds    = IntPrompt.ask("Bedrooms", default=3)
            rent    = FloatPrompt.ask("Estimated rent")
            console.print("\n[dim]Analyzing tenant strategy...[/dim]")
            result = ask_advisor(
                f"I have a {beds}-bedroom rental in {address} renting for ${rent}/mo. "
                f"Walk me through the best tenant strategy: should I prioritize Section 8, "
                f"VASH veterans voucher, or standard market rental? How do I find tenants "
                f"for each? Give me specific steps and the best websites/apps."
            )
            console.print(Panel(Markdown(result), title="[bold green]AI Tenant Strategy[/bold green]", border_style="green"))

    press_enter()


# ── 16. LLC Formation Guide ──────────────────────────────────────────────────

def menu_llc_guide():
    section("LLC FORMATION GUIDE")
    guide = get_llc_formation_guide()

    console.print("[bold]Why You Need an LLC:[/bold]")
    for r in guide["why_llc"]:
        console.print(f"  ✓ {r}")

    console.print("\n[bold]LLC Types for Real Estate:[/bold]")
    for t, desc in guide["types"].items():
        console.print(f"  [bold cyan]{t}:[/bold cyan] {desc}")

    console.print("\n[bold]How to Form (5 Steps):[/bold]")
    for step in guide["how_to_form"]:
        console.print(f"  {step}")

    console.print(f"\n[bold]Cost:[/bold] {guide['cost']}")

    console.print("\n[bold]Resources:[/bold]")
    for name, url in guide["resources"].items():
        console.print(f"  • [bold]{name}:[/bold] {url}")

    press_enter()


# ── 17. Investor Profile ─────────────────────────────────────────────────────

def menu_investor_profile():
    section("MY INVESTOR PROFILE")
    console.print("[dim]Your profile auto-fills every offer email you generate — set it once.[/dim]\n")

    profile = load_profile()

    console.print("[bold]Enter your details[/bold] (press Enter to keep current value)\n")

    def ask(label: str, key: str, default_override=None):
        current = profile.get(key, "") or ""
        val = Prompt.ask(label, default=str(default_override if default_override is not None else current))
        return val

    profile["name"]    = ask("Your full name", "name")
    profile["company"] = ask("Company / LLC name", "company")
    profile["email"]   = ask("Your email", "email")
    profile["phone"]   = ask("Your phone", "phone")
    profile["purchasing_entity"] = ask(
        "Purchasing entity (e.g. 'Smith Holdings LLC')", "purchasing_entity",
        profile.get("company", ""),
    )
    profile["preferred_financing"] = Prompt.ask(
        "Preferred financing",
        choices=["DSCR Loan", "Seller Finance", "Hard Money", "Cash", "$5K Down", "Conventional"],
        default=profile.get("preferred_financing", "DSCR Loan"),
    )

    console.print("\n[bold cyan]── Your Investor Position (used on every deal card) ──[/bold cyan]")
    profile["credit_score"]    = int(FloatPrompt.ask(
        "Your credit score", default=profile.get("credit_score", 730)
    ))
    profile["available_cash"]  = int(FloatPrompt.ask(
        "Cash available to invest ($)", default=profile.get("available_cash", 12000)
    ))
    profile["exit_strategy"]   = Prompt.ask(
        "Primary exit strategy",
        choices=["Wholesale", "Flip", "BRRRR", "Buy & Hold", "Section 8"],
        default=profile.get("exit_strategy", "BRRRR"),
    )
    profile["target_markets"]  = ask(
        "Target markets (e.g. Detroit MI, Birmingham AL)", "target_markets",
        profile.get("target_markets", "Detroit MI, Birmingham AL, Memphis TN"),
    )

    console.print("\n[bold cyan]── Offer Settings ──[/bold cyan]")
    profile["portfolio_size"]   = int(FloatPrompt.ask("Properties in portfolio", default=profile.get("portfolio_size", 0)))
    profile["years_experience"] = int(FloatPrompt.ask("Years of experience", default=profile.get("years_experience", 1)))
    profile["emd_amount"]       = int(FloatPrompt.ask("Earnest Money Deposit ($)", default=profile.get("emd_amount", 1000)))
    profile["closing_days"]     = int(FloatPrompt.ask("Preferred closing days", default=profile.get("closing_days", 30)))
    profile["seller_credit_pct"]= int(FloatPrompt.ask("Seller credit % to request", default=profile.get("seller_credit_pct", 3)))
    profile["bio_line"]         = ask("One-liner bio for offer emails", "bio_line")

    save_profile(profile)

    credit = profile["credit_score"]
    cash   = profile["available_cash"]
    credit_color = "green" if credit >= 700 else ("yellow" if credit >= 650 else "red")
    cash_color   = "green" if cash >= 10000 else ("yellow" if cash >= 5000 else "red")

    # Show what deals they can currently do
    console.print(Panel(
        f"  Name:    [bold]{profile['name']}[/bold] | {profile['company']}\n"
        f"  Credit:  [{credit_color}]{credit}[/{credit_color}]  │  "
        f"Cash:    [{cash_color}]{currency(cash)}[/{cash_color}]  │  "
        f"Strategy: [bold cyan]{profile['exit_strategy']}[/bold cyan]\n\n"
        f"  [bold]What you can do RIGHT NOW:[/bold]\n"
        f"  Wholesale (no money needed):  [bold green]✓ ALWAYS[/bold green]\n"
        f"  DSCR Loan (credit ≥ 680):     "
        f"{'[bold green]✓ QUALIFIED[/bold green]' if credit >= 680 else '[bold red]✗ Work on credit first[/bold red]'}\n"
        f"  Hard Money (10% + points):    "
        f"{'[bold green]✓ YES[/bold green]' if cash >= 5000 else '[bold yellow]Need $5k+ for HML down[/bold yellow]'}\n"
        f"  Detroit BRRRR (buy cash):     "
        f"{'[bold green]✓ YES[/bold green]' if cash >= 8000 else '[bold yellow]Need $8k for buy + some rehab[/bold yellow]'}\n"
        f"  Full Cash BRRRR:              "
        f"{'[bold green]✓ YES for Detroit/Jackson[/bold green]' if cash >= 25000 else f'[bold yellow]Need ~$25k all-in (currently {currency(cash)})[/bold yellow]'}\n"
        f"\n  Targets: {profile['target_markets']}",
        title="[bold green]✓ Profile Saved[/bold green]",
        border_style="green",
    ))
    press_enter()


# ── 11. Deal Pipeline / CRM ──────────────────────────────────────────────────

def menu_pipeline():
    section("DEAL PIPELINE / CRM")

    while True:
        summary = pipeline_summary()
        console.print(Panel(
            f"  Active Deals: [cyan]{summary['active_deals']}[/cyan]   "
            f"Potential Fees: [yellow]${summary['total_potential_fees']:,.0f}[/yellow]   "
            f"Closed: [green]${summary['closed_fees']:,.0f}[/green]",
            border_style="dim",
        ))

        console.print(
            "  [1] View all deals  [2] Add new deal  [3] Update deal stage  "
            "[4] Add notes  [5] Delete deal  [0] Back\n"
        )
        sub = Prompt.ask("Select", choices=["0","1","2","3","4","5"])

        if sub == "0":
            break
        elif sub == "1":
            _pipeline_view()
        elif sub == "2":
            _pipeline_add()
        elif sub == "3":
            _pipeline_advance()
        elif sub == "4":
            _pipeline_notes()
        elif sub == "5":
            _pipeline_delete()


def _pipeline_view():
    deals = get_all_deals()
    if not deals:
        console.print("[yellow]No deals yet. Add your first deal![/yellow]")
        press_enter()
        return

    # Group by stage
    by_stage = {s: [] for s in STAGES}
    for d in deals:
        stage = d.get("stage", "Lead")
        if stage in by_stage:
            by_stage[stage].append(d)

    for stage in STAGES:
        stage_deals = by_stage[stage]
        if not stage_deals:
            continue
        color = STAGE_COLORS.get(stage, "white")
        console.print(f"\n[{color}][bold]{stage.upper()}[/bold] ({len(stage_deals)})[/{color}]")

        t = Table(show_header=True, header_style="bold", box=box.SIMPLE)
        t.add_column("ID", width=8)
        t.add_column("Address")
        t.add_column("Asking", justify="right")
        t.add_column("ARV", justify="right")
        t.add_column("MAO", justify="right")
        t.add_column("Fee", justify="right")
        t.add_column("Source")
        t.add_column("Updated")

        for d in stage_deals:
            updated = d.get("updated_at", "")[:10]
            t.add_row(
                d.get("id", ""),
                d.get("address", "")[:35],
                currency(d.get("asking_price", 0)) if d.get("asking_price") else "-",
                currency(d.get("arv", 0)) if d.get("arv") else "-",
                currency(d.get("mao", 0)) if d.get("mao") else "-",
                currency(d.get("wholesale_fee", 0)),
                d.get("source", "")[:15],
                updated,
            )
        console.print(t)

    press_enter()


def _pipeline_add():
    console.print("\n[bold]Add New Deal to Pipeline[/bold]\n")
    address = Prompt.ask("Property address")
    source = Prompt.ask("Where'd you find it (HUD, tax lien, driving for dollars, etc.)")
    asking = FloatPrompt.ask("Seller asking price (0 if unknown)", default=0)
    arv = FloatPrompt.ask("ARV (0 if not yet analyzed)", default=0)
    repairs = FloatPrompt.ask("Repair estimate (0 if unknown)", default=0)
    fee = FloatPrompt.ask("Wholesale fee target", default=10000)
    notes = Prompt.ask("Notes (seller situation, motivation, etc.)", default="")
    stage = Prompt.ask("Stage", choices=STAGES, default="Lead")

    mao = quick_mao(arv, repairs, fee) if arv and repairs else 0
    deal = add_deal(
        address=address, asking_price=asking, arv=arv, repairs=repairs,
        mao=mao, wholesale_fee=fee, source=source, notes=notes, stage=stage,
    )

    console.print(f"\n[green]✓ Deal added! ID: [bold]{deal['id']}[/bold][/green]")
    if mao:
        is_deal = asking <= mao if asking else True
        status = "[green]✓ Numbers work[/green]" if is_deal else f"[red]✗ Seller {currency(asking - mao)} over MAO[/red]"
        console.print(f"  MAO: {currency(mao)}   {status}")
    press_enter()


def _pipeline_advance():
    deal_id = Prompt.ask("Deal ID to advance")
    deal = None
    for d in get_all_deals():
        if d.get("id") == deal_id:
            deal = d
            break
    if not deal:
        console.print("[red]Deal not found[/red]")
        press_enter()
        return

    current = deal.get("stage", "Lead")
    console.print(f"\nCurrent stage: [bold]{current}[/bold]")

    new_stage = Prompt.ask("New stage", choices=STAGES, default=current)
    note = Prompt.ask("Note about this update", default="")
    update_deal(deal_id, stage=new_stage, notes=note)
    console.print(f"[green]✓ Updated to {new_stage}[/green]")
    press_enter()


def _pipeline_notes():
    deal_id = Prompt.ask("Deal ID")
    note = Prompt.ask("Add note")
    deal = update_deal(deal_id, notes=note)
    if deal:
        console.print("[green]✓ Note saved[/green]")
    else:
        console.print("[red]Deal not found[/red]")
    press_enter()


def _pipeline_delete():
    deal_id = Prompt.ask("Deal ID to delete")
    if Confirm.ask(f"Delete deal {deal_id}?", default=False):
        if delete_deal(deal_id):
            console.print("[green]✓ Deleted[/green]")
        else:
            console.print("[red]Deal not found[/red]")
    press_enter()


# ── 12. Neighborhood & Crime Score ───────────────────────────────────────────

def menu_neighborhood():
    section("NEIGHBORHOOD & CRIME SCORE")
    console.print("[dim]Get crime stats, school ratings, flood risk, and neighborhood data for any property.[/dim]\n")

    city = Prompt.ask("City")
    state = Prompt.ask("State abbreviation (e.g. GA, TX)").upper()
    zip_code = Prompt.ask("Zip code (optional)", default="")

    console.print(f"\n[dim]Pulling neighborhood data for {city}, {state}...[/dim]")

    # Crime data from FBI
    console.print("\n[bold cyan]── CRIME DATA (FBI Official) ──[/bold cyan]")
    crime = get_city_crime_data(city, state)

    if "error" in crime:
        console.print(f"[yellow]Automated lookup unavailable: {crime['error']}[/yellow]")
        console.print("[dim]Use these free manual tools:[/dim]")
        for name, url in crime.get("manual_lookup", {}).items():
            console.print(f"  • [bold]{name}:[/bold] {url}")
    else:
        grade_c = grade_color(crime.get("safety_grade", "C"))
        console.print(Panel(
            f"  Safety Score: [{grade_c}][bold]{crime['safety_score']}/100  Grade: {crime['safety_grade']}[/bold][/{grade_c}]\n\n"
            f"  Violent Crimes: {crime['violent_crimes']:,}  ({crime['violent_rate_per_100k']}/100k residents)\n"
            f"  Property Crimes: {crime['property_crimes']:,}  ({crime['property_rate_per_100k']}/100k residents)\n"
            f"  Population: {crime.get('population', 0):,}\n"
            f"  [dim]Source: {crime['source']} — {crime.get('note', '')}[/dim]",
            title=f"[bold]{city}, {state} — Crime Analysis[/bold]",
            border_style=grade_c,
        ))

    # All neighborhood research links
    console.print("\n[bold cyan]── NEIGHBORHOOD RESEARCH LINKS ──[/bold cyan]")
    links = get_neighborhood_links(address="", city=city, state=state, zip_code=zip_code)
    for category, items in links.items():
        console.print(f"\n[bold yellow]{category}[/bold yellow]")
        for name, url in items.items():
            console.print(f"  • [bold]{name}:[/bold] {url}")

    press_enter()


# ── 13. DSCR Calculator ──────────────────────────────────────────────────────

def menu_dscr():
    section("DSCR CALCULATOR — RENTAL LOAN QUALIFIER")
    console.print("[dim]DSCR loans use property income instead of your personal income. Great for investors.[/dim]\n")
    console.print("[dim]Lenders require DSCR ≥ 1.25. Higher is better.[/dim]\n")

    monthly_rent = FloatPrompt.ask("Expected monthly rent")
    purchase_price = FloatPrompt.ask("Purchase price")
    down_pct = FloatPrompt.ask("Down payment % (DSCR loans typically 20-25%)", default=25) / 100
    rate = FloatPrompt.ask("Interest rate %", default=8.5) / 100

    # Calculate mortgage payment
    loan = purchase_price * (1 - down_pct)
    monthly_rate = rate / 12
    n = 30 * 12
    if monthly_rate > 0:
        mortgage = loan * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
    else:
        mortgage = loan / n

    state = Prompt.ask("State (for tax estimate, e.g. TX)", default="")
    if state:
        tax_data = estimate_property_tax(state, purchase_price)
        monthly_tax = tax_data["monthly_estimate"]
        console.print(f"[dim]Auto-estimated tax: {currency(monthly_tax)}/month ({tax_data['effective_rate_pct']} effective rate for {state.upper()})[/dim]")
    else:
        monthly_tax = FloatPrompt.ask("Monthly property tax estimate", default=250)

    monthly_insurance = FloatPrompt.ask("Monthly insurance estimate", default=150)
    monthly_hoa = FloatPrompt.ask("Monthly HOA (0 if none)", default=0)

    result = calc_dscr(
        monthly_rent=monthly_rent,
        monthly_mortgage=mortgage,
        monthly_tax=monthly_tax,
        monthly_insurance=monthly_insurance,
        monthly_hoa=monthly_hoa,
    )

    color = result["dscr_color"]
    console.print(Panel(
        f"  [{color}][bold]DSCR: {result['dscr']}[/bold][/{color}]\n"
        f"  [{color}]{result['lender_view']}[/{color}]\n\n"
        f"  Monthly NOI: {currency(result['noi_monthly'])}\n"
        f"  Annual NOI: {currency(result['noi_annual'])}\n"
        f"  Annual Debt Service: {currency(result['annual_debt_service'])}\n"
        f"  Vacancy Loss (8%): {currency(result['vacancy_loss'])}\n"
        f"  Management Fee (10%): {currency(result['mgmt_fee'])}\n\n"
        + (f"  [yellow]Rent needed to qualify (DSCR 1.25): {currency(result['rent_needed_for_125'])}\n"
           f"  Rent gap: +{currency(result['rent_gap_to_qualify'])}/month needed[/yellow]"
           if not result['loan_eligible'] and result['rent_gap_to_qualify'] > 0 else "  [green]✓ Qualifies for DSCR lending[/green]"),
        title="[bold]DSCR Analysis[/bold]",
        border_style=color,
    ))

    console.print("\n[bold]Top DSCR Lenders (no income verification):[/bold]")
    console.print("  • Griffin Funding — griffinfunding.com")
    console.print("  • Kiavi — kiavi.com")
    console.print("  • Lima One Capital — limaone.com")
    console.print("  • Visio Lending — visiolending.com")
    console.print("  • Civic Financial — civicfs.com")

    press_enter()


# ── 14. Creative Financing ───────────────────────────────────────────────────

def menu_creative_financing():
    section("CREATIVE FINANCING CALCULATOR")
    console.print("[dim]Structure deals when sellers won't take a low cash offer. Zero money down strategies.[/dim]\n")

    strategies = {
        "1": "Subject-To (Take Over Seller's Mortgage)",
        "2": "Seller Financing (Seller Acts as the Bank)",
        "3": "Seller Credits (Reduce Buyer's Cash Needed)",
        "4": "Lease-Option (Rent-to-Own)",
        "5": "Strategy Recommender (Tell me seller's situation)",
    }

    for k, v in strategies.items():
        console.print(f"  [{k}] {v}")
    console.print()

    choice = Prompt.ask("Select", choices=list(strategies.keys()))

    if choice == "1":
        _creative_subject_to()
    elif choice == "2":
        _creative_seller_finance()
    elif choice == "3":
        _creative_seller_credits()
    elif choice == "4":
        _creative_lease_option()
    elif choice == "5":
        _creative_recommender()


def _creative_subject_to():
    console.print("\n[bold]Subject-To Calculator[/bold]\n")
    loan_balance = FloatPrompt.ask("Seller's existing loan balance")
    monthly_payment = FloatPrompt.ask("Seller's current monthly payment (P&I+T+I)")
    existing_rate = FloatPrompt.ask("Seller's current interest rate %", default=3.5) / 100
    arv = FloatPrompt.ask("ARV")
    your_price = FloatPrompt.ask("Your purchase price (what you're paying seller above the loan)")
    rent = FloatPrompt.ask("Expected monthly rent (0 if wholesale)", default=0)

    result = calc_subject_to(
        existing_loan_balance=loan_balance,
        existing_monthly_payment=monthly_payment,
        existing_rate=existing_rate,
        arv=arv,
        your_purchase_price=your_price,
        monthly_rent=rent,
    )

    _display_creative_result(result)


def _creative_seller_finance():
    console.print("\n[bold]Seller Financing Calculator[/bold]\n")
    price = FloatPrompt.ask("Purchase price")
    down = FloatPrompt.ask("Down payment you're offering")
    rate = FloatPrompt.ask("Interest rate you're offering seller %", default=6.0) / 100
    years = IntPrompt.ask("Loan term (years)", default=30)
    balloon = IntPrompt.ask("Balloon payment in X years (0 for none)", default=5)
    rent = FloatPrompt.ask("Expected monthly rent (0 if wholesale/flip)", default=0)

    result = calc_seller_finance(
        purchase_price=price,
        down_payment=down,
        interest_rate=rate,
        loan_years=years,
        balloon_years=balloon if balloon > 0 else None,
        monthly_rent=rent,
    )

    _display_creative_result(result)


def _creative_seller_credits():
    console.print("\n[bold]Seller Credits Calculator[/bold]\n")
    console.print("[dim]Seller credits make your deal easier to sell to an end buyer.[/dim]\n")
    price = FloatPrompt.ask("Purchase price")
    repairs = FloatPrompt.ask("Estimated repairs buyer will do")
    credit_pct = FloatPrompt.ask("Seller credit % to offer (e.g. 3)", default=3) / 100
    loan_type = Prompt.ask("End buyer's loan type", choices=["conventional", "fha", "va", "usda", "cash"], default="conventional")

    result = calc_seller_credits(
        purchase_price=price,
        repair_cost=repairs,
        credit_percent=credit_pct,
        loan_type=loan_type,
    )

    t = Table(show_header=False, box=box.ROUNDED)
    t.add_column("Field", style="bold")
    t.add_column("Value", justify="right")
    for k, v in result.items():
        if k in ("purchase_price", "seller_credit_pct", "seller_credit_amount",
                 "effective_price_to_buyer", "covers_repairs_pct", "benefit"):
            label = k.replace("_", " ").title()
            val = currency(v) if isinstance(v, (int, float)) else str(v)
            t.add_row(label, f"[green]{val}[/green]" if k == "seller_credit_amount" else val)
    console.print(t)
    console.print(f"\n[bold green]{result['benefit']}[/bold green]")
    press_enter()


def _creative_lease_option():
    console.print("\n[bold]Lease-Option Calculator[/bold]\n")
    price = FloatPrompt.ask("Option purchase price")
    rent = FloatPrompt.ask("Monthly rent")
    term = IntPrompt.ask("Option term (years)", default=2)
    credit_pct = FloatPrompt.ask("Rent credit % that applies toward purchase", default=15) / 100
    fee = FloatPrompt.ask("Option fee (non-refundable upfront)", default=5000)

    result = calc_lease_option(
        purchase_price=price,
        monthly_rent=rent,
        option_term_years=term,
        option_credit_pct=credit_pct,
        option_fee=fee,
    )

    _display_creative_result(result)


def _creative_recommender():
    console.print("\n[bold]Deal Structure Recommender[/bold]\n")
    equity_pct = FloatPrompt.ask("Seller's equity % (e.g. 40 means they own 40% of value)", default=30) / 100
    motivation = Prompt.ask("Seller's situation (e.g. behind on payments, divorce, inherited, need cash fast)")
    existing_rate = FloatPrompt.ask("Seller's current interest rate % (0 if unknown)", default=0) / 100
    behind = Confirm.ask("Are they behind on payments / facing foreclosure?", default=False)
    needs_cash = Confirm.ask("Do they absolutely need cash now?", default=False)

    recommendations = recommend_strategy(
        seller_equity_pct=equity_pct,
        seller_motivation=motivation,
        existing_rate=existing_rate or 0.07,
        is_behind_on_payments=behind,
        needs_cash_now=needs_cash,
    )

    console.print("\n[bold cyan]Recommended Deal Structures (best → fallback):[/bold cyan]\n")
    for i, rec in enumerate(recommendations[:4], 1):
        color = "green" if i == 1 else "cyan" if i == 2 else "yellow"
        console.print(f"  [{color}][bold]#{i}: {rec['strategy']}[/bold][/{color}]")
        console.print(f"       {rec['reason']}\n")

    press_enter()


def _display_creative_result(result: dict):
    strategy = result.get("strategy", "")
    t = Table(show_header=False, box=box.ROUNDED)
    t.add_column("Field", style="bold")
    t.add_column("Value", justify="right")

    skip_keys = {"pros", "risks", "best_for", "strategy"}
    for k, v in result.items():
        if k in skip_keys:
            continue
        label = k.replace("_", " ").title()
        if isinstance(v, float):
            val = currency(v) if v > 10 else str(round(v, 3))
        else:
            val = str(v)
        t.add_row(label, val)

    console.print(Panel(t, title=f"[bold green]{strategy}[/bold green]", border_style="green"))

    if result.get("pros"):
        console.print("\n[bold green]Pros:[/bold green]")
        for p in result["pros"]:
            console.print(f"  ✓ {p}")

    if result.get("risks"):
        console.print("\n[bold red]Risks:[/bold red]")
        for r in result["risks"]:
            console.print(f"  ⚠ {r}")

    if result.get("best_for"):
        console.print(f"\n[bold yellow]Best For:[/bold yellow] {result['best_for']}")

    press_enter()


# ── 15. Property Tax & Insurance ─────────────────────────────────────────────

def menu_tax_insurance():
    section("PROPERTY TAX & INSURANCE ESTIMATES")
    console.print("[dim]Run the numbers before you make an offer. Know your holding costs.[/dim]\n")

    state = Prompt.ask("State abbreviation (e.g. TX, FL, GA)").upper()
    value = FloatPrompt.ask("Property value / purchase price")

    # Tax estimate
    tax = estimate_property_tax(state, value)
    # Insurance estimate
    insurance = estimate_insurance(value, state)

    t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    t.add_column("Item")
    t.add_column("Annual", justify="right")
    t.add_column("Monthly", justify="right")
    t.add_column("Notes")

    t.add_row(
        "Property Tax",
        currency(tax["annual_estimate"]),
        currency(tax["monthly_estimate"]),
        f"{tax['effective_rate_pct']} effective rate for {state}",
    )
    t.add_row(
        "Homeowner Insurance",
        currency(insurance["homeowner_annual"]),
        currency(insurance["homeowner_monthly"]),
        "Owner-occupied",
    )
    t.add_row(
        "Landlord Insurance",
        currency(insurance["landlord_annual"]),
        currency(insurance["landlord_monthly"]),
        "Rental/investment property",
    )
    t.add_row(
        "─" * 15, "─" * 10, "─" * 10, "",
    )
    total_annual = tax["annual_estimate"] + insurance["landlord_annual"]
    total_monthly = tax["monthly_estimate"] + insurance["landlord_monthly"]
    t.add_row(
        "[bold]Total (landlord)[/bold]",
        f"[bold]{currency(total_annual)}[/bold]",
        f"[bold]{currency(total_monthly)}[/bold]",
        "Use in your MAO calculation",
    )

    console.print(t)
    console.print(f"\n[dim]⚠  {tax['note']}[/dim]")
    console.print(f"[dim]⚠  {insurance['note']}[/dim]")

    console.print("\n[bold]Get Real Insurance Quotes:[/bold]")
    for url in insurance["quote_sources"]:
        console.print(f"  • {url}")

    console.print(f"\n[bold]Look Up Actual Tax Records:[/bold]")
    console.print(f"  • {tax['lookup_url']}")

    press_enter()


# ── 23. Live Lead Finder ─────────────────────────────────────────────────────

def menu_live_leads():
    section("LIVE LEAD FINDER — SCRAPE & SCORE NOW")
    console.print("[dim]Scans Craigslist FSBO, Detroit Land Bank, tax deed sites, and HUD HomeStore right now.[/dim]\n")

    profile = load_profile()
    target_markets = profile.get("target_markets", "Detroit MI, Birmingham AL, Memphis TN")

    markets_input = Prompt.ask("Markets to scan (comma-separated)", default=target_markets)
    markets       = [m.strip() for m in markets_input.split(",")]
    max_price     = IntPrompt.ask("Max price filter", default=80000)

    runner = get_runner()

    console.print("\n[bold green]Agents scanning sources...[/bold green]\n")
    result = runner.run_full_pipeline(markets=markets, max_price=max_price, console=console)

    lead_result = result.get("lead_result", {})
    console.print(Panel(
        f"  Found:           [bold cyan]{lead_result.get('new_leads', 0)}[/bold cyan] leads\n"
        f"  High Margin:     [bold green]{lead_result.get('high_margin', 0)}[/bold green] deals\n"
        f"  Queued ≥7 score: [cyan]{lead_result.get('queued_for_analysis', 0)}[/cyan]",
        title="[bold green]SCAN COMPLETE[/bold green]",
        border_style="green",
    ))

    ready    = result.get("ready_for_review", [])
    analyzed = result.get("analyzed_leads", [])

    if ready:
        console.print(f"\n[bold green]⭐ {len(ready)} HIGH MARGIN DEALS — Ready for Review:[/bold green]\n")
        for lead in ready:
            display_full_deal_card(
                lead["full_analysis"],
                address=lead.get("title", "")[:60],
                badge=lead.get("source", ""),
            )
            console.print(f"  [dim]URL: {lead.get('url', '')}[/dim]\n")
            if not Confirm.ask("See next deal?", default=True):
                break
    elif analyzed:
        console.print(f"\n[cyan]{len(analyzed)} analyzed leads:[/cyan]\n")
        t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        t.add_column("Score", justify="right")
        t.add_column("Title", max_width=45)
        t.add_column("Price", justify="right")
        t.add_column("Strategy")
        t.add_column("AI Reasoning", max_width=38)
        for lead in analyzed[:10]:
            score = lead.get("score", 0)
            sc    = "green" if score >= 8 else "yellow" if score >= 6 else "red"
            t.add_row(
                f"[{sc}]{score:.1f}[/{sc}]",
                lead.get("title", "")[:45],
                currency(lead.get("price", 0)),
                lead.get("best_strategy", "?"),
                lead.get("ai_reasoning", "")[:38],
            )
        console.print(t)
    else:
        top_leads = lead_result.get("top_leads", [])
        if top_leads:
            console.print("\n[bold]Top Scored Leads (no full analysis yet):[/bold]")
            for lead in top_leads[:5]:
                score = lead.get("score", 0)
                sc    = "green" if score >= 8 else "yellow"
                console.print(f"  [{sc}]{score:.1f}[/{sc}]  {lead.get('title','')[:55]}")
                if lead.get("url"):
                    console.print(f"       [dim]{lead['url']}[/dim]")
        else:
            console.print("[yellow]No leads scored ≥6 this scan. Try different markets or higher max price.[/yellow]")

    if Confirm.ask("\nSave a deal to your pipeline?", default=False):
        _pipeline_add()
    press_enter()


# ── 24. Luxury Wholesale ──────────────────────────────────────────────────────

def menu_luxury():
    section("LUXURY WHOLESALE + DEVELOPER BUYERS ($500k+)")
    console.print("[dim]Wholesale high-end properties to developers. 65% ARV rule. Fees $25k–$100k+.[/dim]\n")

    console.print(
        "  [1] Browse Luxury Markets & Sources\n"
        "  [2] Analyze a Luxury Deal\n"
        "  [3] Find Developer Buyers\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3"], default="1")
    if sub == "0":
        return

    if sub == "1":
        console.print("\n[bold cyan]── LUXURY MARKETS ──[/bold cyan]\n")
        t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        t.add_column("City", style="bold")
        t.add_column("State")
        t.add_column("Avg Price", justify="right")
        t.add_column("Avg ARV", justify="right")
        t.add_column("Developer Focus")
        for m in LUXURY_MARKETS:
            t.add_row(m["city"], m["state"], currency(m["avg_price"]), currency(m["avg_arv"]), m.get("developer_focus", ""))
        console.print(t)

        console.print("\n[bold cyan]── DEAL SOURCES ──[/bold cyan]\n")
        for src_name, src in LUXURY_DEAL_SOURCES.items():
            console.print(f"  [bold yellow]{src_name}[/bold yellow]")
            console.print(f"    {src['description']}")
            console.print(f"    How to find: {src['how_to_find']}")
            console.print(f"    Typical discount: [green]{src['typical_discount']}[/green]\n")

    elif sub == "2":
        console.print("\n[bold]Luxury Deal Analysis[/bold]\n")
        address = Prompt.ask("Address or description", default="")
        price   = FloatPrompt.ask("Purchase price")
        arv     = FloatPrompt.ask("ARV (after repair value)")
        sqft    = FloatPrompt.ask("Square footage", default=3000)
        repairs = FloatPrompt.ask("Repair cost (0 to use sqft estimate)", default=0)

        result  = calc_luxury_deal(price=price, arv=arv, sqft=float(sqft), repairs=float(repairs))

        grade_c = {"A": "bold green", "B": "bold cyan", "C": "bold yellow", "F": "bold red"}.get(result["grade"], "bold white")
        is_deal_str = "[bold green]✓ IT'S A DEAL[/bold green]" if result["is_deal"] else "[bold red]✗ Not a deal at this price[/bold red]"

        console.print(Panel(
            f"  [{grade_c}]GRADE: {result['grade']}[/{grade_c}]  {is_deal_str}\n\n"
            f"  Price:          {currency(price)}\n"
            f"  ARV:            {currency(arv)}\n"
            f"  Discount:       [yellow]{result['discount_pct']}% below ARV[/yellow]\n"
            f"  Repairs Est:    {currency(result['repairs'])}\n"
            f"  65% Rule MAO:   [bold cyan]{currency(result['mao'])}[/bold cyan]\n\n"
            f"  [bold green]Wholesale Fee:  {currency(result['wholesale_fee'])}[/bold green]\n"
            f"  Profit:         {currency(result['profit'])}\n"
            f"  ROI:            {result['roi']}%\n\n"
            f"  Price/sqft ask: ${result['ppsf_ask']:,.0f}   ARV/sqft: ${result['ppsf_arv']:,.0f}",
            title=f"[bold]Luxury Deal — {address or 'Property'}[/bold]",
            border_style="green" if result["is_deal"] else "red",
        ))

        if Confirm.ask("\nAdd to pipeline?", default=False):
            add_deal(address=address or "Luxury Deal", asking_price=price, arv=arv,
                     repairs=result["repairs"], source="luxury wholesale", stage="Lead")
            console.print("[green]✓ Added to pipeline[/green]")

    elif sub == "3":
        console.print("\n[bold cyan]── LUXURY DEVELOPER BUYERS ──[/bold cyan]\n")
        for section_title, items in LUXURY_DEVELOPER_BUYERS.items():
            if isinstance(items, list):
                console.print(f"[bold yellow]{section_title}:[/bold yellow]")
                for item in items:
                    console.print(f"  • {item}")
                console.print()

        if os.getenv("ANTHROPIC_API_KEY"):
            if Confirm.ask("\nGet AI help finding developers in a specific market?", default=False):
                market = Prompt.ask("Market (e.g. Miami, FL)")
                console.print("\n[dim]Finding developers...[/dim]")
                ai_result = ask_advisor(
                    f"I'm a luxury real estate wholesaler in {market} targeting $500k-$5M properties. "
                    f"Give me: (1) Specific developer companies active in {market}, "
                    f"(2) How to find them via county records, LinkedIn, CoStar, LoopNet, "
                    f"(3) Exact outreach script to get on their buyer list, "
                    f"(4) What deal criteria developers look for. Be specific and actionable."
                )
                console.print(Panel(Markdown(ai_result), title=f"[bold cyan]Developers in {market}[/bold cyan]", border_style="cyan"))

    press_enter()


# ── 25. Lender Directory ──────────────────────────────────────────────────────

def menu_lenders():
    section("LENDER DIRECTORY — HARD MONEY + DSCR LOANS")
    console.print("[dim]Hard money for flips/BRRRRs. DSCR for rentals — no W2 or income verification needed.[/dim]\n")

    console.print(
        "  [1] Hard Money Lenders (flips & BRRRRs)\n"
        "  [2] DSCR Lenders (rental — no income check)\n"
        "  [3] Match lenders to my specific deal\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3"], default="1")
    if sub == "0":
        return

    if sub == "1":
        t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        t.add_column("Lender", style="bold")
        t.add_column("Rates", justify="right")
        t.add_column("LTV")
        t.add_column("Min Credit")
        t.add_column("Specialty")
        t.add_column("URL")
        for lender in HARD_MONEY_LENDERS:
            t.add_row(
                lender["name"],
                lender["rates"],
                lender["ltv"][:25],
                str(lender["min_credit"]),
                lender["specialty"],
                lender["url"],
            )
        console.print(t)
        console.print("\n[bold yellow]Tips:[/bold yellow]")
        console.print("  • Always get 3 quotes — rates vary 1-3% between lenders")
        console.print("  • Points (origination) are negotiable on repeat business")
        console.print("  • Build a relationship — after 3 deals they may skip appraisals")
        console.print("  • Ask about 'extension fees' upfront if you need more flip time")

    elif sub == "2":
        t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        t.add_column("Lender", style="bold")
        t.add_column("Rates", justify="right")
        t.add_column("Min DSCR")
        t.add_column("Min Credit")
        t.add_column("LTV")
        t.add_column("URL")
        for lender in DSCR_LENDERS:
            t.add_row(
                lender["name"],
                lender["rates"],
                str(lender["min_dscr"]),
                str(lender["min_credit"]),
                lender["ltv"],
                lender["url"],
            )
        console.print(t)
        console.print("\n[bold yellow]DSCR Tips:[/bold yellow]")
        console.print("  • No W2 or tax returns needed — property income qualifies you")
        console.print("  • DSCR ≥ 1.25 required: rent / (P&I + tax + insurance) ≥ 1.25")
        console.print("  • Down payment 20-25% of purchase price")
        console.print("  • Rates 1-2% above conventional — worth it for portfolio growth")

    elif sub == "3":
        console.print("\n[bold]Match Lenders to Your Deal[/bold]\n")
        loan_type = Prompt.ask("Loan type", choices=["hard_money", "dscr"], default="hard_money")
        price     = FloatPrompt.ask("Purchase price")
        credit    = IntPrompt.ask("Your credit score", default=730)
        state     = Prompt.ask("State abbreviation", default="MI").upper()

        if loan_type == "hard_money":
            arv     = FloatPrompt.ask("ARV", default=price * 2)
            matches = get_hml_for_deal(price=price, arv=float(arv), credit_score=credit, state=state)
        else:
            dscr_ratio  = FloatPrompt.ask("Your DSCR ratio (rent / PITI)", default=1.3)
            loan_amount = price * 0.75
            matches     = get_dscr_for_deal(dscr_ratio=float(dscr_ratio), credit_score=credit, loan_amount=loan_amount)

        if matches:
            console.print(f"\n[bold green]✓ {len(matches)} lenders match your deal:[/bold green]\n")
            for lender in matches:
                console.print(f"  [bold cyan]{lender['name']}[/bold cyan]")
                console.print(f"    Rates: {lender['rates']}  │  {lender.get('ltv', '')}  │  Min credit: {lender['min_credit']}")
                if lender.get("note"):
                    console.print(f"    Note: [dim]{lender['note']}[/dim]")
                console.print(f"    {lender['url']}\n")
        elif loan_type == "dscr":
            loan_amt = price * 0.75
            console.print(Panel(
                f"[yellow]No DSCR lender matches a ${loan_amt:,.0f} loan.[/yellow]\n\n"
                f"Most DSCR lenders have a [bold]$75k-$100k minimum loan[/bold] — that's why cheap "
                f"Detroit/Birmingham/Memphis properties don't qualify for a direct DSCR purchase.\n\n"
                f"[bold green]The play for cheap markets:[/bold green]\n"
                f"  1. Buy the property [bold]CASH[/bold] (or hard money) — see option 25 → Hard Money\n"
                f"  2. Rehab and rent it\n"
                f"  3. Refinance with a [bold]portfolio lender[/bold] that bundles 3-5 homes into one\n"
                f"     loan above the $75k minimum (try Trident, Lima One, CoreVest)\n\n"
                f"This is the BRRRR strategy — run the numbers on the Deal Card (option 3).",
                title="[bold]DSCR Loan Minimum[/bold]",
                border_style="yellow",
            ))
        else:
            console.print("[yellow]No exact matches — try lowering your credit threshold or check deal size.[/yellow]")

    press_enter()


# ── 26. Run All Agents ────────────────────────────────────────────────────────

def menu_run_agents():
    section("AI AGENTS — FULL PIPELINE")
    console.print(
        "[dim]The agents work the full pipeline:\n"
        "  LeadAgent → scrape + score leads\n"
        "  NegotiationAgent → generate scripts + counter strategies\n"
        "  ClosingAgent → auto-select contract + generate docs\n"
        "  Runner → orchestrate everything, self-improve from outcomes[/dim]\n"
    )

    console.print(
        "  [1] Run full pipeline now (find → analyze → flag)\n"
        "  [2] Start background agents (runs every N hours)\n"
        "  [3] Stop background agents\n"
        "  [4] Generate AI negotiation script\n"
        "  [5] Generate contract for a deal\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3","4","5"], default="1")
    if sub == "0":
        return

    runner  = get_runner()
    profile = load_profile()
    target_markets = profile.get("target_markets", "Detroit MI, Birmingham AL, Memphis TN")

    if sub == "1":
        markets_input = Prompt.ask("Markets (comma-separated)", default=target_markets)
        markets   = [m.strip() for m in markets_input.split(",")]
        max_price = IntPrompt.ask("Max price filter", default=80000)

        console.print("\n[bold green]Running full pipeline...[/bold green]\n")
        result    = runner.run_full_pipeline(markets=markets, max_price=max_price, console=console)

        ready  = result.get("ready_for_review", [])
        stats  = result.get("stats", {})
        lr     = result.get("lead_result", {})

        console.print(Panel(
            f"  Leads Found:   [cyan]{lr.get('new_leads', 0)}[/cyan]\n"
            f"  High Margin:   [bold green]{len(ready)}[/bold green] deals ready for review\n"
            f"  Analyzed:      [cyan]{len(result.get('analyzed_leads', []))}[/cyan]\n\n"
            f"  Total Earned:  [bold green]${stats.get('total_earned', 0):,.0f}[/bold green]\n"
            f"  Close Rate:    [cyan]{stats.get('close_rate', 0)}%[/cyan]",
            title="[bold green]PIPELINE COMPLETE[/bold green]",
            border_style="green",
        ))

        for lead in ready[:3]:
            if lead.get("full_analysis"):
                display_full_deal_card(lead["full_analysis"],
                                       address=lead.get("title","")[:60],
                                       badge=lead.get("source",""))
                console.print(f"  [dim]{lead.get('url','')}[/dim]\n")
                if not Confirm.ask("See next?", default=True):
                    break

    elif sub == "2":
        if runner.is_running():
            console.print("[yellow]Agents already running in background.[/yellow]")
        else:
            hours = IntPrompt.ask("Run every N hours", default=24)
            markets_input = Prompt.ask("Markets", default=target_markets)
            markets = [m.strip() for m in markets_input.split(",")]
            msg = runner.start_background(interval_hours=hours, markets=markets)
            console.print(f"\n[bold green]✓ {msg}[/bold green]")
            console.print("[dim]Check Agent Dashboard (option 27) to see results.[/dim]")

    elif sub == "3":
        if runner.is_running():
            msg = runner.stop_background()
            console.print(f"\n[yellow]{msg}[/yellow]")
        else:
            console.print("[dim]No background agents running.[/dim]")

    elif sub == "4":
        _check_ai_key()
        console.print("\n[bold]AI Negotiation Script[/bold]\n")
        address     = Prompt.ask("Property address")
        seller_name = Prompt.ask("Seller name", default="Seller")
        asking      = FloatPrompt.ask("Their asking price")
        mao         = FloatPrompt.ask("Your MAO (Max Allowable Offer)")
        situation   = Prompt.ask("Seller situation (foreclosure, divorce, inherited, etc.)", default="")

        with console.status("[bold green]Generating script...[/bold green]"):
            neg = runner.run_negotiation(
                address=address, seller_name=seller_name,
                asking_price=asking, mao=mao, seller_situation=situation,
            )

        console.print(Panel(neg["opening_script"],
                            title="[bold cyan]OPENING SCRIPT[/bold cyan]", border_style="cyan"))
        console.print(Panel(
            f"  Open at:   [bold yellow]{currency(neg['your_target'])}[/bold yellow]  (12% below MAO)\n"
            f"  MAO:       [bold cyan]{currency(neg['mao'])}[/bold cyan]\n\n"
            f"  [bold]Walk Assessment:[/bold]  {neg['walk_assessment']['decision']}\n"
            f"  {neg['walk_assessment']['full_analysis'][:400]}",
            title="[bold green]DEAL ASSESSMENT[/bold green]", border_style="green",
        ))

    elif sub == "5":
        console.print("\n[bold]Generate Contract[/bold]\n")
        address     = Prompt.ask("Property address")
        seller_name = Prompt.ask("Seller name")
        price       = FloatPrompt.ask("Purchase price")
        strategy    = Prompt.ask(
            "Strategy",
            choices=["Wholesale", "Flip", "BRRRR", "Buy & Hold", "Subject-To", "Seller Finance"],
            default="Wholesale",
        )
        w_fee = 0
        if strategy == "Wholesale":
            w_fee = FloatPrompt.ask("Assignment / wholesale fee", default=10000)

        deal = {"address": address, "seller_name": seller_name, "price": price,
                "strategy": strategy, "best_strategy": strategy, "wholesale_fee": w_fee}

        # Contract is a free template — skip the paid AI offer packet here.
        with console.status("[bold green]Generating contract...[/bold green]"):
            close_result = runner.prepare_close(deal, include_offer_packet=False)

        contract = close_result["contract"]
        body     = contract.get("content", str(contract))

        console.print(Panel(body,
                            title=f"[bold yellow]{close_result['contract_type'].upper()} CONTRACT[/bold yellow]",
                            border_style="yellow"))

        if close_result.get("warnings"):
            console.print("\n[bold red]Warnings:[/bold red]")
            for w in close_result["warnings"]:
                console.print(f"  ⚠ {w}")

        console.print("\n[bold green]✓ Contract ready to sign![/bold green]")
        console.print("[yellow]⚠  Have a real estate attorney review before signing.[/yellow]")
        # generate_contract() already saved a copy; surface that path.
        if contract.get("filename"):
            console.print(f"[dim]Auto-saved to {contract['filename']}[/dim]")

    press_enter()


# ── 27. Agent Dashboard ───────────────────────────────────────────────────────

def menu_agent_dashboard():
    section("AGENT DASHBOARD")

    runner = get_runner()
    dash   = runner.dashboard()
    stats  = dash["stats"]

    # ── Agent Roster ─────────────────────────────────────────────────────────
    AGENT_ROSTER = [
        {
            "name":       "LeadAgent — The Hunter",
            "model":      "Haiku 4.5 (triage) + Opus 4 (learn)",
            "role":       "Proactively scans Craigslist FSBO, Detroit DLBA, Tax Deed, HUD daily",
            "skills":     [
                "Scores every lead 1–10 with distress-signal analysis",
                "Flags HIGH MARGIN deals (price well below ARV)",
                "Runs all-4-strategy deal card on priced leads",
                "Updates scoring patterns from won/lost outcomes",
            ],
            "proactive":  "Runs every N hours in background — no input needed",
            "learns":     "After every 5 wins: updates best markets, distress signals, min score threshold",
        },
        {
            "name":       "NegotiationAgent — The Deal Closer",
            "model":      "Opus 4",
            "role":       "Writes all seller-facing communication — never lets emotion drive the number",
            "skills":     [
                "Opening negotiation scripts tailored to seller situation",
                "Counter-offer responses that hold MAO",
                "Objection handling (title issues, repairs, timeline pressure)",
                "Walk-away assessment — knows when to fold",
            ],
            "proactive":  "Auto-generates scripts when lead is queued for contact",
            "learns":     "After deals: updates best openers, winning tactics, conditions that close",
        },
        {
            "name":       "ClosingAgent — The Paper Pusher",
            "model":      "Opus 4",
            "role":       "Generates legally-structured contracts — pure Python (no API cost)",
            "skills":     [
                "6 contract types: Assignment, Purchase/Sale, Subject-To, Seller Finance, Lease-Option, Double Close",
                "AI Seller Offer Packet with deal summary + comps + strategy pitch",
                "Auto-selects correct contract based on deal strategy",
                "Saves every contract as timestamped .txt file",
            ],
            "proactive":  "Triggered automatically when deal scores 7+ and strategy is selected",
            "learns":     "Tracks which contract types and timelines produce fastest closes",
        },
        {
            "name":       "AgentRunner — The Orchestrator",
            "model":      "No AI — pure Python",
            "role":       "Schedules agents, manages pipeline state, triggers self-improvement cycle",
            "skills":     [
                "Runs full pipeline: Lead → Enrich → Analyze → Close",
                "Background mode: auto-scans every N hours via daemon thread",
                "Checks needs_learning() flag — fires all 3 agent.learn() after 5 wins",
                "Dashboard: live stats, active leads, high-margin deals, activity log",
            ],
            "proactive":  "Always running in background once started (menu option 26)",
            "learns":     "Routes learning results back to each specialized agent",
        },
    ]

    roster_lines = []
    for ag in AGENT_ROSTER:
        roster_lines.append(f"[bold cyan]▶ {ag['name']}[/bold cyan]  [dim]({ag['model']})[/dim]")
        roster_lines.append(f"  [italic]{ag['role']}[/italic]")
        for sk in ag["skills"]:
            roster_lines.append(f"    [green]•[/green] {sk}")
        roster_lines.append(f"  [yellow]⚡ Proactive:[/yellow] {ag['proactive']}")
        roster_lines.append(f"  [magenta]🧠 Learns:[/magenta]  {ag['learns']}")
        roster_lines.append("")

    console.print(Panel(
        "\n".join(roster_lines),
        title="[bold yellow]AGENT ROSTER — SPECIALIZED ROLES[/bold yellow]",
        border_style="yellow",
        padding=(0, 1),
    ))

    # ── Performance Summary ────────────────────────────────────────────────
    status_str = "[bold green]● RUNNING[/bold green]" if dash["running"] else "[dim]○ Idle[/dim]"
    console.print(Panel(
        f"  Status:          {status_str}\n\n"
        f"  Total Earned:    [bold green]${stats.get('total_earned', 0):,.0f}[/bold green]\n"
        f"  Deals Won:       [cyan]{stats.get('won', 0)}[/cyan]   "
        f"Lost: [red]{stats.get('lost', 0)}[/red]\n"
        f"  Close Rate:      [bold]{stats.get('close_rate', 0)}%[/bold]\n"
        f"  Avg Assignment Fee: [green]${stats.get('avg_fee', 0):,.0f}[/green]\n"
        f"  Avg Days to Close:  [dim]{stats.get('avg_days_to_close', 0)}[/dim]",
        title="[bold green]AGENT PERFORMANCE[/bold green]",
        border_style="green",
    ))

    new_leads = dash.get("new_leads", [])
    if new_leads:
        console.print(f"\n[bold cyan]── NEW LEADS (top {len(new_leads)}) ──[/bold cyan]")
        t = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
        t.add_column("Score", justify="right")
        t.add_column("Title", max_width=48)
        t.add_column("Price", justify="right")
        t.add_column("Strategy")
        t.add_column("Source")
        for lead in new_leads:
            score = lead.get("score", 0)
            sc    = "green" if score >= 8 else "yellow" if score >= 6 else "red"
            t.add_row(
                f"[{sc}]{score:.1f}[/{sc}]",
                lead.get("title", "")[:48],
                currency(lead.get("price", 0)),
                lead.get("best_strategy", "?"),
                lead.get("source", "")[:15],
            )
        console.print(t)

    high_margin = dash.get("high_margin", [])
    if high_margin:
        console.print(f"\n[bold green]── ⭐ HIGH MARGIN DEALS ──[/bold green]")
        for lead in high_margin:
            console.print(f"  [bold green]⭐[/bold green]  {lead.get('title','')[:55]}")
            console.print(f"     ${lead.get('price',0):,}  │  {lead.get('best_strategy','?')}  │  Score {lead.get('score',0):.1f}")
            if lead.get("url"):
                console.print(f"     [dim]{lead['url']}[/dim]")

    recent = dash.get("recent", [])
    if recent:
        console.print(f"\n[bold dim]── RECENT ACTIVITY ──[/bold dim]")
        for act in reversed(recent[-8:]):
            ts = act.get("ts", "")[:16]
            console.print(
                f"  [dim]{ts}[/dim]  [cyan]{act.get('agent','')}[/cyan]  "
                f"{act.get('action','')}  [dim]{act.get('detail','')[:40]}[/dim]"
            )

    patterns = dash.get("learned_patterns", {})
    if any(v for v in patterns.values() if v):
        console.print(f"\n[bold yellow]── AGENT LEARNED PATTERNS ──[/bold yellow]")
        for agent_name, p in patterns.items():
            insights = (p or {}).get("insights", [])
            if insights:
                console.print(f"\n  [bold]{agent_name.upper()}:[/bold]")
                for ins in insights[:3]:
                    console.print(f"    • {ins}")

    if Confirm.ask("\nRecord a deal outcome (train the agents)?", default=False):
        _record_deal_outcome()

    press_enter()


def _record_deal_outcome():
    from agents.memory import record_deal_outcome
    console.print("\n[bold]Record Deal Outcome[/bold]\n")
    address      = Prompt.ask("Property address")
    outcome      = Prompt.ask("Outcome", choices=["won", "lost"], default="won")
    price        = FloatPrompt.ask("Contract purchase price")
    fee          = FloatPrompt.ask("Assignment fee earned (0 if lost)", default=0)
    days         = IntPrompt.ask("Days from first contact to outcome", default=30)
    strategy     = Prompt.ask("Strategy", choices=["Wholesale","Flip","BRRRR","Buy & Hold"], default="Wholesale")
    what_worked  = Prompt.ask("What worked?", default="") if outcome == "won" else ""
    what_failed  = Prompt.ask("What killed this deal?", default="") if outcome == "lost" else ""

    record_deal_outcome({
        "address":        address,
        "outcome":        outcome,
        "price":          price,
        "fee_earned":     fee,
        "days_to_close":  days,
        "strategy":       strategy,
        "what_worked":    what_worked,
        "what_failed":    what_failed,
    })
    console.print(f"\n[green]✓ Outcome recorded. Agents will learn from this![/green]")
    if outcome == "won":
        console.print(f"[bold green]  🎉 ${fee:,.0f} earned![/bold green]")


# ── 30. Owner-Financing Finder ─────────────────────────────────────────────────

def menu_owner_finance():
    section("OWNER-FINANCING FINDER")
    console.print(
        "[dim]The lowest-barrier way in: the seller becomes the bank. No loan "
        "qualification, low down payment, fast close. This finds the sellers who say yes.[/dim]\n"
    )

    console.print(
        "  [1] Where to FIND owner-financed deals (sources)\n"
        "  [2] Seller motivation signals — who will carry the note\n"
        "  [3] Analyze a low-entry deal (down, monthly, cash flow)\n"
        "  [4] The pitch — how to ASK for owner financing\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0", "1", "2", "3", "4"], default="3")
    if sub == "0":
        return

    if sub == "1":
        _of_sources()
    elif sub == "2":
        _of_signals()
    elif sub == "3":
        _of_analyze()
    elif sub == "4":
        _of_pitch()

    press_enter()


def _of_sources():
    console.print("\n[bold green]── WHERE OWNER-FINANCED DEALS LIVE ──[/bold green]\n")
    for name, info in OWNER_FINANCE_SOURCES.items():
        console.print(f"[bold cyan]▶ {name}[/bold cyan]")
        if info.get("url"):
            console.print(f"  [dim]{info['url']}[/dim]")
        console.print(f"  {info['how']}")
        console.print(f"  [yellow]💡 {info['tip']}[/yellow]\n")


def _of_signals():
    console.print("\n[bold green]── WHO WILL CARRY THE NOTE ──[/bold green]\n")
    t = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
    t.add_column("Signal", max_width=38)
    t.add_column("Why it matters")
    for sig, why in MOTIVATION_SIGNALS:
        t.add_row(sig, why)
    console.print(t)

    console.print("\n[bold]Ideal seller profile:[/bold]")
    for k, v in IDEAL_SELLER_PROFILE.items():
        marker = "[red]⚠[/red]" if k == "red_flag" else "[green]✓[/green]"
        console.print(f"  {marker} {v}")


def _of_analyze():
    console.print("\n[bold]Low-Entry Owner-Finance Analyzer[/bold]\n")
    price    = FloatPrompt.ask("Purchase price")
    down_pct = FloatPrompt.ask("Down payment % (e.g. 5)", default=5) / 100
    rate     = FloatPrompt.ask("Interest rate % you'll offer", default=5.0) / 100
    years    = IntPrompt.ask("Amortization (years)", default=30)
    rent     = FloatPrompt.ask("Expected monthly rent (0 if flip/wholesale)", default=0)
    closing  = FloatPrompt.ask("Estimated closing costs", default=2000)
    ti       = FloatPrompt.ask("Monthly taxes + insurance", default=0) if rent else 0

    r = calc_owner_finance_entry(
        purchase_price=price,
        down_payment_pct=down_pct,
        interest_rate=rate,
        loan_years=years,
        monthly_rent=rent,
        closing_costs=closing,
        monthly_taxes_ins=ti,
    )

    t = Table(show_header=False, box=box.ROUNDED, title="[bold green]OWNER-FINANCE DEAL[/bold green]")
    t.add_column("Metric", style="bold")
    t.add_column("Value", justify="right")
    t.add_row("Purchase Price",       currency(r["purchase_price"]))
    t.add_row("Down Payment",         f"{currency(r['down_payment'])}  ({r['down_payment_pct']})")
    t.add_row("[bold]CASH TO CLOSE[/bold]", f"[bold yellow]{currency(r['cash_to_close'])}[/bold yellow]")
    t.add_row("Seller-Carried Note",  currency(r["loan_amount"]))
    t.add_row("Interest Rate",        r["interest_rate_pct"])
    t.add_row("Term",                 f"{r['loan_term_years']} yrs")
    t.add_row("Monthly P&I",          currency(r["monthly_pi"]))
    t.add_row("Monthly Total (P&I+TI)", currency(r["monthly_total"]))
    if r["monthly_cash_flow"] != "N/A":
        cf = r["monthly_cash_flow"]
        cf_color = "green" if cf >= 500 else "yellow" if cf > 0 else "red"
        t.add_row("Monthly Cash Flow", f"[{cf_color}]{currency(cf)}[/{cf_color}]")
        t.add_row("Cash-on-Cash",      f"{r['cash_on_cash_pct']}%")
    console.print(t)

    console.print(Panel(
        r["verdict"],
        border_style=r["verdict_color"],
        title="[bold]VERDICT[/bold]",
    ))


def _of_pitch():
    p = NEGOTIATION_PITCH
    console.print("\n[bold green]── HOW TO ASK FOR OWNER FINANCING ──[/bold green]\n")

    console.print("[bold]The opening question:[/bold]")
    console.print(f"  [italic green]{p['opening_question']}[/italic green]\n")

    console.print("[bold]Trade price for terms:[/bold]")
    console.print(f"  {p['full_price_for_terms']}\n")

    console.print("[bold]The tax angle:[/bold]")
    console.print(f"  [italic]{p['the_tax_angle']}[/italic]\n")

    console.print("[bold]The income angle:[/bold]")
    console.print(f"  [italic]{p['the_income_angle']}[/italic]\n")

    console.print("[bold]De-risk it for the seller:[/bold]")
    for line in p["de_risk_for_them"]:
        console.print(f"  [green]•[/green] {line}")

    console.print("\n[bold]Terms to push for:[/bold]")
    for line in p["terms_to_push_for"]:
        console.print(f"  [cyan]→[/cyan] {line}")


# ── 29. Tenant Pre-Screener ───────────────────────────────────────────────────

def menu_tenant_screener():
    section("TENANT PRE-SCREENER")
    console.print("[dim]Pre-screen tenants before paying for a full background check.[/dim]\n")

    console.print(
        "  [1] Pre-screen a tenant (Q&A scoring)\n"
        "  [2] Section 8 screening checklist\n"
        "  [3] VASH (Veterans) screening guide\n"
        "  [4] Full-service screening providers\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3","4"], default="1")
    if sub == "0":
        return

    if sub == "1":
        console.print("\n[bold]Tenant Pre-Screen[/bold]")
        rent = FloatPrompt.ask("Monthly rent amount")

        console.print("\n[dim]Answer based on what the applicant told you.[/dim]\n")
        answers: dict = {}

        for q in SCREENING_QUESTIONS:
            qid   = q["id"]
            label = q["q"]
            qtype = q["type"]
            opts  = q.get("options", [])

            if qtype == "number":
                val = FloatPrompt.ask(f"  {label}", default=0)
                answers[qid] = val
            elif qtype == "yesno":
                answers[qid] = Confirm.ask(f"  {label}", default=False)
            elif qtype == "choice" and opts:
                console.print(f"\n  [bold]{label}[/bold]")
                for i, opt in enumerate(opts):
                    console.print(f"    [{i}] {opt}")
                idx = Prompt.ask("  Select", choices=[str(i) for i in range(len(opts))], default="0")
                answers[qid] = opts[int(idx)]
            else:
                answers[qid] = Prompt.ask(f"  {label}", default="")

        result = score_tenant(answers, rent)
        score  = result["score"]
        sc     = "green" if score >= 70 else "yellow" if score >= 50 else "red"

        positives_str = ""
        if result.get("positives"):
            positives_str = "[bold green]Positives:[/bold green]\n" + "\n".join(f"  ✓ {p}" for p in result["positives"]) + "\n\n"

        red_flags_str = ""
        if result.get("red_flags"):
            red_flags_str = "[bold red]Red Flags:[/bold red]\n" + "\n".join(f"  ⚠ {r}" for r in result["red_flags"])

        console.print(Panel(
            f"  [bold {sc}]Score: {score}/100[/bold {sc}]\n"
            f"  Recommendation: [bold]{result['recommendation']}[/bold]\n\n"
            + positives_str + red_flags_str,
            title="[bold]SCREENING RESULT[/bold]",
            border_style=sc,
        ))

        console.print("\n[bold]Next Steps:[/bold]")
        if score >= 70:
            console.print("  ✓ Run full background check (option 4 for providers)")
            console.print("  ✓ Verify income directly with employer")
            console.print("  ✓ Call previous landlord references")
        elif score >= 50:
            console.print("  → Ask more questions before proceeding")
            console.print("  → Consider requiring larger security deposit")
        else:
            console.print("  ✗ Decline — too many red flags")
            console.print("  → Document reason (follow Fair Housing laws)")

    elif sub == "2":
        console.print("\n[bold cyan]SECTION 8 TENANT SCREENING[/bold cyan]\n")
        console.print("[bold]What CHANGES with Section 8:[/bold]")
        for item in SECTION8_SCREENING.get("what_changes", []):
            console.print(f"  ✓ {item}")
        console.print("\n[bold]What You STILL Check:[/bold]")
        for item in SECTION8_SCREENING.get("what_you_still_check", []):
            console.print(f"  • {item}")
        console.print("\n[bold]The Process:[/bold]")
        for step in SECTION8_SCREENING.get("process", []):
            console.print(f"  {step}")
        console.print(f"\n  GoSection8.com:  {SECTION8_SCREENING.get('gosection8','')}")
        console.print(f"  Find tenants:    {SECTION8_SCREENING.get('find_tenants','')}")

    elif sub == "3":
        console.print("\n[bold yellow]VASH — VETERANS AFFAIRS SUPPORTIVE HOUSING[/bold yellow]\n")
        console.print(f"  {VASH_SCREENING.get('what_is_vash','')}\n")
        console.print(f"  [bold]VA Case Manager:[/bold] {VASH_SCREENING.get('va_case_manager','')}\n")
        find_list = VASH_SCREENING.get("find_vash_tenants", [])
        if find_list:
            console.print("[bold]How to find VASH tenants:[/bold]")
            for item in find_list:
                console.print(f"  • {item}")

    elif sub == "4":
        console.print("\n[bold cyan]SCREENING SERVICES[/bold cyan]\n")
        t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        t.add_column("Service", style="bold")
        t.add_column("Cost")
        t.add_column("What's Included")
        t.add_column("URL")
        for svc_name, svc in SCREENING_SERVICES.items():
            t.add_row(svc_name, svc.get("cost",""), svc.get("checks",""), svc.get("url",""))
        console.print(t)
        console.print("\n[bold yellow]Tip:[/bold yellow] Charge application fee to tenant — legal and standard practice.")

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
