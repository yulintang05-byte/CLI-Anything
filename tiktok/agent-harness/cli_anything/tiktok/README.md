# cli-anything-tiktok

CLI harness for TikTok — video management via TikTok Open API v2 (OAuth2 + PKCE).

## Install

```bash
cd tiktok/agent-harness
pip install -e .
```

## Quick Start

```bash
# 1. Configure your TikTok app credentials (from developer.tiktok.com)
cli-anything-tiktok auth setup --client-key <KEY> --client-secret <SECRET>

# 2. Login via browser (opens TikTok authorization page)
cli-anything-tiktok auth login

# 3. Check status
cli-anything-tiktok auth status

# 4. Use the CLI
cli-anything-tiktok user info
cli-anything-tiktok video list
cli-anything-tiktok video info <VIDEO_ID>
cli-anything-tiktok upload video myvideo.mp4 --title "My Video"

# 5. Interactive REPL
cli-anything-tiktok repl
```

## TikTok Developer Portal Setup

1. Go to [developer.tiktok.com](https://developers.tiktok.com/)
2. Create an app → Products → Login Kit
3. Add redirect URI: `http://localhost:4199/callback`
4. Set Web/Desktop URL to your verified domain
5. Copy the **Client Key** and **Client Secret**

## Credentials Storage

Credentials are stored locally in `~/.cli-anything-tiktok/config.json` and are never committed to git.

## Scopes

Default scopes: `user.info.basic,video.list,video.upload,video.publish`

Customize with `--scopes` during setup.
