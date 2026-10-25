# LANJUTKAN: titik serah-terima proyek POLARIS

Dokumen ini ditulis pada **25 Oktober 2026** sebagai titik lanjut setelah jeda
ujian. Tujuannya satu: siapa pun yang membuka repo ini nanti, termasuk Anda
sendiri atau agen AI, bisa melanjutkan tanpa perlu membaca ulang seluruh riwayat
percakapan.

Kalau Anda hanya punya waktu membaca satu bagian, baca **Bagian 3**.

| Item | Nilai |
|---|---|
| Commit terakhir | `e75e66d` |
| Cabang | `main` (kode) dan `gh-pages` (landing page), keduanya sudah ter-push |
| Repositori | https://github.com/arill2/kartika-cyber-hackathon (publik) |
| Link Karya tayang | https://arill2.github.io/kartika-cyber-hackathon/ |
| Kondisi repo | bersih, tidak ada perubahan yang belum di-commit |
| Yang tertinggal | 2 langkah, keduanya butuh tangan manusia |

---

## 1. Ringkasan Proyek

**POLARIS** adalah sistem peringatan dini berbasis tipuan (deception) untuk
jaringan IT/OT, dibuat untuk Kartika Cyber Hackathon 2026 (PUSSIBERAD bersama
Codepolitan), kategori 02 Defensive Shield.

Inti idenya: alih-alih menebak mana lalu lintas yang mencurigakan, kita menanam
umpan yang tidak pernah disentuh pengguna sah. Ada yang menyentuh berarti bukti.
Deteksinya biner, dan di situ letak klaim nol false positive.

Purwarupanya **nyata dan berjalan**, bukan mockup. Agen Go menanam 32 listener
umpan, 11 berkas honeytoken yang dipantau inotify, canary credential ber-beacon,
serta decoy Modbus dan HMI. Collector FastAPI memproses event, menebak alat
penyerang, mengorelasikan semuanya menjadi satu incident, dan memetakan teknik
MITRE ATT&CK termasuk ATT&CK for ICS.

---

## 2. Yang Sudah Selesai

### 2.1 Perangkat lunak

| Komponen | Isi |
|---|---|
| `agent/` | Sensor Go, satu binary, hanya pustaka standar, inotify lewat `syscall` |
| `collector/` | FastAPI: ingest, engine deteksi, korelasi, scoring, MITRE, penyaringan, alert |
| `dashboard/` | Konsol vanilla JS: tiga keadaan, keyboard, deep link, responsif sampai 360 piksel |
| `installer/` | Pemasangan satu baris plus unit systemd |
| `scripts/` | `dev-up.sh` dan `dev-down.sh` |
| `demo/` | `demo.sh` plus `ssh_spray.py` dan `modbus_probe.py` |

### 2.2 Materi submission

| Kolom form | Berkas | Status |
|---|---|---|
| Link Karya | `site/` tayang di GitHub Pages | siap |
| Video demo | naskah di `docs/13-video-script.md` | **belum direkam** |
| Slide penjelasan | `submission/POLARIS_Slides_Kartika_2026.pdf`, 14 halaman, 16:9 | siap |
| Thumbnail 1200x630 | `submission/thumbnail-1200x630.png`, 120.674 byte | siap, di bawah 500KB |
| Screenshot | `screenshot/01-dashboard.png`, `02-incident-detail.png`, `03-mobile.png` | siap |

Slide dan proposal juga sudah disalin ke `site/files/` supaya bisa diunduh
langsung dari landing page. Salinan itu sudah dicek identik lewat md5sum.

### 2.3 Bukti dan pemeriksaan

- `docs/14-bukti-demo.md`: keluaran API mentah dari run nyata, angka per angka.
- `docs/15-antislop-gate.md`: laporan Delivery Gate, 50 butir, semuanya PASS.
- `docs/13-video-script.md`: naskah video, dipetakan langkah per langkah ke `demo/demo.sh`.
- `DESIGN.md`: arah desain, tabel referensi, dan catatan perubahan.

### 2.4 Angka hasil run yang sudah diverifikasi

Angka ini yang muncul di dashboard, landing page, slide, dan thumbnail. Jangan
ubah kecuali Anda benar-benar menjalankan ulang demo dan mencatat hasil baru.

| Metrik | Nilai |
|---|---|
| Listener port umpan | 32 |
| Berkas honeytoken | 11 |
| Decoy OT/ICS | 2 (Modbus, HMI) |
| Event mentah | 234 |
| Event disaring ke jalur terpisah | 2 |
| Incident hasil korelasi | 1 |
| Severity dan skor | CRITICAL, 410 |
| Atribusi tool | nmap, keyakinan 0.86 |
| Teknik ATT&CK | 12, termasuk 4 teknik ATT&CK for ICS |
| False positive | 0 |

---

## 3. Sisa Dua Langkah

### Langkah 1: Rekam video demo

Kabar baiknya: **alat perekam sudah terpasang di mesin ini**, `kazam` dan
`simplescreenrecorder`. `ffmpeg` memang tidak ada, tetapi untuk merekam layar
ffmpeg tidak dibutuhkan. Anda tidak perlu memasang apa pun.

#### 3.1.1 Nyalakan ulang tumpukannya

Kalau tumpukan sudah mati setelah ujian:

```bash
# dari akar repo
bash scripts/dev-up.sh

# pastikan tiga hal ini hidup
curl -s http://127.0.0.1:8787/healthz
curl -s http://127.0.0.1:8787/api/stats -H "X-Polaris-Token: polaris-dev-token"
# lalu buka http://127.0.0.1:8787 di browser
```

Kalau agen perlu dibangun ulang, `dev-up.sh` melakukannya sendiri. Pembangunan
manual:

```bash
cd agent && go build -o ../bin/polaris-agent . && cd ..
```

#### 3.1.2 Siapkan proses yang akan direkam

Buka **tiga jendela** dulu sebelum menekan rekam:

1. Terminal untuk demo. Perbesar (minimal 40 baris), font 14 sampai 16.
2. Browser tab 1: dashboard di `http://127.0.0.1:8787`.
3. Browser tab 2: berkas umpan `~/.polaris/decoy/.env` untuk segmen honeytoken.

#### 3.1.3 Mulai merekam

Pilih salah satu:

```bash
# opsi A, Kazam (GUI, paling mudah)
kazam
# pilih mode "Screencast", aktifkan mikrofon, jendela penuh, 30 fps, lalu Rekam

# opsi B, SimpleScreenRecorder (kontrol lebih detail)
simplescreenrecorder
# Video input: "Record the entire screen"
# Frame rate 30, Codec H.264, Container MP4
```

Simpan hasilnya ke `~/Videos/` atau ke `submission/video/`. Kalau folder
`submission/video/` belum ada, buat saja. Berkas video **tidak** ikut ke git
(folder itu tidak dilacak), dan memang sebaiknya begitu karena ukurannya besar
dan tempatnya di YouTube.

#### 3.1.4 Jalankan demonya

Setelah rekaman mulai, jalankan di terminal demo:

```bash
AUTO=1 PAUSE=3 bash demo/demo.sh
```

Jeda 3 detik per langkah. Kalau tempo terasa terlalu cepat untuk narasi, naikkan
jadi `PAUSE=5`. Kalau Anda ingin bicara dulu sebelum tiap langkah, pakai mode
manual `bash demo/demo.sh` dan tekan Enter sendiri.

Ikuti naskah di `docs/13-video-script.md`. Sembilan segmen, total target 4 menit
30 detik. Naskah itu sudah menyebutkan persis kapan pindah tab dan apa yang
diucapkan.

#### 3.1.5 Setelah rekaman

Nilai tiga hal ini pada berkas video:

- [ ] Durasi antara 3 dan 5 menit
- [ ] Suara jelas, tidak ada notifikasi atau panggilan yang nyasar
- [ ] Angka di layar cocok dengan keluaran nyata (`docs/14-bukti-demo.md`)

Kalau angka di video berbeda dari dokumen, **sebut angka yang di layar**, jangan
paksa angka dokumen. Yang tidak boleh berubah cuma tiga: satu incident, nol false
positive, dan nmap sebagai perkiraan tool.

Verifikasi cepat setelah rekaman:

```bash
curl -s http://127.0.0.1:8787/api/stats -H "X-Polaris-Token: polaris-dev-token"
curl -s http://127.0.0.1:8787/api/incidents -H "X-Polaris-Token: polaris-dev-token"
```

Terakhir, unggah ke YouTube dan setel **publik atau unlisted yang bisa dibuka
siapa pun tanpa login**. Juri harus bisa membukanya.

#### 3.1.6 Kalau ada yang gagal saat merekam

| Gejala | Tindakan |
|---|---|
| Collector mati | Hentikan rekaman, `bash scripts/dev-up.sh`, mulai dari langkah 0 |
| Dashboard tidak berubah | Tekan tombol refresh di dashboard, snapshot WebSocket akan dimuat ulang |
| `nmap` tidak ada | Lewati langkah 1 dan 2, sebutkan alasannya di narasi |
| `hydra` tidak ada | Jalankan saja `ssh_spray.py`, event brute force tetap muncul |
| Angka menumpuk dari run lama | Jalankan `curl -X POST` ke `/api/reset` dulu (itu langkah 0 di `demo.sh`) |

Jangan pernah merekam di atas data lama yang menumpuk. Selalu mulai dari
`/api/reset` supaya angka di layar bisa Anda jelaskan.

### Langkah 2: Isi form Codepolitan

Lima kolom, nilainya sudah siap semua:

| Kolom | Isi yang dimasukkan |
|---|---|
| Link Karya/Project | `https://arill2.github.io/kartika-cyber-hackathon/` |
| Video demo (YouTube) | tautan hasil Langkah 1 |
| Slide penjelasan | `https://arill2.github.io/kartika-cyber-hackathon/files/POLARIS_Slides_Kartika_2026.pdf` |
| Thumbnail 1200x630 | unggah `submission/thumbnail-1200x630.png` |
| Screenshot (1 sampai 5) | unggah `screenshot/01-dashboard.png`, `02-incident-detail.png`, `03-mobile.png` |

Proposal lengkap kalau form memintanya:
`https://arill2.github.io/kartika-cyber-hackathon/files/POLARIS_Proposal_Kartika_2026.pdf`

#### Soal tanggal deadline

Ada ketidaksesuaian yang perlu Anda cek sendiri di halaman resmi sebelum submit:

- `README.md` dan `docs/11-submission-checklist.md` menulis **15 November 2026**.
- Halaman Codepolitan saat terakhir diperiksa menulis **16 November 2026**.
- Checklist internal menyarankan submit **14 November 2026**.

Saran: pakai tanggal paling awal, **14 November 2026**, dan jangan menunggu hari
terakhir.

---

## 4. Cara Menyalakan Ulang dari Nol

Kalau mesin sudah restart atau venv hilang:

```bash
# 1. agen (Go, satu binary, tanpa dependensi eksternal)
cd agent && go build -o ../bin/polaris-agent . && cd ..

# 2. collector (Python)
python3 -m venv .venv
.venv/bin/pip install -r collector/requirements.txt

# 3. jalankan collector + agen
bash scripts/dev-up.sh

# 4. hentikan kalau sudah selesai
bash scripts/dev-down.sh
```

Kalau ingin menjalankan di mesin kedua sebagai sensor terpisah:

```bash
bash installer/install.sh --local ./bin/polaris-agent
# atau dari GitHub
curl -fsSL https://raw.githubusercontent.com/arill2/kartika-cyber-hackathon/main/installer/install.sh | bash
```

---

## 5. Jebakan Operasional

Bagian ini penting. Semuanya pernah benar-benar terjadi dan menghabiskan waktu.

1. **Jangan pakai `pkill -f "uvicorn collector.app.main"`.** Pola itu cocok
   dengan shell yang sedang menjalankannya, sehingga shell-nya sendiri yang mati
   (gejala: `Killed by SIGTERM`). Hentikan lewat berkas PID: `bash scripts/dev-down.sh`.

2. **Jangan `wait` setelah menyalakan agen.** Agennya tidak pernah keluar, jadi
   `wait` akan menggantung selamanya.

3. **`ls` tidak ada di PATH pada shell yang dipakai di sesi ini.** Pakai
   `/bin/ls` atau `command ls`.

4. **Selalu mulai demo dari `/api/reset`.** Kalau tidak, angka event dari run
   lama ikut menumpuk dan narasi video jadi tidak bisa dijelaskan.

5. **`ffmpeg`, `qpdf`, dan `convert` sebagai `qpdf` tidak tersedia.** Yang ada:
   `pdftoppm`, `pdfinfo`, `magick`, dan Python PIL. Untuk merekam layar, pakai
   `kazam` atau `simplescreenrecorder`.

6. **Semua lalu lintas demo berasal dari `127.0.0.1`.** Sensor dan penyerang
   berada di satu host, jadi IP penyerang yang muncul memang `127.0.0.1`. Ini
   sudah dinyatakan terbuka di `README.md` bagian Batasan. Jangan panik, dan
   jangan mengklaim seolah penyerangnya dari mesin lain.

7. **`honeytoken_file_access` selalu melaporkan `src_ip 127.0.0.1`.** inotify
   tidak bisa mengatribusi proses pembaca, hanya melaporkan berkasnya dibaca.
   Ini keterbatasan yang sudah didokumentasikan, bukan bug.

8. **Token default `polaris-dev-token` jangan dibawa ke produksi.** Ganti lewat
   `POLARIS_TOKEN` sebelum dipakai di lingkungan nyata.

9. **Port 80 dipakai web decoy.** Di host ini `ip_unprivileged_port_start=0`
   sehingga tidak butuh root, dan `listenWithFallback()` akan mencoba port+10000
   kalau gagal. Di host lain mungkin perlu kapabilitas `CAP_NET_BIND_SERVICE`.

10. **Repo ini publik sekarang.** Jangan pernah menambahkan kredensial asli,
    token Telegram, atau kunci API ke dalamnya. Isi `agent/honeytokens.go` memang
    terlihat seperti kredensial, tetapi semuanya umpan palsu yang di-generate
    templat dengan nilai acak. Secret scanning dan push protection sudah aktif.

---

## 6. Peta Berkas Penting

```
kartika-cyber-hackathon/
├── README.md                         # gerbang masuk, berisi peta ke kolom form
├── DESIGN.md                         # arah desain UI + tabel referensi + catatan perubahan
├── LANJUTKAN.md                      # berkas ini
├── agent/                            # sensor Go
│   ├── config.go                     # daftar port dan variabel lingkungan
│   ├── decoy_ports.go                # 32 listener umpan, banner tiap layanan
│   ├── decoy_web.go                  # web decoy, form login palsu
│   ├── honeytokens.go                # 11 berkas umpan + canary
│   ├── sender.go                     # spool lokal + kirim ulang
│   └── main.go
├── collector/app/
│   ├── main.py                       # seluruh endpoint HTTP dan WebSocket
│   ├── engine.py                     # fingerprint, korelasi, scoring, ringkasan
│   ├── db.py                         # skema SQLite, hidrasi kolom JSON
│   ├── mitre.py                      # tabel pemetaan ATT&CK dan ATT&CK for ICS
│   ├── alerts.py                     # Telegram dan webhook generik
│   └── config.py                     # variabel lingkungan
├── dashboard/                        # konsol operator
├── demo/demo.sh                      # rangkaian serangan untuk rekaman video
├── docs/13-video-script.md           # NASKAH VIDEO, buka ini saat merekam
├── docs/14-bukti-demo.md             # angka hasil run, sumber semua angka
├── docs/15-antislop-gate.md          # laporan Delivery Gate
├── site/                             # landing page + salinan PDF untuk publik
├── submission/                       # slide, thumbnail, proposal
└── screenshot/                       # tiga tangkapan layar untuk form
```

Endpoint collector yang paling sering dipakai saat demo:

| Endpoint | Fungsi |
|---|---|
| `GET /healthz` | cek collector hidup, tidak butuh token |
| `GET /api/stats` | angka ringkasan |
| `GET /api/incidents` | daftar incident |
| `GET /api/incidents/{id}` | detail incident dengan bukti |
| `GET /api/events/suppressed` | event yang disaring ke jalur terpisah |
| `POST /api/reset` | kosongkan state sebelum demo |

---

## 7. Checklist Sebelum Submit

- [ ] Video demo direkam, durasi 3 sampai 5 menit, suara jelas
- [ ] Angka di video cocok dengan `docs/14-bukti-demo.md`
- [ ] Video diunggah ke YouTube, bisa dibuka tanpa login
- [ ] Thumbnail dan screenshot sudah disiapkan untuk diunggah
- [ ] Link Karya, slide, dan proposal sudah diuji bisa dibuka di jendela privat
      (bukan dari sesi yang sudah login GitHub)
- [ ] Tanggal deadline di halaman resmi sudah dicek, sasaran submit 14 November 2026
- [ ] Form Codepolitan terisi lengkap
- [ ] Bukti submit disimpan (tangkapan layar atau surel konfirmasi)
- [ ] Data tim sudah diisi (nama, anggota, kontak) di proposal dan di form

---

## 8. Fitur yang Dibatalkan, Kalau Nanti Mau Dilanjutkan

Sempat muncul ide menambahkan pengambilan CVE terbaru. Ide itu **dibatalkan
dengan sengaja**, dan alasannya penting supaya tidak diulang secara salah.

Masalahnya: klaim terkuat POLARIS ada dua, yaitu jalan tanpa cloud (ramah
air-gap) dan nol false positive. "Fetch CVE terbaru" secara langsung menabrak
keduanya, karena butuh internet dan bisa memunculkan banjir peringatan baru yang
justru melahirkan kembali masalah alert fatigue.

Kalau nanti mau dikerjakan, bentuk yang benar adalah **CVE sebagai bahan
pengayaan bukti, bukan sumber deteksi**:

1. Ambil data sekali, bukan saat kejadian. Simpan ke tabel SQLite lokal.
2. Dua sumber sudah diuji tembus dari mesin ini dan keduanya gratis:
   - NVD API 2.0: `https://services.nvd.nist.gov/rest/json/cves/2.0`
     (butuh kunci API untuk kuota lebih besar)
   - CISA KEV: `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`
     (1.756 entri, 1,8MB, hanya yang terbukti dieksploitasi, sangat cocok untuk air-gap)
3. Cocokkan ke layanan umpan yang tersentuh (mis. banner `OpenSSH_8.9p1`),
   lalu tampilkan sebagai "CVE relevan untuk layanan ini" pada detail incident.
4. Selalu sertakan sumber dan tanggal pengambilan. Jangan pernah mengarang nomor CVE.
5. Untuk air-gap: sinkronkan di host yang terhubung internet, lalu bawa berkas
   SQLite-nya masuk.
6. Kalau tidak ada data tersinkron, tampilkan keadaan kosong yang jujur
   ("Belum ada data CVE lokal"), bukan diam-diam kosong.

Yang harus dihindari: menjadikan CVE sebagai pemicu incident baru.

---

## 9. Perintah yang Paling Sering Dibutuhkan

```bash
# nyalakan dan hentikan tumpukan
bash scripts/dev-up.sh
bash scripts/dev-down.sh

# demo untuk rekaman video
AUTO=1 PAUSE=3 bash demo/demo.sh

# cek angka hasil run
curl -s http://127.0.0.1:8787/api/stats -H "X-Polaris-Token: polaris-dev-token"
curl -s http://127.0.0.1:8787/api/incidents -H "X-Polaris-Token: polaris-dev-token"

# ekspor incident untuk forensik
curl -s http://127.0.0.1:8787/api/export/incidents -H "X-Polaris-Token: polaris-dev-token"

# periksa ulang kepatuhan aturan materi
grep -rn "—" dashboard/ site/ submission/*.html README.md docs/ || echo "bebas em dash"

# ekspor ulang slide ke PDF (chromium, resolusi 1280x720)
chromium --headless=new --disable-gpu --no-sandbox --no-pdf-header-footer \
  --virtual-time-budget=8000 \
  --print-to-pdf=submission/POLARIS_Slides_Kartika_2026.pdf \
  "file://$PWD/submission/slides.html"

# render ulang thumbnail 1200x630
chromium --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --force-device-scale-factor=1 --window-size=1200,630 --virtual-time-budget=6000 \
  --screenshot=submission/thumbnail-1200x630.png \
  "file://$PWD/submission/thumbnail.html"
```

Kalau slide atau thumbnail dirender ulang, jangan lupa menyalin ulang PDF ke
`site/files/` dan push, supaya salinan publiknya tidak ketinggalan:

```bash
cp submission/POLARIS_Slides_Kartika_2026.pdf site/files/
git add -A && git commit -m "..." && git push origin main
# lalu sinkronkan ulang cabang gh-pages dengan isi site/
```
