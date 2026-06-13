# Hermes Twitter/X Threads — Ready to Post

---

## Thread 1: Story (post Day 6, Monday 9 AM PST)

1/7 My ThinkPad is 6 years old. Claude's web app is slow on it. The official Claude CLI uses 200MB RAM. So I spent a weekend building a Rust terminal client for Claude.

It grew from there. Here's what I built 🧵

2/7 The core problem: every time I needed Claude for a coding question, I had to break flow, open a browser, wait for Electron to load, get my answer, come back.

I work in the terminal. I want Claude in the terminal. Fast.

3/7 I chose Rust + ratatui. The TUI starts in ~80ms cold. Binary is 12MB stripped. Works over SSH. Renders correctly in tmux and 256-color terminals.

For the streaming API responses: tokio mpsc channel between the HTTP task and the render loop at 60fps. Never blocks.

4/7 The license system was the interesting part. I needed to ship a binary that validates license keys — but I couldn't put the API key IN the binary (strings command, anyone).

Solution: Cloudflare Worker as a proxy. The binary hits my worker. The worker holds the secret.

5/7 Results are cached locally with a 24h TTL. If you're offline, it falls back to a 72h grace period.

Longest flight I could find: LAX→Singapore, 18h. Plus layover. 72h covers it.

6/7 Pricing: Free (50 msg/day), Pro $12/mo, Ultra $29/mo.

You bring your own Anthropic API key — I never touch your usage or your data. The subscription is for the tooling, not the tokens.

7/7 It's live: curl -fsSL https://hermes.sh/install.sh | bash

If you're a terminal developer who uses Claude, I'd genuinely love to know if this is useful to you.

https://whop.com/hermes

---

## Thread 2: Speed (post Day 7, Tuesday 10 AM PST)

1/7 Measured Hermes vs Claude Code CLI cold start times on a ThinkPad X1 (2018, 8GB RAM):

Hermes: 78ms
Claude Code: ~1400ms

18x faster. Here's why the gap is so wide 🧵

2/7 Claude Code runs on Node.js. Every startup it has to:
- Launch the V8 engine
- Parse and JIT-compile JS
- Load Electron or the Node runtime
- Initialize the module graph

That's 1+ seconds before your first keypress is even registered.

3/7 Hermes is a compiled Rust binary. On launch it:
- Reads ~/.config/hermes/settings.json
- Checks the license cache (no network call if < 24h old)
- Initializes the ratatui TUI

That's it. 78ms.

4/7 RAM comparison (steady state, no active query):
Hermes: ~12MB RSS
Claude Code: ~180MB RSS

If you're on a dev server with 8 shared users, that difference matters.

5/7 The streaming feels faster too, but that's the same underlying API — so it's not actually faster. What IS different: the render loop runs at 60fps with a non-blocking channel drain, so chunks appear the instant they arrive.

No render stutter. No dropped frames.

6/7 Binary size: 12MB stripped. Single static binary — no dependencies, no npm install, no Python runtime. One curl command and it works.

curl -fsSL https://hermes.sh/install.sh | bash

7/7 This isn't anti-Electron. Electron makes sense for some products. For a terminal tool you open 50 times a day, 78ms vs 1400ms is the difference between "part of my workflow" and "the thing I have to wait for."

https://whop.com/hermes | Free tier available

---

## Thread 3: Demo (post Day 8 with a GIF or screen recording)

1/6 Here's Hermes going from zero to answering a Rust question in under 10 seconds.

[GIF: terminal opens, hermes starts, user types question, response streams in]

Let me break down what's happening 🧵

2/6 Step 1: install

curl -fsSL https://hermes.sh/install.sh | bash

Downloads the right binary for your OS/arch, verifies SHA256, adds to PATH. Done.

3/6 Step 2: set your Anthropic API key

export ANTHROPIC_API_KEY=sk-ant-...

Or add it to ~/.config/hermes/settings.json. Your key, your bill, your data.

4/6 Step 3: run `hermes`

First launch walks you through a 5-step onboarding: license key (or trial), API key, model selection, theme. Takes 30 seconds.

After that: straight into the TUI.

5/6 Step 4: ask it something

Type your question, hit Enter. Response streams directly into the terminal buffer — no waiting for the full response, no copy-paste lag.

Use arrow keys to scroll. Ctrl+C to interrupt. Ctrl+L to clear.

6/6 That's it. No npm, no Python, no VS Code extension.

If you live in the terminal, this is Claude in the terminal.

https://whop.com/hermes — free 50 msg/day trial, Pro $12/mo
