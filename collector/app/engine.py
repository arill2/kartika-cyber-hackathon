"""Detection Engine POLARIS.

Empat lapis (docs/04-engine-deteksi.md):
  1. Attacker fingerprinting
  2. Correlation event -> incident
  3. MITRE ATT&CK mapping
  4. Severity scoring
Plus AI summarizer opsional (default: narasi deterministik, bukan LLM).
"""
from __future__ import annotations

import datetime as _dt
import json
import re
from typing import Any

from . import alerts, db, mitre
from .config import cfg

# ---------------------------------------------------------------- waktu

_TS_FRAC = re.compile(r"(\.\d{6})\d+")


def norm_ts(ts: str | None) -> str:
    """Normalisasi ts RFC3339 -> 'YYYY-MM-DD HH:MM:SS.mmm' (UTC) agar
    perbandingan string di SQLite konsisten."""
    if not ts:
        return now_ts()
    s = ts.strip().replace("Z", "+00:00")
    s = _TS_FRAC.sub(r"\1", s)
    try:
        dt = _dt.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=_dt.timezone.utc)
        dt = dt.astimezone(_dt.timezone.utc).replace(tzinfo=None)
    except ValueError:
        dt = _dt.datetime.utcnow()
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def now_ts() -> str:
    return _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


# ---------------------------------------------------------------- severity

SEV_POINTS = {"LOW": 10, "MEDIUM": 30, "HIGH": 60, "CRITICAL": 100}

BASE_SEVERITY = {
    "honeytoken_file_access": "HIGH",
    "canary_cred_used": "CRITICAL",
    "honeytoken_url_fetch": "HIGH",
    "decoy_login_attempt": "HIGH",
    "decoy_connection": "MEDIUM",
    "web_decoy_hit": "MEDIUM",
    "decoy_ot_touch": "HIGH",
}

CAT_LABEL = {
    "decoy_connection": "port scan",
    "web_decoy_hit": "web recon",
    "decoy_login_attempt": "credential brute force",
    "honeytoken_file_access": "honeytoken access",
    "canary_cred_used": "canary credential use",
    "honeytoken_url_fetch": "honeytoken beacon",
    "decoy_ot_touch": "OT/ICS probe",
}

SEV_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def _bump(sev: str, steps: int = 1) -> str:
    i = SEV_ORDER.index(sev) if sev in SEV_ORDER else 0
    return SEV_ORDER[min(i + steps, len(SEV_ORDER) - 1)]


def score_to_severity(score: int) -> str:
    if score >= 100:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 25:
        return "MEDIUM"
    return "LOW"


# ---------------------------------------------------------------- fingerprint

_UA_SIGNATURES = [
    ("sqlmap", "sqlmap", 0.95),
    ("nikto", "nikto", 0.92),
    ("gobuster", "gobuster", 0.9),
    ("dirbuster", "dirbuster", 0.9),
    ("masscan", "masscan", 0.95),
    ("nmap", "nmap", 0.9),
    ("hydra", "hydra", 0.9),
    ("python-requests", "python-requests", 0.75),
    ("curl/", "curl", 0.7),
    ("wget/", "wget", 0.7),
    ("zgrab", "zgrab", 0.9),
    ("go-http-client", "go-http-client", 0.6),
]


def fingerprint(ev: dict[str, Any]) -> tuple[str, float, str]:
    """Tebak tool penyerang dari event ini + pola recent (best-effort)."""
    ua = (ev.get("user_agent") or "").lower()
    for sig, tool, conf in _UA_SIGNATURES:
        if sig in ua:
            return tool, conf, f"User-Agent cocok dengan '{sig}'"

    ip = ev.get("src_ip")
    recent = db.recent_events_for_ip(ip, cfg.FP_WINDOW_SEC) if ip else []
    recent = recent + [ev]

    ports = {e.get("dst_port") for e in recent if e.get("dst_port")}
    web_paths = {e.get("http_path") for e in recent if e.get("event_type") == "web_decoy_hit"}
    ssh_conns = [e for e in recent if (e.get("service") == "ssh")]
    ot_conns = [e for e in recent if e.get("event_type") == "decoy_ot_touch"]

    n_ports = len(ports)
    # rasio event/port: >2 menandakan probe berlapis per port (service detection),
    # bukan sekadar sapuan satu-koneksi-per-port (masscan).
    ratio = len(recent) / max(n_ports, 1)

    if n_ports >= 20:
        return "masscan", 0.85, f"{n_ports} port umpan dipindai dengan sangat cepat (pola sweep)"
    if n_ports >= 6 and ratio >= 2:
        return "nmap", 0.86, f"{n_ports} port dipindai dengan probe berlapis (service/version detection)"
    if n_ports >= 6:
        return "nmap", 0.78, f"{n_ports} port umpan dipindai berurutan"
    if len(ssh_conns) >= cfg.BRUTEFORCE_MIN:
        return "hydra", 0.82, f"{len(ssh_conns)} percobaan auth ke decoy SSH"
    if len(web_paths) >= 4:
        return "gobuster/dirb", 0.75, f"{len(web_paths)} path umpan diakses cepat"
    if n_ports >= 4:
        return "nmap", 0.62, f"{n_ports} port umpan dipindai"
    if len(web_paths) >= 2:
        return "web reconnaissance", 0.6, f"{len(web_paths)} path umpan diakses"
    if ot_conns:
        return "ot-scanner", 0.7, "koneksi ke decoy protokol industri"
    return "unknown scanner", 0.35, "pola belum cukup untuk diidentifikasi"


# ---------------------------------------------------------------- summary

def _fmt_dur(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f} detik"
    return f"{seconds / 60:.1f} menit"


def build_summary(ip: str, events: list[dict], tool: str, conf: float, severity: str) -> str:
    cats = sorted({e["event_type"] for e in events})
    labels = [CAT_LABEL.get(c, c) for c in cats]
    try:
        first = _dt.datetime.strptime(events[0]["ts"], "%Y-%m-%d %H:%M:%S.%f")
        last = _dt.datetime.strptime(events[-1]["ts"], "%Y-%m-%d %H:%M:%S.%f")
        dur = _fmt_dur(max((last - first).total_seconds(), 1))
    except Exception:
        dur = "1 detik"

    distinct_decoy = len({e.get("decoy") for e in events if e.get("decoy")})
    ot = any(e["event_type"] == "decoy_ot_touch" for e in events)

    base = (
        f"IP {ip} memicu {len(events)} interaksi umpan dalam {dur} "
        f"({', '.join(labels)}), menyentuh {distinct_decoy} jenis umpan berbeda. "
        f"Ciri pola mengarah ke {tool} dengan keyakinan {int(conf * 100)}%."
    )
    if ot:
        base += " Terdapat probing terhadap decoy protokol OT/ICS, potensi ancaman ke proses fisik."
    if "canary_cred_used" in cats:
        base += " Kredensial umpan (canary) terbukti digunakan, indikasi kuat kompromi."
    base += (
        " Tidak ada aktivitas sah dari IP ini terhadap umpan. Karena umpan tidak pernah "
        "disentuh operasi normal, insiden ini bersifat deterministik dengan nol false positive."
    )
    return base


# ---------------------------------------------------------------- pipeline

def _incident_title(cats: set[str]) -> str:
    order = ["canary_cred_used", "honeytoken_file_access", "decoy_login_attempt",
             "honeytoken_url_fetch", "decoy_ot_touch", "decoy_connection", "web_decoy_hit"]
    parts = [CAT_LABEL[c] for c in order if c in cats]
    return "Percobaan intrusi: " + " + ".join(parts)


def enrich(ev: dict[str, Any]) -> dict[str, Any]:
    ev["ts"] = norm_ts(ev.get("ts"))
    ev["mitre"] = mitre.map_event(ev.get("event_type", ""), ev.get("service", "") or "")
    ev["tier"] = ev.get("tier") or (1 if ev["event_type"] in (
        "honeytoken_file_access", "canary_cred_used", "honeytoken_url_fetch") else 2)
    return ev


def recompute_incident(inc_id: int, inc: dict, events: list[dict]) -> dict:
    cats = {e["event_type"] for e in events}
    tool, conf, reason = fingerprint(events[-1])

    score = 0
    for c in cats:
        score += SEV_POINTS.get(BASE_SEVERITY.get(c, "LOW"), 20)
    score += 10 * max(len(cats) - 1, 0)          # bonus variasi
    score += min(len(events), 20)                 # bonus volume
    severity = score_to_severity(score)

    if "canary_cred_used" in cats:
        severity = "CRITICAL"
    if "decoy_ot_touch" in cats and SEV_ORDER.index(severity) < SEV_ORDER.index("HIGH"):
        severity = "HIGH"

    techniques: dict[str, dict] = {}
    for e in events:
        for t in mitre.map_event(e["event_type"], e.get("service") or ""):
            techniques[t["id"]] = t

    evidence = [{
        "ts": e["ts"], "event": e["event_type"], "decoy": e.get("decoy"),
        "dst_port": e.get("dst_port"), "path": e.get("http_path"),
        "tool": None, "sha256": e.get("sha256"),
    } for e in events][-40:]

    summary = build_summary(inc["src_ip"], events, tool, conf, severity)

    return {
        "title": _incident_title(cats),
        "severity": severity,
        "score": score,
        "tool_guess": tool,
        "tool_conf": conf,
        "mitre": json.dumps(list(techniques.values())),
        "summary": summary,
        "event_count": len(events),
        "first_ts": events[0]["ts"],
        "last_ts": events[-1]["ts"],
        "updated_ts": now_ts(),
        "evidence": json.dumps(evidence),
    }


def is_suppressed(ev: dict[str, Any]) -> str | None:
    """Kembalikan alasan bila event cocok dengan pola aktivitas jinak yang dikenal.

    Tujuannya bukan menyembunyikan, melainkan memisahkan otomasi internal
    (health check, probe monitoring) agar alert penyerang tetap bersinyal tinggi.
    Semua event yang disaring TETAP disimpan dengan flag suppressed=1 (auditable).
    """
    if cfg.ALLOWLIST_IPS and ev.get("src_ip") in cfg.ALLOWLIST_IPS:
        return f"src_ip di allowlist ({ev.get('src_ip')})"
    parts = [str(ev.get(k) or "") for k in (
        "payload_printable", "http_path", "user_agent", "detail")]
    # sertakan payload biner yang di-decode (hex) agar pola seperti health check
    # tetap terbaca walau tidak printable.
    px = ev.get("payload_hex") or ""
    if px:
        try:
            parts.append(bytes.fromhex(px).decode("latin-1"))
        except ValueError:
            pass
    hay = " ".join(parts).lower()
    for pat in cfg.SUPPRESS_PATTERNS:
        if pat.lower() in hay:
            return f"pola jinak dikenal: '{pat}'"
    return None


def process_event(raw: dict[str, Any]) -> dict[str, Any]:
    """Inti pipeline. Mengembalikan dict hasil untuk di-broadcast/alert."""
    ev = enrich(dict(raw))

    reason = is_suppressed(ev)
    if reason:
        ev["suppressed"] = True
        base = (ev.get("detail") or "").strip()
        ev["detail"] = (base + " " if base else "") + f"[suppressed: {reason}]"
        event_id = db.insert_event(ev)
        ev["id"] = event_id
        return {"event": ev, "incident": None, "is_new": False, "notify": False,
                "suppressed": True}

    event_id = db.insert_event(ev)
    ev["id"] = event_id

    ip = ev.get("src_ip") or "unknown"
    inc = db.open_incident_for_ip(ip, cfg.CORR_WINDOW_SEC)
    is_new = inc is None
    prev_sev = None

    if inc is None:
        inc_id = db.execute(
            """INSERT INTO incidents
               (created_ts, updated_ts, src_ip, title, severity, score, status,
                tool_guess, tool_conf, summary, mitre, event_count, first_ts, last_ts, evidence)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (now_ts(), now_ts(), ip, "new", "LOW", 0, "open", None, 0.0, "", "[]", 0, ev["ts"], ev["ts"], "[]"),
        )
        inc = db.one("SELECT * FROM incidents WHERE id = ?", (inc_id,))
    else:
        prev_sev = inc["severity"]

    db.set_event_incident(event_id, inc["id"])

    events = db.events_for_incident(inc["id"])
    fields = recompute_incident(inc["id"], inc, events)
    db.update_incident(inc["id"], fields)

    updated = db.incident(inc["id"])

    sev_changed = prev_sev != updated["severity"]
    notify = is_new or sev_changed or updated["severity"] == "CRITICAL"
    if notify:
        alerts.dispatch(dict(updated))

    ev_out = dict(ev)
    ev_out["incident_id"] = updated["id"]
    return {"event": ev_out, "incident": updated, "is_new": is_new, "notify": notify}
