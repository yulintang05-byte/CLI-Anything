# ProductHunt Launch Assets

## Tagline (≤60 chars — pick one)
- "Claude AI in your terminal. Built in Rust."  ← RECOMMENDED
- "The terminal Claude deserves."
- "Fast Claude TUI — 80ms startup, 12MB binary."

## Description (paste into PH description field)

Hermes is a native Rust terminal client for Claude AI.

**Why it exists:** The web app breaks flow. The official CLI is too heavy for older machines. Hermes starts in under 100ms, uses ~12MB RAM, and works over SSH without issues.

**How it works:** Bring your own Anthropic API key — your usage costs are transparent and you control your data. Hermes handles the TUI, streaming, and session management.

**Pricing:** Free (50 msg/day trial) · Pro $12/mo (unlimited) · Ultra $29/mo (Opus + team features)

```bash
curl -fsSL https://hermes.sh/install.sh | bash
```

---

## Maker's First Comment (post within 60 seconds of launch)

Hey PH 👋 I'm the builder.

I made this because I was frustrated: I use Claude constantly for coding help but the web app and the official CLI were too slow and heavy for my 6-year-old ThinkPad. I wanted Claude in my terminal the same way I have git and ripgrep — fast, composable, always there.

A few honest things I'm still figuring out:

1. **Pricing**: Is $12/mo right for a CLI tool? I genuinely don't know. I've had people tell me it should be free and people tell me it's too cheap. Happy to hear more opinions.

2. **Open source**: The core is a Rust binary. I'm considering open-sourcing the non-license crates. Not sure if it matters to the target user.

3. **Free tier**: 50 messages/day is the limit. That's a real limit — I want there to be a reason to upgrade. Is that the right number?

If you try it, the thing I most want to know is: does the streaming feel fast enough? The 60fps render loop was the hardest part to get right.

---

## Gallery Screenshots (you need to make these)

### Screenshot 1: Onboarding flow
- Show the 5-step onboarding TUI
- Terminal: dark background, cyan accents
- Caption: "30-second setup"

### Screenshot 2: Active query streaming
- Show a Rust code question being answered
- Response mid-stream (not complete) — shows it's real-time
- Caption: "Streams responses as they arrive"

### Screenshot 3: Model selection screen
- Show the model picker (Sonnet, Haiku, Opus)
- Caption: "Switch models without leaving the terminal"

### Screenshot 4: Install one-liner
- Plain terminal, just the curl command and the output
- Shows the ASCII banner on first run
- Caption: "One command. No npm. No Python."

### Screenshot 5: Settings / config
- ~/.config/hermes/settings.json open in the TUI
- Caption: "Your key, your config, your control"

---

## Launch Timing
- Post at exactly 12:01 AM PST on a Tuesday
- Have 15+ genuine friends/users ready to check it out (NOT to blindly upvote)
- Be online from 12:01 AM to 2 AM, then from 7 AM to 9 PM PST

## Target categories
- Developer Tools
- Productivity
- Artificial Intelligence
