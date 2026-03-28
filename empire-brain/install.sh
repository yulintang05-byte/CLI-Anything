#!/bin/bash
# Empire Brain — One-command install
# Installs skills globally + deploys Cloudflare Worker
# Run from: ~/passive-income/empire-brain/ OR after cloning CLI-Anything

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$HOME/.claude/skills"
AGENTS_DIR="$HOME/.agents/skills"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║  Empire Brain — Installing...        ║"
echo "╚══════════════════════════════════════╝"
echo ""

# 1. Install skills globally
echo "→ Installing skills to $SKILLS_DIR"
mkdir -p "$SKILLS_DIR/recall" "$SKILLS_DIR/remember" "$SKILLS_DIR/auto-fix"
cp "$SCRIPT_DIR/skills/recall/SKILL.md"    "$SKILLS_DIR/recall/SKILL.md"
cp "$SCRIPT_DIR/skills/remember/SKILL.md"  "$SKILLS_DIR/remember/SKILL.md"
cp "$SCRIPT_DIR/skills/auto-fix/SKILL.md"  "$SKILLS_DIR/auto-fix/SKILL.md"
echo "   ✓ /recall, /remember, /auto-fix installed"

# Also install for other agent runtimes if present
if [ -d "$AGENTS_DIR" ]; then
  mkdir -p "$AGENTS_DIR/recall" "$AGENTS_DIR/remember" "$AGENTS_DIR/auto-fix"
  cp "$SCRIPT_DIR/skills/recall/SKILL.md"    "$AGENTS_DIR/recall/SKILL.md"
  cp "$SCRIPT_DIR/skills/remember/SKILL.md"  "$AGENTS_DIR/remember/SKILL.md"
  cp "$SCRIPT_DIR/skills/auto-fix/SKILL.md"  "$AGENTS_DIR/auto-fix/SKILL.md"
  echo "   ✓ Skills also installed to $AGENTS_DIR"
fi

# 2. Deploy Cloudflare Worker
echo ""
echo "→ Deploying empire-brain Worker to Cloudflare..."
if command -v wrangler &> /dev/null; then
  cd "$SCRIPT_DIR/worker"
  wrangler d1 execute empire-brain --file=schema.sql --remote 2>/dev/null || true
  wrangler deploy
  echo ""
  echo "   ✓ Worker deployed!"
  WORKER_URL=$(wrangler whoami 2>/dev/null | grep -o 'https://[^ ]*' | head -1 || echo "")
  echo "   Worker URL: https://empire-brain.<your-subdomain>.workers.dev"
else
  echo "   ⚠ wrangler not found. Install it: npm install -g wrangler"
  echo "   Then run: cd $SCRIPT_DIR/worker && wrangler deploy"
fi

# 3. Update CLAUDE.md if present
CLAUDE_MD="$HOME/passive-income/CLAUDE.md"
if [ -f "$CLAUDE_MD" ]; then
  if ! grep -q "empire-brain" "$CLAUDE_MD"; then
    echo "" >> "$CLAUDE_MD"
    cat >> "$CLAUDE_MD" << 'EOF'

## Empire Brain (Self-Evolving Agent Memory)
Before starting any significant task, run /recall to check for existing patterns.
After completing a task successfully, run /remember to store the pattern.
When debugging a broken tool, run /auto-fix first.

Worker: https://empire-brain.<your-subdomain>.workers.dev
Skills: /recall  /remember  /auto-fix
EOF
    echo "   ✓ CLAUDE.md updated with Empire Brain instructions"
  else
    echo "   ✓ CLAUDE.md already has Empire Brain config"
  fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  Empire Brain installed!                             ║"
echo "║                                                      ║"
echo "║  Skills available in all Claude Code sessions:      ║"
echo "║    /recall     — find patterns before starting      ║"
echo "║    /remember   — store winning solutions            ║"
echo "║    /auto-fix   — check known fixes before debugging ║"
echo "║                                                      ║"
echo "║  Update EMPIRE_BRAIN_URL in CLAUDE.md with your     ║"
echo "║  actual worker subdomain after deploy.              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
