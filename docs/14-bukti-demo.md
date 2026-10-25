# 14: Bukti Demo (hasil run terverifikasi)

Dokumen ini mencatat keluaran nyata dari **satu kali run** `demo/demo.sh` terhadap
purwarupa yang berjalan di host pengembangan. Semua angka di `README.md`,
`site/index.html`, dan `submission/slides.html` harus bisa dilacak ke tabel di
sini. Kalau ada angka di dokumen lain yang tidak ada di sini, angka itu belum
terbukti dan harus dihapus.

Prinsipnya mengikuti aturan anti-slop R-17 dan C-5: tidak ada statistik tanpa
sumber. Bilah angka di landing page secara eksplisit menyebut bahwa data berasal
dari satu kali run demo.

---

## 1. Perintah yang Dijalankan

```bash
bash scripts/dev-up.sh
AUTO=1 PAUSE=3 bash demo/demo.sh
```

Tiga permintaan verifikasi setelah demo:

```bash
curl -s http://127.0.0.1:8787/api/stats -H "X-Polaris-Token: polaris-dev-token"
curl -s http://127.0.0.1:8787/api/incidents -H "X-Polaris-Token: polaris-dev-token"
curl -s http://127.0.0.1:8787/api/events/suppressed -H "X-Polaris-Token: polaris-dev-token"
```

---

## 2. Keluaran `/api/stats`

```json
{
  "events": 234,
  "suppressed_events": 2,
  "incidents": 1,
  "distinct_attackers": 1,
  "by_severity": { "CRITICAL": 1 },
  "false_positives": 0
}
```

Arti tiap baris:

| Field | Nilai | Arti |
|---|---|---|
| `events` | 234 | total interaksi umpan yang terekam |
| `suppressed_events` | 2 | aktivitas jinak yang dipindah ke jalur terpisah |
| `incidents` | 1 | hasil korelasi seluruh event dari satu sumber |
| `distinct_attackers` | 1 | satu alamat sumber, sesuai mode demo satu host |
| `by_severity` | CRITICAL 1 | tingkat incident tunggal |
| `false_positives` | 0 | tidak ada incident yang perlu ditarik kembali |

---

## 3. Incident Hasil Korelasi

| Field | Nilai |
|---|---|
| ID | 1 |
| Severity | CRITICAL |
| Skor | 410 |
| Event terkorelasi | 234 |
| Sumber | 127.0.0.1 |
| Perkiraan tool | nmap |
| Keyakinan tool | 0.86 |
| Rentang waktu | sekitar 1.5 menit |

Judul incident:

> Percobaan intrusi: canary credential use + honeytoken access + credential brute
> force + OT/ICS probe + port scan + web recon

Ringkasan yang dihasilkan engine (deterministik, templat yang diisi fakta):

> IP 127.0.0.1 memicu 234 interaksi umpan dalam 1.5 menit (canary credential use,
> port scan, credential brute force, OT/ICS probe, honeytoken access, web recon),
> menyentuh 10 jenis umpan berbeda. Ciri pola mengarah ke nmap dengan keyakinan
> 86%. Terdapat probing terhadap decoy protokol OT/ICS, potensi ancaman ke proses
> fisik. Kredensial umpan (canary) terbukti digunakan, indikasi kuat kompromi.
> Tidak ada aktivitas sah dari IP ini terhadap umpan. Karena umpan tidak pernah
> disentuh operasi normal, insiden ini bersifat deterministik dengan nol false
> positive.

---

## 4. Teknik ATT&CK yang Terpetakan (12)

| Kode | Nama | Kategori |
|---|---|---|
| T1046 | Network Service Scanning | Discovery |
| T1595 | Active Scanning | Reconnaissance |
| T1190 | Exploit Public-Facing Application | Initial Access |
| T1021.004 | Remote Services: SSH | Lateral Movement |
| T1110 | Brute Force | Credential Access |
| T1552 | Unsecured Credentials | Credential Access |
| T1078 | Valid Accounts | Defense Evasion, Persistence |
| T1083 | File and Directory Discovery | Discovery |
| T0846 | Remote System Discovery | ICS |
| T0812 | Default Credentials | ICS |
| T0835 | Manipulate I/O Image | ICS |
| T0836 | Modify Parameter | ICS |

Empat teknik terakhir berasal dari ATT&CK for ICS, dipicu oleh sentuhan ke decoy
Modbus (502) dan HMI (8080).

---

## 5. Bukti Mekanisme Penyaringan (Suppression)

Host pengembangan menjalankan health check internal yang mengirim header `b3:`.
Pola itu awalnya terbaca sebagai probe, dan pada run awal ia membentuk incident
kedua. Setelah aturan penyaringan ditambahkan, event tersebut tidak lagi menjadi
incident.

Keadaan sekarang, terbaca dari `/api/stats`:

| Field | Nilai |
|---|---|
| `incidents` | 1 |
| `suppressed_events` | 2 |
| `false_positives` | 0 |

Dua event yang disaring bisa diperiksa langsung:

```bash
curl -s http://127.0.0.1:8787/api/events/suppressed -H "X-Polaris-Token: polaris-dev-token"
```

Dua event itu tetap tersimpan dan tetap bisa dilihat, tetapi tidak lagi menjadi
incident. Itu perbedaan yang dibuktikan: aktivitas jinak tidak dibuang diam-diam,
ia dipindah ke jalur yang bisa diaudit.

Catatan kejujuran: angka `2` di sini adalah jumlah event jinak pada run yang
dicatat. Jumlah itu bisa berbeda di host lain karena bergantung pada health check
apa saja yang berjalan di host tersebut.

---

## 6. Cara Mengulang

```bash
# 1. Hentikan state lama
bash scripts/dev-down.sh

# 2. Jalankan ulang dari nol
bash scripts/dev-up.sh
AUTO=1 PAUSE=3 bash demo/demo.sh

# 3. Bandingkan angka
curl -s http://127.0.0.1:8787/api/stats -H "X-Polaris-Token: polaris-dev-token"
```

Angka `events` boleh berbeda antar run karena jumlah percobaan brute force dan
sweep port bergantung waktu. Yang harus tetap: satu incident, nol false positive,
dan nmap sebagai perkiraan tool. Kalau salah satu dari tiga itu berubah, ada yang
salah dan harus diperiksa sebelum video direkam.
