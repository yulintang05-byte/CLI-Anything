# Reddit Post — r/rust

**Title:**
Built a Rust TUI for Claude AI — ratatui + tokio + crossterm, ~12MB binary

**Body:**

Hey r/rust — sharing a project I've been working on. Hermes is a terminal client for Claude AI, built entirely in Rust.

**The stack:**
- `ratatui` + `crossterm` for the TUI — handles 256-color terminals, tmux, and SSH cleanly
- `tokio` for the async runtime — streaming responses from the API land in the TUI without blocking
- `reqwest` with `native-tls` for API calls
- `clap` for the CLI surface
- `serde` + `serde_json` for config and license cache serialization
- `sha2` + `hex` for device fingerprinting (for the license system)
- `dirs` for platform-appropriate config paths (`~/.config/hermes/` on Linux, `~/Library/Application Support/hermes/` on macOS)

**One thing I found interesting:** streaming the Claude API response into ratatui required a bit of thought. The API sends SSE chunks; I have a dedicated tokio task reading from the stream and sending chunks over an `mpsc` channel to the render loop. The render loop ticks at 60fps and drains the channel each tick. Feels smooth.

**The license system** was the most novel part for me. The binary validates a license key against a Cloudflare Worker (so no API keys ship in the binary). Results are cached in `~/.config/hermes/license.json` with a 24h TTL. If validation fails (offline), it falls back to a 72h grace period. The device ID is SHA-256 of `/etc/machine-id` on Linux or `ioreg IOPlatformUUID` on macOS.

**Binary size:** ~12MB stripped. Startup time ~80ms cold on my ThinkPad X1.

The repo has 11 crates in a workspace. I'm considering open-sourcing the core crates and keeping the license/billing layer closed. Not sure yet.

Install if you want to try it:
```bash
curl -fsSL https://hermes.sh/install.sh | bash
```

Happy to talk about any of the Rust decisions — especially if you've done SSE streaming into a TUI before and have opinions.

---

**Best time to post:** Tuesday 8 AM PST
**Flair:** Projects
