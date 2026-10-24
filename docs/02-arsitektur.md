# 02 — Arsitektur Teknis

## 1. Diagram Tingkat Tinggi

```
┌──────────────────────────────────────────────────────────────┐
│                    NODE TARGET (server IT/OT)                 │
│                                                                │
│   ┌───────────────────────────────────────────────────┐       │
│   │              AGENT POLARIS (single binary)         │       │
│   │                                                    │       │
│   │  [Decoy Ports]     [Honeytoken Files]              │       │
│   │   fake-ssh:2222     .env, .aws/credentials         │       │
│   │   fake-mysql:33060  backup_db.sql, id_rsa_bak      │       │
│   │   fake-redis:6379                                  │       │
│   │   decoy-modbus:502  [Canary Credentials]           │       │
│   │   decoy-hmi:8080    fake api tokens                │       │
│   │                                                    │       │
│   │  [Web Decoy Paths]  [Honeytoken URLs]              │       │
│   │   /.env /.git/...    unique beacon URLs            │       │
│   │                                                    │       │
│   │              ▼  event  ▲ akar akar                 │       │
│   │        ┌──────────────────────┐                    │       │
│   │        │  Local Event Buffer  │  (tahan offline)   │       │
│   │        └──────────┬───────────┘                    │       │
│   └───────────────────┼────────────────────────────────┘       │
└───────────────────────┼────────────────────────────────────────┘
                        │ HTTPS callback (lokal, retry bila putus)
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                    COLLECTOR (FastAPI)                        │
│   ingest event → validasi → simpan (SQLite)                   │
└───────────────────────┬──────────────────────────────────────┘
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                    DETECTION ENGINE                           │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│   │ Fingerprint  │  │ Correlation  │  │ MITRE ATT&CK     │   │
│   │ attacker tool│  │ → incident   │  │ mapping          │   │
│   └──────────────┘  └──────────────┘  └──────────────────┘   │
│   ┌──────────────────────────────────────────────────────┐   │
│   │ Severity scoring (tier + jenis + jumlah)              │   │
│   └──────────────────────────────────────────────────────┘   │
│   ┌──────────────────────────────────────────────────────┐   │
│   │ AI Summarizer (opsional) → narasi incident            │   │
│   └──────────────────────────────────────────────────────┘   │
└───────┬───────────────────────────────┬──────────────────────┘
        ▼                               ▼
┌───────────────────┐          ┌───────────────────────────────┐
│  DASHBOARD        │          │  ALERT CHANNELS               │
│  live feed (WS)   │          │  Telegram / Webhook / Discord │
│  incident cards   │          └───────────────────────────────┘
│  attacker profile │
│  timeline         │
└───────────────────┘
```

## 2. Komponen

### 2.1 Agent
- **Bentuk:** single binary statis (lihat `06-tech-stack.md`).
- **Tugas:**
  - Membuka *listener* decoy port.
  - Menanam honeytoken file & memantau aksesnya (inotify `IN_ACCESS`/`IN_OPEN`).
  - Menyediakan decoy web path (handler HTTP ringan).
  - Mengelola honeytoken URL & canary credential.
  - Mengirim event ke Collector (HTTPS/lokal), dengan **buffer lokal** bila Collector down.
- **Prinsip:** low overhead, tidak menyentuh data produksi, tidak pernah destruktif.

### 2.2 Collector
- **Bentuk:** FastAPI service.
- **Tugas:** validasi & ingest event, simpan ke SQLite, teruskan ke engine.
- **Endpoint utama:**
  - `POST /ingest` — terima event dari agent.
  - `GET  /beacon/{token}` — honeytoken URL callback.
  - `WS   /live` — stream event/incident ke dashboard.

### 2.3 Detection Engine
- Fingerprinting tool penyerang.
- Korelasi event → incident.
- MITRE ATT&CK mapping.
- Severity scoring.
- AI summarizer (opsional).

Detail: `04-engine-deteksi.md`.

### 2.4 Dashboard
- Live feed via WebSocket.
- Kartu incident (severity, sumber IP, jenis, MITRE, timeline).
- Profil penyerang (IP, geo opsional, dugaan tool, riwayat).
- Halaman detail incident + evidence.

### 2.5 Alert Channels
- Telegram Bot (instan, demo-able).
- Generic webhook (integrasi SOC/SOAR).
- Discord (opsional).

## 3. Alur Data

```
1. Attacker menyentuh umpan (port/file/URL/cred/OT).
2. Agent menangkap event (+ metadata: src IP, port, payload, timestamp, koneksi).
3. Agent kirim ke Collector (retry + buffer bila offline).
4. Collector simpan & teruskan ke Engine.
5. Engine: fingerprint → cari/ciptakan incident → hitung severity → map MITRE.
6. Incident muncul di Dashboard (live) + Alert dikirim (Telegram/webhook).
7. (Opsional) AI summarizer menambah narasi.
8. Evidence tersimpan untuk investigasi forensik.
```

## 4. Model Deployment

### 4.1 Model A — Standalone (demo)
Agent + Collector + Dashboard di satu mesin. Cocok untuk demo hackathon & satuan kecil.

### 4.2 Model B — Distributed (produksi)
Banyak Agent di banyak node → 1 Collector/Engine pusat → Dashboard SOC.
Cocok untuk jaringan satuan dengan banyak server.

### 4.3 Model C — Air-gapped
Semua komponen on-prem tanpa internet. Alert via webhook ke SOAR internal
atau dashboard lokal. **Ini pembeda utama untuk TNI AD.**

## 5. Model Keamanan

- Event dikirim melalui koneksi terautentikasi (token per-agent).
- Collector memvalidasi payload & membatasi rate.
- Honeytoken credential menggunakan nilai *inert* (tidak memberikan akses nyata).
- Agent berjalan dengan hak minimal (tidak perlu root kecuali untuk port <1024;
  gunakan port tinggi atau capability `CAP_NET_BIND_SERVICE`).
- Tidak ada aksi destruktif otomatis secara default (auto-block bersifat opt-in).

## 6. Skalabilitas

- Agent stateless terhadap Collector → mudah di-scale horizontal.
- Collector stateless (state di SQLite/PG) → bisa multi-instance di belakang LB.
- Korelasi berbasis window waktu → bisa dipartisi per-tenant/satuan.

## 7. Reliability

- Buffer lokal di agent → tidak kehilangan event saat Collector down.
- Retry dengan backoff.
- Health check agent & collector.
- Logging terstruktur (JSON) untuk audit.
