# 08 — Alignment dengan Kriteria Penjurian

Strategi: petakan setiap keunggulan POLARIS ke **bobot penilaian resmi** dan
**latar juri**. Ini yang menentukan menang-tidaknya.

## Bobot Resmi

| Bobot | Kriteria | Posisi POLARIS |
|---|---|---|
| **25%** | Relevansi & Manfaat (kebutuhan IT/OT TNI AD) | Kuat (deception + OT decoy + air-gap) |
| **25%** | Inovasi Teknis | Kuat (paradigma deception deterministik) |
| **25%** | Fungsionalitas Purwarupa | Harus dibuktikan live (prioritas eksekusi) |
| **15%** | Kelayakan Implementasi | Kuat (on-prem, 1-line install, nol cloud) |
| **10%** | Kualitas Dokumentasi | Harus dikerjakan serius |

---

## 1. Relevansi & Manfaat (25%) — Kebutuhan IT/OT TNI AD

**Yang dijual:**
- Deteksi menyentuh **IT + OT/ICS** (Modbus/S7/HMI decoy).
- **Air-gap friendly** → cocok jaringan satuan yang terisolasi.
- **Early warning bersignal tinggi** untuk operasi siber pertahanan.
- Mengurangi beban analis SOC (anti alert-fatigue).

**Kalimat kunci:**
> "Kami tidak hanya melindungi server IT, tapi juga menyentuh protokol industri —
> dan semuanya berjalan tanpa internet, sesuai realitas jaringan satuan."

---

## 2. Inovasi Teknis (25%)

**Yang dijual:**
- **Membalik paradigma** anomaly detection → deception defense deterministik.
- **Zero false positive by design** (bukan tuning threshold).
- **Attacker fingerprinting** dari pola interaksi.
- **Korelasi kill-chain** + **MITRE ATT&CK mapping** (termasuk ATT&CK for ICS).
- **AI summarizer** (opsional) untuk narasi incident.

**Kalimat kunci:**
> "Deteksi kami bukan tebakan. Interaksi dengan umpan adalah bukti intent —
> deterministik, auditable, hampir tanpa false positive."

---

## 3. Fungsionalitas Purwarupa (25%) — EKSEKUSI

Ini bobot terbesar yang bergantung penuh pada kerja nyata. Prioritas:
- **Harus jalan & bisa didemo live.**
- Skenario demo end-to-end (lihat `09-demo-script.md`).
- Rekaman backup bila live gagal.

**Checklist fungsional minimal untuk skor tinggi:**
- [ ] Agent menanam & memantau umpan (port + file + web + OT)
- [ ] Event mengalir ke Collector real-time
- [ ] Incident ter-korelasi terbentuk
- [ ] Alert Telegram masuk saat demo
- [ ] Dashboard menampilkan live feed & profil penyerang
- [ ] MITRE mapping tampil di incident

---

## 4. Kelayakan Implementasi (15%)

**Yang dijual:**
- Instalasi **satu baris**.
- **Nol dependensi cloud** → siap air-gap.
- **Nol infrastruktur baru** (SQLite embedded).
- **Skalabel** dari 1 server ke banyak node satuan tanpa ubah arsitektur.
- Roadmap pengembangan lanjut jelas (PostgreSQL, integrasi SOAR, sensor OT).

**Kalimat kunci:**
> "Dari nol ke terlindung dalam satu baris perintah — dan jalan sepenuhnya on-prem."

---

## 5. Kualitas Dokumentasi (10%)

Deliverable wajib (sesuai halaman hackathon):
- Proposal solusi → `01-proposal-solusi.md`
- Dokumentasi teknis → `docs/` ini + README repo
- Video demo purwarupa → `09-demo-script.md`
- Slide penjelasan → ringkas + visual arsitektur
- Link project yang bisa diakses

**Tips:** dokumentasi yang baik juga mengangkat kriteria lain (relevansi & inovasi
jadi lebih jelas terbaca juri).

---

## Peta ke Dewan Juri

| Juri | Latar | Yang harus kita tonjolkan |
|---|---|---|
| **Lettu Cpn Aghni Anugrah Raesa** | Digital Forensics & **Detection Engineering** | MITRE mapping, Sigma-style rules, evidence forensics-ready, timeline |
| **Mahrus Qusaeri** | Network Security / **Offensive & Practical Defense** | Fingerprinting, demo live nmap/hydra, bypass-resistance, realisme decoy |
| **Sofian Hadiwijaya** | Applied AI / GenAI | AI summarizer, tapi *dengan* batas jelas (AI ringkas, bukan putuskan) |

**Kesimpulan:** menangkan hati ketiganya sekaligus —
**detection engineering rigor (Aghni) + demo ofensif meyakinkan (Mahrus) + AI yang
bertanggung jawab (Sofian).**

---

## Skor Target (self-assessment)

| Kriteria | Target | Kenapa tercapai |
|---|---|---|
| Relevansi & Manfaat | 90% | OT decoy + air-gap + anti-fatigue |
| Inovasi Teknis | 88% | Paradigma deception + fingerprint |
| Fungsionalitas | 85% | Demo end-to-end + backup recording |
| Kelayakan | 90% | 1-line install, nol cloud |
| Dokumentasi | 85% | Proposal + tech doc + video + slide |
| **Total terbobot** | **±87%** | Target agresif tapi realistis |
