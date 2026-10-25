#!/usr/bin/env bash
# Jalankan collector + agent untuk pengembangan / demo lokal.
#   bash scripts/dev-up.sh          # start (background)
#   bash scripts/dev-down.sh        # stop
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
ROOT="$(pwd)"
RUN="${POLARIS_RUN_DIR:-/tmp/polaris-dev}"
mkdir -p "$RUN"

PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || { echo "venv belum ada. jalankan: python3 -m venv .venv && .venv/bin/pip install -r collector/requirements.txt" >&2; exit 1; }

# binary agent
if [ ! -x "$ROOT/bin/polaris-agent" ] || [ -n "$(find "$ROOT/agent" -newer "$ROOT/bin/polaris-agent" -name '*.go' 2>/dev/null)" ]; then
  echo "▶ membangun agent…"
  (cd agent && go build -o ../bin/polaris-agent .) || exit 1
fi

setsid nohup env POLARIS_DB="$RUN/polaris.db" "$PY" -m uvicorn collector.app.main:app \
  --host "${POLARIS_HOST:-127.0.0.1}" --port "${POLARIS_BIND_PORT:-8787}" \
  > "$RUN/core.log" 2>&1 &
echo $! > "$RUN/core.pid"
sleep 3

setsid nohup env POLARIS_WEB_PORT="${POLARIS_WEB_PORT:-80}" \
  POLARIS_DECOY_DIR="${POLARIS_DECOY_DIR:-$HOME/.polaris/decoy}" \
  "$ROOT/bin/polaris-agent" > "$RUN/agent.log" 2>&1 &
echo $! > "$RUN/agent.pid"
sleep 2

echo "✓ core  pid=$(cat "$RUN/core.pid")  log=$RUN/core.log"
echo "✓ agent pid=$(cat "$RUN/agent.pid")  log=$RUN/agent.log"
echo "  dashboard: http://127.0.0.1:${POLARIS_BIND_PORT:-8787}"
