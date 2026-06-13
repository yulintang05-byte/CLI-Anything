# Reddit Post — r/SideProject

**Title:**
I built a terminal client for Claude AI in Rust, put it on Whop — week 1 numbers inside

**Body:**

Context: I'm a developer who uses Claude constantly for coding. The web app kept pulling me out of flow, and the official CLI was too heavy for my old ThinkPad. So I built a native Rust terminal client on a weekend. Then I kept going.

**What I shipped:**
- Native Rust TUI (ratatui-based), starts in <100ms, ~12MB binary
- Single `curl` install
- Bring-your-own-API-key model — your Anthropic bill, your data
- Free tier (50 msg/day), Pro ($12/mo), Ultra ($29/mo for Opus access)
- Offline 72h grace period (useful for travel)

**The technical challenge I didn't expect:** building the license system without shipping API keys in the binary. Ended up with a Cloudflare Worker proxy that validates against Whop. Results are cached locally with a 24h TTL and a 72h offline fallback.

**Distribution so far:**
- Posted in r/rust (technical angle) — got some good architecture feedback
- HN Show HN pending
- Landing page: hermes.sh

**What I'm unsure about:**
- $12/mo — is that right for a CLI tool? I genuinely don't know the market rate
- Whether to open-source the Rust core. There's no moat — it's a static binary — but I'm worried about people just compiling it without the license layer
- The free tier at 50 messages/day — too tight? Too generous?

Install: `curl -fsSL https://hermes.sh/install.sh | bash`

Would love brutal honest feedback, especially from people who've monetized CLI tools before.

---

**Best time to post:** Wednesday 9 AM PST
**Flair:** Launch
