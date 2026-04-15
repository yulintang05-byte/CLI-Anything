#!/bin/bash
# Empire TikTok Uploader — Install
# Clones TiktokAutoUploader into passive-income and sets it up

set -e
EMPIRE_DIR="$HOME/passive-income"
UPLOADER_DIR="$EMPIRE_DIR/TiktokAutoUploader"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Empire TikTok Uploader — Installing...  ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 1. Check dependencies
echo "→ Checking dependencies..."
command -v python3 >/dev/null || { echo "❌ python3 required"; exit 1; }
command -v node >/dev/null || { echo "❌ node 18+ required: brew install node"; exit 1; }
command -v npm >/dev/null || { echo "❌ npm required"; exit 1; }
echo "   ✓ python3, node, npm found"

# 2. Clone repo
if [ -d "$UPLOADER_DIR" ]; then
  echo "→ TiktokAutoUploader already cloned, pulling latest..."
  cd "$UPLOADER_DIR" && git pull
else
  echo "→ Cloning TiktokAutoUploader..."
  cd "$EMPIRE_DIR"
  git clone https://github.com/makiisthenes/TiktokAutoUploader.git
fi

cd "$UPLOADER_DIR"

# 3. Python deps
echo "→ Installing Python dependencies..."
pip3 install -r requirements.txt -q

# 4. Node deps
echo "→ Installing Node dependencies..."
npm install --silent

# 5. Playwright chromium
echo "→ Installing Playwright Chromium (one-time, ~150MB)..."
npx playwright install chromium

# 6. Create videos directory
mkdir -p videos cookies

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  TiktokAutoUploader installed!                       ║"
echo "║                                                      ║"
echo "║  Next: Login as @luckylefty0511                     ║"
echo "║  Run:  cd ~/passive-income/TiktokAutoUploader        ║"
echo "║        python3 cli.py login -n luckylefty0511        ║"
echo "║                                                      ║"
echo "║  Then test upload:                                   ║"
echo "║        python3 cli.py upload --user luckylefty0511  ║"
echo "║          -v path/to/video.mp4 -t 'Your title'       ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
