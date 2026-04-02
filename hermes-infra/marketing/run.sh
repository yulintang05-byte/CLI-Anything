#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/output/hermes-marketing.log"
DAEMON_MODE=false

# Parse flags
for arg in "$@"; do
  case "$arg" in
    --daemon) DAEMON_MODE=true ;;
  esac
done

# ── 1. Check for .env ────────────────────────────────────────────────────────
if [ -f "$SCRIPT_DIR/.env" ]; then
  echo "[hermes] Sourcing $SCRIPT_DIR/.env"
  set -a
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/.env"
  set +a
else
  echo "[hermes] ERROR: No .env file found."
  echo "         Copy the example and fill in your keys:"
  echo "         cp $SCRIPT_DIR/.env.example $SCRIPT_DIR/.env"
  exit 1
fi

# ── 2. Check Python 3.10+ ────────────────────────────────────────────────────
PYTHON_BIN=""
for candidate in python3 python3.12 python3.11 python3.10; do
  if command -v "$candidate" &>/dev/null; then
    version=$("$candidate" -c 'import sys; print(sys.version_info.minor + sys.version_info.major * 100)')
    if [ "$version" -ge 310 ]; then
      PYTHON_BIN="$candidate"
      break
    fi
  fi
done

if [ -z "$PYTHON_BIN" ]; then
  echo "[hermes] ERROR: Python 3.10 or higher is required but was not found."
  echo "         Install it from https://www.python.org/downloads/ and try again."
  exit 1
fi

echo "[hermes] Using $($PYTHON_BIN --version)"

# ── 3. Create virtualenv if missing ─────────────────────────────────────────
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "[hermes] Creating virtual environment at $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# Activate
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# ── 4. Install requirements ──────────────────────────────────────────────────
echo "[hermes] Installing/updating requirements..."
pip install --quiet --upgrade pip
pip install --quiet -r "$SCRIPT_DIR/requirements.txt"

# ── 5. Create output directory ───────────────────────────────────────────────
mkdir -p "$SCRIPT_DIR/output"

# ── 6. Launch orchestrator ───────────────────────────────────────────────────
cd "$SCRIPT_DIR"

if [ "$DAEMON_MODE" = true ]; then
  echo "[hermes] Starting in daemon mode..."
  nohup python orchestrator.py >> "$LOG_FILE" 2>&1 &
  HERMES_PID=$!
  echo "[hermes] Running as PID $HERMES_PID"
  echo "[hermes] Tail logs with:"
  echo "         tail -f $LOG_FILE"
  echo "$HERMES_PID" > "$SCRIPT_DIR/output/hermes.pid"
else
  echo "[hermes] Starting in foreground..."
  python orchestrator.py
fi
