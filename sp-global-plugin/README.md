# sp-global plugin for Claude Code

A company plugin for **S&P Global**. It wires Claude Code to the
[**Kensho LLM-ready API**](https://kensho.com/solutions/llm-ready-api) — Kensho is
S&P Global's AI division — using Kensho's **official `kfinance` MCP server**. No
paid third-party/managed connector required: you authenticate with your own S&P
Global / Kensho entitlements.

## What's in the box

```
sp-global-plugin/
├── .claude-plugin/plugin.json   # plugin manifest
├── .mcp.json                    # registers Kensho's local kfinance MCP server
├── requirements.txt             # kensho-kfinance
└── commands/
    ├── setup.md                 # /sp-global:setup    — install, connect, auth
    └── research.md              # /sp-global:research  — company brief
```

The MCP server itself is **Kensho's**, shipped in the `kensho-kfinance` package —
this plugin just declares and documents it. Launch command:
`python -m kfinance.mcp --stdio`.

## Prerequisites

- Python 3.10+
- `kensho-kfinance` (installed below)
- Access to the Kensho LLM-ready API. Request access from Kensho
  (`llmreadyapi@kensho.com`); for production, generate a public/private key pair
  and send Kensho the public key to receive a `client_id`.

## Quick start

1. **Install the server's dependency:**
   ```bash
   pip install -r sp-global-plugin/requirements.txt   # installs kensho-kfinance
   ```

2. **Install the plugin** from this marketplace and reload:
   ```
   /plugin install sp-global@cli-anything
   ```

3. **Verify it:** run `/sp-global:setup`. On first use the local server has no
   credentials, so it opens an **Okta browser login** to authenticate you.

4. **Use it:** `/sp-global:research AAPL` builds a one-page company brief from
   S&P Global data.

## Authentication

The bundled `.mcp.json` runs the server with **no auth flags**, which triggers the
interactive **browser (Okta)** login — the simplest start and keeps secrets out of
the repo. The server resolves credentials in this precedence order:

1. `--refresh-token <token>`
2. `--client-id <id> --private-key <key>` (server-to-server; recommended for
   production)
3. Browser/Okta fallback (default here)

To use a refresh token or key pair, edit `args` in `.mcp.json` — e.g. inject a
token from your environment so nothing secret is committed:

```jsonc
{
  "mcpServers": {
    "kfinance": {
      "command": "python3",
      "args": ["-m", "kfinance.mcp", "--stdio", "--refresh-token", "${KFINANCE_REFRESH_TOKEN}"]
    }
  }
}
```

(Key-pair variant: `"--client-id", "${KFINANCE_CLIENT_ID}", "--private-key", "${KFINANCE_PRIVATE_KEY}"`.)

## Alternative: Kensho's hosted (remote) MCP

If you'd rather not run a local server, Kensho hosts the same MCP at
`https://kfinance.kensho.com/integrations/mcp` (OAuth via Okta). Swap `.mcp.json`
for:

```json
{
  "mcpServers": {
    "kfinance": {
      "type": "http",
      "url": "https://kfinance.kensho.com/integrations/mcp"
    }
  }
}
```

There is also a prebuilt **"S&P Global" connector** in Claude (Desktop/Team:
*Add connectors → search "S&P Global"*) backed by the same endpoint.

## Commands

| Command               | Description                                                      |
|-----------------------|------------------------------------------------------------------|
| `/sp-global:setup`    | Install, connect, and authenticate the `kfinance` MCP server     |
| `/sp-global:research` | Build a one-page company brief from S&P Global (Kensho) data     |

## Documentation

- Kensho LLM-ready API overview: <https://docs.kensho.com/llmreadyapi/overview>
- MCP servers (local & hosted): <https://docs.kensho.com/llmreadyapi/mcp>
- Authentication: <https://docs.kensho.com/llmreadyapi/kf-authentication>
- `kfinance` source & README: <https://github.com/kensho-technologies/kfinance>
- PyPI: <https://pypi.org/project/kensho-kfinance/>
