import json
import os
import sqlite3
import threading
from typing import Any

from .config import cfg

_lock = threading.RLock()
_conn: sqlite3.Connection | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT NOT NULL,
    agent_id    TEXT,
    event_type  TEXT NOT NULL,
    src_ip      TEXT,
    src_port    INTEGER,
    dst_port    INTEGER,
    decoy       TEXT,
    service     TEXT,
    tier        INTEGER,
    http_path   TEXT,
    http_method TEXT,
    user_agent  TEXT,
    username    TEXT,
    password    TEXT,
    payload     TEXT,
    payload_hex TEXT,
    bytes       INTEGER,
    duration_ms INTEGER,
    token       TEXT,
    file_path   TEXT,
    sha256      TEXT,
    detail      TEXT,
    mitre       TEXT,
    incident_id INTEGER,
    suppressed  INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_events_ip ON events(src_ip);
CREATE INDEX IF NOT EXISTS idx_events_inc ON events(incident_id);

CREATE TABLE IF NOT EXISTS incidents (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_ts  TEXT NOT NULL,
    updated_ts  TEXT NOT NULL,
    src_ip      TEXT,
    title       TEXT,
    severity    TEXT,
    score       INTEGER,
    status      TEXT DEFAULT 'open',
    tool_guess  TEXT,
    tool_conf   REAL,
    summary     TEXT,
    mitre       TEXT,
    event_count INTEGER DEFAULT 0,
    first_ts    TEXT,
    last_ts     TEXT,
    evidence    TEXT
);
CREATE INDEX IF NOT EXISTS idx_inc_ip ON incidents(src_ip);
CREATE INDEX IF NOT EXISTS idx_inc_sev ON incidents(severity);
"""


def _connect() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        os.makedirs(os.path.dirname(cfg.DB_PATH), exist_ok=True)
        _conn = sqlite3.connect(cfg.DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA synchronous=NORMAL")
    return _conn


def _migrate(db: sqlite3.Connection) -> None:
    cols = {r["name"] for r in db.execute("PRAGMA table_info(events)").fetchall()}
    if "payload_hex" not in cols:
        db.execute("ALTER TABLE events ADD COLUMN payload_hex TEXT")
    if "suppressed" not in cols:
        db.execute("ALTER TABLE events ADD COLUMN suppressed INTEGER DEFAULT 0")


def init_db() -> None:
    with _lock:
        db = _connect()
        db.executescript(SCHEMA)
        _migrate(db)
        db.commit()


def query(sql: str, params: tuple = ()) -> list[dict]:
    with _lock:
        cur = _connect().execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


def one(sql: str, params: tuple = ()) -> dict | None:
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: tuple = ()) -> int:
    with _lock:
        db = _connect()
        cur = db.execute(sql, params)
        db.commit()
        return cur.lastrowid


def insert_event(ev: dict[str, Any]) -> int:
    sql = """INSERT INTO events
        (ts, agent_id, event_type, src_ip, src_port, dst_port, decoy, service, tier,
         http_path, http_method, user_agent, username, password, payload, payload_hex, bytes,
         duration_ms, token, file_path, sha256, detail, mitre, incident_id, suppressed)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    return execute(sql, (
        ev.get("ts"), ev.get("agent_id"), ev.get("event_type"), ev.get("src_ip"),
        ev.get("src_port"), ev.get("dst_port"), ev.get("decoy"), ev.get("service"),
        ev.get("tier"), ev.get("http_path"), ev.get("http_method"), ev.get("user_agent"),
        ev.get("username"), ev.get("password"), ev.get("payload"), ev.get("payload_hex"),
        ev.get("bytes"),
        ev.get("duration_ms"), ev.get("token"), ev.get("file_path"), ev.get("sha256"),
        ev.get("detail"), json.dumps(ev.get("mitre", [])), ev.get("incident_id"),
        1 if ev.get("suppressed") else 0,
    ))


def recent_events_for_ip(ip: str, window_sec: int) -> list[dict]:
    return query(
        """SELECT * FROM events
           WHERE src_ip = ? AND suppressed = 0 AND ts >= datetime('now', ?)
           ORDER BY id DESC LIMIT 500""",
        (ip, f"-{window_sec} seconds"),
    )


def open_incident_for_ip(ip: str, window_sec: int) -> dict | None:
    return one(
        """SELECT * FROM incidents
           WHERE src_ip = ? AND status = 'open' AND updated_ts >= datetime('now', ?)
           ORDER BY id DESC LIMIT 1""",
        (ip, f"-{window_sec} seconds"),
    )


def incidents_in_window(ip: str, window_sec: int) -> list[dict]:
    return query(
        """SELECT * FROM incidents WHERE src_ip = ? AND updated_ts >= datetime('now', ?)
           ORDER BY id DESC""",
        (ip, f"-{window_sec} seconds"),
    )


def update_incident(incident_id: int, fields: dict[str, Any]) -> None:
    cols = ", ".join(f"{k} = ?" for k in fields)
    execute(f"UPDATE incidents SET {cols} WHERE id = ?", (*fields.values(), incident_id))


def events_for_incident(incident_id: int) -> list[dict]:
    return query("SELECT * FROM events WHERE incident_id = ? ORDER BY id ASC", (incident_id,))


def set_event_incident(event_id: int, incident_id: int) -> None:
    execute("UPDATE events SET incident_id = ? WHERE id = ?", (incident_id, event_id))


def _hydrate(inc: dict) -> dict:
    """Ubah kolom JSON (mitre/evidence) menjadi list Python. Satu tempat saja,
    agar tidak ada konsumen (dashboard/API) yang menerima JSON mentah."""
    for key in ("mitre", "evidence"):
        val = inc.get(key)
        if isinstance(val, str):
            try:
                inc[key] = json.loads(val or "[]")
            except json.JSONDecodeError:
                inc[key] = []
    return inc


def incidents(limit: int = 100) -> list[dict]:
    return [_hydrate(dict(r)) for r in query(
        "SELECT * FROM incidents ORDER BY updated_ts DESC LIMIT ?", (limit,))]


def incident(inc_id: int) -> dict | None:
    row = one("SELECT * FROM incidents WHERE id = ?", (inc_id,))
    return _hydrate(row) if row else None


def events(limit: int = 200) -> list[dict]:
    return query("SELECT * FROM events WHERE suppressed = 0 ORDER BY id DESC LIMIT ?", (limit,))


def suppressed_events(limit: int = 100) -> list[dict]:
    return query("SELECT * FROM events WHERE suppressed = 1 ORDER BY id DESC LIMIT ?", (limit,))


def stats() -> dict:
    total_events = one("SELECT COUNT(*) c FROM events WHERE suppressed = 0")["c"]
    suppressed = one("SELECT COUNT(*) c FROM events WHERE suppressed = 1")["c"]
    total_inc = one("SELECT COUNT(*) c FROM incidents")["c"]
    by_sev = {r["severity"]: r["c"] for r in query(
        "SELECT severity, COUNT(*) c FROM incidents GROUP BY severity")}
    distinct_ips = one("SELECT COUNT(DISTINCT src_ip) c FROM events WHERE suppressed = 0")["c"]
    return {
        "events": total_events,
        "suppressed_events": suppressed,
        "incidents": total_inc,
        "distinct_attackers": distinct_ips,
        "by_severity": by_sev,
        # by design tidak ada umpan yang boleh disentuh pengguna sah
        "false_positives": 0,
    }


def clear_all() -> None:
    with _lock:
        db = _connect()
        db.execute("DELETE FROM events")
        db.execute("DELETE FROM incidents")
        db.commit()
