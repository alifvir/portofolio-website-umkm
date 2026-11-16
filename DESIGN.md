# DESIGN.md — Portofolio Alif Virgiawan

Arahan desain untuk `portofolio-site`. Dibaca bersama skill `antislop` sebagai filter.
Identitas kuning navy diambil dari mockup awal (`../portofolio.html`) dan dipertahankan.

## Dial

ENERGY 3 / RHYTHM 3 / MOTION 1

- ENERGY 3: berani lewat warna dan bentuk, bukan lewat animasi. Kuning jadi kanvas, navy jadi garis dan teks, merah hanya di titik tawar.
- RHYTHM 3: komposisi antar bagian sengaja berbeda. Hero terbelah dengan tangkapan layar, pita fakta bergaris rambut, kartu portofolio berjajar, panel navy penuh untuk proses, satu kartu harga lebar, panel gelap miring untuk freelance.
- MOTION 1: hanya hover dan fokus, 120ms. Tidak ada animasi saat scroll, tidak ada elemen berdenyut.

## Palet

| Token | Nilai | Dipakai untuk |
|---|---|---|
| `--kuning` | #FFD23F | latar dasar halaman |
| `--kuning-muda` | #FFE79A | latar kartu kecil di atas kuning |
| `--navy` | #1B2A4A | teks utama, semua garis, panel gelap |
| `--navy-tua` | #142038 | hover tombol, dasar panel gelap |
| `--merah` | #E8483B | aksen garis dan tanda kecil, tanpa teks |
| `--merah-tua` | #C9352A | latar label harga dan panel komisi (teks putih) |
| `--kertas` | #FFFBEF | latar bagian terang |
| `--putih` | #FFFFFF | latar kartu |
| `--redup` | #525C70 | teks penjelas di atas kertas dan putih |
| `--redup-terang` | #C6CEDE | teks penjelas di atas navy |

Dua merah adalah satu keluarga: `--merah` hanya untuk garis dan tanda, `--merah-tua` hanya
kalau ada teks putih di atasnya. Alasannya kontras: putih di atas #E8483B hanya 3.86:1,
di atas #C9352A 5.22:1. Label kecil di kartu harga harus terbaca, jadi dipakai yang tua.

Kontras terukur (dihitung dari nilai hex, bukan kira-kira): navy di atas kuning 9.85:1,
navy di atas kertas 13.75:1, redup di atas kertas 6.5:1, redup di atas putih 6.72:1,
redup di atas kuning 4.66:1 (batas aman, jadi redup tidak dipakai untuk teks kecil di atas
kuning), kuning di atas navy 9.85:1, redup-terang di atas navy 9:1, putih di atas merah-tua 5.22:1.

Tidak ada warna di luar daftar ini. Tidak ada gradien, orb blur, atau glow.

## Tipografi

- Plus Jakarta Sans untuk semua, 800 untuk judul, 600 untuk label dan tombol, 400 untuk isi.
  Alasan: huruf ini sudah jadi default proyek dan punya karakter sedikit membulat yang
  cocok untuk usaha kecil, tanpa terasa seperti template SaaS. Inter sengaja tidak dipakai.
- Judul hero `clamp(2.6rem, 7vw, 5.2rem)`, letter-spacing -0.035em, `text-wrap: balance`.
- Judul bagian `clamp(1.9rem, 4vw, 3rem)`.
- Isi 1.02rem, line-height 1.65, lebar maksimum 62ch.

## Bentuk dan bayangan

- Radius dipilih kutub tajam: 6px tombol, 10px kartu dan bingkai, 2px label kecil.
  Satu-satunya lengkung besar adalah bingkai telepon di halaman portofolio (24px), karena
  bentuk perangkat memang begitu.
- Bayangan hanya satu jenis: offset keras navy `8px 8px 0`. Alasannya, di atas latar kuning
  bayangan lembut tidak terlihat dan menghilangkan kesan cetak. Tidak ada bayangan blur.
- Border selalu navy 3px atau 4px. Ini pengganti bayangan halus, jadi hierarki datang dari
  garis, bukan dari elevasi palsu.

## Bingkai tangkapan layar

Semua pratinjau memakai tangkapan layar asli dari situs klien, bukan iframe dan bukan gambar
contoh. Iframe tiga situs sekaligus berarti memuat tiga situs penuh di halaman pembuka, dan
itu terlalu mahal untuk pengunjung dari WhatsApp.

- Bar bingkai berisi nama domain aslinya (`warungmodern-bymk.pages.dev`), bukan tiga titik
  dekoratif. Bar itu jadi keterangan, bukan hiasan.
- Halaman portofolio menampilkan dua tangkapan per proyek: desktop dan telepon 390px, supaya
  klaim "bisa dibuka dari HP" ada buktinya.

## Ornamen

- Label harga berbentuk pita dengan potongan miring dan rotasi -2deg, dipakai satu kali saja
  di hero.
- Garis rambut navy sebagai pembatas bagian. Tidak ada pola latar berulang, tidak ada ikon
  dekoratif, dan tidak ada emoji di teks situs.

## Aturan yang dipegang

- Tidak ada testimoni, jumlah klien, tahun pengalaman, atau statistik karangan. Angka yang
  tampil hanya harga Rp250.000, komisi Rp50.000, dan fakta dari situs klien itu sendiri.
- Tidak ada emoji di teks, termasuk favicon.
- Tidak ada em dash.
- Setiap tautan punya tujuan nyata. Tautan WhatsApp membuka tab baru dengan `rel noopener`.
- Isi paket yang belum diputuskan (domain, jumlah halaman) disebut sebagai hal yang
  dibicarakan sebelum mulai, bukan dijanjikan.
- Setiap gambar punya `width` dan `height`, sebagian besar `loading="lazy"`, kecuali gambar
  hero yang memakai `fetchpriority="high"`.
- Warna aksen tidak dipakai untuk tombol utama. Tombol utama navy, tombol di panel gelap kuning.
