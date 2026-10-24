# POLARIS — Deception-Based Early Warning untuk Jaringan IT/OT

> Working name: **POLARIS** (tentatif). Alternatif: CanaryOne, Tripwire, Sanca.
> Bebas diganti sebelum submit.

Dokumentasi ide & blueprint untuk **Kartika Cyber Hackathon 2026** (PUSSIBERAD x Codepolitan).

---

## One-liner

> "Firewall nahan yang ketahuan. **POLARIS** nangkep yang ngumpet — karena yang
> nyentuh umpan kita, mustahil orang normal. **Zero false positive, by design.**"

---

## Apa ini?

Sistem **peringatan dini berbasis tipuan (deception)** yang ditanam di server
jaringan IT/OT. Kita tanam *umpan* (decoy port, honeytoken file, canary
credential, honeytoken URL, decoy OT/ICS) yang **tidak akan pernah disentuh
pengguna sah**. Ada yang sentuh = *intent terbukti* → alert real-time + incident
ter-korelasi + pemetaan MITRE ATT&CK.

Bukan IDS anomali (yang penuh false positive). Ini deteksi **binary**: kena = alert.

---

## Kenapa menang

1. **Zero-FP by design** — argumen terkuat vs peserta lain yang bikin ML-IDS.
2. **Attacker fingerprint** — kita tebak tool attacker (nmap/masscan/hydra) → demo wow.
3. **Detection engineering rigor** — MITRE ATT&CK + Sigma-style rules + forensics-ready evidence.
4. **IT/OT ready** — decoy Modbus/PLC/HMI, pas dengan kebutuhan TNI AD.
5. **On-prem / air-gap friendly** — nol cloud, jalan di jaringan tertutup.

---

## Hackathon Context

| Item | Detail |
|---|---|
| Penyelenggara | PUSSIBERAD (Pusat Siber TNI AD) + Codepolitan |
| Kategori | **02 DEFENSIVE SHIELD** (Penangkalan) |
| Format | Online 4 minggu → 10 finalis presentasi di Jakarta |
| Deadline submit | **15 November 2026** |
| Final | **24 November 2026** — Hotel Aston Kartika, Jakarta |
| Tim | 2–3 orang (individu diperbolehkan) |
| Hadiah | Rp 100,7 juta + Golden Ticket Bintara Siber TNI AD |

---

## Index Dokumentasi

| File | Isi |
|---|---|
| [00-overview.md](docs/00-overview.md) | Ringkasan ide, problem, solusi, kenapa menang |
| [01-proposal-solusi.md](docs/01-proposal-solusi.md) | **Draft proposal submission** (formal, siap dipakai) |
| [02-arsitektur.md](docs/02-arsitektur.md) | Arsitektur teknis, komponen, data flow, deployment |
| [03-decoy-honeytoken.md](docs/03-decoy-honeytoken.md) | Taksonomi umpan (decoy port, file, cred, URL, web) |
| [04-engine-deteksi.md](docs/04-engine-deteksi.md) | Fingerprint, korelasi, scoring, AI summarizer |
| [05-ot-ics-decoy.md](docs/05-ot-ics-decoy.md) | Decoy OT/ICS (Modbus, S7, DNP3, HMI) |
| [06-tech-stack.md](docs/06-tech-stack.md) | Stack final + justifikasi |
| [07-roadmap.md](docs/07-roadmap.md) | Roadmap mingguan + backlog harian sampai 15 Nov |
| [08-alignment-penilaian.md](docs/08-alignment-penilaian.md) | Mapping ke 5 kriteria penjurian |
| [09-demo-script.md](docs/09-demo-script.md) | Script demo final + video demo |
| [10-pitch-killer.md](docs/10-pitch-killer.md) | Pitch, analogy, objection handling juri |
| [11-submission-checklist.md](docs/11-submission-checklist.md) | Checklist deliverable & deadline |
| [12-mitre-mapping.md](docs/12-mitre-mapping.md) | Tabel pemetaan MITRE ATT&CK |

---

## Status

- [x] Riset aturan & kriteria penjurian
- [x] Konsep & arsitektur
- [ ] Register tim di Codepolitan
- [ ] Ikut Webinar Pembekalan 2 (27 Okt)
- [ ] MVP (agent + collector + alert)
- [ ] Engine deteksi + OT decoy
- [ ] Dokumentasi + video demo + slide
- [ ] Submit (deadline 15 Nov)
