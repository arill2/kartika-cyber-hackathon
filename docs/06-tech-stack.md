# 06 — Tech Stack

Filosofi pemilihan: **cepat dibangun (solo), kredibel, mudah di-deploy (bobot 15%)**.

## 1. Ringkasan

| Lapisan | Pilihan | Alasan |
|---|---|---|
| Agent | **Go** | Single binary statis, cross-compile, concurrency, low overhead |
| Collector | **Python + FastAPI** | Cepat dikembangkan, asyncio, ekosistem luas |
| Engine | **Python** | Sama dengan collector, analitik mudah |
| DB | **SQLite** | Embedded, nol konfigurasi, cocok on-prem/air-gap |
| Dashboard | **FastAPI + WebSocket + vanilla JS** (atau React bila sempat) | Ringan, live, tanpa build heavy |
| Alert | **Telegram Bot API** + generic webhook | Instan, demo-able, integrasi SOAR |
| Installer | **Bash one-liner** | Pameran "kelayakan implementasi" |
| AI (opsional) | API LLM / model lokal | AI summarizer narasi incident |

## 2. Justifikasi

### 2.1 Kenapa Go untuk Agent
- **Single static binary** → install = copy file, tidak ada dependency runtime.
- **Cross-compile** mudah (`GOOS`/`GOARCH`) → Linux/Windows/ARM.
- **Concurrency native** → puluhan listener decoy tanpa berat.
- **Footprint kecil & cepat** → argumen "low overhead" di depan juri.
- **Networking stdlib kuat** → listener TCP/UDP & HTTP gampang.

Alternatif: Python + PyInstaller (lebih cepat ditulis, tapi binary lebih berat &
rawan masalah packaging). Go tetap rekomendasi utama.

### 2.2 Kenapa Python untuk Collector & Engine
- Kecepatan pengembangan untuk logika deteksi, korelasi, & integrasi.
- FastAPI: cepat, async, auto docs (Swagger) → poin dokumentasi.
- Ekosistem data/ML bila AI summarizer dikembangkan.

> Bila ingin **satu bahasa** demi kecepatan solo: seluruh stack bisa Python
> (agent pakai PyInstaller). Trade-off: agent kurang "produk". Rekomendasi tetap Go.

### 2.3 Kenapa SQLite
- Nol server DB → selaras dengan "mudah diterapkan / air-gap".
- Cukup untuk skala demo & satuan.
- Migrasi ke PostgreSQL mudah bila naik skala (jelaskan sebagai roadmap).

### 2.4 Kenapa Telegram
- API bot simpel, gratis, **real-time**.
- Demo live "alert masuk HP" sangat meyakinkan.
- Webhook generik → jalur integrasi ke SOC/SOAR TNI AD.

## 3. Struktur Repo (usulan)

```
polaris/
├── agent/                 # Go
│   ├── main.go
│   ├── decoy/
│   │   ├── ports.go       # decoy port listeners
│   │   ├── files.go       # honeytoken files + inotify
│   │   ├── web.go         # web decoy paths
│   │   └── ot_modbus.go   # decoy Modbus/TCP
│   ├── sender/            # callback + local buffer
│   └── go.mod
├── collector/             # Python FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── ingest.py
│   │   ├── engine/
│   │   │   ├── fingerprint.py
│   │   │   ├── correlate.py
│   │   │   ├── mitre.py
│   │   │   └── severity.py
│   │   ├── alerts/
│   │   │   ├── telegram.py
│   │   │   └── webhook.py
│   │   └── db.py
│   └── requirements.txt
├── dashboard/             # static web
│   ├── index.html
│   ├── app.js
│   └── style.css
├── installer/
│   └── install.sh
├── docs/                  # dokumen ini + dokumentasi teknis
└── README.md
```

## 4. Dependensi Minimal

**Go agent:** stdlib utama; `fsnotify` (inotify), `net`.
**Python collector:** `fastapi`, `uvicorn`, `httpx`, `pydantic`, `aiosqlite`.
**Opsional:** `python-telegram-bot` atau langsung HTTP ke Bot API.

## 5. Prinsip Teknis

- **Structured logging (JSON)** untuk audit & evidence.
- **Config via file/env** → mudah di-deploy di satuan berbeda.
- **Auth token per-agent** saat callback.
- **No destructive action** secara default.
- **Graceful degradation** → buffer lokal saat Collector down.

## 6. Alternatif yang Dipertimbangkan

| Alternatif | Kenapa tidak dipilih (untuk hackathon solo) |
|---|---|
| Full Rust | Terlalu lama dikembangkan & diperbaiki |
| Kubernetes-native | Overkill, tidak cocok air-gap demo |
| Cloud SIEM integration | Bertentangan dengan kebutuhan air-gap |
| Heavy ML anomaly | Sumber false positive, sulit didemokan live |
