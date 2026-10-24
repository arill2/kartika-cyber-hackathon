# 09 — Demo Script

Dua bagian: **video demo (syarat submit)** dan **demo live (final, 10 menit)**.

Setup: laptop A = "attacker", laptop B = "server korban" (agent POLARIS jalan),
Dashboard + Collector bisa di laptop B atau laptop lain.

---

## A. Video Demo Purwarupa (3–5 menit)

Rekam rapi, ada narasi. Struktur:

1. **0:00–0:30 — Masalah.** Tunjukkan betapa banyak alert FP-nya IDS biasa (atau
   cukup narasi). Nyatakan janji: "zero false positive by design."
2. **0:30–1:00 — Arsitektur.** Tampilkan diagram (dari `02-arsitektur.md`).
3. **1:00–2:00 — Pemasangan.** Jalankan installer 1 baris di server. Tunjukkan
   umpan terpasang (list port, file honeytoken).
4. **2:00–3:00 — Serangan & deteksi IT.**
   - Dashboard masih bersih.
   - `nmap` dari attacker → alert recon + **fingerprint nmap**.
   - `hydra` ke decoy SSH → alert brute force.
   - Buka `/.env` palsu di browser → **honeytoken T1 critical** + Telegram masuk.
5. **3:00–4:00 — Serangan & deteksi OT.**
   - Attacker sentuh decoy Modbus (502) → alert OT + MITRE for ICS.
6. **4:00–4:30 — Incident + MITRE + AI summary.**
   - Tunjukkan 1 incident ter-korelasi, teknik MITRE, narasi AI.
7. **4:30–5:00 — Penutup.** Air-gap friendly + 1-line deploy + impact.

---

## B. Demo Live Final (10 menit presentasi)

### Struktur waktu
| Menit | Segmen |
|---|---|
| 0–1 | Hook + masalah (alert fatigue, penyusup lolos perimeter) |
| 1–3 | Konsep deception + arsitektur (1 slide) |
| 3–7 | **DEMO LIVE** (bagian emas) |
| 7–9 | MITRE coverage + forensics evidence + air-gap + roadmap |
| 9–10 | Impact + penutup |

### Skenario Demo Live (urutan)
1. **Dashboard bersih** → "sistem normal, nol alert."
2. **Recon:** jalankan `nmap -sV <server>` dari laptop attacker.
   → Alert muncul: **Network Service Scanning** + dugaan tool **nmap**.
3. **Web recon:** akses `http://<server>/.env` dan `/.git/config`.
   → Alert **Active Scanning (T1595)**.
4. **Brute force:** `hydra` ke decoy SSH 2222.
   → Alert **Brute Force (T1110)**.
5. **Honeytoken凉的 kritikal:** buka `passwords.xlsx` / `.env` umpan.
   → Alert **CRITICAL (T1552/T1083)** + **notifikasi Telegram muncul di HP di depan juri.**
6. **OT:** sentuh decoy Modbus 502 (modbus client).
   → Alert **OT/ICS + ATT&CK-for-ICS**.
7. **Incident:** buka kartu incident → tunjukkan korelasi semua event di atas
   jadi **1 incident + severity + MITRE + timeline + evidence**.
8. **AI summary:** tunjukkan narasi incident.

### Kalimat pembuka demo
> "Saya akan menyimulasikan penyusup yang mencoba bergerak di dalam jaringan.
> IDS biasa akan kebanjiran noise. POLARIS? Lihat — dashboard masih bersih.
> Sekarang, teman saya mulai melakukan pemindaian..."

### Kalimat penutup
> "Setiap interaksi yang Anda lihat adalah bukti intent — bukan tebakan.
> Nol false positive, jalan tanpa internet, dan bisa dipasang dalam satu baris.
> Ini yang kami tawarkan untuk pertahanan siber satuan."

---

## C. Fallback & Antisipasi

- **Rekam seluruh demo live lebih dulu** → putar bila live gagal.
- Siapkan **VM snapshot** server agar bisa direset cepat.
- Siapkan hotspot lokal bila venue WiFi buruk (semua komponen lokal, jadi aman).
- Cek **Telegram notifikasi** terkirim (jangan bergantung pada sinyal venue →
  sediakan alternatif tampilkan webhook log).
- Latihan **minimal 2x** dengan stopwatch.

---

## D. Checklist Sebelum Demo

- [ ] Agent jalan di server (umpan terpasang)
- [ ] Collector + Dashboard jalan
- [ ] Telegram bot aktif & teruji
- [ ] Attacker tool siap (nmap, hydra, curl, modbus client)
- [ ] Dashboard di layar besar / resolusi jelas
- [ ] Video backup siap
- [ ] Stopwatch & urutan hafal
