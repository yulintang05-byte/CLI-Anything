#!/bin/bash
# Empire TikTok Uploader — Install
# Clones TiktokAutoUploader into passive-income and runs its own setup.sh

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

mkdir -p "$EMPIRE_DIR"

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

# 3. Run repo's own setup (python deps + tiktok-signature npm + playwright chromium + dirs)
echo "→ Running repo setup.sh (Python deps, Node signature module, Playwright Chromium)..."
bash ./setup.sh

# 4. Ensure expected directories exist (setup.sh creates them too, belt-and-suspenders)
mkdir -p CookiesDir VideosDirPath

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  TiktokAutoUploader installed!                       ║"
echo "║                                                      ║"
echo "║  Next: Login as @luckylefty0511                      ║"
echo "║  Run:  cd ~/passive-income/TiktokAutoUploader        ║"
echo "║        python3 cli.py login -n luckylefty0511        ║"
echo "║                                                      ║"
echo "║  Then test upload (video must live in                ║"
echo "║  ./VideosDirPath — pass just the filename):          ║"
echo "║        python3 cli.py upload -u luckylefty0511 \\    ║"
echo "║          -v myclip.mp4 -t 'Your title' -vi 0         ║"
echo "║                                                      ║"
echo "║  Or use the Empire wrapper (handles staging):        ║"
echo "║        python3 empire_post.py --video path/clip.mp4 \\║"
echo "║          --title 'Your title'                        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
