"""Alert channels: Telegram + generic webhook (docs/02 -> Alert Channels).

Dijalankan di thread terpisah agar tidak memblokir event loop FastAPI.
Dependency-free (urllib) supaya tetap jalan di jaringan air-gap/internal.
"""
import json
import logging
import threading
import urllib.parse
import urllib.request

from .config import cfg

log = logging.getLogger("polaris.alerts")

SEV_EMOJI = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}


def _post_json(url: str, body: dict, timeout: int = 6) -> None:
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
    except Exception as exc:  # pragma: no cover - jaringan
        log.warning("alert gagal dikirim ke %s: %s", url, exc)


def _telegram(text: str) -> None:
    url = f"https://api.telegram.org/bot{cfg.TELEGRAM_TOKEN}/sendMessage"
    body = urllib.parse.urlencode({
        "chat_id": cfg.TELEGRAM_CHAT,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(url, data=body)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            resp.read()
    except Exception as exc:  # pragma: no cover
        log.warning("telegram gagal: %s", exc)


def format_incident(inc: dict) -> str:
    emoji = SEV_EMOJI.get(inc.get("severity", ""), "⚪")
    mitre = inc.get("mitre") or []
    if isinstance(mitre, str):
        try:
            mitre = json.loads(mitre)
        except Exception:
            mitre = []
    tags = " ".join(f"#{t['id'].replace('.', '')}" for t in mitre[:5])
    return (
        f"{emoji} <b>POLARIS INCIDENT #{inc['id']}</b> | {inc.get('severity')}\n"
        f"<b>Sumber:</b> <code>{inc.get('src_ip')}</code>\n"
        f"<b>Judul:</b> {inc.get('title')}\n"
        f"<b>Tool terduga:</b> {inc.get('tool_guess') or 'unknown'} "
        f"({int((inc.get('tool_conf') or 0) * 100)}%)\n"
        f"<b>Event:</b> {inc.get('event_count')}  ·  <b>Skor:</b> {inc.get('score')}\n"
        f"<b>MITRE:</b> {tags}\n\n{inc.get('summary') or ''}"
    )


def dispatch(incident: dict) -> None:
    """Kirim alert tanpa memblokir. Aman dipanggil dari thread/async."""
    tg_text = format_incident(incident)
    webhook_body = {"source": "polaris", "type": "incident", "incident": incident}

    def _work() -> None:
        if cfg.telegram_enabled():
            _telegram(tg_text)
        if cfg.WEBHOOK_URL:
            _post_json(cfg.WEBHOOK_URL, webhook_body)
        log.info("ALERT %s incident#%s ip=%s", incident.get("severity"), incident.get("id"), incident.get("src_ip"))

    threading.Thread(target=_work, daemon=True).start()
