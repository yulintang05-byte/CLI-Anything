# Wholesale AI — Real Estate Wholesale + Gov Property Finder

Free alternative to Tranchi.ai built on public government data + Claude AI.
Find distressed and gov-owned properties under market value, analyze deals,
and close faster — for pennies on the dollar vs. a monthly subscription.

## Features (Matches Tranchi.ai Core Capabilities)

### Deal Analysis
| Feature | Description |
|---|---|
| **MAO Calculator** | 70% rule: `(ARV × 0.70) - Repairs - Fee` — know your max offer instantly |
| **AI Deal Analyzer** | Full grade (A/B/C/F), strategy, red flags, next steps (Claude-powered) |
| **Cash Flow Analysis** | Monthly P&L, cap rate, cash-on-cash return |
| **DSCR Calculator** | Debt-Service Coverage Ratio — qualifies property for DSCR rental loans without using your income |
| **Repair Estimator** | Light/medium/heavy/gut cost ranges + room-by-room reference guide |

### Creative Financing (Zero Money Down Strategies)
| Feature | Description |
|---|---|
| **Subject-To** | Take over seller's existing mortgage — keep their low rate |
| **Seller Financing** | Seller acts as bank — no bank needed |
| **Seller Credits** | Reduce cash buyer needs at closing — makes deals easier to sell |
| **Lease-Option** | Control property with small option fee |
| **Strategy Recommender** | Enter seller's situation — AI picks the best deal structure |

### Neighborhood & Property Intelligence *(Like Tranchi.ai's Crime Analysis)*
| Feature | Description |
|---|---|
| **Crime Score** | FBI Crime Data Explorer API — violent + property crime rates, safety grade A-F |
| **Neighborhood Links** | SpotCrime, AreaVibes, NeighborhoodScout, CrimeMapping — all free |
| **School Ratings** | GreatSchools, Niche, SchoolDigger links pre-built for any address |
| **Flood Risk** | FEMA flood map links auto-generated per property |
| **Walk Score** | Walkability + transit score links |
| **Property Tax Estimate** | State effective tax rates — auto monthly/annual estimate |
| **Insurance Estimate** | Landlord vs. homeowner insurance by state + quote links |
| **Tax Records** | NETR Online county records links — ownership history, liens, deeds |

### Government Property Sources (All Free to Search)
| Source | Type |
|---|---|
| **HUD Home Store** | Gov foreclosures — typically 10-30% below market |
| **HomePath (Fannie Mae)** | REO properties |
| **HomeSteps (Freddie Mac)** | REO properties |
| **USDA Rural** | Gov-owned rural properties |
| **GSA Auctions** | Federal surplus at propertyforsale.gsa.gov |
| **US Marshals** | Seized asset sales |
| **IRS Auctions** | Seized property |
| **FDIC** | Failed bank real estate |
| **Tax Lien / Deed Sales** | State-specific portals (RealAuction, GovEase, Bid4Assets) |

### Seller Outreach & Negotiation
| Feature | Description |
|---|---|
| **Negotiation Script** | Word-for-word script tailored to seller's specific situation |
| **Offer Letter / LOI** | Ready-to-send Letter of Intent with assignment clause |
| **Motivated Seller Sources** | Probate, tax delinquent, NOD/pre-foreclosure, code violations, absentee owners |
| **Cash Buyer Strategy** | How to find and close cash buyers in your specific market |

### Deal Pipeline / CRM
| Feature | Description |
|---|---|
| **Pipeline Tracker** | Save and track deals: Lead → Analyzing → Offer Sent → Under Contract → Marketing → Closed |
| **Stage Advancement** | Move deals through the pipeline with notes and history |
| **Fee Dashboard** | See total active deals, potential fees, and closed income |

### AI Advisor (Claude-Powered)
| Feature | Description |
|---|---|
| **Strategy Guides** | Assignment, double close, subject-to, tax liens, HUD homes, probate — explained step by step |
| **Free Q&A** | Ask anything about wholesaling, contracts, finding deals |
| **HUD Fair Market Rents** | Official rent comps by state/county (free HUD API token) |

## Quick Start

```bash
cd wholesale-ai
bash setup.sh                   # one-time install
cp .env.example .env            # then open .env and add your keys
python main.py                  # interactive menu

# Quick MAO from command line
python main.py --mao --arv 200000 --repairs 30000 --fee 12000
# → MAO: $98,000
```

## Free API Keys Needed

| Key | Where | Cost |
|---|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Free $5 credit, then ~$0.01-0.05/analysis |
| `HUD_API_TOKEN` | [huduser.gov/portal/dataset/api.html](https://www.huduser.gov/portal/dataset/api.html) | Free forever |

## Cost vs Tranchi.ai

| | Tranchi.ai | Wholesale AI |
|---|---|---|
| Monthly cost | $$$/month subscription | Under $5/month (AI calls only) |
| Data sources | Proprietary | Same gov data — HUD, FBI, GSA, FDIC |
| Deal pipeline | Yes | Yes (local JSON, yours to keep) |
| AI analysis | Yes | Yes (Claude Opus) |
| Offer letters | Yes | Yes |
| Creative financing | Limited | Subject-To, Seller Finance, Lease-Option, Credits |
| Crime scores | Yes | Yes (FBI CDE API) |

## The Core Wholesale Formula

```
MAO = (ARV × 0.70) - Repairs - Wholesale Fee

Where:
  ARV     = After Repair Value (what similar fixed-up homes sell for)
  0.70    = 70% rule — leaves room for end buyer to profit
  Repairs = Always get 2-3 contractor bids
  Fee     = Your assignment fee ($5k-$15k typical)

Example:
  ARV $200k × 70% = $140k
  $140k - $30k repairs - $10k fee = MAO $100k
  You offer seller ≤ $100k, sell contract for $110k, pocket $10k
```
