# 11 — Submission Checklist (Kartika Cyber Hackathon 2026)

## Deadline
**15 November 2026** — Batas akhir submission.
Finalis diumumkan **20 Nov**, final **24 Nov 2026** di Hotel Aston Kartika, Jakarta.

---

## Yang Wajib Disubmit (Babak 1 — Penyisihan Online)

Berdasarkan halaman resmi hackathon, submission berisi:

- [ ] **Proposal solusi** → dari `01-proposal-solusi.md`
- [ ] **Dokumentasi teknis** → `docs/` ini + README repo
- [ ] **Video demo purwarupa** → script di `09-demo-script.md`
- [ ] **Link karya/project yang bisa diakses** → repo GitHub (private→share ke juri / atau public saat submit)
- [ ] **Video presentasi**
- [ ] **Slide penjelasan project**

> ⚠️ **Catatan penting:** repo ini di-set **private**. Saat submit, pastikan juri
> bisa mengakses — pilih salah satu:
> - Jadikan **public** sebelum submit, ATAU
> - **Invite** akun juri/panitia ke repo sebagai collaborator, ATAU
> - Siapkan **zip** artefak yang di-upload ke platform submit.

---

## Checklist Kualitas Dokumen

### Proposal
- [ ] Latar belakang & masalah jelas
- [ ] Solusi & inovasi tertulis tegas
- [ ] Relevansi IT/OT TNI AD ditonjolkan
- [ ] Arsitektur ringkas disertakan (diagram)
- [ ] Roadmap pengembangan
- [ ] Data tim lengkap

### Dokumentasi Teknis
- [ ] Arsitektur lengkap + diagram
- [ ] Cara install (1-line)
- [ ] Cara pakai + konfigurasi
- [ ] Struktur umpan & detection rules
- [ ] Bukti screenshot/log
- [ ] Batasan & roadmap jujur

### Video Demo
- [ ] 3–5 menit, narasi jelas
- [ ] Menampilkan end-to-end (recon → alert → incident → OT)
- [ ] Kualitas suara & gambar layak
- [ ] Ada caption / subtitle (opsional, nilai tambah)

### Video Presentasi + Slide
- [ ] ≤ 10 menit
- [ ] Struktur: masalah → solusi → demo → dampak
- [ ] Visual arsitektur & MITRE coverage
- [ ] Konsisten dengan pitch (`10-pitch-killer.md`)

---

## Checklist Fungsional Purwarupa

- [ ] Agent menanam & memantau umpan (port + file + web)
- [ ] Decoy OT (Modbus 502) berfungsi
- [ ] Event mengalir ke Collector real-time
- [ ] Incident ter-korelasi terbentuk (bukan alert mentah)
- [ ] Fingerprint tool attacker tampil
- [ ] MITRE ATT&CK mapping tampil
- [ ] Alert Telegram terkirim real-time
- [ ] Dashboard live menampilkan timeline & evidence
- [ ] Installer 1 baris berfungsi di mesin bersih

---

## Checklist Sebelum Submit (D-day)

- [ ] Semua deliverable lengkap
- [ ] Link repo sudah bisa diakses juri
- [ ] Video sudah ter-upload & playable
- [ ] Slide ter-upload
- [ ] Isi form submission di Codepolitan
- [ ] Simpan **bukti submit** (screenshot/email konfirmasi)
- [ ] Submit **≥1 hari sebelum deadline** (hindari server down di menit akhir)

---

## Timeline Pengingat

| Tanggal | Aksi |
|---|---|
| 27 Okt | Webinar pembekalan 2 |
| 4 Nov | Cek progres W2 (engine + OT) |
| 11 Nov | Mulai dokumentasi + rekam video |
| 13 Nov | Dry run demo + revisi slide |
| 14 Nov | **Submit** (jangan tunggu 15 Nov) |
| 15 Nov | Deadline resmi |
| 20 Nov | Pengumuman finalis |
| 24 Nov | Final di Jakarta |
