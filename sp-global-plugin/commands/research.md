---
description: Build a company financial brief using the Kensho kfinance MCP (S&P Global data).
argument-hint: <ticker-or-company> [annual|quarterly]
---

# S&P Global (Kensho) — Company research brief

Target: **$1**
Period (optional): **$2** (default: annual)

Use the **kfinance** MCP server tools (Kensho LLM-ready API → S&P Global data) to
build a concise brief on the target. First discover the available kfinance tools,
then use the right ones — typical capabilities include identifier resolution,
company info, financial statements (income / balance sheet / cash flow), line
items, and pricing.

1. **Resolve** `$1` to an S&P Global company/identifier (use the kfinance
   resolution or search tool; if several match, show the alternatives you saw).
2. **Profile** — pull company info / business description.
3. **Financials** — pull the income statement for period `$2` (or annual) and
   summarize revenue, margins, and the trend; add balance-sheet leverage if a
   tool exposes it.
4. **Market** — pull the latest price / market cap if a pricing tool is available.

If a tool returns an authentication or permission error, surface it plainly and
point me to `/sp-global:setup` instead of inventing numbers.

Deliver a one-page brief: identity, what they do, the latest financial snapshot,
and any caveats from missing or restricted data.
