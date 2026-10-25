# 13: Video Demo Script (3 sampai 5 menit)

Dokumen ini adalah naskah rekaman untuk **Video Demo Purwarupa**, syarat submit
Babak 1. Semua perintah di sini persis yang dijalankan oleh `demo/demo.sh`, jadi
rekaman tidak perlu improvisasi dan tidak perlu menyunting perintah.

Semua angka di naskah ini berasal dari **satu kali run demo** yang sudah diverifikasi
(lihat `docs/14-bukti-demo.md`). Kalau angka di layar rekaman Anda berbeda, sebut
angka yang muncul di layar, jangan angka di dokumen ini.

---

## 0. Persiapan Rekaman

### Susunan mesin

| Peran | Isi |
|---|---|
| Sensor + Collector + Dashboard | satu host, menjalankan `bash scripts/dev-up.sh` |
| Penyerang | bisa host yang sama (mode demo) atau host lain di LAN |

Pada mode satu host, semua lalu lintas datang dari `127.0.0.1`. Alamat ini yang
akan tampil sebagai IP penyerang di dashboard. Itu benar dan dijelaskan di
`README.md` bagian Batasan.

### Yang harus sudah jalan sebelum menekan Rec

```bash
bash scripts/dev-up.sh
# buka dashboard di browser: http://127.0.0.1:8787
```

Cek cepat ketiga komponen:

```bash
curl -s http://127.0.0.1:8787/healthz        # harus menjawab: ok
curl -s http://127.0.0.1:8787/api/stats -H "X-Polaris-Token: polaris-dev-token"
```

### Setelan terminal

- Terminal untuk demo: tinggi minimal 40 baris, font 14 sampai 16, latar gelap.
- Jalankan demo dengan jeda otomatis supaya tempo rekaman konsisten:

```bash
AUTO=1 PAUSE=3 bash demo/demo.sh
```

- Mode manual (`bash demo/demo.sh` tanpa `AUTO=1`) memberi jeda pada tombol Enter.
  Pakai mode ini kalau ingin bicara dulu sebelum tiap langkah.
- Tutup notifikasi desktop dan tab lain. Matikan kursor berkedip kalau perekam
  Anda menangkapnya sebagai noise.

### Tab yang disiapkan

1. Terminal demo (layar utama, porsi terbesar).
2. Browser tab 1: dashboard POLARIS.
3. Browser tab 2 (opsional): berkas `.env` umpan untuk segmen honeytoken.

---

## 1. Peta Waktu

Total target: **4 menit 30 detik**. Semua segmen boleh melar sedikit, kecuali
segmen 4 dan 5 yang justru paling kuat kalau padat.

| Menit | Segmen | Langkah `demo.sh` | Fokus layar |
|---|---|---|---|
| 0:00–0:25 | Masalah | (tidak ada perintah) | Dashboard |
| 0:25–0:45 | Cara kerja | (tidak ada perintah) | Dashboard |
| 0:45–1:15 | Sistem bersih | `0. Reset state` | Terminal + Dashboard |
| 1:15–2:00 | Recon jaringan | `1. nmap -sV`, `2. sweep cepat` | Terminal |
| 2:00–2:35 | Recon web | `3. Web recon` | Terminal |
| 2:35–3:05 | Brute force | `4. hydra + spray` | Terminal |
| 3:05–3:35 | Honeytoken | `5. berkas .env`, `6. canary URL` | Terminal + tab `.env` |
| 3:35–4:00 | Decoy OT/ICS | `7. Modbus + HMI` | Terminal |
| 4:00–4:30 | Incident + penutup | `8. Hasil` + Dashboard | Dashboard |

---

## 2. Naskah per Segmen

Cara pakai: teks **Narasi** diucapkan apa adanya, teks `perintah` dijalankan di
terminal. Kurung siku adalah arahan layar, bukan untuk diucapkan.

---

### Segmen 1: Masalah (0:00–0:25)

`[Layar: dashboard POLARIS, belum ada incident. Bicara langsung ke kamera atau
overlay teks di atas dashboard.]`

**Narasi:**

> "Sistem deteksi intrusi biasa bekerja dengan menebak. Ia harus memutuskan mana
> lalu lintas normal dan mana yang mencurigakan. Karena tebakan, ia salah dua
> arah: alert palsu yang membuang waktu analis, dan serangan nyata yang lolos
> karena tersembunyi di antara noise."

`[Layar: tetap di dashboard. Tidak ada perintah dijalankan di sini.]`

---

### Segmen 2: Cara kerja POLARIS (0:25–0:45)

`[Layar: tetap dashboard. Kalau ada slide arsitektur di layar kedua, tampilkan.]`

**Narasi:**

> "POLARIS membalik pertanyaannya. Kami tidak menebak apa yang normal. Kami
> menanam umpan yang secara desain tidak pernah disentuh pengguna sah: port tanpa
> layanan, berkas kredensial yang tidak dipakai proses apa pun, dan perangkat
> OT tiruan yang tidak ada di topologi nyata. Kalau ada yang menyentuh umpan,
> tidak ada penjelasan jinak. Setiap interaksi adalah bukti, bukan tebakan."

---

### Segmen 3: Sistem bersih (0:45–1:15)

`[Layar: terminal. Jalankan langkah 0.]`

```bash
curl -sS -X POST -H "X-Polaris-Token: polaris-dev-token" \
  http://127.0.0.1:8787/api/reset
```

`[Layar: pindah ke tab dashboard. Tunjukkan keadaan kosong dan baris statistik
yang masih nol.]`

**Narasi:**

> "Kita mulai dari keadaan bersih. Sensor sudah berjalan, umpan sudah terpasang,
> dan dashboard menunjukkan nol incident. Kondisi ini penting: apa yang muncul
> nanti bukan akumulasi sampah lama, melainkan murni dari serangan yang kita
> lakukan sendiri."

`[Catat nomor statistik yang tampil. Karena baru reset, incident masih 0.
Kalau dashboard belum ter-refresh, tekan tombol refresh di dashboard.]`

---

### Segmen 4: Recon jaringan (1:15–2:00)

`[Layar: terminal.]`

```bash
# 1. Recon: nmap service/version detection ke port umpan (T1046)
nmap -sV -Pn -T4 --version-intensity 2 \
  -p 2222,3306,6379,3389,445,502,8080 127.0.0.1
```

**Narasi saat perintah berjalan:**

> "Pertama, pemindaian layanan. Port yang saya sentuh semuanya umpan: SSH tiruan
> di 2222, MySQL tiruan di 3306, Redis, RDP, SMB, Modbus di 502, dan HMI di 8080.
> Tidak ada layanan sah di port itu. Setiap respons dari port ini adalah sensor."

```bash
# 2. Sweep cepat menyeluruh: pola scanner high-rate (indikasi masscan)
nmap -Pn -n -T4 --min-rate 4000 -p "$(seq -s, 1 1024)" 127.0.0.1
```

**Narasi:**

> "Lalu pemindaian cepat seribu port. POLARIS memisahkan dua pola ini. Pemindaian
> berlapis dengan deteksi versi punya ciri koneksi yang berbeda dari sweep
> cepat berkecepatan tinggi. Dari ciri itu, POLARIS menyimpulkan alat yang
> dipakai adalah nmap, dengan keyakinan delapan puluh enam persen."

`[Layar: pindah ke dashboard sebentar, tunjukkan kartu incident bertambah dan
label tool muncul. Lalu kembali ke terminal.]`

---

### Segmen 5: Recon web (2:00–2:35)

`[Layar: terminal, langkah 3.]`

```bash
for p in /.env /.git/config /.aws/credentials /actuator/env /server-status /wp-admin; do
  curl -sS -o /dev/null -w "%{http_code}  $p\n" \
    -A 'Mozilla/5.00 (Nikto/2.5.0)' "http://127.0.0.1:80$p"
done
```

**Narasi:**

> "Scanner web akan mengetuk pintu yang sama berulang kali: berkas kredensial
> cloud, konfigurasi git, endpoint manajemen. Umpan kita menjawab dengan status
> dua ratus dan isi palsu, supaya penyerang terus bergerak dan terus terekam.
> Menariknya, kita tidak perlu menghentikannya di sini. Yang kita inginkan justru
> interaksi lanjutannya."

`[Catat kode status yang muncul untuk tiap path. Semuanya 200 merupakan perilaku
umpan yang disengaja.]`

---

### Segmen 6: Brute force kredensial (2:35–3:05)

`[Layar: terminal, langkah 4.]`

```bash
timeout 15 hydra -l admin -P <(printf 'admin\n123456\npassword\ntoor\n') \
  -t 4 -W 3 ssh://127.0.0.1:2222
python3 demo/ssh_spray.py 127.0.0.1 2222 6
```

**Narasi:**

> "Sekarang brute force. Hydra mencoba beberapa kredensial ke SSH tiruan, lalu
> ada credential spray terstruktur. Perhatikan satu hal: umpan ini tidak pernah
> memberi akses. Tidak ada akun sah di baliknya. Tapi setiap percobaan tercatat
> lengkap dengan waktu, nama pengguna, dan sumbernya. Penyerang mengira sedang
> menembus pintu. Sebenarnya ia sedang menandatangani daftar kehadiran."

---

### Segmen 7: Honeytoken (3:05–3:35)

`[Layar: tampilkan isi berkas umpan, lalu jalankan canary URL.]`

```bash
head -4 "$HOME/.polaris/decoy/.env"
BEACON="$(grep -ao 'http://[^ ]*beacon/[A-Za-z0-9-]*' "$HOME/.polaris/decoy/.env" | head -1)"
curl -sS -A 'curl/8.5.0' "$BEACON"
```

**Narasi:**

> "Berkas ini adalah honeytoken. Isinya kredensial yang terlihat meyakinkan:
> kunci API, kunci cloud, dan satu URL canary. Tidak ada proses sah yang membaca
> berkas ini, jadi pembacaan berarti bukti. Kredensial canary di dalamnya punya
> jebakan kedua: kalau benar-benar dipakai, ia memanggil URL beacon kita. Saat
> beacon itu dipanggil, kita tahu bukan hanya berkasnya dibaca, tapi kredensial
> itu sudah masuk ke tangan penyerang."

`[Layar: dashboard. Incident naik ke CRITICAL. Tunjukkan kartu bertanda CRITICAL.]`

**Narasi:**

> "Dashboard menaikkan tingkat ke CRITICAL. Ini bukan karena satu alert, tapi
> karena korelasi: recon, brute force, dan penggunaan kredensial canary terjadi
> dari sumber yang sama dalam rentang waktu berdekatan."

---

### Segmen 8: Decoy OT/ICS (3:35–4:00)

`[Layar: terminal, langkah 7.]`

```bash
python3 demo/modbus_probe.py 127.0.0.1 502
printf 'GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n' | timeout 3 nc 127.0.0.1 8080
```

**Narasi:**

> "Bagian yang jarang ada di produk sejenis. Kita menanam decoy protokol industri.
> Modbus di port 502 dan panel HMI tiruan di 8080. Keduanya meniru perangkat ICS
> yang tidak ada di topologi asli. Probe protokol OT ke alamat ini tidak punya
> penjelasan wajar, dan POLARIS memetakannya ke ATT and CK for ICS: remote system
> discovery, eksploitasi kredensial default, manipulasi I/O image, dan modifikasi
> parameter. Untuk jaringan OT yang dijaga satuan, inilah sinyal yang benar
> benar penting."

---

### Segmen 9: Incident, bukti, penutup (4:00–4:30)

`[Layar: terminal, langkah 8.]`

```bash
curl -sS http://127.0.0.1:8787/api/stats -H "X-Polaris-Token: polaris-dev-token"
curl -sS http://127.0.0.1:8787/api/incidents -H "X-Polaris-Token: polaris-dev-token"
```

`[Layar: pindah ke dashboard. Klik kartu incident. Tampilkan daftar teknik ATT and
CK, timeline, dan bukti per event.]`

**Narasi:**

> "Semua yang kita lakukan tadi masuk ke satu incident. Dua ratus tiga puluh empat
> event mentah, dua di antaranya aktifitas jinak yang disaring ke jalur terpisah,
> dan sisanya terkorelasi menjadi satu incident dengan skor empat ratus sepuluh
> dan dua belas teknik ATT and CK. Yang paling penting: nol false positive.
> Bukan karena ambang batas yang berhasil kami setel, tapi karena umpan tidak
> pernah disentuh operasi normal. Deteksinya biner: disentuh berarti bukti."

`[Layar: kembali ke kamera atau overlay penutup, kalau ada.]`

**Narasi penutup:**

> "POLARIS berjalan tanpa internet, tanpa layanan cloud, dan tanpa database
> terpisah. Agennya satu binary Go tanpa dependensi eksternal, dan seluruh
> tumpukan bisa dijalankan dengan satu perintah. Setiap angka di layar ini datang
> dari satu kali jalan yang bisa Anda ulang. Terima kasih."

---

## 3. Kalau Ada yang Gagal di Tengah Rekaman

| Gejala | Tindakan saat rekaman |
|---|---|
| Collector mati | Hentikan rekaman, jalankan ulang `bash scripts/dev-up.sh`, mulai dari langkah 0 |
| Dashboard tidak memperbarui | Tekan tombol refresh di dashboard, WebSocket akan memuat ulang snapshot |
| `nmap` tidak terpasang | Lewati langkah 1 dan 2, sebutkan bahwa segmen tersebut dilewati demi waktu |
| `hydra` tidak terpasang | Jalankan saja `ssh_spray.py`, itu sudah menghasilkan event brute force |
| Angka berbeda dari dokumen | Sebut angka yang muncul di layar, jangan paksa angka dokumen |

Catatan penting: **jangan** merekam dengan data lama yang menumpuk. Selalu mulai
dengan langkah 0 (`api/reset`) supaya angka di layar bisa Anda jelaskan sebagai
hasil satu kali serangan.

---

## 4. Checklist Sebelum Menekan Rec

- [ ] `bash scripts/dev-up.sh` selesai tanpa error, `healthz` menjawab `ok`
- [ ] Dashboard terbuka dan menampilkan data (bukan layar loading terus)
- [ ] `nmap`, `hydra`, `nc`, `python3` tersedia
- [ ] Berkas umpan ada di `$HOME/.polaris/decoy`
- [ ] Terminal sudah diperbesar dan dibersihkan
- [ ] Naskah dibaca sekali penuh dengan stopwatch sebelum rekaman sungguhan
- [ ] Naskah tidak dibacakan sambil melihat dokumen ini di layar yang terekam
- [ ] Rekaman uji pertama dihapus, jangan sampai salah unggah

---

## 5. Cara Memverifikasi Hasil Rekaman

Setelah rekaman selesai, cocokkan angka di video dengan keluaran nyata:

```bash
curl -s http://127.0.0.1:8787/api/stats -H "X-Polaris-Token: polaris-dev-token"
curl -s http://127.0.0.1:8787/api/incidents -H "X-Polaris-Token: polaris-dev-token"
curl -s http://127.0.0.1:8787/api/events/suppressed -H "X-Polaris-Token: polaris-dev-token"
```

Tiga perintah itu menampilkan: jumlah event, jumlah incident, jumlah event yang
disaring, dan daftar teknik ATT and CK. Angka di video harus cocok dengan ini.
Kalau tidak cocok, rekam ulang. Video demo yang angkanya tidak bisa diulang
lebih merugikan daripada video yang lebih pendek.
