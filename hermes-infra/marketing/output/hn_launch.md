# Show HN: Hermes — a Rust terminal for Claude AI (faster, lighter, $12/mo)

**Title (copy-paste this exactly):**
Show HN: Hermes – Claude AI in your terminal, built in Rust

---

## Body (post this as your text)

I got tired of the web interface breaking my flow every time I needed Claude for a coding question. I tried the official Claude Code CLI but found it too heavy for my ThinkPad — 1.4s startup, 200MB+ RAM. So I spent a weekend building a native Rust terminal client. It grew from there.

Hermes is a TUI for Claude built with ratatui and tokio. It starts in under 100ms, uses ~12MB of RAM, and works over SSH without any issues. The whole thing is a single static binary.

Technical stuff that might interest HN:
- Built on top of the Anthropic API — you bring your own key, so your usage costs are transparent and you control your data
- License validation runs through a Cloudflare Worker so the API key never ships in the binary
- 72-hour offline grace period: if you're on a plane or have spotty internet, it keeps working
- The TUI uses ratatui with crossterm — renders correctly in 256-color terminals, tmux, and over mosh

Pricing is tiered: free (50 msg/day trial), Pro ($12/mo), Ultra ($29/mo for Opus access). I know someone will ask — yes, you still pay for your own API usage separately. The subscription covers the tooling, not the tokens.

Install:
```
curl -fsSL https://hermes.sh/install.sh | bash
```

GitHub: [link]
Whop: https://whop.com/hermes

Happy to answer questions about the Rust architecture, the license system, or why I made the choices I did.

---

## Your first reply (post this within 60 seconds of the HN post going live)

Thanks for checking it out. A few things I'm still unsure about and would love feedback on:

1. The pricing — is $12/mo the right number for a CLI tool? I can't tell if developers expect these to be free or are fine paying for polish.
2. The offline grace period is 72 hours. Is that enough? I set it based on "longest flight + layover" logic.
3. I'm debating whether to open-source the core — the Rust crates compile to a static binary so there's no moat either way. Curious what people think.

---

## Best time to post
Tuesday or Wednesday, 9–10 AM PST.
Do NOT post Friday or Monday.

## Account requirements
- Must have HN account with some history (even a few comments)
- Do NOT use a throwaway — HN detects and penalizes new accounts
