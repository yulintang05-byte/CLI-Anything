# Wholesale AI — Real Estate Wholesale + Gov Property Finder

Free alternative to Tranchi.ai — find government-owned and distressed properties under market value, analyze deals, and close faster with AI.

## What It Does

| Feature | Description |
|---|---|
| **Deal Calculator** | MAO, ARV, ROI, cash flow analysis using the 70% rule |
| **Gov Property Finder** | HUD homes, Fannie Mae, Freddie Mac, GSA, USDA, US Marshals, IRS auctions |
| **AI Deal Analyzer** | Full deal grade, strategy, red flags, and next steps (Claude-powered) |
| **Negotiation Script** | Word-for-word script tailored to your seller's situation |
| **Offer Letter Generator** | Ready-to-send LOI with assignment clause |
| **HUD Fair Market Rents** | Official rent data by state/county for comps |
| **Strategy Guides** | Assignment, double close, subject-to, tax liens, HUD homes, probate |
| **Cash Buyer Strategy** | How to find and close cash buyers in any market |

## Quick Start

```bash
# 1. Install
cd wholesale-ai
bash setup.sh

# 2. Add your Claude AI key to .env (free at console.anthropic.com)
echo "ANTHROPIC_API_KEY=sk-ant-your-key" >> .env

# 3. Run
python main.py

# Quick MAO from command line
python main.py --mao --arv 150000 --repairs 25000 --fee 10000
```

## Free Government Property Sources Built In

- **HUD Home Store** — gov foreclosures, typically 10-30% below market
- **HomePath** (Fannie Mae) — REO properties
- **HomeSteps** (Freddie Mac) — REO properties
- **USDA Rural Properties** — rural government-owned homes
- **GSA Surplus** — federal property auctions at propertyforsale.gsa.gov
- **US Marshals** — seized asset sales
- **IRS Auctions** — seized property
- **FDIC** — failed bank real estate

## API Keys (Both Free)

| Key | Where To Get | Required? |
|---|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | For AI features |
| `HUD_API_TOKEN` | [huduser.gov/portal/dataset/api.html](https://www.huduser.gov/portal/dataset/api.html) | For HUD rent data |

## Cost vs Tranchi.ai

- Tranchi.ai: Monthly subscription ($$$)
- This tool: ~$0.01–$0.05 per AI analysis (typical month under $5)

## Deal Formula

```
MAO = (ARV × 0.70) - Repairs - Your Wholesale Fee
```

- **ARV** — what the property sells for fully fixed up (pull real comps)
- **70%** — standard discount (use 65% in slower markets)
- **Repairs** — always get contractor bids
- **Your Fee** — typically $5k–$15k per deal
