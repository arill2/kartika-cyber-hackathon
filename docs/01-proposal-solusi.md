# 01: Draft Proposal Solusi (Submission Kartika Cyber Hackathon 2026)

> Format formal, siap disubmit / dikembangkan. Isi placeholder `[...]` sesuai data tim.

---

## Judul
**POLARIS, Sistem Peringatan Dini Berbasis Deception (Tipuan) untuk Deteksi
Penyusupan Jaringan IT/OT dengan Zero False Positive**

**Kategori:** Defensive Shield (Penangkalan)

**Tim:** [Nama Tim], [Anggota 1], [Anggota 2], [Anggota 3]

---

## 1. Latar Belakang

Pertahanan siber Angkatan Darat menghadapi ancaman yang semakin canggih:
penyusup yang berhasil menembus perimeter bergerak secara stealth di dalam
jaringan, melakukan pemetaan (reconnaissance), eskalasi hak akses, dan
pergerakan lateral menuju aset kritikal. Sistem deteksi konvensional
(SIEM/IDS/IPS) yang beroperasi pada paradigma *anomaly detection* menghasilkan
volume alert yang sangat besar dengan tingkat *false positive* tinggi, kondisi
yang berujung pada *alert fatigue* dan tertutupnya sinyal ancaman nyata.

Di sisi lain, jaringan satuan TNI AD memiliki karakteristik khas: sebagian
merupakan **jaringan terisolasi (air-gapped)** dan merupakan **lingkungan
gabungan IT dan OT/ICS** (SCADA, PLC, HMI). Solusi yang bergantung pada cloud,
threat-intelligence eksternal, atau konektivitas internet tidak dapat diterapkan
pada lingkungan tersebut.

## 2. Permasalahan

- Deteksi berbasis anomali bersifat probabilistik → false positive tinggi.
- Penyusup yang telah masuk tidak terdeteksi karena bergerak dalam batas pola normal.
- Tidak ada mekanisme deteksi bertanda tangan tinggi yang bebas tuning threshold.
- Solusi komersial bergantung pada komponen eksternal yang tidak sesuai jaringan terisolasi.
- Kebutuhan mapping terhadap standar **MITRE ATT&CK** dan kesiapan **forensik** belum terpenuhi.

## 3. Solusi yang Diusulkan

**POLARIS** adalah sistem peringatan dini berbasis pendekatan **deception defense**
yang membalik paradigma deteksi: alih-alih menebak mana yang "anomali", POLARIS
menanam **umpan (decoy & honeytoken)** yang secara desain **tidak akan pernah
disentuh oleh pengguna sah**. Setiap interaksi terhadap umpan merupakan
**indikasi intent penyerang yang terbukti (deterministik)**, sehingga deteksi
bersifat biner dan hampir tanpa false positive.

POLARIS mencakup:

1. **Lapisan Umpan**
   - Decoy port (layanan palsu: SSH, MySQL, Redis, RDP).
   - Honeytoken file (berkas kredensial/config/dump palsu).
   - Canary credential (kredensial umpan di konfigurasi).
   - Honeytoken URL (URL unik penanda akses).
   - Decoy web path (endpoint admin/recon populer).
   - **Decoy OT/ICS**: Modbus/TCP dan panel HMI sudah berjalan di purwarupa;
     S7comm dan DNP3 masuk roadmap.

2. **Agent Ringan**: single binary di server target, menanam & memantau umpan,
   low overhead, instalasi satu baris.

3. **Engine Deteksi**
   - Fingerprinting tool penyerang (nmap, masscan, hydra, dsb).
   - Korelasi event → *incident* (bukan alert terpisah-pisah).
   - Pemetaan otomatis **MITRE ATT&CK**.
   - Severity scoring berbasis tier kepercayaan.

4. **Dashboard & Alert**
   - Dashboard live (feed event, kartu incident, profil penyerang, timeline).
   - Alert real-time via Telegram atau webhook generik (dua kanal ini sudah ada
     di kode collector; aktif begitu token atau URL diisi lewat environment).

5. **Ringkasan incident**: purwarupa memakai templat deterministik yang diisi
   fakta dari event. Summarizer berbasis LLM bersifat opsional dan masuk roadmap,
   bukan bagian yang diklaim sudah berjalan.

## 4. Inovasi Teknis

1. **Deteksi berbasis umpan (deception) menggantikan anomaly detection** →
   false positive mendekati nol tanpa tuning threshold.
2. **Fingerprinting tool penyerang** dari pola koneksi/probe/banner.
3. **Korelasi event menjadi incident** dengan severity scoring.
4. **Pemetaan MITRE ATT&CK otomatis** dan output **forensics-ready**.
5. **Dukungan OT/ICS** melalui decoy protokol industri (Modbus/TCP dan HMI di
   purwarupa, S7comm/DNP3 di roadmap).
6. **Arsitektur on-prem penuh**: tanpa ketergantungan cloud, siap air-gap.

## 5. Relevansi & Manfaat untuk IT/OT TNI AD

- **Cocok untuk jaringan terisolasi**: semua komponen berjalan lokal.
- **IT + OT**: deteksi menyentuh dua domain sekaligus.
- **Early warning bersignal tinggi**: mendukung kesiapan operasi siber satuan.
- **Mengurangi beban analis**: alert sedikit namun bermakna.
- **Dasar investigasi forensik**: evidence tersimpan sejak detik pertama.
- **Mudah diimplementasikan**: instalasi satu baris, tanpa infrastruktur baru.

## 6. Arsitektur Ringkas

```
[Agent POLARIS di server IT/OT]
      |  (callback HTTPS lokal)
      v
[Collector + Detection Engine]
      |
      +--> [Dashboard live]  +--> [Alert: Telegram / Webhook]
```

Detail: lihat `02-arsitektur.md`.

## 7. Kelayakan Implementasi

- Agent ditulis sebagai satu binary statis (cross-platform).
- Collector & engine berjalan di server lokal, tanpa dependensi cloud.
- Database embedded (SQLite): nol konfigurasi.
- Instalasi satu baris: `curl -fsSL .../install.sh | bash`.
- Dapat di-scale ke banyak node satuan tanpa perubahan arsitektur.

## 8. Roadmap Pengembangan

| Fase | Target |
|---|---|
| Minggu 1 | MVP: agent decoy port + honeytoken + collector + alert |
| Minggu 2 | Engine deteksi (fingerprint, korelasi, MITRE) + dashboard |
| Minggu 3 | Decoy OT/ICS + installer + penguatan |
| Minggu 4 | Dokumentasi, video demo, slide, finalisasi |

## 9. Penutup

POLARIS menawarkan pendekatan deteksi yang **tegas, efisien, dan sesuai
kebutuhan operasional TNI AD**: membalik asumsi anomaly detection menjadi
deception defense yang deterministik, hemat sumber daya, dan siap diterapkan
baik di jaringan IT maupun OT, termasuk lingkungan terisolasi.

---

*Lampiran: dokumentasi teknis lengkap, video demo purwarupa, dan tautan proyek
disertakan bersama proposal ini.*
