# 05 — Decoy OT/ICS

Pembeda utama untuk kriteria **"Relevansi IT/OT TNI AD" (25%)**. Peserta lain
kebanyakan cuma main di log server IT — kita sentuh domain OT/ICS (SCADA, PLC, HMI).

> **Prinsip keselamatan:** decoy OT adalah **simulasi protokol**, bukan perangkat
> nyata. Tidak terhubung ke proses fisik. 100% observasi, nol dampak operasional.

## 1. Kenapa OT Penting di Konteks TNI AD

- Satuan militer mengoperasikan **sistem OT** (fasilitas, utilitas, komando & kontrol).
- Serangan terhadap OT berdampak **fisik**, bukan cuma digital.
- Tooling deteksi OT sangat sedikit & mahal.
- Network traffic OT sering **unencrypted & deterministik** → mudah dimodelkan
  sebagai umpan.

## 2. Protokol OT yang Bisa Dijadikan Umpan

| Protokol | Port umum | Fungsi industri | Nilai sebagai umpan |
|---|---|---|---|
| **Modbus/TCP** | 502 | PLC, sensor, aktuator | Paling umum, sederhana, mudah disimulasikan |
| **S7comm** | 102 | Siemens PLC | Target populer di serangan nyata |
| **DNP3** | 20000 | Utilitas, grid | Kritis di infrastruktur |
| **EtherNet/IP** | 44818 | Rockwell/Allen-Bradley | Umum di manufaktur |
| **BACnet** | 47808 | Building automation | Fasilitas/gedung |
| **IEC 60870-5-104** | 2404 | SCADA tenaga listrik | Sangat kritikal |
| **OPC UA** | 4840 | Interoperabilitas industri | Modern, populer |

**Prioritas MVP:** Modbus/TCP (502) — paling mudah & paling ikonik.

## 3. Cara Kerja Decoy OT

1. Agent membuka listener pada port protokol OT (mis. 502).
2. Listener **merespons seolah perangkat OT asli**:
   - Modbus: membalas function code (mis. Read Holding Registers) dengan data register palsu.
   - Menerima unit ID, alamat register, dsb.
3. Setiap koneksi/interaksi dicatat sebagai event:
   - Siapa yang menghubungi (biasanya **bukan** workstation engineering normal).
   - Function code apa yang diminta (membaca vs **menulis** = red flag besar).
   - Frekuensi & pola (alat engineering? atau scanner/attacker?).
4. Event terhubung ke engine deteksi seperti umpan lain.

## 4. Decoy HMI (Web)

Banyak HMI/SCADA modern punya antarmuka web. Decoy HMI:
- Halaman login HMI palsu (mis. "SCADA HMI - Login").
- Panel dashboard palsu dengan nilai proses fiktif.
- Setiap akses/login = event.

Kombinasi decoy HMI + decoy Modbus = skenario OT yang meyakinkan untuk demo.

## 5. Deteksi & MITRE untuk OT

| Aksi attacker | MITRE (ICS) |
|---|---|
| Discovery protokol OT | T0846 Remote System Discovery / T0842 Network Sniffing |
| Modbus function code write | T0831 Manipulation of Control / T0836 Modify Parameter |
| Login ke HMI palsu | T0812 Default Credentials / T0859 Valid Accounts |
| Scan port OT | T0846 |

> Gunakan **MITRE ATT&CK for ICS** (bukan versi enterprise) untuk pemetaan OT —
> ini detail yang dicatat juri bertema detection engineering.

## 6. Realisme Decoy OT

- Unit ID & register map yang masuk akal untuk perangkat tertentu.
- Respons timing menyerupai perangkat asli (bukan instan).
- Banner/error yang konsisten dengan vendor yang diklaim.
- Jangan taruh decoy OT di host yang jelas-jelas bukan segmen OT bila ingin
  realistis — tapi untuk demo, satu host bisa menampung IT + OT decoy (jelaskan
  sebagai "sensor tunggal multi-protokol").

## 7. Batasan & Kejujuran Teknis

- Decoy OT **bukan** pengganti sensor OT pasif (SPAN/TAP) di produksi.
- Untuk lingkungan nyata, decoy OT paling tepat ditaruh di **segmen OT** atau
  **jembatan IT/OT** (paling sering jadi jalur serangan).
- Nilai utamanya: **early warning bersignal tinggi** bahwa ada pihak tak sah
  menyentuh protokol industri — bukan kontrol penuh OT.

## 8. Rencana Implementasi (MVP → Lanjut)

1. **MVP:** Modbus/TCP decoy (port 502) — respons function code dasar + logging.
2. **Tahap 2:** Decoy HMI web + S7comm basic.
3. **Tahap 3:** DNP3 + mapping ATT&CK-for-ICS lengkap + sensor multi-protokol.
