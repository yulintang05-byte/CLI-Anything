#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/output/hermes-marketing.log"
VENV_DIR="$SCRIPT_DIR/.venv"
DAEMON=false

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
for arg in "$@"; do
  case "$arg" in
    --daemon) DAEMON=true ;;
    --help|-h)
      echo "Usage: $0 [--daemon]"
      echo ""
      echo "  --daemon   Run orchestrator in the background via nohup."
      echo "             Logs are written to output/hermes-marketing.log"
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 1
      ;;
  esac
done

# ---------------------------------------------------------------------------
# 1. Check for .env file
# ---------------------------------------------------------------------------
if [[ -f "$SCRIPT_DIR/.env" ]]; then
  echo "[hermes] Sourcing $SCRIPT_DIR/.env"
  # shellcheck disable=SC1090
  set -a
  source "$SCRIPT_DIR/.env"
  set +a
else
  echo ""
  echo "[hermes] ERROR: No .env file found."
  echo "  Copy the example and fill in your keys:"
  echo ""
  echo "    cp $SCRIPT_DIR/.env.example $SCRIPT_DIR/.env"
  echo "    \$EDITOR $SCRIPT_DIR/.env"
  echo ""
  exit 1
fi

# ---------------------------------------------------------------------------
# 2. Check Python 3.10+
# ---------------------------------------------------------------------------
PYTHON=""
for candidate in python3.12 python3.11 python3.10 python3 python; do
  if command -v "$candidate" &>/dev/null; then
    version=$("$candidate" -c 'import sys; print(sys.version_info.major * 100 + sys.version_info.minor)' 2>/dev/null || echo 0)
    if [[ "$version" -ge 310 ]]; then
      PYTHON="$candidate"
      break
    fi
  fi
done

if [[ -z "$PYTHON" ]]; then
  echo ""
  echo "[hermes] ERROR: Python 3.10 or higher is required but was not found."
  echo "  Install Python 3.10+ and ensure it is on your PATH."
  echo ""
  exit 1
fi

echo "[hermes] Using Python: $($PYTHON --version)"

# ---------------------------------------------------------------------------
# 3. Create virtualenv if it does not exist
# ---------------------------------------------------------------------------
if [[ ! -d "$VENV_DIR" ]]; then
  echo "[hermes] Creating virtualenv at $VENV_DIR"
  "$PYTHON" -m venv "$VENV_DIR"
fi

# Activate
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

# ---------------------------------------------------------------------------
# 4. Install / upgrade requirements
# ---------------------------------------------------------------------------
echo "[hermes] Installing requirements..."
pip install --quiet --upgrade pip
pip install --quiet -r "$SCRIPT_DIR/requirements.txt"

# ---------------------------------------------------------------------------
# 5. Ensure output/ directory exists
# ---------------------------------------------------------------------------
mkdir -p "$SCRIPT_DIR/output"

# ---------------------------------------------------------------------------
# 6. Run orchestrator
# ---------------------------------------------------------------------------
if [[ "$DAEMON" == true ]]; then
  echo "[hermes] Starting orchestrator in background (daemon mode)..."
  nohup "$VENV_DIR/bin/python" "$SCRIPT_DIR/orchestrator.py" \
    >> "$LOG_FILE" 2>&1 &
  HERMES_PID=$!
  echo ""
  echo "[hermes] Orchestrator running with PID $HERMES_PID"
  echo ""
  echo "  Tail logs with:"
  echo "    tail -f $LOG_FILE"
  echo ""
  echo "  Stop the daemon with:"
  echo "    kill $HERMES_PID"
  echo ""
else
  echo "[hermes] Starting orchestrator in foreground..."
  echo ""
  exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/orchestrator.py"
fi
