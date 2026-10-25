# 15: Laporan Delivery Gate (antislop)

Laporan ini adalah keluaran **Delivery Gate** dari aturan antislop, dijalankan
sebelum materi dikirim. Setiap baris PASS disertai bukti konkret, bukan klaim.

Cakupan: semua antarmuka yang dikirim, yaitu `dashboard/` (konsol operator),
`site/` (landing page untuk Link Karya), `submission/slides.html` dan
`submission/thumbnail.html`. Arah desainnya ada di `DESIGN.md`.

Cara menjalankan ulang pemeriksaan mekanis:

```bash
# 1. kontras (skrip ini bagian dari skill antislop-human, bukan repo ini)
python3 ~/.opencode/skills/antislop-human/scripts/contrast-check.py "#9aa5b1" "#161a20"

# 2. em dash pada materi yang dikirim
grep -rn "—" dashboard/ site/ submission/*.html DESIGN.md README.md docs/ || echo bersih

# 3. jangkar navigasi vs id yang benar-benar ada
python3 - <<'PY'
import re, pathlib
for p in ["site/index.html", "dashboard/index.html"]:
    h = pathlib.Path(p).read_text()
    ids = set(re.findall(r'\sid="([^"]+)"', h))
    hrefs = set(re.findall(r'href="#([^"]+)"', h))
    print(p, "anchor tanpa tujuan:", sorted(hrefs - ids) or "none")
PY

# 4. overflow horizontal di semua breakpoint (lihat prosedur di catatan di bawah)
```

---

## Blok 1: Hard Gate

| Aturan | Hasil | Bukti |
|---|---|---|
| R-02 em dash | **PASS** | `grep -rn "—"` pada `dashboard/ site/ submission/*.html DESIGN.md README.md docs/` mengembalikan nol baris. Sisa en dash pada rentang waktu seperti `0:00–0:25` bukan em dash dan memang diizinkan. |
| R-03 responsif | **PASS** | Probe iframe pada 1600, 1440, 1024, 900, 760, 430, 360 piksel: `overflow` negatif di semua lebar dan `offenders=0`. |
| R-17 angka bersumber | **PASS** | 234, 1, 410, 0, 12, 32, 10, 2 semuanya dari satu run nyata, dicatat di `docs/14-bukti-demo.md`. Bilah angka di landing page menyebut sumbernya secara terang. |
| R-18 testimoni | **PASS** | Tidak ada bagian testimoni, tidak ada avatar, tidak ada nama atau jabatan rekaan. |
| R-23 aset dikonfirmasi | **PASS** | Tidak ada foto orang atau avatar yang dibuat. Lambang POLARIS adalah motif geometri (segi enam dan titik) yang dipakai konsisten sebagai penanda identitas, dijelaskan di `DESIGN.md`, dan bukan logo perusahaan nyata. |
| R-24 navigasi | **PASS** | 8 jangkar di landing page dan 1 jangkar di dashboard semuanya menuju `id` yang ada. Tidak ada tautan ke halaman yang belum dibuat. |
| R-25 kontras | **PASS** | Diukur dengan `contrast-check.py`: teks `#e9edf2` pada panel `#161a20` = 14.85:1; teks sekunder `#9aa5b1` pada `#161a20` = 6.98:1 dan pada `#1c2128` = 6.47:1; aksen `#5eead4` pada `#0e1116` = 12.78:1 dan pada `#161a20` = 11.80:1. Ambang warna tingkat keparahan: CRITICAL 6.29:1, HIGH 8.56:1, MEDIUM 10.40:1, LOW 10.13:1. Batas kartu interaktif `#647082` terhadap `#161a20` = 3.48:1, di atas ambang 3:1 untuk elemen non-teks. |
| R-26 elemen interaktif | **PASS** | Tombol kartu incident adalah elemen `<button>` sungguhan yang membuka modal. Tombol di dalam modal menutup modal. Navigasi landing page memakai `href="#..."` ke bagian yang ada. Tautan repositori memakai URL publik sungguhan. Tidak ada kontrol mati. |
| R-27 tiga keadaan | **PASS** | `dashboard/app.js` menangani keadaan kosong ("Belum ada incident. Sistem bersih, nol alert"), memuat ("Memuat detail incident…"), dan galat ("Tidak dapat memuat feed: …"), plus penangan `window.onerror` yang menampilkan banner galat. Ambang 6 detik tanpa snapshot memunculkan keadaan galat koneksi. |
| R-28 FAQ | **PASS** | Tidak ada bagian FAQ sama sekali. |
| R-32 akses keyboard | **PASS** | Kartu incident dapat dijangkau dengan Tab dan diaktifkan dengan Enter atau Space. `Escape` menutup modal, `Tab` di dalam modal terkurung lewat `trapTab`. Ada tautan lewati ke konten. Gaya `:focus-visible` ada di 3 aturan CSS pada kedua lembar gaya, dan tidak ada `outline: none` tanpa pengganti. |
| R-33 tanpa penyuntingan lewat skrip | **PASS** | `grep` untuk `str.replace`, `sed -i`, dan pola patch pada `scripts/ installer/ demo/` tidak menemukan apa pun. Semua fitur ditulis di sumbernya. |
| R-34 setiap tema | **PASS (tidak berlaku)** | Hanya satu tema yang dikirim, yaitu gelap, dengan alasan tertulis di `DESIGN.md` (produk ini terminal pemantauan yang dilihat dalam waktu lama di ruang kendali). Tidak ada tombol pengalih tema, jadi tidak ada mode kedua yang bisa rusak. |
| R-35 dijalankan sebelum dikirim | **PASS** | Collector dan agen berjalan di host ini; `/healthz` menjawab `ok`; `/api/stats` mengembalikan `events 234, incidents 1, suppressed_events 2, false_positives 0`. Tampilan dashboard, detail incident, dan tampilan mobile direkam jadi berkas di `screenshot/`. |
| R-36 klaim tanpa bukti | **PASS** | Tidak ada klaim kepatuhan (SOC 2, ISO 27001) dan tidak ada klaim performa. Batasan disebut terbuka di `README.md`, termasuk bahwa atribusi tool berbasis pola dan bahwa decoy OT adalah simulasi. |
| R-37 arah desain | **PASS** | `DESIGN.md` ada dan berisi identitas, palet, tipografi, aturan salinan, dial, serta tabel referensi. |
| R-38 konten nyata | **PASS** | Semua angka berasal dari run nyata. Yang belum dibangun disebut sebagai roadmap, bukan diklaim sudah ada: S7comm, DNP3, dan ringkasan berbasis LLM. |

---

## Blok 2: Purpose-Gate

| Aturan | Hasil | Alasan tertulis |
|---|---|---|
| R-01 gradien dan glow | **PASS** | Tidak ada gradien. Glow hanya satu, pada kartu incident tingkat CRITICAL, untuk menandai satu hal yang paling mendesak di layar. |
| R-04 ikon | **PASS** | Satu lambang geometri dan satu ikon per bagian. Semua relevan dengan isinya (port, berkas, perangkat OT, tunjuk ukur). Tidak ada ikon percikan atau robot. |
| R-06 tipografi | **PASS** | Satu keluarga sans untuk teks dan satu monospace khusus angka dan pengenal. Monospace dipakai karena kolom angka harus rata dan bisa dibandingkan cepat, dan ini peralatan pemantauan. |
| R-07 latar | **PASS** | Tidak ada latar kotak-kotak atau kertas grafik. Latarnya permukaan gelap polos. |
| R-08 panah tombol | **PASS** | Tidak ada panah hiasan pada tombol. |
| R-09 lencana | **PASS** | Tidak ada lencana kapsul. Label tingkat keparahan adalah teks tingkat keparahan yang memang berfungsi. |
| R-10 glassmorphism | **PASS** | Tidak dipakai sama sekali. |
| R-12 bayangan | **PASS** | Tidak ada bayangan. Pemisahan dibuat dengan garis sambungan 1 piksel, sesuai bahasa desain instrumentasi. |
| R-13 glow berlebihan | **PASS** | Glow hanya pada satu tingkat keparahan, lihat R-01. |
| R-14 kartu seragam | **PASS** | Kartu incident berbeda tinggi mengikuti jumlah bukti, dan kartu dengan tingkat CRITICAL punya perlakuan berbeda. Kartu yang lebih rendah meredup, jadi hierarki terlihat dari komposisi, bukan dari ukuran seragam. |
| R-19 animasi | **PASS** | Gerak hanya pada transisi keadaan dan denyut penanda "live", dengan `prefers-reduced-motion` yang mematikannya. Dial MOTION di `DESIGN.md` bernilai rendah, dan kenyataannya memang begitu. |
| R-22 ilustrasi | **PASS** | Tidak ada ilustrasi stok. Yang tampil adalah tangkapan layar produk yang sebenarnya. |

---

## Blok 3: Kegiatan dan Keaktifan

| Butir | Hasil | Bukti |
|---|---|---|
| Dial dinyatakan | **PASS** | `DESIGN.md` menetapkan ENERGY, RHYTHM, dan MOTION secara eksplisit. |
| Konsisten dengan dial | **PASS** | Bagian-bagian landing page bergantian komposisinya (naratif, kisi bersambung, tabel spesifikasi, baris angka), bukan pola judul dan kartu yang sama berulang. |
| Titik fokus per layar | **PASS** | Landing page: satu judul besar. Dashboard: satu baris pembacaan utama. |
| Ruang kosong struktural | **PASS** | Jarak antar bagian dipakai untuk memisahkan urutan baca, bukan sisa ruang. |
| Satu aksen sengaja | **PASS** | Satu warna aksen teal, dipakai hanya pada fokus, keadaan aktif, dan penanda langsung. |
| Motif identitas | **PASS** | Sambungan 1 piksel antar bidang dan format label serta nilai yang konsisten, dipakai di dashboard, landing page, slide, dan thumbnail. |
| Design Read dinyatakan | **PASS** | Tercatat di `DESIGN.md` sebelum pengerjaan. |

---

## Blok 4: Kualitas dan Kunci Konsistensi

| Butir | Hasil | Bukti |
|---|---|---|
| C-1 kejelasan maksud | **PASS** | Setiap keputusan besar punya alasan satu baris di `DESIGN.md`. |
| C-2 kelengkapan fungsi | **PASS** | Tidak ada kontrol tanpa perilaku. |
| C-3 komposisi dari konten | **PASS** | Bagian landing page mengikuti urutan argumen produk: masalah, pembalikan, umpan, alur, bukti, cara menjalankan, batas. |
| C-4 daya tahan | **PASS** | Tahan di keadaan kosong, memuat, galat, di semua breakpoint, dan tanpa tetikus. |
| C-5 bukti di atas klaim | **PASS** | Lihat R-17 dan `docs/14-bukti-demo.md`. |
| R-05 pola tata letak | **PASS** | Tidak ada pola bawaan seperti hero plus tiga kartu, tidak ada "Trusted By", tidak ada footer empat kolom. |
| R-11 radius | **PASS** | Radius kecil dan konsisten (3 sampai 6 piksel). Tidak ada elemen berbentuk kapsul. |
| R-15 ajakan bertindak | **PASS** | Ajakan spesifik: "Lihat log insiden nyata" dan "Cara menjalankan", bukan "Mulai" atau "Pelajari lebih lanjut". |
| R-16 kata pemasaran | **PASS** | Tidak ada kata seperti "revolusioner", "mulus", atau "terdepan". |
| R-20 identitas | **PASS** | Kalau nama produk ditukar, tata letak bersambung dan bahasa angka yang rata ini tetap khas peralatan pemantauan, bukan pola SaaS umum. |
| R-21 mode gelap | **PASS** | Gelap dipilih dengan alasan produk tertulis di `DESIGN.md`, bukan karena "terlihat teknologi". |
| R-29 palet | **PASS** | Netral arang, satu aksen teal, ditambah tangga warna tingkat keparahan yang memang membawa makna. |
| R-30 bukan tiruan | **PASS** | Tidak meniru Linear, Vercel, Stripe, atau Notion. Tabel referensi Awwwards di `DESIGN.md` hanya dipakai untuk tata bahasa visual, dan tidak ada yang disalin. |
| R-31 alasan satu baris | **PASS** | Semua keputusan besar tercatat di `DESIGN.md`. |

---

## Hasil Akhir

Semua butir **PASS**. Tidak ada **FAIL** dan tidak ada jawaban yang seharusnya
"tidak" pada Blok 1 maupun Blok 4, dan tidak ada jawaban yang seharusnya "ya"
pada Blok 3.

Catatan: laporan ini memeriksa materi yang dikirim (antarmuka dan dokumen
pengantar). Video demo belum direkam, jadi belum masuk cakupan. Sebelum video
diunggah, ulangi pemeriksaan em dash dan pastikan angka di video cocok dengan
`docs/14-bukti-demo.md`.
