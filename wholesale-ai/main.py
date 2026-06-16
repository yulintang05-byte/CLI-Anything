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
    VASH_SCREENING, score_tenant, rent_qualification,
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
from modules.cash_buyers import (
    match_buyers_to_deal, add_buyer, get_all_buyers,
    buyer_list_summary, PLATFORMS_BY_SPEED, BUYER_PROFILES,
    record_buyer_deal_sent, record_buyer_deal_closed,
)
from modules.skip_trace import (
    SKIP_TRACE_SERVICES, FREE_SKIP_TRACE_METHODS, ABSENTEE_OWNER_SIGNALS,
    get_lookup_links, absentee_check_from_lead, get_motivated_lead_sources,
)
from modules.outreach import (
    SELLER_TYPES, get_all_scripts, generate_sms,
    generate_cold_call_script, generate_email, generate_voicemail,
    generate_direct_mail_postcard, generate_door_knock_script,
    detect_seller_type_from_lead,
)
from modules.comps import (
    validate_arv, quick_comp_check, FREE_COMP_SOURCES, adjust_comp,
)
from modules.daily_digest import (
    generate_morning_digest, get_last_digest, get_pipeline_health,
)
from modules.scheduler import (
    load_scheduler_config, save_scheduler_config, get_next_run_time,
    start_scheduler, stop_scheduler, is_scheduler_running, get_scheduler_status,
    SchedulerConfig,
)
from modules.rehab_estimator import (
    estimate_by_scope, estimate_room_by_room, estimate_flip_profit,
    get_contractor_tips, get_rehab_checklist, SCOPE_LEVELS, ROOM_COSTS,
)
from modules.title_company import (
    TITLE_COMPANIES, CLOSING_COSTS_BY_STATE, WHAT_TITLE_DOES,
    INVESTOR_TITLE_TIPS, calc_closing_costs, get_title_companies_for_state,
    get_hud1_settlement_guide, find_title_company_tips,
)
from modules.market_intel import (
    MARKET_DATA, wholesale_market_score, get_market_comparison,
    get_market_trends_report, get_best_markets_for_strategy,
    calc_market_appreciation, list_available_markets, get_market_quick_stats,
)
from modules.property_mgmt import (
    get_pm_for_market, estimate_pm_cost, list_covered_markets,
    FEE_BREAKDOWN, PM_VET_QUESTIONS, SECTION8_PM_TIPS,
    NATIONAL_PM_COMPANIES,
)
from modules.hml_trigger import (
    evaluate_brrrr_trigger, brrrr_scenarios, hml_trigger_summary,
    BRRRR_HML_TRIGGER,
)
from modules.elevenlabs_voice import (
    has_api_key as voice_has_key,
    generate_voicemail, generate_buyer_pitch_audio, list_available_voices,
)
from modules.obsidian_sync import (
    export_deal_to_obsidian, export_pipeline_digest_to_obsidian, vault_status,
)
from modules.email_sender import queue_deal_outreach, email_status
from modules.agent_offer import send_agent_offer
from modules.dispo import (
    build_pitch as dispo_build_pitch, fire_blast as dispo_fire,
    preflight as dispo_preflight, load_deals as dispo_load_deals,
    save_deal as dispo_save_deal, matched_buyers as dispo_matched_buyers,
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
    ai_status  = "[green]✓ Active[/green]" if os.getenv("ANTHROPIC_API_KEY") else "[red]✗ Not set (add to .env)[/red]"
    hud_status = "[green]✓ Active[/green]" if os.getenv("HUD_API_TOKEN") else "[yellow]○ Optional[/yellow]"
    rc_status  = "[green]✓ Live feed[/green]" if os.getenv("RENTCAST_API_KEY") else "[dim]○ Sample mode[/dim]"
    summary    = pipeline_summary()
    pipe_status = f"[cyan]{summary['active_deals']} active deals | ${summary['closed_fees']:,.0f} closed[/cyan]"

    # Quick digest check — show alert if there are high-margin leads waiting
    last = get_last_digest()
    digest_alert = ""
    if last and last.get("high_margin_24h", 0) > 0:
        digest_alert = f"  [bold green]⭐ {last['high_margin_24h']} HIGH MARGIN deal(s) waiting — option 33[/bold green]\n"

    console.print(
        f"  AI: {ai_status}   HUD: {hud_status}   RentCast: {rc_status}   Pipeline: {pipe_status}\n"
        + digest_alert
    )


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


def data_source_banner(what: str = "real for-sale listings with real ARV + rent"):
    """Show whether the live RentCast feed is connected. Reused by every
    lane (live leads, owner finance, luxury) so the user always knows if
    they're on REAL data or sample/link mode."""
    from modules import rentcast
    diag = rentcast.diagnose()
    if diag["ok"]:
        console.print(Panel(
            f"[bold green]LIVE DATA CONNECTED[/bold green] — RentCast feed active.\n"
            f"Agents will pull {what}.",
            border_style="green", title="Data Source",
        ))
    else:
        console.print(Panel(
            f"[yellow]Sample/link mode[/yellow] — no live listings feed.\n"
            f"Reason: [bold]{diag['reason']}[/bold]\n"
            f"Fix: {diag.get('fix','')}\n"
            f"[dim]Free key at https://app.rentcast.io/app/api → add "
            f"RENTCAST_API_KEY to your .env[/dim]",
            border_style="yellow", title="Data Source",
        ))
    return diag["ok"]


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

            "  [bold green]── OUTREACH & CLOSE ────────────────────────────────────────[/bold green]\n"
            "  [bold cyan][31][/bold cyan] [bold]Cash Buyer Matcher[/bold] — Who to assign this deal to RIGHT NOW\n"
            "  [bold cyan][32][/bold cyan] Skip Trace — Find the owner's phone + email\n"
            "  [bold cyan][33][/bold cyan] [bold]Morning Digest[/bold] — Today's deals, pipeline, action items\n"
            "  [bold cyan][34][/bold cyan] Outreach Script Generator (SMS, call, email, door knock)\n"
            "  [bold cyan][35][/bold cyan] Comp Validator — Is your ARV right?\n\n"

            "  [bold green]── AUTOMATION & INTELLIGENCE ────────────────────────────────[/bold green]\n"
            "  [bold cyan][36][/bold cyan] [bold]Auto-Scheduler[/bold] — Daily 6am scan runs itself, no babysitting\n"
            "  [bold cyan][37][/bold cyan] Granular Rehab Estimator — Room-by-room breakdown + contractor tips\n"
            "  [bold cyan][38][/bold cyan] Title Company Finder + Closing Cost Calculator\n"
            "  [bold cyan][39][/bold cyan] [bold]Market Intelligence[/bold] — Score & compare 17 markets\n"
            "  [bold cyan][40][/bold cyan] Appreciation Projector — Future value by market\n"
            "  [bold cyan][41][/bold cyan] [bold]Property Management Finder[/bold] — Local + national PMs by market\n"
            "  [bold cyan][42][/bold cyan] [bold]BRRRR HML Trigger[/bold] — Auto-match hard money lenders when deal qualifies\n"
            "  [bold cyan][43][/bold cyan] [bold]DISPO BLAST[/bold] — Sell a locked deal to your cash-buyer bench (1 command)\n"
            "  [bold cyan][44][/bold cyan] [bold]CASH-FLOW DEAL HUNTER[/bold] — Flip OR landlord math, all markets, live\n\n"

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

        valid = [str(i) for i in range(22)] + ["23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","43","44"]
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
        elif choice == "31":
            menu_cash_buyer_matcher()
        elif choice == "32":
            menu_skip_trace()
        elif choice == "33":
            menu_morning_digest()
        elif choice == "34":
            menu_outreach_scripts()
        elif choice == "35":
            menu_comp_validator()
        elif choice == "36":
            menu_scheduler()
        elif choice == "37":
            menu_rehab_estimator()
        elif choice == "38":
            menu_title_company()
        elif choice == "39":
            menu_market_intelligence()
        elif choice == "40":
            menu_appreciation_projector()
        elif choice == "41":
            menu_property_mgmt()
        elif choice == "42":
            menu_brrrr_hml()
        elif choice == "43":
            menu_dispo_blast()
        elif choice == "44":
            menu_deal_hunter()


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


def display_full_deal_card(data: dict, address: str = "", badge: str = "", warning: str = ""):
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

    # Data-quality warning — fires when the AVM rent/value looked unreliable
    # (e.g. land valued as a house). Always show it BEFORE the strategy math so
    # Alberto never acts on a phantom number.
    if warning:
        console.print(Panel(
            f"[bold yellow]⚠ VERIFY BEFORE YOU ACT[/bold yellow]\n{warning}",
            border_style="yellow", title="[bold red]DATA CHECK[/bold red]",
        ))

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

    # ── Auto tenant pre-screen (fires on any rental deal) ───────────────
    _show_prescreen(data.get("market_rent", 0), sec8.get("fmr_est", 0))

    # ── Cash buyer match (fires automatically on HIGH MARGIN deals) ──────
    if data.get("high_margin"):
        _show_cash_buyer_match(data, address)


def _show_prescreen(market_rent: float, fmr: float = 0):
    """Instant tenant-qualification bar for a rental deal. Uses LIVE rent +
    LIVE FMR so the numbers are never stale. Shown on every deal card."""
    q = rent_qualification(market_rent, section8_fmr=fmr)
    if not q.get("applicable"):
        return
    s8_line = ""
    if q.get("section8"):
        s8 = q["section8"]
        col = "green" if s8.get("covers_market_rent") else "yellow"
        s8_line = f"\n  [bold {col}]Section 8:[/bold {col}] {s8['note']}"
    console.print(Panel(
        f"  To fill at [green]{currency(q['monthly_rent'])}/mo[/green], a tenant needs:\n"
        f"  Income (3× rent): [bold yellow]{currency(q['income_needed_3x'])}/mo[/bold yellow]"
        f"   │  Deposit: {currency(q['security_deposit'])}"
        f"   │  Move-in cash: {currency(q['cash_to_move_in'])}\n"
        f"  [dim]Ideal:[/dim] {q['ideal_tenant']}"
        f"{s8_line}\n"
        f"  [dim]Fastest fill: {q['fastest_fill'][0]}; require 3× income proof up front.[/dim]",
        title="[bold cyan]🧍 TENANT PRE-SCREEN (auto)[/bold cyan]",
        border_style="cyan",
    ))


def _one_click_close_package(lead: dict):
    """
    Full close package for a HIGH MARGIN deal — runs automatically.
    Generates: outreach scripts + negotiation + contract + pipeline entry.
    Alberto only needs to sign.
    """
    section("⚡ ONE-CLICK CLOSE PACKAGE")
    analysis = lead.get("full_analysis", {})
    address  = lead.get("title", "Unknown")
    price    = lead.get("price", 0)
    arv      = analysis.get("arv", 0) or lead.get("arv", 0)
    repairs  = analysis.get("repairs", 0)
    strategy = analysis.get("best_strategy", "Wholesale")
    mao_val  = analysis.get("flip", {}).get("mao", 0) or price

    if not arv:
        console.print("[yellow]⚠ No ARV data — run comp validator (35) before sending outreach.[/yellow]")
        arv = price * 1.4

    # 1. Auto-detect seller type from lead signals
    seller_type = detect_seller_type_from_lead(lead)
    profile = load_profile()
    inv_name  = profile.get("name", "Alberto Soriano")
    inv_phone = profile.get("phone", "")
    inv_email = profile.get("email", "")

    console.print(f"\n[bold]Building full close package for:[/bold] {address}\n")

    # 2. Outreach scripts
    scripts = get_all_scripts(
        seller_type=seller_type, property_address=address,
        investor_name=inv_name, investor_phone=inv_phone,
        investor_email=inv_email, offer_price=mao_val, arv=arv,
    )
    console.print(Panel(
        f"[bold]Auto-detected seller type:[/bold] [cyan]{scripts['seller_type']}[/cyan]\n\n"
        f"[bold green]SMS (send first):[/bold green]\n{scripts['sms']}\n\n"
        f"[bold yellow]Call opener:[/bold yellow]\n{scripts['cold_call']['opener'][:250]}",
        title="[bold green]1. OUTREACH SCRIPTS — READY TO SEND[/bold green]",
        border_style="green",
    ))

    # 3. Auto add to pipeline
    deal_in_pipe = add_deal(
        address=address, asking_price=price, arv=arv, repairs=repairs,
        mao=mao_val, wholesale_fee=analysis.get("flip", {}).get("wholesale_fee", 10000),
        source=lead.get("source", "Agent"), stage="Lead",
        notes=f"HIGH MARGIN auto-added. Strategy: {strategy}. Score: {lead.get('score',0):.1f}",
    )
    console.print(f"[green]✓ Added to pipeline — ID: {deal_in_pipe['id']}[/green]")

    # 4. Cash buyer match
    city  = address.split(",")[0].strip() if "," in address else address[:20]
    state = address.split(",")[-1].strip()[:2] if "," in address else ""
    buyer_result = match_buyers_to_deal(
        price=price, arv=arv, strategy=strategy,
        city=city, state=state,
        market_rent=analysis.get("market_rent", 0),
        repairs=repairs, is_high_margin=True,
    )
    ranked_buyers = buyer_result.get("ranked_buyer_types", [])[:2]
    if ranked_buyers:
        buyer_lines = []
        for bname, bp in ranked_buyers:
            buyer_lines.append(f"  [bold]{bname}[/bold]: {bp.get('find_at',[''])[0]}")
        console.print(Panel(
            "\n".join(buyer_lines) + f"\n\n[dim]Script:[/dim] {buyer_result['scripts']['text'][:120]}",
            title="[bold cyan]2. BUYER MATCH — WHO GETS THIS CONTRACT[/bold cyan]",
            border_style="cyan",
        ))

    # 5. Save full package to file — always auto-save
    if True:
        safe   = address.replace(" ", "_").replace(",", "")[:30]
        fname  = f"close_package_{safe}.txt"
        email  = scripts["email"]
        content = f"""CLOSE PACKAGE — {address}
Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}
Pipeline ID: {deal_in_pipe['id']}

=== DEAL NUMBERS ===
Price: ${price:,.0f} | ARV: ${arv:,.0f} | Repairs: ${repairs:,.0f} | MAO: ${mao_val:,.0f}
Strategy: {strategy}

=== OUTREACH ===
SMS:
{scripts['sms']}

VOICEMAIL:
{scripts['voicemail']}

COLD CALL OPENER:
{scripts['cold_call']['opener']}

EMAIL SUBJECT: {email['subject']}
EMAIL:
{email['body']}

=== FOLLOW-UP SEQUENCE ===
{chr(10).join(scripts['follow_up_sequence'])}
"""
        Path(fname).write_text(content)
        console.print(f"[green]✓ Full package saved to {fname}[/green]")

    # ── ElevenLabs voicemail audio ────────────────────────────────────────────
    vm_path = None
    if voice_has_key():
        console.print("\n[dim]Generating voicemail audio via ElevenLabs...[/dim]")
        phone   = inv_phone
        vm_path = generate_voicemail(
            property_address = address,
            investor_name    = inv_name,
            investor_phone   = phone,
            seller_type      = seller_type,
            output_dir       = "output/voicemails",
        )
        if vm_path:
            console.print(f"[green]✓ Voicemail MP3:[/green] {vm_path}  [dim](play this when seller picks up)[/dim]")

    # ── Obsidian vault export ─────────────────────────────────────────────────
    vs = vault_status()
    if vs["configured"]:
        export_deal_to_obsidian(
            deal_data   = {
                "price":            price,
                "arv":              arv,
                "repair_estimate":  repairs,
                "wholesale_spread": arv - price - repairs,
                "city":             address.split(",")[1].strip() if "," in address else "",
                "source":           "Close Package",
            },
            address     = address,
            status      = "active",
            sms_script  = scripts.get("sms", ""),
            email_body  = scripts.get("email", {}).get("body", ""),
        )

    # ── Auto email outreach ───────────────────────────────────────────────────
    es = email_status()
    email_sent = False
    seller_email = lead.get("seller_email", lead.get("contact_email", ""))
    if es["configured"] and seller_email:
        console.print(f"\n[dim]Sending outreach email via {es['provider']}...[/dim]")
        email_data = scripts.get("email", {})
        email_sent = queue_deal_outreach(
            seller_email      = seller_email,
            property_address  = address,
            email_subject     = email_data.get("subject", f"Quick question about {address}"),
            email_body        = email_data.get("body", ""),
            investor_name     = inv_name,
            investor_email    = inv_email,
        )

    if vm_path:
        voices_line = "[green]✓ Voicemail audio generated (ElevenLabs)[/green]"
    elif voice_has_key():
        voices_line = "[yellow]⚠ Voicemail FAILED — check ElevenLabs key / credits[/yellow]"
    else:
        voices_line = ""
    obsidian_line = "[green]✓ Deal note saved to Obsidian vault[/green]" if vs["configured"] else ""
    email_line   = f"[green]✓ Outreach email sent ({es['provider']})[/green]" if email_sent else ""

    status_lines = "\n  ".join(filter(None, [voices_line, obsidian_line, email_line]))

    console.print(Panel(
        f"  [bold green]✓ Pipeline entry created[/bold green]  ID: {deal_in_pipe['id']}\n"
        f"  [bold green]✓ Outreach scripts ready[/bold green]  (SMS → call → email)\n"
        f"  [bold green]✓ Buyer match complete[/bold green]   (who to assign to)\n"
        + (f"  {status_lines}\n" if status_lines else "")
        + f"\n  [bold yellow]NEXT STEP:[/bold yellow] Send the SMS above to the seller NOW.\n"
        f"  When they respond: run negotiation script (option 26 → option 4)\n"
        f"  When they accept: generate contract (option 26 → option 5)",
        title="[bold green]⚡ PACKAGE COMPLETE — Alberto only signs[/bold green]",
        border_style="green",
    ))


def _auto_generate_contract(lead: dict):
    """
    Auto-generate assignment contract the moment a HIGH MARGIN deal is found.
    Alberto only needs to sign — everything else is pre-filled.
    """
    from agents.closing_agent import ClosingAgent
    profile  = load_profile()
    address  = lead.get("title", "Unknown")
    price    = lead.get("price", 0)
    analysis = lead.get("full_analysis", {})
    # Clamp the fee to Alberto's target band — analysis wholesale_fee can be
    # fantasy-large when the ARV is inflated (e.g. $88k on a $30k house).
    fee_min  = profile.get("target_assignment_fee_min", 5000)
    fee_max  = profile.get("target_assignment_fee_max", 15000)
    raw_fee  = analysis.get("flip", {}).get("wholesale_fee", 10000)
    fee      = max(fee_min, min(raw_fee, fee_max))

    agent = ClosingAgent(profile=profile)
    result = agent.generate_contract(
        contract_type   = "assignment",
        buyer_name      = f"{profile.get('name','Alberto Soriano')} and/or assigns",
        seller_name     = lead.get("seller_name", "[SELLER NAME]"),
        address         = address,
        purchase_price  = price,
        emd             = profile.get("emd_amount", 1000),
        closing_days    = profile.get("closing_days", 21),
        assignment_fee  = fee,
        inspection_days = 14,
        extra_terms     = "Buyer and/or assigns. Seller to cooperate with assignment.",
    )
    console.print(Panel(
        f"  [bold green]✓ Assignment contract generated[/bold green]\n"
        f"  File: [cyan]{result['filename']}[/cyan]\n"
        f"  Assignment fee: [bold green]${fee:,.0f}[/bold green]  |  Close in {profile.get('closing_days',21)} days\n\n"
        f"  [bold yellow]ALBERTO'S ONLY JOB:[/bold yellow] Open the file above and sign line 208.",
        title="[bold green]3. CONTRACT — READY TO SIGN[/bold green]",
        border_style="green",
    ))


def _auto_send_agent_offer(lead: dict):
    """
    LEGAL outreach: email a cash Letter of Intent to the LISTING AGENT.

    This is the hands-off path to deal #1 — contacting the listing agent with
    a written cash offer is normal business contact (not TCPA-restricted cold
    homeowner contact). Fires automatically on real HIGH MARGIN deals. If no
    agent email or email provider is set, the LOI is still saved to disk so
    Alberto can send it in one paste.
    """
    profile  = load_profile()
    analysis = lead.get("full_analysis", {})
    mao = (analysis.get("flip", {}).get("mao", 0)
           or lead.get("price", 0))
    if mao <= 0:
        return

    result = send_agent_offer(lead, mao=mao, profile=profile, auto_send=True)

    if result["sent"]:
        body = (
            f"  [bold green]✓ Cash offer EMAILED to listing agent[/bold green]\n"
            f"  To: [cyan]{result['to_name'] or 'Listing Agent'}[/cyan] <{result['to_email']}>\n"
            f"  Opening: [bold green]${result['opening_offer']:,.0f}[/bold green]   "
            f"Walk-away ceiling: [yellow]${result['walk_away']:,.0f}[/yellow]\n\n"
            f"  [dim]When the agent replies, run option 26 → 4 for the negotiation script.[/dim]"
        )
        border = "green"
    else:
        body = (
            f"  [yellow]Offer NOT auto-sent — {result['reason']}.[/yellow]\n"
            f"  Saved ready-to-send: [cyan]{result['saved_to']}[/cyan]\n"
            f"  Opening: [bold]${result['opening_offer']:,.0f}[/bold]   "
            f"Walk-away ceiling: ${result['walk_away']:,.0f}\n"
        )
        if result["to_email"]:
            body += f"  [bold yellow]ONE STEP:[/bold yellow] paste that file's body to {result['to_email']}.\n"
        else:
            body += (
                "  [bold yellow]ONE STEP:[/bold yellow] this listing has no agent email — "
                "open the RentCast/Zillow link, copy the agent's email, paste the offer.\n"
            )
        border = "yellow"

    console.print(Panel(
        body,
        title="[bold green]4. CASH OFFER → LISTING AGENT (legal, hands-off)[/bold green]",
        border_style=border,
    ))


def _show_cash_buyer_match(data: dict, address: str = ""):
    """Auto-fire buyer matching on HIGH MARGIN deals — shows who to call FIRST."""
    profile = load_profile()
    result  = match_buyers_to_deal(
        price        = data.get("price", 0),
        arv          = data.get("arv", 0),
        strategy     = data.get("best_strategy", "Wholesale"),
        city         = address.split(",")[0].strip() if "," in address else address,
        state        = address.split(",")[-1].strip() if "," in address else "",
        market_rent  = data.get("market_rent", 0),
        bedrooms     = data.get("bedrooms", 3),
        repairs      = data.get("repairs", 0),
        is_high_margin = True,
    )

    ranked = result.get("ranked_buyer_types", [])[:3]
    personal = result.get("personal_matches", [])
    scripts  = result.get("scripts", {})

    lines = []
    if personal:
        lines.append("[bold green]YOUR PERSONAL BUYER LIST — CALL FIRST:[/bold green]")
        for b in personal[:3]:
            lines.append(
                f"  [bold]{b['name']}[/bold]  {b.get('phone','')}  {b.get('email','')}"
                f"  [dim]{b.get('buyer_type','')} · {', '.join(b.get('markets',[])[:2])}[/dim]"
            )
        lines.append("")

    if ranked:
        lines.append("[bold yellow]BEST BUYER TYPES FOR THIS DEAL:[/bold yellow]")
        for i, (buyer_type, profile_data) in enumerate(ranked, 1):
            lines.append(f"  [cyan]{i}.[/cyan] [bold]{buyer_type}[/bold]  [dim]{profile_data.get('pitch','')[:70]}[/dim]")
            find_list = profile_data.get("find_at", [])
            if find_list:
                lines.append(f"     → {find_list[0]}")
        lines.append("")

    # Top platform
    top_platform = result["platforms"][0] if result.get("platforms") else None
    if top_platform:
        lines.append(
            f"[bold]FASTEST way to a buyer:[/bold] [green]{top_platform['name']}[/green] "
            f"({top_platform['speed']}) — {top_platform['how'][:70]}"
        )
        lines.append("")

    lines.append(f"[dim]READY TEXT:[/dim] {scripts.get('text','')[:120]}")

    console.print(Panel(
        "\n".join(lines),
        title="[bold green]🎯 CASH BUYER MATCH — WHO TO CALL RIGHT NOW[/bold green]",
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
            asking_price=price,
            arv=arv,
            repairs=data["repairs"],
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
    section("LIVE LEAD FINDER — FIND & SCORE DEALS NOW")
    console.print("[dim]Pulls ALL for-sale listings (RentCast live feed) + Craigslist FSBO, "
                  "Land Bank, tax deed, and HUD. Scores every house for a $10-15k spread.[/dim]\n")

    # Show data-source status so you always know if you're on REAL or sample data
    data_source_banner()

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
        console.print(f"\n[bold green]⭐ {len(ready)} HIGH MARGIN DEAL(S) — Auto-processing all...[/bold green]\n")
        for i, lead in enumerate(ready, 1):
            if lead.get("is_link_only") or lead.get("status") == "link_only":
                continue
            console.print(f"[bold cyan]── Deal {i}/{len(ready)}: {lead.get('title','')[:60]} ──[/bold cyan]")
            display_full_deal_card(
                lead["full_analysis"],
                address=lead.get("title", "")[:60],
                badge=lead.get("source", ""),
                warning=lead.get("data_warning", ""),
            )
            console.print(f"  [dim]URL: {lead.get('url', '')}[/dim]\n")
            # Any data_warning means the numbers are suspect — hold auto-outreach
            # until verification. DLBA deals need buildingdetroit.org check;
            # inflated ARV deals need manual comps (option 35) first.
            warning_text = str(lead.get("data_warning", ""))
            if warning_text:
                if "DLBA RISK" in warning_text or "Land Bank" in warning_text:
                    reason = "verify owner is NOT Detroit Land Bank at buildingdetroit.org"
                elif "AVM ARV" in warning_text:
                    reason = "run comp validator (option 35) to get a real ARV before outreach"
                else:
                    reason = "review the warning above before sending outreach"
                console.print(
                    f"[bold yellow]⏸ HELD — {reason}.[/bold yellow]\n"
                )
                continue
            _one_click_close_package(lead)
            _auto_generate_contract(lead)
            _auto_send_agent_offer(lead)
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

    press_enter()


# ── 24. Luxury Wholesale ──────────────────────────────────────────────────────

def menu_luxury():
    section("LUXURY WHOLESALE + DEVELOPER BUYERS ($500k+)")
    console.print("[dim]Wholesale high-end properties to developers. 65% ARV rule. Fees $25k–$100k+.[/dim]\n")

    console.print(
        "  [1] Browse Luxury Markets & Sources\n"
        "  [2] Analyze a Luxury Deal\n"
        "  [3] Find Developer Buyers\n"
        "  [4] [bold]PULL LIVE luxury listings now ($500k+)[/bold]\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3","4"], default="1")
    if sub == "0":
        return

    if sub == "4":
        _luxury_live()
        press_enter()
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


def _luxury_live():
    """Pull live high-end listings for developer wholesale."""
    from modules import rentcast
    console.print()
    if not data_source_banner("luxury listings ($500k+) for developer wholesale"):
        console.print("\n[dim]Set the key and come back — this will pull real luxury inventory.[/dim]")
        return

    market    = Prompt.ask("Luxury market (City ST)", default="Miami FL")
    parts     = market.split()
    city      = " ".join(parts[:-1]) if len(parts) > 1 else market
    state     = parts[-1] if len(parts) > 1 else ""
    min_price = IntPrompt.ask("Min price", default=500000)
    max_price = IntPrompt.ask("Max price (0 = no cap)", default=0)

    console.print("\n[bold green]Scanning live luxury listings...[/bold green]\n")
    leads = rentcast.search_luxury(
        city=city, state=state, min_price=min_price, max_price=max_price, limit=100,
    )

    if not leads:
        console.print("[yellow]No luxury listings returned. Try another market or lower the min price.[/yellow]")
        return

    t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED,
              title=f"[bold green]LUXURY LISTINGS — {market}[/bold green]")
    t.add_column("Address", max_width=38)
    t.add_column("Price", justify="right")
    t.add_column("Beds", justify="right")
    t.add_column("SqFt", justify="right")
    t.add_column("Status", max_width=34)
    for lead in leads[:20]:
        note = lead.get("luxury_note", "")
        nc = "green" if "Stale" in note else "yellow" if "days" in note else "dim"
        t.add_row(
            lead.get("title", "")[:38],
            currency(lead.get("price", 0)),
            str(lead.get("bedrooms", "?")),
            f"{lead.get('sqft') or '?'}",
            f"[{nc}]{note}[/{nc}]",
        )
    console.print(t)
    stale = [l for l in leads if "Stale" in l.get("luxury_note", "")]
    console.print(f"\n[bold]{len(leads)} luxury listings[/bold] · "
                  f"[green]{len(stale)} stale (best developer leverage)[/green]")
    console.print("[dim]Run option 2 to analyze any one with the 65% ARV rule, "
                  "then option 3 to find the developer buyers.[/dim]")


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
        "  [1] Run pipeline — find & score leads (review mode, no auto-close)\n"
        "      → Use option [bold]23[/bold] for the full auto-close experience\n"
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
        "  [5] [bold]PULL LIVE owner-finance candidates now[/bold]\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0", "1", "2", "3", "4", "5"], default="5")
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
    elif sub == "5":
        _of_live()

    press_enter()


def _of_live():
    """Pull live listings and rank owner-finance candidates."""
    from modules import rentcast
    console.print()
    if not data_source_banner("owner-finance candidates from live listings"):
        console.print("\n[dim]Set the key and come back — this will pull real houses.[/dim]")
        return

    profile = load_profile()
    default_mkt = profile.get("target_markets", "Detroit MI").split(",")[0].strip()
    market = Prompt.ask("Market (City ST)", default=default_mkt)
    parts  = market.split()
    city   = " ".join(parts[:-1]) if len(parts) > 1 else market
    state  = parts[-1] if len(parts) > 1 else ""
    max_price = IntPrompt.ask("Max price", default=120000)

    console.print("\n[bold green]Scanning live listings for owner-finance candidates...[/bold green]\n")
    leads = rentcast.search_owner_finance(city=city, state=state, max_price=max_price, limit=100)

    if not leads:
        console.print("[yellow]No listings returned. Try a different market or raise max price.[/yellow]")
        return

    t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED,
              title=f"[bold green]OWNER-FINANCE CANDIDATES — {market}[/bold green]")
    t.add_column("Conf", justify="center")
    t.add_column("Address", max_width=38)
    t.add_column("Price", justify="right")
    t.add_column("DOM", justify="right")
    t.add_column("Signal", max_width=40)
    conf_color = {"high": "green", "medium": "yellow", "low": "dim"}
    for lead in leads[:20]:
        c = lead.get("owner_finance_confidence", "low")
        t.add_row(
            f"[{conf_color[c]}]{c.upper()}[/{conf_color[c]}]",
            lead.get("title", "")[:38],
            currency(lead.get("price", 0)),
            str(lead.get("days_on_market", "?")),
            lead.get("owner_finance_signal", "")[:40],
        )
    console.print(t)
    high = [l for l in leads if l.get("owner_finance_confidence") == "high"]
    console.print(f"\n[bold green]{len(high)} explicit owner-finance listings[/bold green] "
                  f"· [dim]{len(leads)} total candidates ranked[/dim]")
    console.print("[dim]Tip: option 4 gives you the exact pitch to lock the note.[/dim]")


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

    # If it's a rental, auto-screen who can fill it
    if rent and rent > 0:
        _show_prescreen(rent)


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
        "  [5] Rent qualification bar (who can fill this rent?)\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3","4","5"], default="1")
    if sub == "0":
        return

    if sub == "5":
        rent = FloatPrompt.ask("Monthly rent (use the live deal's rent)")
        fmr  = FloatPrompt.ask("HUD FMR for the area (0 if unknown)", default=0)
        _show_prescreen(rent, fmr)
        press_enter()
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


# ── 31. Cash Buyer Matcher ────────────────────────────────────────────────────

def menu_cash_buyer_matcher():
    section("CASH BUYER MATCHER — WHO BUYS THIS DEAL")
    console.print("[dim]Instantly match your deal to the right buyer type, "
                  "your personal buyer list, and the platforms to find new buyers fast.[/dim]\n")

    console.print(
        "  [1] Match a specific deal to buyers\n"
        "  [2] Add a buyer to my personal list\n"
        "  [3] View my buyer list\n"
        "  [4] Browse buyer-finding platforms\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3","4"], default="1")
    if sub == "0":
        return

    if sub == "1":
        console.print("\n[bold]Deal Details[/bold]\n")
        price    = FloatPrompt.ask("Purchase / assignment price")
        arv      = FloatPrompt.ask("ARV")
        repairs  = FloatPrompt.ask("Estimated repairs", default=0)
        strategy = Prompt.ask("Strategy", choices=["Wholesale","Flip","BRRRR","Buy & Hold","Section 8","Owner Finance"], default="Wholesale")
        city     = Prompt.ask("City (e.g. Detroit)", default="")
        state    = Prompt.ask("State abbreviation", default="MI").upper()
        beds     = IntPrompt.ask("Bedrooms", default=3)
        rent     = FloatPrompt.ask("Monthly rent estimate (0 if flip/wholesale)", default=0)

        result = match_buyers_to_deal(
            price=price, arv=arv, strategy=strategy,
            city=city, state=state, market_rent=rent,
            bedrooms=beds, repairs=repairs, is_high_margin=True,
        )

        ranked   = result["ranked_buyer_types"]
        personal = result["personal_matches"]
        scripts  = result["scripts"]
        platforms = result["platforms"]

        if personal:
            console.print(f"\n[bold green]✓ {len(personal)} buyer(s) in YOUR LIST match this deal:[/bold green]")
            t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
            t.add_column("Name", style="bold")
            t.add_column("Phone")
            t.add_column("Email")
            t.add_column("Type")
            t.add_column("Markets")
            for b in personal:
                t.add_row(b["name"], b.get("phone","—"), b.get("email","—"),
                          b.get("buyer_type",""), ", ".join(b.get("markets",[])[:2]))
            console.print(t)
        else:
            console.print("\n[yellow]No buyers in your personal list yet — add them as you meet them (option 2).[/yellow]")

        console.print(f"\n[bold cyan]── TOP BUYER TYPES FOR THIS DEAL ──[/bold cyan]\n")
        for i, (buyer_type, bp) in enumerate(ranked[:3], 1):
            color = "green" if i == 1 else "cyan" if i == 2 else "yellow"
            console.print(f"  [{color}][bold]#{i}: {buyer_type}[/bold][/{color}]")
            console.print(f"     Wants: {bp.get('wants','')[:80]}")
            console.print(f"     Pitch: [italic]{bp.get('pitch','')[:80]}[/italic]")
            console.print(f"     Close time: [green]{bp.get('daysToClose','')}[/green]")
            find_at = bp.get("find_at", [])
            if find_at:
                console.print(f"     Find them: {find_at[0]}")
            console.print()

        console.print("[bold yellow]── FASTEST PLATFORMS ──[/bold yellow]")
        t2 = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
        t2.add_column("Platform", style="bold")
        t2.add_column("Speed")
        t2.add_column("Cost")
        t2.add_column("How")
        for p in platforms[:5]:
            t2.add_row(p["name"], p["speed"], p["cost"], p["how"][:60])
        console.print(t2)

        console.print(Panel(
            f"[bold]TEXT TO SEND:[/bold]\n{scripts['text']}\n\n"
            f"[bold]EMAIL SUBJECT:[/bold] {scripts['email_subject']}\n\n"
            f"[bold]COLD CALL OPENER:[/bold]\n{scripts['cold_call_opener'][:200]}",
            title="[bold green]OUTREACH SCRIPTS — COPY & SEND[/bold green]",
            border_style="green",
        ))

    elif sub == "2":
        console.print("\n[bold]Add a Cash Buyer to Your List[/bold]\n")
        name     = Prompt.ask("Buyer name")
        phone    = Prompt.ask("Phone", default="")
        email    = Prompt.ask("Email", default="")
        btype    = Prompt.ask("Buyer type", choices=list(BUYER_PROFILES.keys()), default="Fix & Flip Investor")
        markets  = Prompt.ask("Markets (comma-separated, e.g. Detroit, Birmingham)", default="")
        p_min    = FloatPrompt.ask("Min deal price they buy", default=0)
        p_max    = FloatPrompt.ask("Max deal price they buy", default=200000)
        notes    = Prompt.ask("Notes (criteria, preferences)", default="")

        b = add_buyer(
            name=name, phone=phone, email=email,
            markets=[m.strip() for m in markets.split(",") if m.strip()],
            buyer_type=btype, price_min=p_min, price_max=p_max, notes=notes,
        )
        console.print(f"\n[green]✓ Buyer added! ID: {b['id']}[/green]")
        console.print("[dim]Next time you match a deal, this buyer will appear automatically.[/dim]")

    elif sub == "3":
        buyers = get_all_buyers()
        if not buyers:
            console.print("[yellow]No buyers yet — add your first buyer (option 2).[/yellow]")
        else:
            t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED, title="MY BUYER LIST")
            t.add_column("ID", width=8)
            t.add_column("Name", style="bold")
            t.add_column("Phone")
            t.add_column("Type")
            t.add_column("Markets")
            t.add_column("Price Range", justify="right")
            t.add_column("Deals")
            for b in buyers:
                t.add_row(
                    b.get("id",""), b.get("name",""), b.get("phone",""),
                    b.get("buyer_type",""), ", ".join(b.get("markets",[])[:2]),
                    f"${b.get('price_min',0):,.0f}–${b.get('price_max',0):,.0f}",
                    f"sent:{b.get('deals_sent',0)} closed:{b.get('deals_closed',0)}",
                )
            console.print(t)

    elif sub == "4":
        console.print("\n[bold cyan]── BUYER-FINDING PLATFORMS (fastest → slowest) ──[/bold cyan]\n")
        for p in PLATFORMS_BY_SPEED:
            speed_color = "green" if "Same day" in p["speed"] or "1-2" in p["speed"] else "yellow"
            console.print(f"  [bold]{p['name']}[/bold]  [{speed_color}]{p['speed']}[/{speed_color}]  [dim]{p['cost']}[/dim]")
            console.print(f"    {p['how']}")
            if p.get("url") and "facebook" not in p["url"]:
                console.print(f"    [dim]{p['url']}[/dim]")
            console.print()

    press_enter()


# ── 32. Skip Trace ────────────────────────────────────────────────────────────

def menu_skip_trace():
    section("SKIP TRACE — FIND THE OWNER")
    console.print("[dim]Get the seller's phone, email, and mailing address from any property. "
                  "Free methods first. Paid options for instant bulk results.[/dim]\n")

    console.print(
        "  [1] Lookup links for a specific address\n"
        "  [2] Free skip trace methods (step-by-step)\n"
        "  [3] Paid skip trace services (fastest)\n"
        "  [4] Pre-motivated seller lead sources (gold mine lists)\n"
        "  [5] Absentee owner signals — who's most motivated\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3","4","5"], default="1")
    if sub == "0":
        return

    if sub == "1":
        address  = Prompt.ask("Property address")
        city     = Prompt.ask("City")
        state    = Prompt.ask("State (e.g. MI)").upper()
        zip_code = Prompt.ask("Zip code (optional)", default="")

        links = get_lookup_links(address, city, state, zip_code)
        console.print(Panel(
            "\n".join(f"  [bold]{k}:[/bold] {v}" for k, v in links.items()),
            title=f"[bold cyan]SKIP TRACE LINKS — {address}[/bold cyan]",
            border_style="cyan",
        ))
        console.print("\n[bold yellow]Process:[/bold yellow]")
        console.print("  1. Start with County Records (NETR) → get owner name + mailing address")
        console.print("  2. Google the owner name + city → find phone/email")
        console.print("  3. If stuck: pay BatchSkipTracing $0.17 → instant phone + email")

    elif sub == "2":
        console.print("\n[bold green]── FREE SKIP TRACE METHODS ──[/bold green]\n")
        for method, info in FREE_SKIP_TRACE_METHODS.items():
            console.print(f"  [bold cyan]{method}[/bold cyan]  [dim]({info['time']})[/dim]")
            console.print(f"    {info['description']}")
            console.print(f"    How: [italic]{info['how']}[/italic]")
            console.print(f"    Gets you: [green]{info['what_you_get']}[/green]")
            if info.get("url"):
                console.print(f"    [dim]{info['url']}[/dim]")
            console.print()

    elif sub == "3":
        console.print("\n[bold green]── PAID SKIP TRACE SERVICES (FASTEST) ──[/bold green]\n")
        t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        t.add_column("Service", style="bold")
        t.add_column("Cost")
        t.add_column("Speed")
        t.add_column("Data")
        t.add_column("URL")
        for name, svc in SKIP_TRACE_SERVICES.items():
            t.add_row(name, svc["cost"], svc["speed"], svc["data"][:45], svc["url"])
        console.print(t)
        console.print("\n[bold yellow]Recommendation:[/bold yellow]")
        console.print("  Start: BatchSkipTracing.com — best quality, $0.17/record")
        console.print("  Quick single: SkipGenie.com — $0.10-0.15 instant")
        console.print("  All-in-one: PropStream — comps + skip trace + outreach together")

    elif sub == "4":
        console.print("\n[bold green]── PRE-MOTIVATED SELLER LEAD SOURCES ──[/bold green]\n")
        console.print("[dim]These lists are gold — owners with problems who NEED to sell.[/dim]\n")
        sources = get_motivated_lead_sources()
        for source, info in sources.items():
            motivation_color = "green" if "10/10" in str(info["motivation"]) else \
                               "yellow" if "9/10" in str(info["motivation"]) or "8/10" in str(info["motivation"]) else "white"
            console.print(f"  [bold]{source}[/bold]  [{motivation_color}]Motivation: {info['motivation']}[/{motivation_color}]")
            console.print(f"    {info['description']}")
            console.print(f"    How to get: [italic]{info['how_to_get']}[/italic]")
            free_str = "[green]FREE[/green]" if info["free"] is True else f"[yellow]{info['free']}[/yellow]"
            console.print(f"    Cost: {free_str}")
            console.print()

    elif sub == "5":
        console.print("\n[bold green]── ABSENTEE OWNER SIGNALS ──[/bold green]\n")
        console.print("[dim]The more of these signals a property has, the more motivated the owner is.[/dim]\n")
        t = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
        t.add_column("Signal", max_width=38, style="bold")
        t.add_column("Why it means they're motivated")
        for signal, why in ABSENTEE_OWNER_SIGNALS:
            t.add_row(signal, why)
        console.print(t)

    press_enter()


# ── 33. Morning Digest ────────────────────────────────────────────────────────

def menu_morning_digest():
    section("MORNING DEAL DIGEST")
    console.print("[dim]Your daily briefing — what the agents found, pipeline status, what to do today.[/dim]\n")

    profile = load_profile()
    target_markets = profile.get("target_markets", "Detroit MI, Birmingham AL, Memphis TN")
    markets = [m.strip() for m in target_markets.split(",")]

    with console.status("[bold green]Compiling your morning briefing...[/bold green]"):
        digest = generate_morning_digest(markets)
        health = get_pipeline_health()

    console.print(Panel(
        f"  [bold]Good morning![/bold] {digest['date']}\n\n"
        f"  [bold cyan]NEW LEADS (last 24h):[/bold cyan]  {digest['new_leads_24h']} leads · "
        f"[bold green]{digest['high_margin_24h']} HIGH MARGIN[/bold green]\n\n"
        f"  [bold cyan]PIPELINE:[/bold cyan]\n"
        f"    Active deals:     {digest['pipeline']['active']}\n"
        f"    Under contract:   [bold green]{digest['pipeline']['under_contract']}[/bold green]\n"
        f"    Offers out:       [yellow]{digest['pipeline']['offer_sent']}[/yellow]\n"
        f"    Marketing:        {digest['pipeline']['marketing']}\n\n"
        f"  [bold cyan]YOUR NUMBERS:[/bold cyan]\n"
        f"    Earned:    [bold green]${digest['stats']['total_earned']:,.0f}[/bold green]  "
        f"    Goal: $15,000  →  "
        f"[{'green' if digest['stats']['goal_pct'] >= 100 else 'yellow'}]{digest['stats']['goal_pct']}%[/{'green' if digest['stats']['goal_pct'] >= 100 else 'yellow'}] there\n"
        f"    To go:     [yellow]${digest['stats']['to_go']:,.0f}[/yellow]  "
        f"    ({1 if digest['stats']['avg_fee'] > 0 else '?'} more deal closes it)",
        title="[bold green]☀ MORNING BRIEFING[/bold green]",
        border_style="green",
    ))

    if digest["action_items"]:
        console.print("\n[bold yellow]── TODAY'S ACTION ITEMS ──[/bold yellow]")
        for i, item in enumerate(digest["action_items"], 1):
            console.print(f"  {i}. {item}")

    if health["stale"]:
        console.print(f"\n[bold red]── STALE DEALS (no update {health['stale'][0]['days_idle']}+ days) ──[/bold red]")
        for d in health["stale"][:3]:
            console.print(f"  [red]•[/red] [{d['stage']}] {d['address']} — {d['days_idle']} days idle — update or kill it")

    if health["urgent"]:
        console.print(f"\n[bold red]── URGENT ──[/bold red]")
        for d in health["urgent"]:
            console.print(f"  [bold red]⚠[/bold red] {d['address']} — {d['stage']}")

    hot = digest.get("hot_deals", [])
    if hot:
        console.print(f"\n[bold cyan]── HOT LEADS FROM AGENTS ──[/bold cyan]")
        t = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
        t.add_column("Score", justify="right")
        t.add_column("Property", max_width=48)
        t.add_column("Price", justify="right")
        t.add_column("Strategy")
        for lead in hot[:5]:
            score = lead.get("score", 0)
            sc    = "green" if score >= 8 else "yellow"
            t.add_row(f"[{sc}]{score:.1f}[/{sc}]", lead.get("title","")[:48],
                      currency(lead.get("price", 0)), lead.get("best_strategy","?"))
        console.print(t)

    console.print("\n[dim]Tip: Run option [bold]23[/bold] for a live scan right now. Option [bold]36[/bold] to set up daily auto-scan.[/dim]")
    press_enter()


# ── 34. Outreach Script Generator ─────────────────────────────────────────────

def menu_outreach_scripts():
    section("OUTREACH SCRIPT GENERATOR")
    console.print("[dim]Generate SMS, cold call, voicemail, email, and door knock scripts "
                  "for any seller situation — ready to copy and send.[/dim]\n")

    profile = load_profile()
    inv_name  = profile.get("name", "Alberto Soriano")
    inv_phone = profile.get("phone", "")
    inv_email = profile.get("email", "")

    console.print("[bold]Seller type:[/bold]")
    type_list = list(SELLER_TYPES.items())
    for i, (k, v) in enumerate(type_list):
        console.print(f"  [{i:2}] {v}")
    console.print()
    idx = Prompt.ask("Select seller type", default="0")
    try:
        seller_type = type_list[int(idx)][0]
    except (ValueError, IndexError):
        seller_type = "generic"

    address  = Prompt.ask("Property address")
    seller_name = Prompt.ask("Seller name (optional)", default="")
    offer_price = FloatPrompt.ask("Your offer price (0 to skip)", default=0)
    arv         = FloatPrompt.ask("ARV (0 to skip)", default=0)

    scripts = get_all_scripts(
        seller_type     = seller_type,
        property_address = address,
        seller_name     = seller_name,
        investor_name   = inv_name,
        investor_phone  = inv_phone,
        investor_email  = inv_email,
        offer_price     = offer_price,
        arv             = arv,
    )

    console.print(f"\n[bold]Generated scripts for:[/bold] [cyan]{scripts['seller_type']}[/cyan]\n")

    console.print(Panel(scripts["sms"], title="[bold green]📱 SMS (Copy & Text)[/bold green]", border_style="green"))
    console.print()
    console.print(Panel(scripts["voicemail"], title="[bold cyan]📞 VOICEMAIL SCRIPT[/bold cyan]", border_style="cyan"))
    console.print()

    call_script = scripts["cold_call"]
    console.print(Panel(
        f"[bold green]OPENER:[/bold green]\n{call_script['opener']}\n\n"
        f"[bold yellow]VALUE PROP:[/bold yellow]\n{call_script['value_prop']}\n\n"
        f"[bold cyan]CLOSE:[/bold cyan]\n{call_script['close']}\n\n"
        f"[bold]COMMON OBJECTIONS:[/bold]\n"
        + "\n\n".join(f"  [red]'{obj}'[/red]\n  → {resp}" for obj, resp in list(call_script["objections"].items())[:3]),
        title="[bold yellow]📞 COLD CALL SCRIPT[/bold yellow]",
        border_style="yellow",
    ))
    console.print()

    email_data = scripts["email"]
    console.print(Panel(
        f"[bold]SUBJECT:[/bold] {email_data['subject']}\n\n{email_data['body']}",
        title="[bold blue]📧 EMAIL[/bold blue]",
        border_style="blue",
    ))
    console.print()
    console.print(Panel(scripts["direct_mail"], title="[bold magenta]✉ DIRECT MAIL POSTCARD[/bold magenta]", border_style="magenta"))

    console.print("\n[bold yellow]FOLLOW-UP SEQUENCE:[/bold yellow]")
    for step in scripts["follow_up_sequence"]:
        console.print(f"  {step}")

    if Confirm.ask("\nSave all scripts to file?", default=False):
        safe = address.replace(" ", "_").replace(",", "")[:30]
        fname = f"outreach_{safe}.txt"
        content = f"OUTREACH PACKAGE — {address}\nSeller Type: {scripts['seller_type']}\n\n"
        content += f"SMS:\n{scripts['sms']}\n\n"
        content += f"VOICEMAIL:\n{scripts['voicemail']}\n\n"
        content += f"EMAIL SUBJECT: {email_data['subject']}\nEMAIL BODY:\n{email_data['body']}\n\n"
        content += f"DIRECT MAIL:\n{scripts['direct_mail']}\n"
        Path(fname).write_text(content)
        console.print(f"[green]✓ Saved to {fname}[/green]")

    press_enter()


# ── 35. Comp Validator ────────────────────────────────────────────────────────

def menu_comp_validator():
    section("COMP VALIDATOR — IS YOUR ARV RIGHT?")
    console.print("[dim]Validate your ARV against comparable sales before you make an offer. "
                  "One bad ARV estimate kills a deal.[/dim]\n")

    console.print(
        "  [1] Quick sanity check (no comps needed)\n"
        "  [2] Full comp validation (enter your comps)\n"
        "  [3] Where to pull comps (free sources)\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3"], default="1")
    if sub == "0":
        return

    if sub == "1":
        console.print("\n[bold]Quick ARV Sanity Check[/bold]\n")
        price    = FloatPrompt.ask("Purchase price")
        arv      = FloatPrompt.ask("Your ARV estimate")
        repairs  = FloatPrompt.ask("Repair estimate")
        fee      = FloatPrompt.ask("Wholesale fee target", default=10000)
        sqft     = FloatPrompt.ask("Square footage", default=1200)
        city     = Prompt.ask("City (for market benchmark)", default="")
        state    = Prompt.ask("State", default="").upper()

        result = quick_comp_check(
            purchase_price=price, your_arv_guess=arv,
            repairs=repairs, wholesale_fee=fee,
            city=city, state=state, sqft=sqft,
        )

        deal_color = "green" if result["is_deal_70"] else "yellow" if result["is_deal_65"] else "red"
        deal_str   = (
            "[bold green]✓ DEAL (70% rule)[/bold green]" if result["is_deal_70"]
            else "[bold yellow]⚠ Deal at 65% only (tighter margin)[/bold yellow]" if result["is_deal_65"]
            else f"[bold red]✗ NOT A DEAL — need ${result['below_mao_gap']:,.0f} price reduction[/bold red]"
        )

        console.print(Panel(
            f"  {deal_str}\n\n"
            f"  Purchase Price:  {currency(price)}\n"
            f"  Your ARV:        {currency(arv)}\n"
            f"  Repairs:         {currency(repairs)}\n"
            f"  Spread:          [{'green' if result['spread'] > 0 else 'red'}]{currency(result['spread'])} "
            f"({result['spread_pct']}% of ARV)[/{'green' if result['spread'] > 0 else 'red'}]\n\n"
            f"  MAO at 70% rule: [bold cyan]{currency(result['mao_70_rule'])}[/bold cyan]  "
            f"  MAO at 65%:      [cyan]{currency(result['mao_65_rule'])}[/cyan]\n"
            + (f"\n  Market benchmark ({city}): ${result.get('market_ppsf',0)}/sqft → ARV est {currency(result.get('market_arv_estimate',0))}\n"
               f"  {result.get('arv_market_note','')}" if result.get("market_ppsf") else ""),
            title="[bold]QUICK COMP CHECK[/bold]",
            border_style=deal_color,
        ))

        console.print("\n[bold]Pull real comps here to confirm:[/bold]")
        for name, url in result.get("comp_sources", {}).items():
            console.print(f"  • [bold]{name}:[/bold] {url}")

    elif sub == "2":
        console.print("\n[bold]Full Comp Validation[/bold]")
        console.print("[dim]Enter 3-5 comparable sales you found on Redfin/Zillow. "
                      "We'll adjust for differences and validate your ARV.[/dim]\n")

        your_arv = FloatPrompt.ask("Your ARV estimate")
        sub_beds = IntPrompt.ask("Subject property bedrooms", default=3)
        sub_baths = FloatPrompt.ask("Subject bathrooms", default=1.5)
        sub_sqft = FloatPrompt.ask("Subject sqft", default=1200)
        sub_cond = Prompt.ask("Subject condition", choices=["excellent","good","average","below","poor"], default="average")

        comps = []
        console.print("\n[dim]Enter comparable sales (press Enter on address to finish):[/dim]\n")
        while len(comps) < 7:
            idx = len(comps) + 1
            addr = Prompt.ask(f"Comp #{idx} address (Enter to finish)", default="")
            if not addr:
                break
            price = FloatPrompt.ask(f"  Sale price")
            beds  = IntPrompt.ask(f"  Beds", default=sub_beds)
            baths = FloatPrompt.ask(f"  Baths", default=sub_baths)
            sqft  = FloatPrompt.ask(f"  Sqft", default=sub_sqft)
            cond  = Prompt.ask(f"  Condition", choices=["excellent","good","average","below","poor"], default="good")
            comps.append({"address": addr, "price": price, "beds": beds, "baths": baths, "sqft": sqft, "condition": cond})

        if not comps:
            console.print("[yellow]No comps entered — can't validate.[/yellow]")
            press_enter()
            return

        result = validate_arv(
            your_arv=your_arv, comps=comps,
            subject_beds=sub_beds, subject_baths=sub_baths,
            subject_sqft=sub_sqft, subject_condition=sub_cond,
        )

        color = result["confidence_color"]
        console.print(Panel(
            f"  [{color}][bold]{result['confidence']}[/bold][/{color}]\n\n"
            f"  Your ARV:             {currency(result['your_arv'])}\n"
            f"  Comp Average (adj.):  [bold]{currency(result['avg_comp_arv'])}[/bold]\n"
            f"  Comp Low:             {currency(result['low_comp_arv'])}\n"
            f"  Comp High:            {currency(result['high_comp_arv'])}\n"
            f"  Variance:             {result['variance_pct']}% off comps\n"
            f"  Comps used:           {result['comp_count']}\n\n"
            f"  [italic]{result['bias_note']}[/italic]\n\n"
            f"  [bold]Recommendation:[/bold] {result['recommendation']}",
            title="[bold]ARV VALIDATION[/bold]",
            border_style=color,
        ))

    elif sub == "3":
        console.print("\n[bold green]── WHERE TO PULL COMPS (FREE) ──[/bold green]\n")
        for name, info in FREE_COMP_SOURCES.items():
            console.print(f"  [bold cyan]{name}[/bold cyan]  [dim]{info.get('reliability','')[:50]}[/dim]")
            console.print(f"    How: {info['how'][:90]}")
            console.print(f"    Best for: {info['use_for']}")
            if info.get("url"):
                console.print(f"    [dim]{info['url']}[/dim]")
            console.print()

    press_enter()


# ── 36. Auto-Scheduler ───────────────────────────────────────────────────────

def menu_scheduler():
    section("AUTO-SCHEDULER — DAILY SCAN RUNS ITSELF")
    console.print(
        "[dim]Set it once. Every morning at 6am (or every N hours) the agents scan "
        "for deals, score everything, and save your morning digest automatically. "
        "You wake up to a briefing — no babysitting required.[/dim]\n"
    )

    status = get_scheduler_status()
    running_str = "[bold green]● RUNNING[/bold green]" if status["running"] else "[dim]○ Idle[/dim]"
    next_run_str = status.get("next_run", "Not scheduled")
    last_run_str = status.get("last_run", "Never")
    last_summary = status.get("last_scan_summary", {})

    console.print(Panel(
        f"  Status:     {running_str}\n"
        f"  Next Run:   [cyan]{next_run_str}[/cyan]\n"
        f"  Last Run:   [dim]{last_run_str}[/dim]\n"
        + (
            f"  Last Scan:  [green]{last_summary.get('new_leads', 0)} leads found · "
            f"{last_summary.get('high_margin', 0)} HIGH MARGIN[/green]"
            if last_summary else ""
        ),
        title="[bold green]SCHEDULER STATUS[/bold green]",
        border_style="green" if status["running"] else "dim",
    ))

    console.print(
        "\n  [1] Start scheduler (daily or interval)\n"
        "  [2] Stop scheduler\n"
        "  [3] Run scan RIGHT NOW (manual trigger)\n"
        "  [4] View last scan results\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3","4"], default="1")
    if sub == "0":
        return

    if sub == "1":
        if status["running"]:
            console.print("[yellow]Scheduler already running.[/yellow]")
            press_enter()
            return

        mode = Prompt.ask("Run mode", choices=["daily", "interval"], default="daily")
        profile = load_profile()
        default_markets = profile.get("target_markets", "Detroit MI, Birmingham AL, Memphis TN")
        markets_input = Prompt.ask("Markets to scan", default=default_markets)
        markets = [m.strip() for m in markets_input.split(",")]
        max_price = IntPrompt.ask("Max price filter", default=80000)

        if mode == "daily":
            run_time = Prompt.ask("Run time (24hr, e.g. 06:00)", default="06:00")
            cfg = SchedulerConfig(run_time=run_time, interval_hours=None,
                                  markets=markets, max_price=max_price, enabled=True)
        else:
            hours = IntPrompt.ask("Run every N hours", default=12)
            cfg = SchedulerConfig(run_time="06:00", interval_hours=hours,
                                  markets=markets, max_price=max_price, enabled=True)

        save_scheduler_config(cfg)
        msg = start_scheduler(cfg)
        console.print(f"\n[bold green]✓ {msg}[/bold green]")
        console.print("[dim]Agents will run automatically. Check Morning Digest (option 33) for results.[/dim]")

    elif sub == "2":
        if not status["running"]:
            console.print("[dim]Scheduler not running.[/dim]")
        else:
            msg = stop_scheduler()
            console.print(f"\n[yellow]{msg}[/yellow]")

    elif sub == "3":
        profile = load_profile()
        markets_input = Prompt.ask(
            "Markets", default=profile.get("target_markets", "Detroit MI, Birmingham AL")
        )
        markets = [m.strip() for m in markets_input.split(",")]
        max_price = IntPrompt.ask("Max price", default=80000)
        console.print("\n[bold green]Running scan now...[/bold green]")

        runner = get_runner()
        with console.status("[bold green]Finding and scoring deals...[/bold green]"):
            result = runner.run_full_pipeline(markets=markets, max_price=max_price, console=None)

        ready  = result.get("ready_for_review", [])
        lr     = result.get("lead_result", {})
        console.print(Panel(
            f"  Leads Found:  [cyan]{lr.get('new_leads', 0)}[/cyan]\n"
            f"  High Margin:  [bold green]{len(ready)} deals[/bold green]\n"
            f"  Analyzed:     [cyan]{len(result.get('analyzed_leads', []))}[/cyan]\n\n"
            + (f"  [bold green]⭐ TOP DEAL: {ready[0].get('title','')[:55]}[/bold green]" if ready else "  [dim]No HIGH MARGIN deals this scan[/dim]"),
            title="[bold green]SCAN COMPLETE[/bold green]",
            border_style="green",
        ))

        if ready:
            if Confirm.ask("\nView top deal?", default=True):
                lead = ready[0]
                if lead.get("full_analysis"):
                    display_full_deal_card(lead["full_analysis"],
                                           address=lead.get("title",""), badge="AGENT FOUND")

    elif sub == "4":
        last = get_scheduler_status().get("last_scan_summary", {})
        if not last:
            console.print("[yellow]No scan results saved yet. Run a scan first.[/yellow]")
        else:
            console.print(Panel(
                "\n".join(f"  {k}: {v}" for k, v in last.items()),
                title="[bold cyan]LAST SCAN RESULTS[/bold cyan]",
                border_style="cyan",
            ))

    press_enter()


# ── 37. Granular Rehab Estimator ──────────────────────────────────────────────

def menu_rehab_estimator():
    section("GRANULAR REHAB ESTIMATOR")
    console.print(
        "[dim]Know exactly what rehab costs BEFORE you make an offer. "
        "Scoping it wrong by $10k kills your profit margin.[/dim]\n"
    )

    console.print(
        "  [1] Quick estimate by scope (cosmetic / medium / heavy / gut)\n"
        "  [2] Room-by-room breakdown (most accurate)\n"
        "  [3] Flip profit sanity check (repairs → net profit)\n"
        "  [4] Contractor tips (how to avoid getting burned)\n"
        "  [5] Rehab sequence checklist (what order to do work)\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3","4","5"], default="1")
    if sub == "0":
        return

    if sub == "1":
        console.print("\n[bold]Quick Scope Estimate[/bold]\n")
        sqft = FloatPrompt.ask("Square footage", default=1200)
        scope = Prompt.ask("Scope", choices=list(SCOPE_LEVELS.keys()), default="medium")
        region = Prompt.ask(
            "Region (affects labor costs)",
            choices=["midwest", "south", "southeast", "northeast", "west"],
            default="midwest",
        )
        beds  = IntPrompt.ask("Bedrooms", default=3)
        baths = IntPrompt.ask("Bathrooms", default=1)

        r = estimate_by_scope(sqft, scope, region, beds, baths)

        t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED,
                  title=f"[bold green]REHAB ESTIMATE — {scope.upper()}[/bold green]")
        t.add_column("Line Item", style="bold")
        t.add_column("Low", justify="right")
        t.add_column("Mid", justify="right")
        t.add_column("High", justify="right")

        for item in r.get("line_items", []):
            t.add_row(
                item.get("item", ""),
                currency(item.get("low", 0)),
                currency(item.get("mid", 0)),
                currency(item.get("high", 0)),
            )

        t.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold green]{currency(r['total_low'])}[/bold green]",
            f"[bold yellow]{currency(r['total_mid'])}[/bold yellow]",
            f"[bold red]{currency(r['total_high'])}[/bold red]",
        )
        console.print(t)

        console.print(f"\n[bold]Scope:[/bold] {SCOPE_LEVELS.get(scope, scope)}")
        if r.get("recommendations"):
            console.print("\n[bold yellow]Recommendations:[/bold yellow]")
            for rec in r["recommendations"][:5]:
                console.print(f"  • {rec}")

        console.print(f"\n[dim]Use MID estimate in your MAO calc. Add 10-15% contingency buffer.[/dim]")

    elif sub == "2":
        console.print("\n[bold]Room-by-Room Breakdown[/bold]\n")
        console.print("[dim]Include each system/room you need to address:[/dim]\n")

        rooms = {}
        room_list = [
            ("roof", "Roof (need replacement?)", "bool"),
            ("foundation", "Foundation issues?", "bool"),
            ("hvac", "HVAC (full replace?)", "bool"),
            ("electrical", "Electrical rewire?", "bool"),
            ("plumbing", "Plumbing (full)?", "bool"),
            ("kitchen", "Kitchen upgrade?", "bool"),
            ("bathrooms", "Bathrooms (how many to rehab?)", "int"),
            ("flooring", "New flooring throughout?", "bool"),
            ("paint_interior", "Interior paint?", "bool"),
            ("paint_exterior", "Exterior paint?", "bool"),
            ("windows", "How many windows to replace?", "int"),
        ]

        sqft = FloatPrompt.ask("Property square footage", default=1200)
        region = Prompt.ask("Region", choices=["midwest","south","southeast","northeast","west"], default="midwest")

        for key, label, rtype in room_list:
            if rtype == "bool":
                rooms[key] = {"include": Confirm.ask(f"  {label}", default=False), "sqft": sqft}
            else:
                n = IntPrompt.ask(f"  {label} (0 = skip)", default=0)
                rooms[key] = {"include": n > 0, "count": n, "sqft": sqft}

        r = estimate_room_by_room(rooms)

        t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        t.add_column("Item", style="bold")
        t.add_column("Low", justify="right")
        t.add_column("Mid", justify="right")
        t.add_column("High", justify="right")
        for item in r.get("line_items", []):
            t.add_row(item["item"], currency(item["low"]), currency(item["mid"]), currency(item["high"]))
        t.add_row("[bold]TOTAL[/bold]",
                  f"[bold green]{currency(r['total_low'])}[/bold green]",
                  f"[bold yellow]{currency(r['total_mid'])}[/bold yellow]",
                  f"[bold red]{currency(r['total_high'])}[/bold red]")
        console.print(t)

    elif sub == "3":
        console.print("\n[bold]Flip Profit Calculator[/bold]\n")
        purchase = FloatPrompt.ask("Purchase price")
        arv      = FloatPrompt.ask("ARV (after repair value)")
        repairs  = FloatPrompt.ask("Repair estimate (mid range)")
        fee      = FloatPrompt.ask("Wholesale fee if assigning (0 if flipping yourself)", default=0)
        months   = IntPrompt.ask("Holding months (flip timeline)", default=4)

        r = estimate_flip_profit(purchase, arv, repairs, fee, months)

        net_color = "green" if r["net_profit"] > 0 else "red"
        deal_str = "[bold green]✓ DEAL[/bold green]" if r["is_deal"] else "[bold red]✗ NOT A DEAL[/bold red]"

        console.print(Panel(
            f"  Purchase:         {currency(r['purchase'])}\n"
            f"  Repairs:          {currency(r['repairs'])}\n"
            f"  Holding Costs:    {currency(r['holding_costs'])}\n"
            f"  Closing Costs:    {currency(r['closing_costs'])}\n"
            f"  ARV:              {currency(r['arv'])}\n"
            f"  ─────────────────────────────────\n"
            f"  Gross Profit:     {currency(r.get('gross_profit', 0))}\n"
            f"  Wholesale Fee:    {currency(r['wholesale_fee'])}\n"
            f"  [bold]NET PROFIT:       [{net_color}]{currency(r['net_profit'])}[/{net_color}][/bold]\n"
            f"  ROI:              [{net_color}]{r['roi_pct']}%[/{net_color}]\n\n"
            f"  {deal_str}",
            title="[bold yellow]FLIP PROFIT ANALYSIS[/bold yellow]",
            border_style=net_color,
        ))

    elif sub == "4":
        tips = get_contractor_tips()
        console.print("\n[bold yellow]CONTRACTOR TIPS — HOW NOT TO GET BURNED[/bold yellow]\n")
        for tip in tips:
            console.print(f"  [green]•[/green] {tip}")

    elif sub == "5":
        scope = Prompt.ask("Scope", choices=list(SCOPE_LEVELS.keys()), default="medium")
        checklist = get_rehab_checklist(scope)
        console.print(f"\n[bold cyan]REHAB SEQUENCE — {scope.upper()}[/bold cyan]\n")
        console.print("[dim]Do work in this order. Doing it backwards costs 30%+ more.[/dim]\n")
        for item in checklist:
            console.print(f"  {item}")

    press_enter()


# ── 38. Title Company Finder ──────────────────────────────────────────────────

def menu_title_company():
    section("TITLE COMPANY FINDER + CLOSING COSTS")
    console.print(
        "[dim]Find investor-friendly title companies in your market. "
        "Calculate exact closing costs before you make an offer — "
        "not knowing this eats your profit.[/dim]\n"
    )

    console.print(
        "  [1] Find title companies for my state\n"
        "  [2] Calculate closing costs (assignment vs double close)\n"
        "  [3] What does title insurance do?\n"
        "  [4] HUD-1 / Closing Disclosure guide\n"
        "  [5] Investor title tips\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3","4","5"], default="1")
    if sub == "0":
        return

    if sub == "1":
        state = Prompt.ask("State abbreviation (e.g. MI, TX, FL)", default="MI").upper()
        companies = get_title_companies_for_state(state)

        console.print(f"\n[bold green]Title Companies for {state}:[/bold green]\n")
        for c in companies:
            name = c.get("name", c.get("Name",""))
            ctype = c.get("type", "")
            website = c.get("website", "")
            notes   = c.get("notes", "")
            states  = ", ".join(c.get("states_strong", [])[:5])
            color = "green" if "national" in ctype else "cyan"
            console.print(f"  [bold {color}]{name}[/bold {color}]  [dim]({ctype})[/dim]")
            console.print(f"    {website}")
            console.print(f"    [dim]{notes[:100]}[/dim]")
            console.print(f"    Strong in: {states}\n")

        state_data = CLOSING_COSTS_BY_STATE.get(state)
        if state_data:
            atty = "[yellow]YES — Attorney required by law[/yellow]" if state_data.get("attorney_required") else "[green]No — title company handles it[/green]"
            console.print(Panel(
                f"  Typical total closing cost: [bold yellow]{state_data.get('typical_total_pct', 0.02)*100:.1f}%[/bold yellow]\n"
                f"  Attorney required: {atty}\n"
                f"  [dim]{state_data.get('notes', '')}[/dim]",
                title=f"[bold]{state} CLOSING NOTES[/bold]",
                border_style="cyan",
            ))

        console.print("\n[bold yellow]HOW TO FIND ONE LOCALLY:[/bold yellow]")
        for tip in find_title_company_tips()[:5]:
            console.print(f"  • {tip}")

    elif sub == "2":
        console.print("\n[bold]Closing Cost Calculator[/bold]\n")
        price = FloatPrompt.ask("Purchase / assignment price")
        state = Prompt.ask("State", default="MI").upper()
        w_fee = FloatPrompt.ask("Wholesale fee (0 if keeping deal)", default=10000)
        tx_type = Prompt.ask("Transaction type", choices=["assignment", "double_close"], default="assignment")
        is_assign = tx_type == "assignment"

        r = calc_closing_costs(price, state, is_assignment=is_assign, wholesale_fee=w_fee)

        lines = [f"  Transaction Type: [bold]{r['transaction_type']}[/bold]\n"]
        for k, v in r.items():
            if k in ("transaction_type", "notes"):
                continue
            if isinstance(v, (int, float)) and v > 0:
                lines.append(f"  {k.replace('_',' ').title()}: {currency(v)}")

        lines.append(f"\n  [bold]TOTAL CLOSING COSTS: [yellow]{currency(r['total_closing_costs'])}[/yellow][/bold]")
        lines.append(f"  [dim]{r['notes']}[/dim]")

        console.print(Panel("\n".join(lines), title="[bold yellow]CLOSING COST BREAKDOWN[/bold yellow]", border_style="yellow"))

        if is_assign:
            console.print(
                f"\n[green]Assignment Net = Fee ${w_fee:,.0f} − Closing ${r['total_closing_costs']:,.0f} "
                f"= [bold]${w_fee - r['total_closing_costs']:,.0f} to you[/bold][/green]"
            )

    elif sub == "3":
        console.print("\n[bold cyan]WHAT TITLE INSURANCE DOES[/bold cyan]\n")
        for item in WHAT_TITLE_DOES:
            console.print(f"  [green]•[/green] {item}")

    elif sub == "4":
        guide = get_hud1_settlement_guide()
        console.print(f"\n[bold cyan]HUD-1 / CLOSING DISCLOSURE GUIDE[/bold cyan]\n")
        console.print(f"[bold]What is it?[/bold] {guide['what_is_it']}\n")
        for section_name, desc in guide["key_sections"].items():
            console.print(f"  [bold yellow]{section_name}[/bold yellow]")
            console.print(f"    {desc}")
        console.print(f"\n[bold green]Pro Tip:[/bold green] {guide['pro_tip']}")
        console.print(f"[bold cyan]Wholesaler Tip:[/bold cyan] {guide['wholesaler_tip']}")

    elif sub == "5":
        console.print("\n[bold yellow]INVESTOR TITLE TIPS[/bold yellow]\n")
        for tip in INVESTOR_TITLE_TIPS:
            console.print(f"  [green]•[/green] {tip}")

    press_enter()


# ── 39. Market Intelligence ───────────────────────────────────────────────────

def menu_market_intelligence():
    section("MARKET INTELLIGENCE — SCORE & COMPARE MARKETS")
    console.print(
        "[dim]Data on 17 wholesale markets: appreciation, vacancy, cash buyer %, "
        "rental yield, entry price, best strategy. Know where the money is.[/dim]\n"
    )

    console.print(
        "  [1] Score a specific market (full analysis)\n"
        "  [2] Compare multiple markets side by side\n"
        "  [3] Best markets by strategy (BRRRR, Flip, Section 8, etc.)\n"
        "  [4] National trends report (2025)\n"
        "  [5] Browse all 17 markets (quick stats)\n"
        "  [0] Back\n"
    )
    sub = Prompt.ask("Select", choices=["0","1","2","3","4","5"], default="1")
    if sub == "0":
        return

    if sub == "1":
        available = list_available_markets()
        console.print(f"[dim]Available: {', '.join(available[:10])}... ({len(available)} total)[/dim]\n")
        market = Prompt.ask("Market name (e.g. Detroit, Memphis, Atlanta)", default="Detroit")
        score  = wholesale_market_score(market)

        if not score.get("found"):
            console.print(f"[yellow]{score['verdict']}[/yellow]")
            press_enter()
            return

        s = score["overall_score"]
        s_color = "green" if s >= 7 else "yellow" if s >= 5 else "red"
        ll_str = "[green]YES — landlord-friendly[/green]" if score["landlord_friendly"] else "[red]NO — tenant-friendly (harder evictions)[/red]"

        console.print(Panel(
            f"  [bold]Overall Score:[/bold]  [{s_color}]{s}/10[/{s_color}]\n"
            f"  Best Strategy:    [bold cyan]{score['best_strategy']}[/bold cyan]\n"
            f"  Entry Barrier:    [bold]{score['entry_barrier']}[/bold]  ({score.get('entry_price_range','')})\n"
            f"  Exit Speed:       {score['exit_speed']}\n\n"
            f"  Rental Yield:     [green]{score['rental_yield_pct']}%/yr[/green]\n"
            f"  Appreciation:     [green]{score['appreciation_1yr_pct']}%/yr[/green]\n"
            f"  Vacancy Rate:     {'[red]' if score['vacancy_rate_pct'] > 10 else '[green]'}{score['vacancy_rate_pct']}%[/{'red' if score['vacancy_rate_pct'] > 10 else 'green'}]\n"
            f"  Cash Buyers:      {score['cash_buyer_pct']}% of sales\n"
            f"  Landlord Laws:    {ll_str}\n\n"
            f"  Hot Zip Codes:    [dim]{', '.join(score['hot_zip_codes'])}[/dim]\n"
            f"  Typical Fee:      [yellow]{score.get('typical_wholesale_fee','?')}[/yellow]\n\n"
            f"  [italic]{score['notes']}[/italic]\n\n"
            f"  [bold]VERDICT:[/bold] {score['verdict']}",
            title=f"[bold green]MARKET SCORE — {market.upper()}[/bold green]",
            border_style=s_color,
        ))

        if score.get("warnings"):
            console.print("\n[bold red]Warnings:[/bold red]")
            for w in score["warnings"]:
                console.print(f"  [red]⚠[/red] {w}")

    elif sub == "2":
        markets_input = Prompt.ask(
            "Markets to compare (comma-separated)",
            default="Detroit, Birmingham, Memphis, Indianapolis, Kansas City",
        )
        markets = [m.strip() for m in markets_input.split(",") if m.strip()]

        results = get_market_comparison(markets)

        t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED,
                  title="[bold green]MARKET COMPARISON[/bold green]")
        t.add_column("Rank", justify="center", width=5)
        t.add_column("Market", style="bold")
        t.add_column("Score", justify="center")
        t.add_column("Strategy")
        t.add_column("Yield", justify="right")
        t.add_column("Entry")
        t.add_column("Vacancy", justify="right")
        t.add_column("Risk")

        for i, r in enumerate(results, 1):
            s = r["overall_score"]
            s_color = "green" if s >= 7 else "yellow" if s >= 5 else "red"
            rank_str = f"#{i}" + (" ⭐" if i == 1 else "")
            t.add_row(
                rank_str,
                r["market"],
                f"[{s_color}]{s}[/{s_color}]",
                r.get("best_strategy", "?"),
                f"{r.get('rental_yield_pct', 0)}%",
                r.get("entry_barrier", "?"),
                f"{r.get('vacancy_rate_pct', 0)}%",
                r.get("risk_level", "?") if r.get("found") else "N/A",
            )
        console.print(t)

    elif sub == "3":
        strategy = Prompt.ask(
            "Strategy",
            choices=["Wholesale", "BRRRR", "Flip", "Section 8", "Luxury"],
            default="BRRRR",
        )
        results = get_best_markets_for_strategy(strategy)

        console.print(f"\n[bold green]TOP MARKETS FOR {strategy.upper()}:[/bold green]\n")
        for i, r in enumerate(results, 1):
            s = r["overall_score"]
            s_color = "green" if s >= 7 else "yellow" if s >= 5 else "red"
            console.print(
                f"  [bold]#{i}: {r['market']}[/bold] [{s_color}]{s}/10[/{s_color}] — "
                f"{r.get('best_strategy','')} | Entry: {r.get('entry_barrier','')} | "
                f"Yield: {r.get('rental_yield_pct',0)}%"
            )
            console.print(f"     [dim]{r.get('notes','')}[/dim]\n")

    elif sub == "4":
        report = get_market_trends_report()
        trends = report["trends"]

        console.print(Panel(
            f"  [bold]Interest Rates:[/bold] {trends['interest_rates']}\n"
            f"  [bold]Investor Activity:[/bold] {trends['investor_activity']}\n"
            f"  [bold]Rental Demand:[/bold] {trends['rental_demand']}\n\n"
            f"  [bold yellow]🔥 HOT STRATEGIES 2025:[/bold yellow]\n"
            + "\n".join(f"  • {s}" for s in trends["hot_strategies"]) + "\n\n"
            f"  [bold red]Headwinds:[/bold red]\n"
            + "\n".join(f"  • {h}" for h in trends.get("headwinds", [])) + "\n\n"
            f"  [bold green]Top 5 Recommended Markets:[/bold green] "
            + ", ".join(m["market"] for m in report["top_markets"]),
            title="[bold green]NATIONAL MARKET TRENDS — 2025[/bold green]",
            border_style="green",
        ))

    elif sub == "5":
        available = list_available_markets()
        console.print(f"\n[bold cyan]ALL {len(available)} MARKETS — QUICK STATS[/bold cyan]\n")

        t = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
        t.add_column("Market", style="bold")
        t.add_column("ARV 3BR", justify="right")
        t.add_column("Rent", justify="right")
        t.add_column("Yield", justify="right")
        t.add_column("Apprec", justify="right")
        t.add_column("Strategy")
        t.add_column("Risk")

        for mkt in available:
            data = MARKET_DATA[mkt]
            yield_pct = round(data["avg_rent_3br"] * 12 / data["avg_arv_3br"] * 100, 1)
            risk_color = "green" if data["risk_level"] == "low" else "yellow" if data["risk_level"] == "medium" else "red"
            t.add_row(
                mkt,
                f"${data['avg_arv_3br']:,}",
                f"${data['avg_rent_3br']:,}/mo",
                f"{yield_pct}%",
                f"{data['appreciation_1yr']}%",
                data["best_strategy"],
                f"[{risk_color}]{data['risk_level']}[/{risk_color}]",
            )
        console.print(t)

    press_enter()


# ── 40. Appreciation Projector ────────────────────────────────────────────────

def menu_appreciation_projector():
    section("APPRECIATION PROJECTOR — FUTURE VALUE BY MARKET")
    console.print(
        "[dim]See what a property is worth in 1, 3, 5, and 10 years "
        "based on each market's actual appreciation rate. "
        "Compounding appreciation is how buy-and-hold builds wealth.[/dim]\n"
    )

    available = list_available_markets()
    console.print(f"[dim]Available markets: {', '.join(available[:8])}... (type any market name)[/dim]\n")

    market   = Prompt.ask("Market", default="Detroit")
    price    = FloatPrompt.ask("Current purchase price or ARV")
    max_yrs  = IntPrompt.ask("Projection years", default=10)

    result = calc_market_appreciation(price, max_yrs, market)
    rate   = result["annual_appreciation_pct"]

    t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED,
              title=f"[bold green]APPRECIATION PROJECTION — {market.upper()} ({rate}%/yr)[/bold green]")
    t.add_column("Year", justify="center")
    t.add_column("Projected Value", justify="right")
    t.add_column("Total Gain", justify="right")
    t.add_column("Total Return", justify="right")

    for yr, val in result["projected_values"].items():
        gain = val - price
        ret  = (val - price) / price * 100
        yr_color = "green" if yr >= 5 else "cyan" if yr >= 3 else "white"
        t.add_row(
            f"[{yr_color}]Year {yr}[/{yr_color}]",
            f"[{yr_color}]{currency(val)}[/{yr_color}]",
            f"[green]{currency(gain)}[/green]",
            f"[green]{ret:.1f}%[/green]",
        )
    console.print(t)

    final = result["final_value"]
    total_gain = result["total_appreciation"]
    console.print(Panel(
        f"  Buy at:        {currency(price)}\n"
        f"  In {max_yrs} years:   [bold green]{currency(final)}[/bold green]\n"
        f"  Total gain:    [bold green]{currency(total_gain)}[/bold green]\n"
        f"  Total return:  [bold green]{result['total_return_pct']}%[/bold green]\n\n"
        f"  [dim]This is appreciation only — does not include rental income or equity from payments.[/dim]\n"
        f"  [dim]Add rental cash flow and equity paydown for total wealth creation.[/dim]",
        title="[bold green]WEALTH PROJECTION[/bold green]",
        border_style="green",
    ))

    if Confirm.ask("\nCompare to another market?", default=False):
        mkt2  = Prompt.ask("Second market", default="Indianapolis")
        price2 = price
        r2 = calc_market_appreciation(price2, max_yrs, mkt2)
        rate2 = r2["annual_appreciation_pct"]
        final2 = r2["final_value"]
        winner = market if final > final2 else mkt2
        console.print(Panel(
            f"  {market} ({rate}%/yr):     {currency(final)} in {max_yrs} yrs\n"
            f"  {mkt2} ({rate2}%/yr):  {currency(final2)} in {max_yrs} yrs\n\n"
            f"  [bold green]Winner: {winner}[/bold green]  "
            f"(+{currency(max(final, final2) - min(final, final2))} more)",
            title="[bold cyan]MARKET COMPARISON[/bold cyan]",
            border_style="cyan",
        ))

    press_enter()


# ── 41. Property Management Finder ───────────────────────────────────────────

def menu_property_mgmt():
    section("PROPERTY MANAGEMENT FINDER")
    console.print("[dim]Find local + national PMs for your target market, vet questions, fee breakdown.[/dim]\n")

    markets = list_covered_markets()
    console.print(f"[bold]Markets covered:[/bold] {', '.join(markets)}\n")

    sub = Prompt.ask(
        "What do you want to do?",
        choices=["find", "fees", "vet", "section8", "national", "cost"],
        default="find",
    )

    if sub == "find":
        mkt = Prompt.ask("Which market?", default="Detroit")
        result = get_pm_for_market(mkt)
        if not result["found"]:
            console.print(f"[yellow]No local data for {mkt}. Try: {', '.join(markets[:5])}[/yellow]")
            press_enter()
            return

        section(f"PM OPTIONS — {result['market'].upper()}")

        if result["local"]:
            console.print("[bold green]LOCAL Property Managers:[/bold green]\n")
            for pm in result["local"]:
                console.print(Panel(
                    f"  [bold]{pm['name']}[/bold]\n"
                    f"  Fee:       {pm['fee']}\n"
                    f"  Specialty: {pm['specialty']}\n"
                    f"  Note:      [dim]{pm['note']}[/dim]\n"
                    f"  Website:   [cyan]{pm['url']}[/cyan]",
                    border_style="green",
                ))

        if result["national"]:
            console.print("\n[bold cyan]NATIONAL chains with local presence:[/bold cyan]\n")
            for pm in result["national"]:
                mkt_str = ", ".join(pm["markets"]) if isinstance(pm["markets"], list) else pm["markets"]
                console.print(Panel(
                    f"  [bold]{pm['name']}[/bold]\n"
                    f"  Fee:       {pm['fee_range']}\n"
                    f"  Specialty: {pm['specialty']}\n"
                    f"  Pro:       {pm['pro']}\n"
                    f"  Note:      [dim]{pm['note']}[/dim]\n"
                    f"  Website:   [cyan]{pm['url']}[/cyan]",
                    border_style="cyan",
                ))

    elif sub == "cost":
        rent = FloatPrompt.ask("Monthly rent estimate", default=1100.0)
        pct_in = FloatPrompt.ask("PM fee % (e.g. 8)", default=8.0)
        c = estimate_pm_cost(rent, pct_in / 100)
        console.print(Panel(
            f"  Monthly rent:          {currency(c['monthly_rent'])}\n"
            f"  Monthly PM fee ({pct_in}%): {currency(c['monthly_mgmt'])}\n"
            f"  Annual PM fees:        {currency(c['annual_mgmt'])}\n"
            f"  Leasing fee (est):     {currency(c['leasing_fee'])}\n"
            f"  Lease renewal fee:     {currency(c['renewal_fee'])}\n"
            f"  [bold]Total annual PM cost:  {currency(c['annual_total_pm'])}[/bold]\n\n"
            f"  Net annual after PM:   [bold green]{currency(c['net_annual'])}[/bold green]\n"
            f"  Net monthly after PM:  [bold green]{currency(c['net_monthly'])}[/bold green]",
            title="PM COST BREAKDOWN",
            border_style="cyan",
        ))

    elif sub == "fees":
        section("FEE STRUCTURE GUIDE")
        for fee_type, data in FEE_BREAKDOWN.items():
            console.print(Panel(
                f"  Typical: {data['typical']}\n"
                + (f"  [dim]{data.get('note','')}[/dim]" if data.get("note") else ""),
                title=f"[bold]{fee_type.replace('_',' ').title()}[/bold]",
                border_style="dim",
            ))

    elif sub == "vet":
        section("VET YOUR PROPERTY MANAGER — 11 Questions")
        console.print("[dim]Ask every one of these before signing a management agreement.[/dim]\n")
        for i, q in enumerate(PM_VET_QUESTIONS, 1):
            console.print(f"  [bold cyan][{i:2}][/bold cyan]  {q}")

    elif sub == "section8":
        section("SECTION 8 / VOUCHER PM TIPS")
        for tip in SECTION8_PM_TIPS:
            console.print(f"  [green]•[/green] {tip}")

    elif sub == "national":
        section("NATIONAL PM CHAINS — All Markets")
        for pm in NATIONAL_PM_COMPANIES:
            mkt_str = ", ".join(pm["markets"]) if isinstance(pm["markets"], list) else pm["markets"]
            console.print(Panel(
                f"  [bold]{pm['name']}[/bold]\n"
                f"  Fee:      {pm['fee_range']}\n"
                f"  Markets:  {mkt_str}\n"
                f"  Min rent: ${pm['min_rent']}/mo\n"
                f"  Specialty:{pm['specialty']}\n"
                f"  Pro:      {pm['pro']}\n"
                f"  Note:     [dim]{pm['note']}[/dim]\n"
                f"  Website:  [cyan]{pm['url']}[/cyan]",
                border_style="cyan",
            ))

    press_enter()


# ── 42. BRRRR HML Auto-Trigger ────────────────────────────────────────────────

def menu_brrrr_hml():
    section("BRRRR — HARD MONEY LENDER AUTO-TRIGGER")
    console.print(
        "[dim]Enter your deal numbers. If it clears all thresholds, the system auto-matches\n"
        "the top 3 hard money lenders and generates a pre-qual checklist.[/dim]\n"
    )

    sub = Prompt.ask(
        "What do you want to do?",
        choices=["evaluate", "scenarios", "thresholds"],
        default="evaluate",
    )

    if sub == "thresholds":
        t = BRRRR_HML_TRIGGER
        console.print(Panel(
            f"  Max purchase to ARV:    {t['max_purchase_to_arv']*100:.0f}%  (buy at ≤70 cents on the dollar)\n"
            f"  Max rehab to ARV:       {t['max_rehab_to_arv']*100:.0f}%  (rehab ≤40% ARV)\n"
            f"  Min equity after rehab: ${t['min_equity_after']:,.0f}\n"
            f"  Min DSCR after refi:    {t['min_dscr_after_refi']:.2f}\n"
            f"  Min ARV:                ${t['min_arv']:,.0f}  (HML floor)\n\n"
            f"  Refi assumption:        75% ARV cash-out @ 7.5% / 30yr\n"
            f"  Expense ratio:          45%  (taxes, ins, mgmt, repairs)\n"
            f"  Vacancy assumption:     8%",
            title="TRIGGER THRESHOLDS",
            border_style="cyan",
        ))
        press_enter()
        return

    if sub == "scenarios":
        arv   = FloatPrompt.ask("ARV (After Repair Value)", default=90000.0)
        rent  = FloatPrompt.ask("Expected monthly rent", default=1050.0)
        scens = brrrr_scenarios(arv, rent)
        t = Table(title=f"BRRRR Scenarios — ARV ${arv:,.0f} | Rent ${rent:,.0f}/mo", box=box.SIMPLE)
        t.add_column("Scenario",  style="bold")
        t.add_column("Purchase",  justify="right")
        t.add_column("Rehab",     justify="right")
        t.add_column("Total In",  justify="right")
        t.add_column("DSCR",      justify="right")
        t.add_column("Equity",    justify="right")
        t.add_column("Cash Flow", justify="right")
        t.add_column("HML Fires?", justify="center")
        for s in scens:
            ok = "[bold green]YES[/bold green]" if s["triggered"] else "[red]NO[/red]"
            t.add_row(
                s["label"],
                currency(s["purchase"]),
                currency(s["rehab"]),
                currency(s["total_in"]),
                f"{s['dscr']:.2f}",
                currency(s["equity"]),
                f"{currency(s['cash_flow'])}/mo",
                ok,
            )
        console.print(t)
        press_enter()
        return

    # Evaluate a specific deal
    purchase = FloatPrompt.ask("Purchase price", default=55000.0)
    rehab    = FloatPrompt.ask("Estimated rehab cost", default=18000.0)
    arv      = FloatPrompt.ask("ARV (After Repair Value)", default=90000.0)
    rent     = FloatPrompt.ask("Expected monthly rent", default=1050.0)
    credit   = IntPrompt.ask("Your credit score (approx)", default=680)
    state    = Prompt.ask("State (2-letter, optional)", default="")

    result = evaluate_brrrr_trigger(purchase, rehab, arv, rent, credit, state)
    m = result["metrics"]

    status_color = "green" if result["triggered"] else "red"
    status_text  = "TRIGGERED — HML Match Found" if result["triggered"] else "NOT Triggered"

    console.print(Panel(
        f"  Purchase:           {currency(m['purchase_price'])}\n"
        f"  Rehab:              {currency(m['estimated_rehab'])}\n"
        f"  Total in:           {currency(m['total_in'])}\n"
        f"  ARV:                {currency(m['arv'])}\n"
        f"  Purchase / ARV:     {m['purchase_to_arv']}%\n"
        f"  Rehab / ARV:        {m['rehab_to_arv']}%\n"
        f"  Equity after:       {currency(m['equity_after'])}\n"
        f"  Refi loan (75%):    {currency(m['refi_loan'])}\n"
        f"  Refi payment/mo:    {currency(m['refi_payment_mo'])}\n"
        f"  Effective rent:     {currency(m['effective_rent'])}\n"
        f"  NOI/mo:             {currency(m['noi_monthly'])}\n"
        f"  DSCR after refi:    [bold]{m['dscr_after_refi']:.2f}[/bold]\n"
        f"  Monthly cash flow:  [bold]{currency(m['monthly_cash_flow'])}[/bold]\n"
        f"  Cash at close:      {currency(m['cash_at_close'])}",
        title=f"[bold {status_color}]{status_text}[/bold {status_color}]",
        border_style=status_color,
    ))

    if not result["triggered"]:
        console.print("\n[red bold]Trigger fails:[/red bold]")
        for f in result["fails"]:
            console.print(f"  [red]✗[/red] {f}")
        console.print("\n[dim]Run [scenarios] option to find a purchase/rehab combo that works.[/dim]")
        press_enter()
        return

    # Show matched lenders
    if result["matched_lenders"]:
        section("TOP MATCHED HARD MONEY LENDERS")
        for i, lender in enumerate(result["matched_lenders"], 1):
            console.print(Panel(
                f"  [bold]{lender['name']}[/bold]\n"
                f"  Rates:       {lender.get('rates','N/A')}\n"
                f"  LTV:         {lender.get('ltv','N/A')}\n"
                f"  Loan range:  {lender.get('loan_range','N/A')}\n"
                f"  Close time:  {lender.get('close_time','N/A')}\n"
                f"  Min credit:  {lender.get('min_credit','N/A')}\n"
                f"  Pro:         {lender.get('pro','')}\n"
                f"  Note:        [dim]{lender.get('note','')}[/dim]\n"
                f"  Website:     [cyan]{lender.get('url','N/A')}[/cyan]",
                title=f"#{i} Match",
                border_style="green",
            ))

    # Pre-qual checklist
    if result["pre_qual_checklist"]:
        section("PRE-QUAL CHECKLIST — Gather Before Calling")
        for i, item in enumerate(result["pre_qual_checklist"], 1):
            console.print(f"  [cyan][ ][/cyan] {item}")

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


# ── 43. Dispo Blast ────────────────────────────────────────────────────────────

def menu_dispo_blast():
    section("DISPO BLAST — SELL A LOCKED DEAL TO YOUR BUYER BENCH")
    console.print(
        "[dim]The moment you have a deal under contract (assignable), blast every "
        "cash buyer on your bench. First verified proof-of-funds takes it. "
        "Preview first — nothing sends until you confirm.[/dim]\n"
    )

    deals = dispo_load_deals()
    deal = None

    if deals:
        console.print("[bold]Saved deals:[/bold]")
        for i, d in enumerate(deals, 1):
            console.print(f"  [cyan]{i}.[/cyan] {d.get('address','?')}  "
                          f"[dim]${d.get('all_in',0):,} all-in · ARV ${d.get('arv',0):,}[/dim]")
        console.print(f"  [cyan]{len(deals)+1}.[/cyan] Enter a new deal")
        pick = IntPrompt.ask("Pick a deal", default=1)
        if 1 <= pick <= len(deals):
            deal = deals[pick - 1]

    if deal is None:
        console.print("\n[bold]New deal — enter the locked numbers:[/bold]")
        deal = {
            "address":    Prompt.ask("Address (Street, City ST ZIP)"),
            "all_in":     IntPrompt.ask("All-in price to buyer (contract + your fee)"),
            "beds":       IntPrompt.ask("Beds", default=3),
            "baths":      IntPrompt.ask("Baths", default=2),
            "sqft":       IntPrompt.ask("Sqft", default=1200),
            "year":       Prompt.ask("Year built", default=""),
            "arv":        IntPrompt.ask("ARV (conservative)"),
            "comps":      Prompt.ask("Comps (one line, optional)", default=""),
            "rehab_low":  IntPrompt.ask("Rehab estimate low", default=0),
            "rehab_high": IntPrompt.ask("Rehab estimate high", default=0),
            "emd":        IntPrompt.ask("EMD on assignment", default=5000),
            "close_days": IntPrompt.ask("Close in N days", default=14),
            "state":      Prompt.ask("State (2-letter, for buyer match)", default="MI").upper(),
            "highlights": Prompt.ask("Highlights (roof, vacant, etc.)", default=""),
        }
        dispo_save_deal(deal)
        console.print("[green]✓ Deal saved — it'll be in the list next time.[/green]")

    # Preview (sends nothing)
    res = dispo_fire(deal, send=False)
    pf  = res["preflight"]

    console.print(Panel(
        f"  Provider:       {pf['provider']}" + ("" if pf["configured"] else "  [red]✗ not configured[/red]") + "\n"
        f"  Verified sender:{' ' + pf['sender'] if pf['sender'] else ' [red]✗ EMAIL_FROM not set[/red]'}\n"
        f"  Buyers matched: [bold]{pf['buyers_total']}[/bold]  "
        f"([green]{pf['emailable']} emailable[/green], {pf['phone_only']} phone-only)\n"
        f"  Status:         {'[bold green]✓ READY TO FIRE[/bold green]' if pf['ok'] else '[bold red]✗ FIX ABOVE FIRST[/bold red]'}",
        title="[bold cyan]PREFLIGHT[/bold cyan]",
        border_style="green" if pf["ok"] else "red",
    ))

    console.print(Panel(
        f"[bold]SUBJECT:[/bold] {res['subject']}\n\n{res['body']}",
        title="[bold green]EMAIL THAT GOES OUT[/bold green]",
        border_style="green",
    ))

    if res["would_email"]:
        console.print("[bold]Would email:[/bold]")
        for b in res["would_email"]:
            console.print(f"  • {b.get('name','?')} <{b.get('email')}>")
    if res["phone_only"]:
        console.print("\n[bold yellow]Phone-only (copy-paste SMS below):[/bold yellow]")
        for b in res["phone_only"]:
            console.print(f"  • {b.get('name','?')} — {b.get('phone','?')}")
        console.print(f"\n  [dim]{res['sms']}[/dim]")

    if not pf["ok"]:
        console.print("\n[yellow]Not ready to send. Fix the preflight items, then re-run.[/yellow]")
        press_enter()
        return

    console.print()
    if Confirm.ask(f"[bold red]FIRE for real to {pf['emailable']} buyer(s)?[/bold red]", default=False):
        out = dispo_fire(deal, send=True)
        console.print(Panel(
            f"  [bold green]✓ {out['emailed']} emailed[/bold green]"
            + (f"   [red]{out['failed']} failed[/red]" if out["failed"] else "")
            + f"   {len(out['phone_only'])} phone-only\n"
            + ("  [yellow]⚠ Some sends failed — check SendGrid key/credits/sender.[/yellow]\n" if out["failed"] else "")
            + "  First verified proof-of-funds locks it. Reply scripts: option 26 → 4.",
            title="[bold green]🚀 DISPO BLAST SENT[/bold green]",
            border_style="green",
        ))
    else:
        console.print("[dim]Held — nothing sent.[/dim]")
    press_enter()


# ── 44. Cash-Flow Deal Hunter ──────────────────────────────────────────────────

def menu_deal_hunter():
    section("CASH-FLOW DEAL HUNTER — FLIP *OR* LANDLORD MATH")
    console.print(
        "[dim]Pulls live RentCast listings across your markets and scores each on BOTH "
        "exits: fix-and-flip (70% rule) AND buy-and-hold (Section-8 cash flow). "
        "Detroit/Midwest are rental markets — this catches the cash-flow deals the "
        "flip-only scan throws away. Honest gates: real rehab, real taxes + insurance.[/dim]\n"
    )

    if not os.getenv("RENTCAST_API_KEY"):
        console.print(Panel(
            "[yellow]No RENTCAST_API_KEY in .env.[/yellow]\n"
            "This hunt needs the live RentCast feed. Add your key to "
            "[bold]wholesale-ai/.env[/bold] (option 21 → Setup), then re-run.\n"
            "[dim]Free tier: 50 calls/month at app.rentcast.io[/dim]",
            title="[bold red]LIVE FEED NOT CONFIGURED[/bold red]", border_style="red",
        ))
        press_enter()
        return

    from agents.deal_hunter import hunt as deal_hunt, MARKETS, MIN_FEE

    console.print(f"[bold green]Scanning {len(MARKETS)} markets live...[/bold green] "
                  "[dim](one API call per market; ~10-20s)[/dim]\n")
    with console.status("[bold green]Hunting deals across all markets...", spinner="dots"):
        result = deal_hunt()

    cands = result.get("candidates", [])
    console.print(Panel(
        f"  Listings pulled:  [bold cyan]{result['listings_pulled']}[/bold cyan]\n"
        f"  Pass the gate:    [bold green]{result['candidates_passing_gate']}[/bold green]  "
        f"([cyan]{result.get('flip_candidates', 0)} flip[/cyan] / "
        f"[magenta]{result.get('landlord_candidates', 0)} landlord[/magenta])\n"
        f"  Min fee gate:     ${result['min_fee_gate']:,}\n"
        f"  Saved to:         output/deal_candidates.json",
        title="[bold green]HUNT COMPLETE[/bold green]", border_style="green",
    ))
    if result.get("market_log"):
        console.print("[dim]" + "  |  ".join(result["market_log"][:8]) + "[/dim]\n")

    if not cands:
        console.print("[yellow]No deals cleared the gate this run. The MLS is thin — "
                      "that's normal. Re-run tomorrow for new listings, or widen the "
                      "markets in agents/deal_hunter.py.[/yellow]")
        press_enter()
        return

    t = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
    t.add_column("#", justify="right")
    t.add_column("Type")
    t.add_column("Fee", justify="right")
    t.add_column("Address", max_width=34)
    t.add_column("Ask", justify="right")
    t.add_column("Rent", justify="right")
    t.add_column("Cap", justify="right")
    t.add_column("Agent")
    for i, c in enumerate(cands[:15], 1):
        dt = c["deal_type"]
        color = "green" if dt == "both" else "magenta" if dt == "landlord" else "cyan"
        rent = f"${c['monthly_rent']:,}" if c.get("monthly_rent") else "—"
        cap  = f"{c['cap_rate_target']*100:.0f}%" if c.get("cap_rate_target") else "—"
        agent = "✉" if c.get("agent_email") else ("☎" if c.get("agent_phone") else "—")
        flag = " ⚠" if c.get("fee_flag") else ""
        t.add_row(str(i), f"[{color}]{dt}[/{color}]", f"${c['best_fee']:,}{flag}",
                  c.get("address", "?"), f"${c['price']:,}", rent, cap, agent)
    console.print(t)
    console.print("[dim]⚠ = fee looks too good; verify rent/ARV (option 35) before you bank it. "
                  "✉ = listing-agent email on file (legal outreach channel).[/dim]\n")

    # The one legal, hands-off action: cash LOI to a listing agent.
    emailable = [c for c in cands[:15] if c.get("agent_email")]
    if not emailable:
        console.print("[dim]No listing-agent emails on these candidates — nothing to auto-send. "
                      "Numbers + agent phones are in the saved JSON above.[/dim]")
        press_enter()
        return

    if not Confirm.ask("\nSend a cash LOI to a listing agent now (legal, one email)?", default=False):
        press_enter()
        return

    console.print("\n[bold]Candidates with an agent email:[/bold]")
    for i, c in enumerate(emailable, 1):
        console.print(f"  [cyan]{i}.[/cyan] {c['address']}  "
                      f"[dim]{c['deal_type']} · fee ${c['best_fee']:,} · agent {c.get('agent_name', '?')}[/dim]")
    pick = IntPrompt.ask("Pick one", default=1)
    if not (1 <= pick <= len(emailable)):
        press_enter()
        return
    c = emailable[pick - 1]

    profile = load_profile()
    # Our max purchase price that still nets at least the min fee on assignment.
    mao = max(c["price"], c["price"] + c["best_fee"] - MIN_FEE)
    res = send_agent_offer(c, mao=mao, profile=profile, auto_send=False)  # preview only

    console.print(Panel(
        f"[bold]TO:[/bold] {res['to_name'] or 'Listing Agent'} <{res['to_email']}>\n"
        f"[bold]Opening offer:[/bold] ${res['opening_offer']:,}   "
        f"[bold]Walk-away (MAO):[/bold] ${res['walk_away']:,}\n\n"
        f"[bold]SUBJECT:[/bold] {res['subject']}\n\n{res['body']}",
        title="[bold green]CASH LOI PREVIEW[/bold green]", border_style="green",
    ))

    if Confirm.ask(f"[bold red]Send this LOI to {res['to_email']}?[/bold red]", default=False):
        out = send_agent_offer(c, mao=mao, profile=profile, auto_send=True)
        if out["sent"]:
            console.print(Panel(
                f"[bold green]✓ LOI emailed to {out['to_email']}[/bold green]\n"
                f"Saved: {out['saved_to']}",
                title="[bold green]OFFER SENT[/bold green]", border_style="green"))
        else:
            console.print(Panel(
                f"[yellow]Not auto-sent: {out['reason']}[/yellow]\n"
                f"LOI saved to: {out['saved_to']}\n"
                f"[dim]Open that file and paste it into an email to {out['to_email']}.[/dim]",
                title="[bold yellow]SAVED — SEND MANUALLY[/bold yellow]", border_style="yellow"))
    else:
        console.print(f"[dim]Held — LOI saved to {res['saved_to']}, nothing sent.[/dim]")
    press_enter()


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
