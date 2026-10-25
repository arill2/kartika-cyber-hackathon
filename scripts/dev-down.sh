#!/usr/bin/env bash
set -uo pipefail
RUN="${POLARIS_RUN_DIR:-/tmp/polaris-dev}"
for n in core agent; do
  if [ -f "$RUN/$n.pid" ]; then
    pid="$(cat "$RUN/$n.pid")"
    if kill -0 "$pid" 2>/dev/null; then kill "$pid" && echo "✓ hentikan $n (pid $pid)"; fi
    rm -f "$RUN/$n.pid"
  fi
done
