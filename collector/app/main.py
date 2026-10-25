"""POLARIS Collector (FastAPI): ingest, engine, dashboard, alert, live WS."""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from fastapi import Body, FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict

from . import db, engine
from .config import cfg
from .hub import hub

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("polaris.collector")

app = FastAPI(title="POLARIS Collector", version="0.1.0")

DASHBOARD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dashboard"))


class EventIn(BaseModel):
    model_config = ConfigDict(extra="allow")

    agent_id: str | None = None
    event_type: str
    ts: str | None = None
    src_ip: str | None = None
    src_port: int | None = None
    dst_port: int | None = None
    decoy: str | None = None
    service: str | None = None
    tier: int | None = None
    payload_printable: str | None = None
    payload_hex: str | None = None
    user_agent: str | None = None
    http_path: str | None = None
    http_method: str | None = None
    username: str | None = None
    password: str | None = None
    bytes: int | None = None
    duration_ms: int | None = None
    token: str | None = None
    file_path: str | None = None
    sha256: str | None = None
    detail: str | None = None


@app.on_event("startup")
def _startup() -> None:
    db.init_db()
    log.info("POLARIS collector siap. db=%s telegram=%s webhook=%s",
             cfg.DB_PATH, cfg.telegram_enabled(), bool(cfg.WEBHOOK_URL))


def _check_token(token: str | None) -> None:
    if token != cfg.TOKEN:
        raise HTTPException(status_code=401, detail="token agent tidak valid")


@app.get("/healthz", response_class=PlainTextResponse)
def healthz() -> str:
    return "ok"


@app.post("/api/ingest")
async def ingest(payload: EventIn, x_polaris_token: str | None = Header(default=None)) -> JSONResponse:
    _check_token(x_polaris_token)
    result = await run_in_threadpool(engine.process_event, payload.model_dump(exclude_none=True))
    await hub.broadcast("event", result["event"])
    if result.get("incident"):
        await hub.broadcast("incident", result["incident"])
    return JSONResponse({"ok": True, "event_id": result["event"]["id"],
                         "incident_id": (result["incident"] or {}).get("id"),
                         "suppressed": bool(result.get("suppressed"))})


@app.get("/beacon/{token}")
async def beacon(token: str, request: Request) -> JSONResponse:
    """Honeytoken URL: tidak ada alasan sah untuk di-fetch (docs/03 -> Honeytoken URLs)."""
    client = request.client.host if request.client else "unknown"
    xff = request.headers.get("x-forwarded-for")
    if xff:
        client = xff.split(",")[0].strip()
    ev_type = "canary_cred_used" if token.startswith("cred-") else "honeytoken_url_fetch"
    ev = {
        "agent_id": "beacon",
        "event_type": ev_type,
        "src_ip": client,
        "tier": 1,
        "token": token,
        "service": "http",
        "decoy": "honeytoken-url",
        "user_agent": request.headers.get("user-agent"),
        "http_path": f"/beacon/{token}",
        "http_method": request.method,
        "detail": "honeytoken URL di-fetch, beacon T1",
    }
    result = await run_in_threadpool(engine.process_event, ev)
    await hub.broadcast("event", result["event"])
    if result.get("incident"):
        await hub.broadcast("incident", result["incident"])
    # balas seolah endpoint kosong biasa (tidak membocorkan bahwa ini umpan)
    return JSONResponse({"status": "ok"}, status_code=200)


@app.websocket("/api/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await hub.connect(ws)
    try:
        await ws.send_text(json.dumps({"type": "snapshot", "data": _snapshot()}, default=str))
        while True:
            await ws.receive_text()  # keep-alive / ping
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await hub.disconnect(ws)


def _snapshot() -> dict[str, Any]:
    return {
        "stats": db.stats(),
        "incidents": db.incidents(50),
        "events": db.events(60),
        "clients": hub.count,
    }


@app.get("/api/stats")
def api_stats() -> dict:
    return db.stats()


@app.get("/api/events")
def api_events(limit: int = 200) -> list[dict]:
    return db.events(limit)


@app.get("/api/events/suppressed")
def api_suppressed(limit: int = 100) -> list[dict]:
    """Event yang disaring sebagai aktivitas jinak, untuk audit, bukan alert."""
    return db.suppressed_events(limit)


@app.get("/api/incidents")
def api_incidents(limit: int = 100) -> list[dict]:
    return db.incidents(limit)


@app.get("/api/incidents/{inc_id}")
def api_incident(inc_id: int) -> dict:
    inc = db.incident(inc_id)
    if not inc:
        raise HTTPException(status_code=404, detail="incident tidak ditemukan")
    inc["events"] = db.events_for_incident(inc_id)
    return inc


@app.get("/api/attacker/{ip}")
def api_attacker(ip: str) -> dict:
    events = db.query("SELECT * FROM events WHERE src_ip = ? ORDER BY id DESC LIMIT 200", (ip,))
    incs = db.query("SELECT * FROM incidents WHERE src_ip = ? ORDER BY id DESC LIMIT 50", (ip,))
    return {"ip": ip, "event_count": len(events), "events": events, "incidents": incs}


@app.post("/api/reset")
async def api_reset(x_polaris_token: str | None = Header(default=None)) -> dict:
    _check_token(x_polaris_token)
    db.clear_all()
    await hub.broadcast("snapshot", _snapshot())
    return {"ok": True}


@app.get("/api/export/incidents")
def export_incidents() -> dict:
    """Artefak forensics-ready (docs/04 -> Output Artefak)."""
    out = db.incidents(1000)
    return {"generated": engine.now_ts(), "count": len(out), "incidents": out}


# Dashboard statis (vanilla JS) dilayani di root
if os.path.isdir(DASHBOARD_DIR):
    app.mount("/", StaticFiles(directory=DASHBOARD_DIR, html=True), name="dashboard")
else:  # pragma: no cover
    @app.get("/")
    def _no_dashboard() -> dict:
        return {"error": "dashboard dir tidak ditemukan", "expected": DASHBOARD_DIR}
