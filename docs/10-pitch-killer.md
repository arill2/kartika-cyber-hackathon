# 10 — Pitch Killer & Objection Handling

## 1. Tagline

> **"Firewall nahan yang ketahuan. POLARIS nangkep yang ngumpet."**

Alternatif:
- "Nol tebakan. Nol false positive."
- "Yang nyentuh umpan kami, mustahil orang normal."
- "Deception defense: deteksi deterministik untuk jaringan IT/OT."

## 2. Analogi (untuk juri non-teknis)

**Analogi rumah:** IDS anomali = satpam yang nebak "orang ini mencurigakan apa
bukan?" → banyak salah tuduh. POLARIS = kamu taruh **uang bertanda** di meja.
Siapa pun yang ambil, itu pencuri — nggak perlu nebak.

**Analogi militer:** deception adalah taktik militer klasik. Kita menempatkan
*decoy* yang membuat penyusup membuka diri.

## 3. Tiga Pilar Pitch

1. **Deterministik, bukan probabilistik.** Interaksi umpan = intent terbukti.
2. **IT + OT.** Bukan cuma server, tapi juga protokol industri.
3. **Siap lapangan.** Air-gap friendly, 1-line deploy, nol cloud.

## 4. Objection Handling (siapkan jawaban)

**Q: "Ini kan cuma honeypot biasa?"**
> Honeypot tradisional = satu decoy pasif. POLARIS = **jaringan umpan
> multi-vektor** (port, file, cred, URL, web, OT) yang **terkorelasi** menjadi
> incident, dengan **fingerprinting** & **MITRE mapping**. Ini sistem, bukan satu pot.

**Q: "Bagaimana kalau attacker pintar dan mengenali honeypot?"**
> Realisme jadi fokus desain (banner, timing, lokasi, variasi). Meski dikenali,
> biaya attacker naik dan interaksi pertama tetap tercatat. Selain itu, detection
> kami tidak bergantung pada attacker "tertipu" — cukup mereka **menyentuh**.

**Q: "AI-nya bisa halusinasi dong?"**
> AI **hanya meringkas**, tidak memutuskan. Keputusan deteksi murni deterministik
> dan auditable (rule-based). AI adalah lapisan kenyamanan operator, bukan otak.

**Q: "False positive-nya benar nol?"**
> "Hampir nol, by design." Kami tetap jujur: bisa ada edge case (user sah salah
> buka file umpan), karena itu tier kepercayaan & konteks dipakai. Tapi jauh di
> bawah IDS berbasis anomali. Kejujuran ini penting — juri menghargainya.

**Q: "Kenapa nggak pakai ML anomali saja?"**
> ML anomali = sumber false positive & butuh data latih besar. Untuk lingkungan
> militer yang butuh signal tinggi, deception deterministik lebih tepat. ML bisa
> jadi pelengkap, bukan pondasi.

**Q: "Apakah ini jalan di jaringan air-gap?"**
> Ya — seluruh komponen on-prem, nol dependensi internet. Ini justru alasan
> utama kami memilih arsitektur lokal.

**Q: "Bagaimana kalau agent-nya sendiri kena compromise?"**
> Agent berjalan dengan hak minimal, tidak menyentuh data produksi, dan tidak
> menyimpan kredensial nyata. Umpan yang ditanam bersifat *inert*.

**Q: "Skalanya gimana untuk banyak satuan?"**
> Arsitektur agent→collector memungkinkan multi-node tanpa ubah desain. Roadmap:
> PostgreSQL + kolektor terpusat + integrasi SOAR.

**Q: "Apa bedanya dengan produk komersial (Checkpoint dll)?"**
> Kami melengkapi, bukan menggantikan. Fokus kami: deception bersignal tinggi &
> visibilitas OT yang sering absen di produk umum, siap air-gap.

## 5. Kalimat yang Harus Dihindari

- ❌ "Mungkin bisa..." / "Sepertinya..." → lemahkan kredibilitas.
- ❌ Klaim berlebihan ("100% nol FP", "deteksi semua serangan").
- ❌ Terlalu teknis tanpa analogi di depan juri non-teknis.
- ❌ Menjelekkan produk lain/sponsor (Checkpoint = sponsor!).

## 6. Closing Statement

> "Ancaman siber tidak mengenal seragam — dan pertahanannya juga tidak bisa
> bergantung pada satu lapis. POLARIS menambah lapis yang paling sulit ditipu:
> **kebenaran bahwa penyusup tidak bisa menyentuh umpan tanpa membuka diri.**
> Deterministik, siap air-gap, siap lapangan."
