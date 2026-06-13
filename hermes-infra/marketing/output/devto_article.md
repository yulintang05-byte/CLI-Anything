---
title: "I built a Rust terminal for Claude AI. Here's what I learned."
tags: [rust, cli, ai, productivity]
canonical_url: https://hermes.sh/blog/building-hermes
published: true
---

My ThinkPad X1 is six years old. It runs everything I throw at it — except Electron apps.

When I needed Claude for a coding question, I'd open a browser tab, wait for the web app to load, type my question, get my answer, and then fight to get back into flow. The official Claude Code CLI was better, but 1.4 seconds to first render and 200MB RAM is still a lot to ask of a machine with 8GB.

So I built Hermes: a native Rust TUI for Claude AI that starts in under 100ms and uses ~12MB of RAM.

This is what I learned.

---

## The stack

```toml
# Cargo.toml (abbreviated)
ratatui = "0.29"
crossterm = "0.28"
tokio = { version = "1", features = ["full"] }
reqwest = { version = "0.12", features = ["json", "native-tls", "stream"] }
clap = { version = "4", features = ["derive"] }
serde = { version = "1", features = ["derive"] }
```

I chose `ratatui` over alternatives because it's the most active TUI library in the Rust ecosystem right now, and it has first-class support for mouse events, Unicode, and 256-color terminals. `crossterm` handles the platform differences cleanly — the same code works on Linux, macOS, and Windows Terminal.

---

## The hardest part: streaming into a TUI

Claude's API returns responses as server-sent events (SSE). Each chunk arrives as:

```
data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"Hello"}}
```

The naive approach — blocking on the HTTP response in the render thread — makes the TUI freeze while waiting for chunks. Instead, I split it into two tasks:

```rust
// In the streaming task
let (tx, mut rx) = mpsc::channel::<String>(64);

tokio::spawn(async move {
    let mut stream = api_client.stream_message(request).await?;
    while let Some(chunk) = stream.next().await {
        if let Ok(text) = chunk {
            tx.send(text).await.ok();
        }
    }
    Ok::<_, anyhow::Error>(())
});

// In the render loop (60fps tick)
loop {
    // Drain the channel — take everything available, don't block
    while let Ok(chunk) = rx.try_recv() {
        state.current_response.push_str(&chunk);
    }
    terminal.draw(|f| render(f, &state))?;
    tokio::time::sleep(Duration::from_millis(16)).await;
}
```

The `try_recv()` is important — it's non-blocking, so the render loop never stalls waiting for API chunks. The TUI stays responsive even if the API is slow.

---

## The license system (and why it's a Cloudflare Worker)

I wanted to charge for Hermes. That means a license key system. The obvious approach is to validate keys against an API, but then I'd need to ship an API key for the validation endpoint in the binary — which anyone can extract with `strings`.

The solution: a Cloudflare Worker as a proxy. The binary sends the license key to `api.hermes.sh/v1/validate`. The Worker holds the actual Whop API key as a secret and calls the Whop API on behalf of the client.

```javascript
// worker/src/index.js (simplified)
export default {
  async fetch(request, env) {
    const { license_key } = await request.json();
    
    const whop = await fetch(
      `https://api.whop.com/api/v2/memberships/${license_key}/validate`,
      { headers: { Authorization: `Bearer ${env.WHOP_API_KEY}` } }
    );
    
    const data = await whop.json();
    return Response.json({ valid: data.status === "active", tier: data.plan_id });
  }
}
```

On the Rust side, results are cached locally:

```rust
// ~/.config/hermes/license.json
{
  "key": "HERMES-XXXX-XXXX-XXXX",
  "tier": "pro",
  "validated_at": "2026-04-28T09:00:00Z",
  "expires_at": "2026-05-28T09:00:00Z"
}
```

If the cache is less than 24 hours old, I skip the network call. If validation fails (no internet), I check if the cache is less than 72 hours old — if yes, allow access. This covers flights, hotels with bad WiFi, and spotty mobile connections.

The device ID that gets sent with each validation is SHA-256 of `/etc/machine-id` on Linux or `ioreg IOPlatformUUID` on macOS. It's not user-identifiable but it lets Whop detect if the same key is used on 50 different machines simultaneously.

---

## What I got wrong

**First mistake:** I tried to build the TUI and the license system at the same time. I spent two weeks on both and had a working demo of neither. Separated them into distinct crates and finished both in a week.

**Second mistake:** The initial free tier was 100 messages per day. I moved it to 50 after realizing that 100 is basically unlimited for most developers — there was no pressure to upgrade.

**Third mistake:** I built an elaborate plugin system before I had a single paying customer. It's still there, but no one uses it yet. Don't abstract until you have the problem.

---

## The result

Hermes starts in ~80ms on cold launch. The binary is 12MB stripped. It works over SSH, in tmux, and in terminals with 16 colors if you disable the theme.

```bash
curl -fsSL https://hermes.sh/install.sh | bash
```

Free tier is 50 messages/day. Pro is $12/mo (unlimited messages, priority routing). Ultra is $29/mo (Opus access, team features).

If you're a Rust developer curious about the architecture, the repo is at [GitHub link]. Happy to answer questions about ratatui, the SSE streaming pattern, or the license system in the comments.
