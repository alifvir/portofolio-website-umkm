# DESIGN.md — Portofolio Alif Virgiawan

Arahan desain untuk `portofolio-site`. Ditulis ulang 21 November 2026, revisi
kedua: palet kembali ke kertas + navy dengan kuning sebagai aksen.

Semua angka kontras di bawah **dihitung dari nilai hex**, bukan dikira-kira.

## Dial

ENERGY 3 / RHYTHM 4 / MOTION 1

- ENERGY 3: tenang lewat ruang kosong dan tipografi, tapi kartu punya bobot.
  Fraunces diganti Newsreader; palet cerah tapi tidak menyala.
- RHYTHM 4: setiap bagian punya bentuk berbeda. Hero terbelah, pita fakta
  bergaris rambut, kisi proyek bertimbul, tiga kartu paket identik, blok
  tentang saya dua kolom, pita navy penuh untuk alasan, daftar langkah
  bernomor, akordeon tanya jawab, panel navy penutup.
- MOTION 1: hover 120ms, zoom gambar 500ms, akordeon 180ms, denyut dot 2.2s.
  Tidak ada animasi saat scroll. Semua dimatikan lewat `prefers-reduced-motion`.

## Palet

| Token | Nilai | Dipakai untuk |
|---|---|---|
| `--kertas` | #fffbef | latar dasar halaman |
| `--kertas-2` | #f6f1e2 | bagian bergantian, footer |
| `--putih` | #ffffff | kartu, bingkai gambar |
| `--navy` | #1b2a4a | teks utama, garis, tombol, panel |
| `--navy-tua` | #142038 | hover tombol |
| `--redup` | #525c70 | teks penjelas |
| `--kuning` | #ffd23f | aksen: label bidang, nomor langkah, bilah aktif nav, sorotan judul |
| `--kuning-muda` | #ffe79a | isi kotak fakta, hover kuning |
| `--merah` | #c9352a | hanya penanda diskon dan harga normal dicoret |
| `--hijau` | #1f7a4d | hanya dot penanda live |

Kenapa kuning jarang: kuning sebagai latar halaman terasa seperti poster murah.
Sebagai aksen kecil (label, nomor, penanda) ia memberi kehangatan tanpa
mengambil alih. Semua kartu berlatar putih, kuning hanya di dalamnya.

Kenapa merah hanya untuk diskon: warna itu satu-satunya yang menarik mata.
Kalau dipakai untuk tombol juga, ia kehilangan tugasnya.

## Kontras terukur

| Pasangan | Rasio | Status |
|---|---|---|
| navy / kertas | 13.75:1 | lolos |
| navy / putih | 14.22:1 | lolos |
| navy / kertas-2 | 12.60:1 | lolos |
| redup / kertas | 6.50:1 | lolos |
| redup / putih | 6.72:1 | lolos |
| kuning / navy | 9.85:1 | lolos |
| navy / kuning | 9.85:1 | lolos |
| putih / navy | 14.22:1 | lolos |
| merah / kertas | 5.04:1 | lolos |
| navy / kuning-muda | 11.61:1 | lolos |
| navy / merah | 2.73:1 | **tidak boleh dipakai** |

Batas AA adalah 4.5:1 untuk teks biasa. Yang paling mepet `merah / kertas`
di 5.04:1, jadi jangan digeser lebih terang.

Penting: **navy di atas merah hanya 2.73:1**, jadi teks di atas latar merah
harus putih, tidak boleh navy. Saat ini merah hanya dipakai sebagai teks dan
garis di atas kertas, bukan sebagai latar, sehingga aman.

Diverifikasi juga **pada hasil render**: semua teks lolos, tidak ada yang di
bawah 4.5:1.

## Tipografi

- **Newsreader** (serif) untuk semua judul. Memberi kesan penerbitan, bukan
  template SaaS. Punya italic asli untuk frasa "jadi dulu baru bayar".
- **Plus Jakarta Sans** untuk isi, label, dan tombol.
- Judul hero `clamp(2.5rem, 6.2vw, 4.6rem)`, letter-spacing -0.03em.
- Label huruf kecil 0.72rem, 800, spasi 0.13em, huruf besar semua.
- Isi 1.0125rem, line-height 1.68, lebar maksimum 68ch.

## Bentuk

- Radius: 2px label, 6px tombol, 10px kartu.
- **Semua kartu memakai bayangan keras** `6px 6px 0 navy`, tanpa blur. Ini yang
  membuat kartu terlihat timbul seperti versi pertama. Tidak ada bayangan lembut.
- Border kartu dan tombol 2-3px navy, bukan abu tipis.
- Hover kartu proyek: naik 2px, bayangan melebar ke 8px.
- Hover tombol: latar menggelap ke `--navy-tua`, teks jadi `--kuning-muda`,
  font-weight naik ke 800, dan tombol naik 2px. Perubahannya sengaja dibuat
  lebih tegas dari sekadar menggelap, sesuai permintaan "lebih bold dari warna
  dasarnya".

## Logo

Favicon bukan lagi huruf "AV". Bentuknya tiga lapis belah ketupat kuning di atas
latar navy, mengesankan tumpukan rak atau lapisan dagangan. Dibuat sebagai SVG
supaya tajam di semua ukuran.

## Kode promo

Bilah navy di paling atas, menempel saat digulir.

- Pengunjung mengetik kode, harga berubah seketika, hitungan mundur muncul.
- Kode yang tampil di halaman hanya `UMKMMAJU` (Website UMKM, 50%) dan `MURAHBANGET`
  (Company Profile, 50%). Huruf besar kecil tidak masalah.
- `THREADS50` bertanda `hanya_tautan`: tidak pernah dicetak, ditolak kalau diketik, hanya
  bisa masuk lewat tautan `?kode=THREADS50`.
- Masa berlaku **per kode**: `UMKMMAJU` 7 hari, `THREADS50` 14 hari, disimpan di localStorage
  peramban pengunjung. Tidak ada server, jadi tidak ada data pribadi terkirim.
- Hitungan muncul di dua tempat: bilah atas dan kartu paket yang kodenya dipakai.
- Tidak ada tombol batal. Hitungan berjalan sampai habis, dan perangkat itu terkunci.

### Bug gulir saat mengetik kode

Awalnya layar melompat ke atas begitu input kode difokus. Penyebabnya
`scroll-padding-top: 150px` pada `html`: peramban menganggap elemen di bilah
sticky berada jauh di atas layar, lalu menggulir untuk menyesuaikan. Diukur:
scrollY 900 jatuh ke 405 hanya karena fokus.

Perbaikannya dua lapis:

1. `scroll-padding-top` diganti `[id] { scroll-margin-top: 150px }`. Jarak saat
   lompat ke bagian tetap ada, tapi peramban tidak lagi menggulir saat fokus.
2. Penjaga di `site.js`: saat fokus masuk ke bilah promo, posisi gulir
   dikembalikan ke angka semula. Diukur sesudah perbaikan: 900 tetap 900.

## Foto

Semua pratinjau memakai tangkapan layar asli situs klien, bukan iframe dan
bukan gambar contoh. Iframe enam situs sekaligus berarti memuat enam situs
penuh di halaman pembuka, terlalu mahal untuk pengunjung dari WhatsApp.

Keenam situs sudah online, jadi semua badge di kartu dan bingkai berstatus live.

Setiap tangkapan dibuat **dua ukuran** (1100w dan 700w) dan dipilih lewat
`srcset`. Terbukti: HP 390px DPR2 mengunduh varian 700w, bukan 1100w.

## Aturan yang dipegang

- Tidak ada testimoni, jumlah klien, atau statistik karangan. Angka yang tampil
  hanya harga paket, dan fakta dari situs klien itu sendiri.
- **Tidak ada kalimat yang berakhir dengan titik dua.** Diperiksa otomatis
  setiap build.
- Tidak ada emoji, em dash, atau karakter non-ASCII. Diperiksa otomatis.
- Nama bank ditulis apa adanya (RCBC, BCA) atas permintaan pemilik situs,
  tanpa catatan perjanjian kerja.
- Klaim SEO jujur: yang dijanjikan hanya "tidak ada kesalahan teknis", bukan
  peringkat satu Google.
- Tidak menulis "alamat situs gratis" di paket UMKM, karena terkesan murah.
  Diganti "alamat web milikmu sendiri".
- Setiap gambar punya `width`/`height`, `loading="lazy"` kecuali gambar hero
  yang memakai `fetchpriority="high"`.

## Catatan pengerjaan (bug yang sudah kena)

1. **`repeat(4, 1fr)` meluber di 1024px.** Lebar minimum kolom `1fr` adalah
   `min-content`. Obatnya `repeat(4, minmax(0, 1fr))`.
2. **`.lewat` dengan `left: -9999px` menambah lebar dokumen.** Diganti
   `transform: translateY(-120%)`.
3. **`[hidden]` kalah dari `display: flex`.** Status promo dan formulirnya
   sempat tampil bersamaan. Obatnya `[hidden] { display: none !important }`,
   satu baris yang berlaku untuk seluruh halaman.
4. **`<small>mulai</small>` menempel tanpa jarak** pada Rp6.000.000. Diperbaiki
   dengan `display: block` pada `small`.
5. **Teks status promo terpotong di 390px.** Diringkas jadi
   "Kode UMKMMAJU aktif, 50%", nama paketnya dipindah ke atribut `title`.
