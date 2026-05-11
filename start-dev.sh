#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-127.0.0.1}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

if [[ -x "$BACKEND_DIR/venv/bin/python" ]]; then
  BACKEND_PYTHON="$BACKEND_DIR/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  BACKEND_PYTHON="$(command -v python3)"
else
  echo "No Python interpreter found for backend startup." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is not installed or not in PATH." >&2
  exit 1
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo "frontend/node_modules is missing. Run 'cd frontend && npm install' first." >&2
  exit 1
fi

if ! "$BACKEND_PYTHON" -c "import uvicorn" >/dev/null 2>&1; then
  echo "Backend dependency check failed: uvicorn is not installed in $BACKEND_PYTHON." >&2
  echo "Run 'cd backend && ./venv/bin/pip install -r requirements.txt' first." >&2
  exit 1
fi

if ! "$BACKEND_PYTHON" -c "from alembic.config import Config" >/dev/null 2>&1; then
  echo "Backend dependency check failed: alembic is not installed in $BACKEND_PYTHON." >&2
  echo "Run 'cd backend && ./venv/bin/pip install -r requirements.txt' first." >&2
  exit 1
fi

BACKEND_PID=""
FRONTEND_PID=""

port_listener_info() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"$port" -sTCP:LISTEN 2>/dev/null || true
  fi
}

find_available_port() {
  local name="$1"
  local requested_port="$2"
  local port="$requested_port"
  local listener_info

  while true; do
    listener_info="$(port_listener_info "$port")"
    if [[ -z "$listener_info" ]]; then
      if [[ "$port" != "$requested_port" ]]; then
        echo "$name port $requested_port is busy, using $port instead."
      fi
      printf '%s\n' "$port"
      return 0
    fi
    port=$((port + 1))
  done
}

cleanup() {
  local exit_code=$?
  trap - EXIT INT TERM

  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi

  if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" >/dev/null 2>&1; then
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  fi

  wait >/dev/null 2>&1 || true
  exit "$exit_code"
}

trap cleanup EXIT INT TERM

BACKEND_PORT="$(find_available_port "Backend" "$BACKEND_PORT")"
FRONTEND_PORT="$(find_available_port "Frontend" "$FRONTEND_PORT")"

echo "Starting backend on http://$BACKEND_HOST:$BACKEND_PORT"
bash -lc "cd \"$BACKEND_DIR\" && exec \"$BACKEND_PYTHON\" -m uvicorn app.main:app --reload --host \"$BACKEND_HOST\" --port \"$BACKEND_PORT\"" &
BACKEND_PID=$!

echo "Starting frontend on http://$FRONTEND_HOST:$FRONTEND_PORT"
bash -lc "cd \"$FRONTEND_DIR\" && exec npm run dev -- --host \"$FRONTEND_HOST\" --port \"$FRONTEND_PORT\"" &
FRONTEND_PID=$!

echo
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Backend URL:  http://$BACKEND_HOST:$BACKEND_PORT"
echo "Frontend URL: http://$FRONTEND_HOST:$FRONTEND_PORT"
echo "Press Ctrl+C to stop both services."
echo

while true; do
  if ! kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    wait "$BACKEND_PID" >/dev/null 2>&1 || true
    break
  fi

  if ! kill -0 "$FRONTEND_PID" >/dev/null 2>&1; then
    wait "$FRONTEND_PID" >/dev/null 2>&1 || true
    break
  fi

  sleep 1
done
