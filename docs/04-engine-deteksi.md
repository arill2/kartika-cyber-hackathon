# 04 — Engine Deteksi

Otak POLARIS. Empat lapis: **fingerprint → correlation → MITRE mapping → severity**,
plus AI summarizer opsional.

## 1. Attacker Fingerprinting

Menebak tool penyerang dari pola interaksi. Ini fitur demo paling "wow".

### 1.1 Sinyal yang dipakai
- **Pola scan:** urutan port yang disentuh, kecepatan, spacing antar-koneksi.
- **Probe payload:** byte pertama yang dikirim (nmap NSE punya signature khas).
- **Banner interaction:** apakah attacker membaca banner, lalu kirim apa.
- **TLS handshake (opsional):** JA3/JA4 fingerprint.
- **User-Agent (web decoy):** `nmap`, `masscan`, `curl/8.x`, `python-requests`, dsb.

### 1.2 Heuristik contoh

| Tool | Ciri yang mudah dikenali |
|---|---|
| **nmap** | Probe spesifik NSE, urutan scan terurut, sering ada banner grab |
| **masscan** | Scan sangat cepat, banyak port dalam waktu sangat singkat, SYN-heavy |
| **hydra / medusa** | Auth attempt berulang terstruktur ke decoy SSH/MySQL |
| **gobuster / dirb** | Burst request ke banyak web path (404-heavy) |
| **curl / wget** | User-Agent khas, request tunggal terarah |
| **ZMap** | Pola scan internet-wide, spacing khas |
| **sqlmap** | Probe SQLi ke decoy DB/path |

> Catatan: fingerprint bersifat **best-effort**. Bila ragu → tampilkan "unknown scanner"
> beserta ciri-cirinya (jangan salah tebak; akurasi > gengsi).

## 2. Correlation Engine

Alih-alih mengirim 40 alert raw, gabungkan menjadi **incident**.

### 2.1 Kunci korelasi
- **Source IP** sebagai dimensi utama.
- **Jendela waktu** (mis. 15 menit) untuk menggabungkan event berurutan.
- **Chain kill-chain:** recon → access attempt → credential use → movement.

### 2.2 Contoh pembentukan incident
```
IP 203.0.113.7 dalam 4 menit:
  • koneksi ke 12 decoy port        (T1046 Network Service Scanning)
  • 3x hit web decoy /.env          (T1595 Active Scanning)
  • 2x auth attempt decoy SSH       (T1110 Brute Force)
  → INCIDENT: "Attempted Intrusion — active scanning + brute force"
    severity: HIGH
```

### 2.3 Skoring incident
```
score = Σ (bobot_tier × jenis) + bonus_variasi + bonus_kecepatan
severity:
  >= X  → CRITICAL (mis. canary cred dipakai / >5 umpan variatif)
  >= Y  → HIGH
  >= Z  → MEDIUM
  else  → LOW
```
(Threshold final ditentukan saat tuning; dokumentasikan agar auditable.)

## 3. MITRE ATT&CK Mapping

Setiap event/incident dipetakan otomatis. Tabel lengkap: `12-mitre-mapping.md`.

Contoh:
| Sumber umpan | Teknik |
|---|---|
| Decoy port | T1046 Network Service Scanning |
| Web decoy path | T1595 Active Scanning |
| Decoy login brute | T1110 Brute Force |
| Honeytoken file | T1083 File and Directory Discovery |
| Canary credential | T1552 Unsecured Credentials |
| Decoy OT port | T0846 (ICS: Remote System Discovery) |
| Honeytoken URL | T1071 Application Layer Protocol / T1190 |

Output: tiap incident menampilkan daftar teknik + taktik (Reconnaissance, Initial
Access, Discovery, Credential Access, Lateral Movement).

## 4. Severity Model

Severity = kombinasi **tier kepercayaan** + **jenis** + **konteks**:

- T1 (honeytoken/cred/URL) → umumnya High–Critical.
- T2 (port/web/OT) → Medium–High.
- T3 (korelasi) → naik satu tingkat bila mencakup ≥2 kategori umpan.

Override penting:
- Canary credential dipakai → **Critical** (hampir pasti compromise).
- Decoy OT disentuh → **High** (potensi ancaman ke proses fisik).

## 5. AI Summarizer (Opsional)

Mengubah alert teknis menjadi narasi singkat untuk operator cepat paham.

**Input:** data incident (IP, jenis event, tool dugaan, MITRE, timeline).
**Output:** 2–4 kalimat Bahasa Indonesia, mis.:
> "IP 203.0.113.7 melakukan pemindaian aktif terhadap 12 port umpan dan 3
> endpoint admin dalam 4 menit, lalu mencoba brute force SSH. Ciri mengarah ke
> scanner otomatis (kemungkinan nmap + hydra). Tidak ada aktivitas sah dari IP ini."

**Penting:** AI hanya *meringkas*, bukan *memutuskan*. Keputusan deteksi tetap
deterministik & auditable. Ini menjawab kekhawatiran "AI halusinasi" saat ditanya juri.

## 6. Detection Rules (Sigma-style)

Contoh aturan (format dekat Sigma agar familiar bagi detection engineer):

```yaml
title: POLARIS - Decoy Port Connection
id: polaris-decoy-port
status: experimental
description: Koneksi ke port umpan (tidak ada layanan sah)
logsource:
  product: polaris
  category: decoy_network
detection:
  selection:
    event_type: decoy_connection
  condition: selection
level: medium
tags:
  - attack.discovery
  - attack.t1046
```

Aturan lain: `decoy_file_access` (T1083), `canary_cred_used` (T1552),
`web_decoy_hit` (T1595), `decoy_login_bruteforce` (T1110), `decoy_ot_touch` (T0846).

## 7. Output Artefak

Setiap incident menyimpan (forensics-ready):
- Timeline event (timestamp + tipe).
- Sumber IP (+ geo opsional).
- Payload/probe mentah (hex/printable, redacted bila perlu).
- Dugaan tool + tingkat keyakinan.
- Daftar teknik MITRE.
- Hash evidence (integritas).
