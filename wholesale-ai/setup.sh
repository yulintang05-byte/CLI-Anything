#!/bin/bash
# Wholesale AI — One-time setup

set -e

echo "🏠 Wholesale AI — Setup"
echo "========================"

# Python check
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 required. Install from python.org"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

# Create .env if missing
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env — add your API keys!"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Add ANTHROPIC_API_KEY to .env (free at console.anthropic.com)"
echo "  2. Optionally add HUD_API_TOKEN to .env (free at huduser.gov)"
echo "  3. Run: python main.py"
echo ""
