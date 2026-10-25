# POLARIS: Deception-Based Early Warning untuk Jaringan IT/OT

> Nama kerja: **POLARIS**. Alternatif: CanaryOne, Tripwire, Sanca.

Purwarupa dan dokumentasi untuk **Kartika Cyber Hackathon 2026** (PUSSIBERAD x Codepolitan).

---

## One-liner

> "Firewall nahan yang ketahuan. **POLARIS** nangkep yang ngumpet: karena yang
> nyentuh umpan kita, mustahil orang normal. Nol false positive by design."

---

## Apa ini?

Sistem **peringatan dini berbasis tipuan (deception)** yang ditanam di server
jaringan IT/OT. Kita tanam *umpan* berikut, yang **tidak akan pernah disentuh
pengguna sah**:

| Jenis umpan | Bentuk di purwarupa |
|---|---|
| Decoy port | 32 listener palsu (SSH, MySQL, Redis, RDP, SMB, plus port spray) |
| Web decoy | Path admin/recon populer yang membalas konten palsu |
| Honeytoken file | 11 berkas kredensial/config/dump palsu, dipantau inotify |
| Canary credential | Kredensial umpan yang memanggil URL beacon bila dipakai |
| Decoy OT/ICS | Modbus/TCP di port 502 dan panel HMI di port 8080 |

Ada yang menyentuh umpan = *intent terbukti*. Hasilnya alert real-time, incident
yang terkorelasi, dan pemetaan MITRE ATT&CK.

Ini bukan IDS anomali yang penuh false positive. Deteksinya **biner**: disentuh
berarti bukti.

---

## Kenapa menang

1. **Nol false positive by design**: argumen terkuat dibanding peserta lain yang membangun IDS berbasis ML.
2. **Atribusi tool penyerang**: pola koneksi dipakai untuk menebak alat yang dipakai (nmap, masscan, hydra).
3. **Korelasi, bukan banjir alert**: ratusan event mentah menjadi satu incident dengan skor dan bukti.
4. **Siap IT/OT**: decoy Modbus dan HMI, dipetakan ke ATT&CK for ICS.
5. **On-prem dan ramah air-gap**: nol cloud, nol dependensi eksternal di agen, SQLite sebagai penyimpanan.
6. **Pemasangan satu baris**: installer plus service systemd.

---

## Yang Sudah Jalan

Purwarupa ini nyata dan bisa dijalankan ulang, bukan mockup. Angka di bawah
berasal dari satu kali run `demo/demo.sh` yang hasilnya dicatat lengkap di
[`docs/14-bukti-demo.md`](docs/14-bukti-demo.md).

| Metrik | Nilai |
|---|---|
| Listener port umpan | 32 (7 decoy bernama, 24 port spray, 1 web decoy) |
| Berkas honeytoken | 11, dipantau lewat inotify |
| Decoy OT/ICS | 2 (Modbus/TCP, HMI) |
| Interaksi umpan pada satu run demo | 234 event |
| Aktivitas jinak yang disaring | 2 event (tetap tersimpan dan bisa diaudit) |
| Incident hasil korelasi | 1, severity CRITICAL, skor 410 |
| Teknik ATT&CK terpetakan | 12, termasuk 4 teknik ATT&CK for ICS |
| Atribusi tool | nmap, keyakinan 0.86 |
| False positive | 0 |
| Dependensi eksternal di agen | 0 (hanya pustaka standar Go) |

Yang **belum** dikerjakan, dan disebut apa adanya: S7comm, DNP3, dan ringkasan
berbasis LLM masih di roadmap. Ringkasan incident di purwarupa memakai templat
deterministik yang diisi fakta dari event.

---

## Quick Start

### Prasyarat

- Go 1.22 atau lebih baru (untuk membangun agen)
- Python 3.10 atau lebih baru
- Linux, karena agen memakai inotify melalui `syscall`

### Jalankan dari sumber

```bash
git clone https://github.com/arill2/kartika-cyber-hackathon.git
cd kartika-cyber-hackathon

# 1. bangun agen (satu binary, tanpa dependensi eksternal)
cd agent && go build -o ../bin/polaris-agent . && cd ..

# 2. siapkan collector
python3 -m venv .venv
.venv/bin/pip install -r collector/requirements.txt

# 3. jalankan collector + agen
bash scripts/dev-up.sh

# 4. buka dashboard
#    http://127.0.0.1:8787
```

Hentikan dengan `bash scripts/dev-down.sh`.

### Pasang sebagai agen di server lain

```bash
# dari berkas yang sudah dibangun
bash installer/install.sh --local ./bin/polaris-agent

# atau satu baris dari GitHub (butuh release asset bin/polaris-agent-<os>-<arch>)
curl -fsSL https://raw.githubusercontent.com/arill2/kartika-cyber-hackathon/main/installer/install.sh | bash
```

Installer menaruh binary di `/usr/local/bin/polaris-agent`, menulis konfigurasi
ke `~/.polaris/agent.env`, dan mencetak unit systemd siap pakai.

### Menjalankan demo serangan

```bash
# otomatis, jeda tetap, cocok untuk rekaman video
AUTO=1 PAUSE=3 bash demo/demo.sh

# manual, tekan Enter tiap langkah
bash demo/demo.sh
```

Butuh `nmap`, `hydra`, `nc`, dan `python3` di mesin yang sama. Semua lalu lintas
datang dari `127.0.0.1`, jadi IP penyerang yang muncul adalah alamat itu sendiri.
Lihat bagian Batasan.

---

## API Collector

Semua endpoint selain healthz membutuhkan header `X-Polaris-Token`.

| Metode | Endpoint | Fungsi |
|---|---|---|
| GET | `/healthz` | cek kesehatan collector |
| POST | `/api/ingest` | terima event dari agen |
| GET | `/beacon/{token}` | callback honeytoken URL |
| WS | `/api/ws` | snapshot dan stream event/incident ke dashboard |
| GET | `/api/events` | daftar event mentah |
| GET | `/api/events/suppressed` | daftar event yang disaring ke jalur terpisah |
| GET | `/api/incidents` | daftar incident hasil korelasi |
| GET | `/api/incidents/{id}` | detail incident lengkap dengan bukti |
| GET | `/api/attacker/{ip}` | profil satu alamat sumber |
| GET | `/api/stats` | ringkasan angka |
| GET | `/api/export/incidents` | ekspor incident untuk forensik |
| POST | `/api/reset` | kosongkan state sebelum demo |

### Konfigurasi penting

| Variabel | Default | Arti |
|---|---|---|
| `POLARIS_TOKEN` | `polaris-dev-token` | token autentikasi agen dan API |
| `POLARIS_BIND_PORT` | `8787` | port collector dan dashboard |
| `POLARIS_WEB_PORT` | `80` | port web decoy di agen |
| `POLARIS_DECOY_DIR` | `~/.polaris/decoy` | lokasi berkas honeytoken |
| `POLARIS_DB` | `~/.polaris/polaris.db` | berkas SQLite |
| `POLARIS_ALLOWLIST_IPS` | kosong | IP infrastruktur yang tidak pernah menjadi incident |
| `POLARIS_SUPPRESS_PATTERNS` | health check umum | pola aktivitas jinak yang dipindah ke jalur terpisah |
| `POLARIS_TELEGRAM_TOKEN` + `POLARIS_TELEGRAM_CHAT` | kosong | mengaktifkan alert Telegram |
| `POLARIS_WEBHOOK_URL` | kosong | mengaktifkan webhook generik untuk SOC/SOAR |

---

## Struktur Repo

```
kartika-cyber-hackathon/
├── agent/              # sensor Go, satu binary, hanya pustaka standar
├── collector/          # FastAPI: ingest, engine deteksi, korelasi, alert
│   └── app/            # main.py, engine.py, db.py, mitre.py, alerts.py, hub.py
├── dashboard/          # dashboard vanilla JS (index.html, style.css, app.js)
├── demo/               # demo.sh + skrip serangan pendukung
├── installer/          # install.sh (satu baris + unit systemd)
├── scripts/            # dev-up.sh, dev-down.sh
├── docs/               # dokumentasi teknis 00 sampai 14
├── site/               # landing page untuk Link Karya (GitHub Pages)
├── submission/         # slide deck, thumbnail, proposal
├── screenshot/         # tangkapan layar untuk form submission
├── DESIGN.md           # arah desain UI + tabel referensi + catatan perubahan
└── README.md
```

---

## Deliverables Submission

Peta langsung ke lima kolom form Codepolitan:

| Kolom form | Isi | Berkas |
|---|---|---|
| Link Karya/Project | landing page publik lewat GitHub Pages | `site/index.html` |
| Video demo | rekaman 3 sampai 5 menit | naskah di [`docs/13-video-script.md`](docs/13-video-script.md) |
| Slide penjelasan | 14 slide, PDF 16:9 | `submission/POLARIS_Slides_Kartika_2026.pdf` |
| Thumbnail 1200x630 | PNG, di bawah 500KB | `submission/thumbnail-1200x630.png` |
| Screenshot (1 sampai 5) | dashboard, detail incident, tampilan mobile | `screenshot/01-dashboard.png`, `02-incident-detail.png`, `03-mobile.png` |

Proposal lengkap ada di `submission/POLARIS_Proposal_Kartika_2026.pdf`.

---

## Bukti dan Kejujuran Angka

Aturan yang kami pegang: setiap angka yang tampil di dashboard, landing page,
slide, atau dokumen ini harus bisa dilacak ke satu sumber yang nyata.

- Rekaman run lengkap, keluaran API mentah, dan tabel teknik ATT&CK ada di
  [`docs/14-bukti-demo.md`](docs/14-bukti-demo.md).
- Bilah angka di landing page menyebutkan secara terang bahwa data berasal dari
  satu kali run demo.
- Tidak ada testimoni, tidak ada logo klien, dan tidak ada klaim kepatuhan
  standar apa pun di seluruh materi.

---

## Batasan yang Kami Akui

Dokumen ini sengaja menyebut batasnya di depan, bukan menyembunyikannya.

1. **Sensor dan penyerang satu host pada demo.** Karena itu sumber serangan
   tercatat sebagai `127.0.0.1`. Pada deployment nyata, agen dipasang di host
   target dan penyerang datang dari alamat lain.
2. **Atribusi tool berbasis pola, bukan bukti pasti.** Angka keyakinan 0.86
   berarti pola koneksi cocok dengan ciri nmap, bukan berarti nmap pasti.
3. **Honeytoken file tidak bisa mengatribusi pembaca di tingkat proses.**
   inotify hanya melaporkan bahwa berkas dibaca, bukan lewat proses apa, jadi
   `src_ip` untuk event jenis ini dilaporkan sebagai `127.0.0.1`.
4. **Decoy OT adalah simulasi protokol.** Modbus dan HMI di sini meniru banner
   dan respons dasar, bukan perangkat PLC sungguhan. Simulasi ini tidak boleh
   dipasang di segmen OT produksi tanpa pengujian lapangan.
5. **Nol false positive berlaku pada umpan, bukan pada seluruh ruang deteksi.**
   Klaimnya: apa pun yang menyentuh umpan memang menyentuh umpan. Itu pernyataan
   tentang umpan, bukan tentang seluruh jaringan.
6. **Ringkasan incident deterministik.** Belum memakai model bahasa.
7. **Alert Telegram dan webhook sudah ada di kode** tetapi belum diuji dengan
   token sungguhan, jadi belum diklaim teruji.
8. **Belum ada autentikasi multi-pengguna di dashboard.** Ini alat satu operator.

---

## Hackathon Context

| Item | Detail |
|---|---|
| Penyelenggara | PUSSIBERAD (Pusat Siber TNI AD) + Codepolitan |
| Kategori | **02 DEFENSIVE SHIELD** (Penangkalan) |
| Format | Online 4 minggu, 10 finalis presentasi di Jakarta |
| Deadline submit | **15 November 2026** |
| Final | **24 November 2026**, Hotel Aston Kartika, Jakarta |
| Tim | 2 sampai 3 orang (individu diperbolehkan) |
| Hadiah | Rp 100,7 juta + Golden Ticket Bintara Siber TNI AD |

---

## Index Dokumentasi

| File | Isi |
|---|---|
| [00-overview.md](docs/00-overview.md) | Ringkasan ide, problem, solusi, kenapa menang |
| [01-proposal-solusi.md](docs/01-proposal-solusi.md) | Draft proposal submission |
| [02-arsitektur.md](docs/02-arsitektur.md) | Arsitektur teknis, komponen, data flow, deployment |
| [03-decoy-honeytoken.md](docs/03-decoy-honeytoken.md) | Taksonomi umpan (decoy port, file, cred, URL, web) |
| [04-engine-deteksi.md](docs/04-engine-deteksi.md) | Fingerprint, korelasi, scoring, ringkasan |
| [05-ot-ics-decoy.md](docs/05-ot-ics-decoy.md) | Decoy OT/ICS (Modbus, HMI, plus roadmap S7 dan DNP3) |
| [06-tech-stack.md](docs/06-tech-stack.md) | Stack final dan justifikasinya |
| [07-roadmap.md](docs/07-roadmap.md) | Roadmap mingguan dan backlog |
| [08-alignment-penilaian.md](docs/08-alignment-penilaian.md) | Pemetaan ke 5 kriteria penjurian |
| [09-demo-script.md](docs/09-demo-script.md) | Script demo live dan struktur video |
| [10-pitch-killer.md](docs/10-pitch-killer.md) | Pitch, analogi, antisipasi pertanyaan juri |
| [11-submission-checklist.md](docs/11-submission-checklist.md) | Checklist deliverable dan deadline |
| [12-mitre-mapping.md](docs/12-mitre-mapping.md) | Tabel pemetaan MITRE ATT&CK |
| [13-video-script.md](docs/13-video-script.md) | Naskah rekaman video demo, dipetakan ke `demo.sh` |
| [14-bukti-demo.md](docs/14-bukti-demo.md) | Keluaran run nyata, angka per angka |

Arah desain UI ada di [DESIGN.md](DESIGN.md): palet, tipografi, aturan salinan,
tabel referensi, dan catatan perubahan.

---

## Status

- [x] Riset aturan dan kriteria penjurian
- [x] Konsep dan arsitektur
- [x] Agen Go: 32 listener umpan, 11 honeytoken, decoy Modbus dan HMI
- [x] Collector dan engine: ingest, fingerprint, korelasi, MITRE, penyaringan
- [x] Dashboard: state kosong, memuat, error, keyboard, deep link, responsif
- [x] Demo end-to-end terbukti, 234 event menjadi 1 incident, nol false positive
- [x] Installer satu baris dan unit systemd
- [x] Landing page, slide 14 halaman, thumbnail 1200x630, screenshot
- [x] Naskah video dan dokumen bukti
- [ ] Rekam video demo (butuh perekam layar, ffmpeg tidak tersedia di host ini)
- [ ] Deploy `site/` ke GitHub Pages
- [ ] Register tim, ikut webinar pembekalan, submit ke Codepolitan
