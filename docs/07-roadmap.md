# 07: Roadmap & Backlog (sampai 15 Nov 2026)

Asumsi: solo, ~3 minggu efektif. Deadline submit **15 November 2026**.

---

## Ringkasan Mingguan

| Minggu | Tanggal | Target | Status |
|---|---|---|---|
| W0 | 24–27 Okt | Register + ikut Webinar 2 + blueprint | ⬜ |
| W1 | 28 Okt–3 Nov | **MVP end-to-end jalan** | ⬜ |
| W2 | 4–10 Nov | Engine deteksi + OT decoy + dashboard | ⬜ |
| W3 | 11–15 Nov | Installer + dokumentasi + video + slide + submit | ⬜ |

---

## W0: Fondasi (24–27 Okt)

- [ ] Register tim/individu di Codepolitan (kategori Defensive Shield, isi ide)
- [ ] **Ikut Webinar Pembekalan 2 (27 Okt)**: catat insight TNI AD/mentor
- [ ] Sesuaikan framing berdasarkan webinar
- [ ] Kunci nama final + stack
- [ ] Setup repo + environment (Go, Python)

---

## W1: MVP End-to-End (28 Okt–3 Nov)

**Goal: colok umpan → alert Telegram bunyi.**

- [ ] **Agent (Go) skeleton**
  - [ ] Struktur proyek + config
  - [ ] 1 decoy port listener (fake SSH 2222) → log koneksi
  - [ ] Sender: callback ke Collector + local buffer
- [ ] **Collector (FastAPI) skeleton**
  - [ ] `POST /ingest` + validasi + SQLite
  - [ ] Model event dasar
- [ ] **Alert Telegram**
  - [ ] Bot + kirim pesan saat event masuk
- [ ] **Honeytoken file dasar**
  - [ ] Tanam file + inotify `IN_ACCESS` → event
- [ ] ✅ **Milestone: end-to-end works**

---

## W2: Otak Deteksi (4–10 Nov)

- [ ] **Multi decoy port** (SSH, MySQL, Redis) + banner palsu
- [ ] **Web decoy paths** (`/.env`, `/.git/config`, `/wp-admin`, ...)
- [ ] **Honeytoken URL** + endpoint `/beacon/{token}`
- [ ] **Canary credential** (format API token/AWS palsu)
- [ ] **Fingerprinting** tool attacker (heuristik nmap/masscan/hydra)
- [ ] **Correlation engine** → incident + severity scoring
- [ ] **MITRE ATT&CK mapping** (tabel di `12-mitre-mapping.md`)
- [ ] **Dashboard live** (WebSocket feed + kartu incident)
- [ ] **Decoy OT Modbus/TCP (502)** + decoy HMI web
- [ ] ✅ **Milestone: demo bisa dipamerkan penuh**

---

## W3: Polish & Submit (11–15 Nov)

- [ ] **1-line installer** (`curl -fsSL .../install.sh | bash`)
- [ ] **AI summarizer** (opsional, bila waktu cukup)
- [ ] **Dokumentasi teknis** lengkap (arsitektur, cara pakai, cara install)
- [ ] **Proposal solusi** final (dari `01-proposal-solusi.md`)
- [ ] **Video demo purwarupa** (3–5 menit)
- [ ] **Video presentasi** + **slide**
- [ ] **Rekam & latihan demo** (dry run minimal 2x)
- [ ] ✅ **SUBMIT sebelum 15 Nov**

---

## Backlog Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Waktu kurang | MVP tidak selesai | Kunci scope: port + file + alert dulu; OT belakangan |
| Go inotify ribet | Honeytoken file delay | Fallback: polling mtime + damon sederhana |
| Decoy OT kompleks | Delay | Modbus respons minimal dulu (cukup terima & log) |
| Demo gagal live | Nilai turun | Siapkan rekaman backup + dry run 2x |
| Fingerprint salah tebak | Kredibilitas | Tampilkan "unknown" + ciri, jangan asal klaim |
| Laptop server tidak siap | Blokir demo | Pakai VM/container lokal sebagai alternatif |

---

## Definition of Done (per fitur)

- Berjalan tanpa error di environment demo
- Menghasilkan event terstruktur (JSON) yang masuk ke Collector
- Tercatat di dashboard / alert
- Ada bukti (log/screenshot) untuk dokumentasi

---

## Catatan Strategi

- **Jangan remehkan dokumentasi (10%)**: proposal, tech doc, video, slide wajib rapi.
- **Video demo = syarat submit**: jangan dikerjakan di menit terakhir.
- Kalau W2 selesai lebih cepat, pakai sisa waktu untuk memperdalam **OT/ICS** dan
  **forensics evidence** (bidang juri Lettu Aghni).
