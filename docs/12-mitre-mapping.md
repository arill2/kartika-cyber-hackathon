# 12 — Pemetaan MITRE ATT&CK

Peta teknik yang dicakup POLARIS. Enterprise untuk IT, ICS untuk OT.

## Enterprise ATT&CK (IT)

| Sumber umpan | Teknik | ID | Taktik |
|---|---|---|---|
| Decoy port disentuh | Network Service Scanning | T1046 | Discovery |
| Web decoy path diakses | Active Scanning | T1595 | Reconnaissance |
| Decoy login brute force | Brute Force | T1110 | Credential Access |
| Honeytoken file dibaca | File and Directory Discovery | T1083 | Discovery |
| Canary credential dipakai | Unsecured Credentials | T1552 | Credential Access |
| Honeytoken URL di-fetch | Application Layer Protocol | T1071 | Command and Control |
| Honeytoken URL di-fetch (web) | Exploit Public-Facing Application | T1190 | Initial Access |
| Valid account umpan dipakai | Valid Accounts | T1078 | Initial Access / Persistence |
| SMB decoy disentuh | SMB/Windows Admin Shares | T1021.002 | Lateral Movement |
| RDP decoy disentuh | Remote Services: RDP | T1021.001 | Lateral Movement |

## ICS ATT&CK (OT)

| Sumber umpan | Teknik | ID | Taktik |
|---|---|---|---|
| Scan decoy port OT | Remote System Discovery | T0846 | Discovery |
| Sniffing protokol OT | Network Sniffing | T0842 | Discovery |
| Modbus function code write | Manipulation of Control | T0831 | Impact |
| Modbus parameter write | Modify Parameter | T0836 | Impact |
| Login HMI palsu (default cred) | Default Credentials | T0812 | Lateral Movement |
| Login HMI palsu (akun valid) | Valid Accounts | T0859 | Lateral Movement |

## Taktik yang Dicakup (Ringkas)

- **Reconnaissance** — T1595
- **Initial Access** — T1078, T1190
- **Discovery** — T1046, T1083, T0846, T0842
- **Credential Access** — T1110, T1552
- **Lateral Movement** — T1021.001, T1021.002, T0812, T0859
- **Command and Control** — T1071
- **Impact (OT)** — T0831, T0836

## Output di Incident

Setiap incident menampilkan:
```
MITRE ATT&CK Coverage
─────────────────────
T1046  Network Service Scanning     (Discovery)
T1595  Active Scanning              (Reconnaissance)
T1110  Brute Force                  (Credential Access)
T1552  Unsecured Credentials        (Credential Access)
```

## Catatan Detection Engineering

- Gunakan **ATT&CK for ICS** untuk event OT (bukan enterprise) — detail teknis
  ini menonjol di mata juri bertema detection engineering.
- Setiap detection rule (Sigma-style) di-tag dengan teknik terkait agar coverage
  dapat diaudit.
- Roadmap: tambahkan **ATT&CK Navigator layer** untuk memvisualisasikan coverage —
  nilai tambah dokumentasi.
