#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$SCRIPT_DIR/services/api"
WEB_DIR="$SCRIPT_DIR/services/web"
MODE="${1:-${WORKBENCH_MODE:-dev}}"

PYTHON_BIN="${PYTHON_BIN:-python3}"
API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8000}"
WEB_HOST="${WEB_HOST:-0.0.0.0}"
DEV_WEB_PORT="${DEV_WEB_PORT:-5173}"
PROD_WEB_PORT="${PROD_WEB_PORT:-4173}"
if ! command -v pnpm >/dev/null 2>&1; then
  echo "Error: pnpm is required to run the web service. Install pnpm and try again." >&2
  exit 127
fi


case "$MODE" in
  dev)
    API_RELOAD="${API_RELOAD:-1}"
    WEB_COMMAND=(pnpm --dir "$WEB_DIR" run dev -- --host "$WEB_HOST" --port "$DEV_WEB_PORT")
    WEB_URL="http://127.0.0.1:$DEV_WEB_PORT"
    ;;
  prod)
    API_RELOAD="${API_RELOAD:-0}"
    echo "Building web service for production preview..."
    pnpm --dir "$WEB_DIR" run build
    WEB_COMMAND=(pnpm --dir "$WEB_DIR" run preview -- --host "$WEB_HOST" --port "$PROD_WEB_PORT")
    WEB_URL="http://127.0.0.1:$PROD_WEB_PORT"
    ;;
  *)
    printf 'Usage: %s [dev|prod]\n' "$0" >&2
    exit 2
    ;;
esac

export API_HOST API_PORT API_RELOAD
export WEB_API_PROXY_TARGET="${WEB_API_PROXY_TARGET:-http://127.0.0.1:$API_PORT}"

API_COMMAND=(
  "$PYTHON_BIN"
  -m
  uvicorn
  main:app
  --app-dir
  "$API_DIR"
  --host
  "$API_HOST"
  --port
  "$API_PORT"
)

if [[ "$API_RELOAD" != "0" ]]; then
  API_COMMAND+=(--reload --reload-dir "$API_DIR")
fi

PIDS=()

stop_children() {
  local pid
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  wait 2>/dev/null || true
}

trap stop_children EXIT INT TERM

echo "Starting SOME/IP workbench in $MODE mode"
echo "API: http://127.0.0.1:$API_PORT"
echo "OpenAPI docs: http://127.0.0.1:$API_PORT/docs"
echo "Web: $WEB_URL"

"${API_COMMAND[@]}" &
PIDS+=("$!")

"${WEB_COMMAND[@]}" &
PIDS+=("$!")

wait -n "${PIDS[@]}"
