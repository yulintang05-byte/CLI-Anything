---
description: Install, connect, and authenticate the Kensho kfinance MCP server (S&P Global LLM-ready API).
---

# S&P Global (Kensho) — Setup & verify

Help me get the **kfinance** MCP server (Kensho LLM-ready API → S&P Global data)
working in Claude Code.

1. **Dependency** — check that `kensho-kfinance` is installed for the Python that
   launches the server:
   - `python3 -c "import kfinance; print(getattr(kfinance, '__version__', 'ok'))"`
   - If it's missing: `pip install -r sp-global-plugin/requirements.txt`
2. **Connection** — confirm Claude Code loaded the `kfinance` MCP server declared
   in `sp-global-plugin/.mcp.json`. List its available tools; if none appear, tell
   me to reload the plugin / restart Claude Code.
3. **Authentication** — the local server (`python -m kfinance.mcp --stdio`) picks
   credentials in this order:
   - `--refresh-token`, else `--client-id` + `--private-key`, else an interactive
     **browser (Okta)** login on first use.
   Tell me which path is active. If I need credentials, note that LLM-ready API
   access is requested from Kensho (llmreadyapi@kensho.com), and that I can switch
   the `args` in `.mcp.json` to pass a refresh token or key pair.
4. **Smoke test** — once connected, call a simple kfinance tool (e.g. resolve a
   well-known ticker such as AAPL, or fetch its company info) and report whether
   it succeeded or returned an auth/permission error.

Keep it to a short checklist: installed? connected? authenticated? data flowing?
