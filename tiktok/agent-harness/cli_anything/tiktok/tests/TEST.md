# TikTok CLI — Test Guide

## Unit Tests (no credentials required)

```bash
cd tiktok/agent-harness
pip install -e ".[dev]"
pytest cli_anything/tiktok/tests/test_core.py -v
```

## Live Integration Tests

Set environment variables then run:

```bash
export TIKTOK_ACCESS_TOKEN=your_token_here
pytest cli_anything/tiktok/tests/test_full_e2e.py -v
```

## Manual Smoke Test

```bash
cli-anything-tiktok --help
cli-anything-tiktok auth setup --client-key KEY --client-secret SECRET
cli-anything-tiktok auth login
cli-anything-tiktok auth status
cli-anything-tiktok user info
cli-anything-tiktok video list
cli-anything-tiktok --json video list
cli-anything-tiktok repl
```
