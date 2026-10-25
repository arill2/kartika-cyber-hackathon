#!/usr/bin/env bash
# =============================================================================
#  POLARIS: Live Demo Orchestrator
#  Menjalankan rangkaian serangan asli terhadap sensor tipuan yang berjalan lokal.
#  Cocok untuk rekaman video demo (docs/09-demo-script.md).
#
#  Pakai:
#     AUTO=1 bash demo/demo.sh      # jalan otomatis, jeda tetap (untuk rekaman)
#     bash demo/demo.sh             # mode manual, tekan Enter tiap langkah
# =============================================================================
set -uo pipefail

CORE_URL="${POLARIS_CORE_URL:-http://127.0.0.1:8787}"
TOKEN="${POLARIS_TOKEN:-polaris-dev-token}"
TARGET="${POLARIS_DEMO_TARGET:-127.0.0.1}"
WEB_PORT="${POLARIS_WEB_PORT:-80}"
DECOY_DIR="${POLARIS_DECOY_DIR:-$HOME/.polaris/decoy}"
AUTO="${AUTO:-0}"
PAUSE="${PAUSE:-2}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

C="\033[1;36m"; G="\033[1;32m"; Y="\033[1;33m"; D="\033[2m"; R="\033[0m"

step(){ printf "\n${C}▶ %s${R}\n" "$*"; }
note(){ printf "  ${D}%s${R}\n" "$*"; }
ok(){   printf "  ${G}✓ %s${R}\n" "$*"; }
warn(){ printf "  ${Y}! %s${R}\n" "$*"; }
pause(){ if [ "$AUTO" = "1" ]; then sleep "$PAUSE"; else read -r -p "  ${D}[Enter] lanjut…${R}" _ || true; fi; }
have(){ command -v "$1" >/dev/null 2>&1; }

printf "\n\033[1mPOLARIS\033[0m: Deception-Based Early Warning · demo IT/OT\n"
printf "${D}dashboard live : %s\n" "$CORE_URL"
printf "target sensor : %s (web decoy :%s)\n${R}" "$TARGET" "$WEB_PORT"

# -----------------------------------------------------------------------------
step "0. Reset state: tunjukkan bahwa sistem dalam keadaan bersih (nol alert)"
curl -sS -X POST -H "X-Polaris-Token: $TOKEN" "$CORE_URL/api/reset" >/dev/null 2>&1 \
  && ok "state direset" || warn "collector belum jalan di $CORE_URL"
pause

# -----------------------------------------------------------------------------
step "1. Recon: nmap service/version detection ke port umpan (T1046)"
if have nmap; then
  nmap -sV -Pn -T4 --version-intensity 2 \
    -p 2222,3306,6379,3389,445,502,8080 "$TARGET" 2>/dev/null | sed -n '1,12p'
  ok "setiap port di atas adalah umpan: tidak ada layanan sah di sana"
else
  warn "nmap tidak terpasang, langkah dilewati"
fi
pause

# -----------------------------------------------------------------------------
step "2. Sweep cepat menyeluruh: pola scanner high-rate (indikasi masscan)"
if have nmap; then
  PORTS="$(seq -s, 1 1024)"
  note "memindai 1024 port dalam mode agresif…"
  nmap -Pn -n -T4 --min-rate 4000 -p "$PORTS" "$TARGET" 2>/dev/null | tail -6
  ok "pola sweep cepat terpisah dari probe berlapis milik nmap -sV"
else
  warn "nmap tidak terpasang, langkah dilewati"
fi
pause

# -----------------------------------------------------------------------------
step "3. Web recon: path admin/credential yang hanya menarik bagi scanner (T1595)"
for p in /.env /.git/config /.aws/credentials /actuator/env /server-status /wp-admin; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' -A 'Mozilla/5.00 (Nikto/2.5.0)' \
         "http://$TARGET:$WEB_PORT$p" || echo "ERR")
  printf "  %-24s -> %s\n" "$p" "$code"
done
if have nikto; then
  note "nikto (scanner web) :"
  timeout 60 nikto -host "http://$TARGET:$WEB_PORT" -maxtime 40s -nointeractive \
    2>/dev/null | grep -Ei "OSVDB|/\.env|/\.git|Target|Server" | head -6 || true
fi
ok "umpan membalas 200 dengan konten palsu agar penyerang melanjutkan interaksi"
pause

# -----------------------------------------------------------------------------
step "4. Brute force kredensial ke decoy SSH (T1110)"
if have hydra; then
  note "hydra (percobaan nyata, umpan tidak memiliki akun sah):"
  timeout 15 hydra -l admin -P <(printf 'admin\n123456\npassword\ntoor\n') \
    -t 4 -W 3 "ssh://$TARGET:2222" 2>&1 | grep -Ev '^(Hydra|\[DATA\])' | head -4 || true
fi
note "credential spray terstruktur:"
python3 "$HERE/ssh_spray.py" "$TARGET" 2222 6
ok "umpan tidak pernah memberi akses nyata, tapi setiap percobaan terekam"
pause

# -----------------------------------------------------------------------------
step "5. Honeytoken file: berkas kredensial palsu dibaca (T1083/T1552, T1)"
if [ -f "$DECOY_DIR/.env" ]; then
  note "isi $DECOY_DIR/.env (contoh 4 baris pertama):"
  head -4 "$DECOY_DIR/.env" | sed 's/^/    /'
else
  warn "honeytoken belum ada di $DECOY_DIR"
fi
pause

# -----------------------------------------------------------------------------
step "6. Honeytoken URL / canary credential dipakai (T1: indikasi kompromi)"
BEACON="$(grep -ao "http://[^ ]*beacon/[A-Za-z0-9-]*" "$DECOY_DIR/.env" 2>/dev/null | head -1 || true)"
if [ -n "$BEACON" ]; then
  note "canary URL dari berkas umpan: $BEACON"
  curl -sS -A 'curl/8.5.0' "$BEACON" >/dev/null && ok "beacon termuat → kredensial umpan terbukti dipakai"
else
  warn "beacon URL tidak ditemukan"
fi
pause

# -----------------------------------------------------------------------------
step "7. Decoy OT/ICS: Modbus & HMI disentuh (ATT&CK for ICS)"
python3 "$HERE/modbus_probe.py" "$TARGET" 502
note "port decoy HMI/SCADA :8080"
printf 'GET / HTTP/1.1\r\nHost: %s\r\n\r\n' "$TARGET" | timeout 3 nc "$TARGET" 8080 2>/dev/null | head -3
pause

# -----------------------------------------------------------------------------
step "8. Hasil: incident ter-korelasi"
python3 - "$CORE_URL" <<'PY' 2>/dev/null || curl -sS "$CORE_URL/api/incidents"
import json, sys, urllib.request
base = sys.argv[1]
print(json.dumps(json.load(urllib.request.urlopen(base + "/api/stats")), indent=1))
for i in json.load(urllib.request.urlopen(base + "/api/incidents")):
    print(f"\n  #{i['id']}  {i['severity']:<8} skor={i['score']:<4} events={i['event_count']} "
          f"tool={i['tool_guess']} ({i['tool_conf']})")
    print("   ", i['title'])
    print("    MITRE:", ", ".join(t['id'] for t in i['mitre']))
PY
printf "\n${G}Demo selesai.${R} Buka dashboard %s untuk melihat timeline & evidence.\n\n" "$CORE_URL"
