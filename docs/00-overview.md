# 00 — Overview

## 1. Problem Statement

Pertahanan siber modern menghadapi tiga masalah struktural:

1. **Alert fatigue.** SIEM/IDS tradisional menghasilkan ribuan alert, mayoritas
   false positive. Analis kewalahan, alert penting tenggelam di noise.
2. **Serangan yang lolos perimeter.** Attacker yang berhasil masuk (initial
   access) bergerak *stealth* — recon internal, lateral movement, credential
   access. Perimeter device tidak lihat ini karena sudah di dalam.
3. **Konteks militer IT/OT.** Jaringan TNI AD banyak yang **terisolasi/air-gap**
   dan mencampur **IT + OT/ICS** (SCADA, PLC, HMI). Solusi berbasis cloud/threat-intel
   eksternal tidak jalan di sana.

## 2. Insight Kunci

> Titik lemah deteksi klasik adalah **mencoba membedakan "normal" vs "mencurigakan"**.
> Itu inherently probabilistic → penuh false positive.

**Pendekatan kita: balik logikanya.** Jangan tebak. Tanam sesuatu yang **secara
desain mustahil disentuh pengguna sah**. Interaksi dengan umpan = intent
terbukti, bukan tebakan. Deteksi jadi **binary & high-confidence**.

Ini *deception defense* — doktrin yang sudah lama dikenal di dunia militer,
sekarang kita bawa ke level teknis otomatis.

## 3. Solusi: POLARIS

Sistem deployment ke server yang:

- **Menanam umpan** di titik yang menarik bagi penyerang (credential, config, port, panel admin, OT device).
- **Mendeteksi interaksi** dengan umpan → konfirmasi kehadiran penyerang.
- **Fingerprint** tool yang dipakai attacker (nmap, masscan, hydra, curl, dsb).
- **Korelasi** event menjadi **incident** (bukan alert raw berserakan).
- **Pemetaan MITRE ATT&CK** + evidence forensics-ready.
- **Alert real-time** (Telegram/webhook) + **dashboard live**.
- **Opsional AI summarizer** mengubah alert jadi narasi "apa yang terjadi & kenapa penting".

## 4. Kenapa Berbeda

| IDS/IPS Konvensional | POLARIS |
|---|---|
| Deteksi probabilistik (anomali) | Deteksi deterministik (umpan) |
| Ribuan alert, banyak FP | Sedikit alert, hampir nol FP |
| Perlu tuning threshold | Tidak perlu tuning |
| Bergantung pattern/signature | Bergantung *tidak adanya* user sah di umpan |
| Butuh cloud/threat-intel | Full on-prem, air-gap friendly |
| IT saja | IT **+ OT/ICS** |

## 5. Kategori & Kesesuaian

Masuk kategori **02 DEFENSIVE SHIELD (Penangkalan)** — contoh resmi panitia:
*Smart IDS/IPS, Threat Intelligence Platform, Automated Incident Response, Zero-Day Detection*.
POLARIS = Smart IDS/IPS + Automated Incident Response + Zero-Day Detection (via deception).

## 6. Prinsip Desain

1. **Zero false positive by design** — umpan tidak boleh tersentuh operasi normal.
2. **Deterministic first** — sinyal biner sebelum heuristic.
3. **Evidence-disciplined** — setiap alert punya bukti (request, timestamp, artifact, hash).
4. **On-prem / air-gap friendly** — nol dependensi cloud.
5. **Low overhead** — agent ringan, tidak mengganggu beban server.
6. **Deploy 1 baris** — kemudahan implementasi (bobot 15%).

## 7. Target Dampak

- SOC TNI AD mendapat **early warning** yang actionable, bukan noise.
- **Detection engineering** yang terukur (MITRE coverage).
- **Forensics-ready** — saat incident lanjut ke investigasi, evidence sudah lengkap.
- Dapat diperluas ke **segmen OT/ICS** tanpa arsitektur baru.
