# 03 — Taksonomi Umpan (Decoy & Honeytoken)

Ini "amunisi" POLARIS. Setiap umpan punya **tier kepercayaan** — makin tinggi
tier, makin mustahil disentuh user sah, makin tinggi severity.

## Tabel Tier & Confidence

| Tier | Jenis | Confidence | MITRE | Severity dasar |
|---|---|---|---|---|
| T1 | Honeytoken file dibaca | ~100% | T1083 | High |
| T1 | Canary credential dipakai | ~100% | T1552 | Critical |
| T1 | Honeytoken URL di-fetch | ~100% | T1071 / T1595 | High |
| T1 | OTP/register umpan dipakai | ~100% | T1078 | Critical |
| T2 | Koneksi ke decoy port | Tinggi | T1046 | Medium–High |
| T2 | Decoy OT/ICS port disentuh | Tinggi | T0846 (ICS) | High |
| T2 | Decoy web path diakses | Tinggi | T1595 | Medium |
| T2 | Auth attempt ke decoy login | Tinggi | T1110 | High |
| T3 | Korelasi multi-umpan 1 IP | Kontekstual | (multi) | Critical |

> Prinsip: **umpan tidak boleh berpotensi tersentuh operasi normal.** Kalau ragu,
> turunkan tier atau jangan pakai.

---

## 1. Decoy Ports

Listener yang menerima koneksi apa pun → catat event. Opsional balas banner palsu
untuk memancing interaksi lebih lanjut (memperkaya fingerprint).

| Layanan palsu | Port | Banner palsu | Catatan |
|---|---|---|---|
| SSH | 2222, 22 (bila bebas) | `SSH-2.0-OpenSSH_8.9p1` | Target klasik brute & scan |
| MySQL | 33060, 3306 | handshake MySQL palsu | Menarik exploit DB |
| Redis | 6379 | `+PONG` / `-ERR` | Menarik exploit Redis |
| RDP | 3389 | RDP negotiation palsu | Menarik lateral movement |
| SMB | 445 | SMB negotiation palsu | Pergerakan lateral Windows |
| HMI/SCADA web | 8080, 102 | halaman HMI palsu | Khusus OT (lihat 05) |

**Implementasi:** satu listener per port (goroutine/asyncio). Catat: waktu, src IP,
src port, payload awal (bytes pertama), durasi koneksi, jumlah byte.

---

## 2. Honeytoken Files

Berkas umpan dengan nama & isi yang menggoda. Deteksi akses via filesystem watch.

**Daftar nama umpan (contoh):**
```
.env
.aws/credentials
.aws/config
.git/config
backup_db.sql
passwords.xlsx
credentials.txt
id_rsa_backup
config.old.php
wp-config.php.bak
kubernetes.yaml
docker-compose.yml.bak
vault-token.txt
```

**Isi:** kredensial palsu dengan domain/host umpan milik kita (agar jejak balik
ke Collector). Sertakan canary string unik.

**Deteksi:**
- `inotify` event `IN_ACCESS`, `IN_OPEN`, `IN_MODIFY` pada berkas/directory umpan.
- Alternatif lebih kuat: `fanotify` (butuh root) untuk cakupan lebih luas.
- File integrity: hash berubah → alert (indikasi tampering).
- Taruh di lokasi yang masuk akal (bukan folder aneh) supaya terciptanya "realisme".

---

## 3. Canary Credentials

Kredensial palsu yang ditempatkan di file config umpan. Bila **"dipakai"** atau
muncul di jalur eksfiltrasi → alert Critical.

**Bentuk:**
- API token palsu (format menyerupai token nyata).
- AWS Access Key + Secret (format valid tapi inert).
- Database credential.
- JWT palsu dengan claim menarik.

**Deteksi kredensial ini dipakai:**
- Bila target punya telemetri auth sendiri → korelasikan.
- Honeytoken URL di dalam config → bila penyerang mengekstrak & mencoba memakainya ke layanan umpan kita, terbaca.
- **Kombinasi terkuat:** credential → menunjuk ke *service umpan* milik POLARIS →
  penggunaan langsung tercatat di Collector.

---

## 4. Honeytoken URLs

URL unik yang ditanam di dokumentasi/config/DM palsu. Bila di-fetch (mis. attacker
generate PDF, coba SSRF, atau eksfil) → callback ke Collector.

```
http://<collector>/beacon/9f3a1c-<random>
```

**Deteksi:** request masuk ke `/beacon/{token}` = tidak ada alasan sah → alert.
Berguna untuk mendeteksi:
- SSRF (server-side request forgery) yang mengekstrak config.
- Exfil via link yang tidak sengaja diakses.
- Bot/scraper mengambil DM palsu.

---

## 5. Web Decoy Paths

Endpoint palsu yang hanya menarik bagi *recon* otomatis.

```
/.env                 /.git/config          /.aws/credentials
/wp-admin             /phpmyadmin           /adminer.php
/actuator/env         /actuator/heapdump    /manager/html
/console              /debug                /server-status
/.well-known/...      /api/v1/internal/...
```

**Deteksi:** setiap hit = recon (MITRE T1595 Active Scanning).
Balas dengan halaman/status yang meyakinkan (mis. 200 + konten palsu) supaya
attacker lanjut berinteraksi → memperkaya data.

---

## 6. Decoy Login / OTP Trap

Form login palsu pada decoy path. Setiap submit dicatat:
- username/password yang dicoba (kredensial attacker + password spraying corpus).
- pola brute force (rate, username enumeration).

Bila ada endpoint OTP/registrasi diverifikasi pihak kita → OTP umpan yang
"berhasil" hanya dari IP attacker = indikasi.

---

## 7. Prinsip Realisme (Anti-Detection)

Penyerang berpengalaman bisa mengenali honeypot. Supaya POLARIS tidak mudah
dikenali:
- Banner & respons menyerupai layanan asli (versi umum, bukan default honeypot).
- Umpan ditaruh di lokasi yang logis, bukan folder bernama "honeypot".
- Konsistensi: nama file, permission, timestamp yang masuk akal.
- Hindari pola respons yang identik antar-decoy (beri variasi).

## 8. Keselamatan (Safety)

- Tidak memancing interaksi yang merusak.
- Tidak menjalankan payload attacker.
- Tidak memberikan akses nyata lewat canary credential.
- Tidak menyentuh/mengubah data produksi.
- Semua aksi bersifat **observasi**.
