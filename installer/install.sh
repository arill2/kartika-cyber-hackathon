#!/usr/bin/env bash
# =============================================================================
#  POLARIS: One-line installer (optimasi bobot "kemudahan implementasi")
#
#  Instalasi jarak jauh (contoh):
#     curl -fsSL https://raw.githubusercontent.com/arill2/kartika-cyber-hackathon/main/installer/install.sh | bash
#
#  Instalasi dari sumber lokal (offline / air-gap):
#     bash installer/install.sh --local ./bin/polaris-agent
#
#  Variabel opsional:
#     POLARIS_REPO=owner/repo   POLARIS_PREFIX=/usr/local/bin
#     POLARIS_CORE_URL=http://127.0.0.1:8787   POLARIS_TOKEN=...
# =============================================================================
set -euo pipefail

REPO="${POLARIS_REPO:-arill2/kartika-cyber-hackathon}"
REF="${POLARIS_REF:-main}"
PREFIX="${POLARIS_PREFIX:-/usr/local/bin}"
CONF_DIR="${HOME}/.polaris"
CONF_FILE="${CONF_DIR}/agent.env"
LOCAL_BIN=""

while [ $# -gt 0 ]; do
  case "$1" in
    --local) LOCAL_BIN="${2:-}"; shift 2 ;;
    --prefix) PREFIX="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "argumen tidak dikenal: $1" >&2; exit 2 ;;
  esac
done

say(){ printf "\033[1;36m▶\033[0m %s\n" "$*"; }
ok(){  printf "\033[1;32m✓\033[0m %s\n" "$*"; }
warn(){ printf "\033[1;33m!\033[0m %s\n" "$*"; }

# --- 1. deteksi platform ------------------------------------------------------
os="$(uname -s | tr '[:upper:]' '[:lower:]')"
arch="$(uname -m)"
case "$arch" in
  x86_64|amd64) arch="amd64" ;;
  aarch64|arm64) arch="arm64" ;;
  armv7l) arch="armv7" ;;
esac
say "platform terdeteksi: ${os}/${arch}"

# --- 2. ambil binary ----------------------------------------------------------
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
dst="${tmp}/polaris-agent"

if [ -n "$LOCAL_BIN" ]; then
  [ -f "$LOCAL_BIN" ] || { echo "binary lokal tidak ditemukan: $LOCAL_BIN" >&2; exit 1; }
  cp "$LOCAL_BIN" "$dst"
  ok "menggunakan binary lokal: $LOCAL_BIN"
else
  url="https://github.com/${REPO}/releases/download/${REF}/polaris-agent-${os}-${arch}"
  say "mengunduh agent: $url"
  if ! curl -fsSL "$url" -o "$dst"; then
    url="https://raw.githubusercontent.com/${REPO}/${REF}/bin/polaris-agent-${os}-${arch}"
    warn "release tidak tersedia, mencoba: $url"
    if ! curl -fsSL "$url" -o "$dst"; then
      url="https://raw.githubusercontent.com/${REPO}/${REF}/bin/polaris-agent"
      warn "menyusul: $url"
      curl -fsSL "$url" -o "$dst" || {
        echo "unduhan gagal. Bangun dulu (cd agent && go build -o ../bin/polaris-agent .)" >&2
        echo "lalu pasang dengan: bash installer/install.sh --local ./bin/polaris-agent" >&2
        exit 1
      }
    fi
  fi
fi
chmod +x "$dst"
ok "binary siap ($(du -h "$dst" | cut -f1))"

# --- 3. pasang ----------------------------------------------------------------
target="${PREFIX}/polaris-agent"
if ! install -m 0755 "$dst" "$target" 2>/dev/null; then
  PREFIX="${HOME}/.local/bin"
  mkdir -p "$PREFIX"
  target="${PREFIX}/polaris-agent"
  install -m 0755 "$dst" "$target"
  warn "tidak ada izin tulis ke ${POLARIS_PREFIX:-/usr/local/bin}; dipasang ke $target"
  case ":$PATH:" in *":$PREFIX:"*) ;; *) warn "tambahkan $PREFIX ke PATH" ;; esac
fi
ok "terpasang: $target"

# --- 4. konfigurasi -----------------------------------------------------------
mkdir -p "$CONF_DIR" && chmod 700 "$CONF_DIR"
if [ ! -f "$CONF_FILE" ]; then
  cat > "$CONF_FILE" <<EOF
# POLARIS agent configuration
POLARIS_AGENT_ID=$(hostname)
POLARIS_CORE_URL=${POLARIS_CORE_URL:-http://127.0.0.1:8787}
POLARIS_TOKEN=${POLARIS_TOKEN:-polaris-dev-token}
POLARIS_DECOY_DIR=${CONF_DIR}/decoy
POLARIS_WEB_PORT=${POLARIS_WEB_PORT:-80}
POLARIS_PORT_SSH=2222
POLARIS_PORT_MYSQL=3306
POLARIS_PORT_REDIS=6379
POLARIS_PORT_RDP=3389
POLARIS_PORT_SMB=445
POLARIS_PORT_HMI=8080
POLARIS_PORT_MODBUS=502
EOF
  chmod 600 "$CONF_FILE"
  ok "konfigurasi dibuat: $CONF_FILE"
else
  ok "konfigurasi sudah ada: $CONF_FILE (dibiarkan)"
fi

# --- 5. ringkasan -------------------------------------------------------------
cat <<EOF

  POLARIS agent siap dijalankan:

    set -a; . "$CONF_FILE"; set +a
    $target

  Sebagai service (systemd, butuh root):
    sudo tee /etc/systemd/system/polaris-agent.service >/dev/null <<'UNIT'
[Unit]
Description=POLARIS Deception Agent
After=network.target
[Service]
Type=simple
EnvironmentFile=%h/.polaris/agent.env
ExecStart=/usr/local/bin/polaris-agent
Restart=always
RestartSec=5
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=true
[Install]
WantedBy=multi-user.target
UNIT
    sudo systemctl daemon-reload && sudo systemctl enable --now polaris-agent

EOF
ok "instalasi selesai."
