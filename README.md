# portofolio-site

Portofolio jasa website UMKM. Situs statis, tanpa framework, siap diunggah
ke Cloudflare Pages. Dibuat dari mockup satu halaman `../portofolio.html` dengan isi yang
sama, dipecah per halaman.

## Isi

| Halaman | Berkas | Isi |
|---|---|---|
| Beranda | `index.html` | Hero, tiga contoh situs, ringkasan paket, empat langkah, ajakan terakhir |
| Portofolio | `portofolio/index.html` | Tiga studi kasus, tiap proyek punya tangkapan layar lebar dan telepon |
| Paket | `paket/index.html` | Yang termasuk, yang tidak termasuk, urutan pengerjaan |
| Kontak | `kontak/index.html` | Nomor WhatsApp, hal yang perlu disebutkan, alternatif tanpa jasa |
| 404 | `404.html` | Halaman tidak ditemukan |

## Halaman freelance (sedang dilepas)

Bagian marketing freelance sengaja dilepas dari situs karena kurang pas untuk calon klien.
Halamannya tidak dibangun, tautannya tidak muncul di navigasi, footer, maupun beranda.

Untuk menyalakannya lagi, ubah di `data/site.json`:

```json
"tampilkan_freelance": true
```

Lalu jalankan `python build.py`. Halaman `/freelance/`, tautan navigasi, panel komisi di
beranda, dan entri sitemap akan kembali sendiri. Semua teksnya masih tersimpan di
`site.json` pada kunci `freelance`, jadi tidak ada yang hilang.

## Struktur

```
data/site.json      semua teks, harga, daftar proyek, link WhatsApp
assets/css/         style.css (token dan alasan ada di DESIGN.md)
assets/js/          site.js (hanya menu mobile)
assets-src/         tangkapan layar asli tiga situs klien, PNG 1280 dan 390
dist/               hasil build, yang diunggah ke hosting
build.py            penyusun halaman, sekaligus pemroses gambar ke webp
```

## Cara mengubah

Hampir semua perubahan cukup di `data/site.json`: menambah proyek baru, mengubah harga,
mengganti teks bagian, atau mengubah pesan WhatsApp. Setelah itu jalankan:

```
python build.py
```

Butuh Pillow (`pip install pillow`). Hasilnya ada di `dist/`.

Menambah proyek baru: taruh `assets-src/<slug>-desktop.png` (lebar 1280) dan
`assets-src/<slug>-mobile.png` (lebar 390), lalu tambah satu entri di `data/site.json`
dengan `slug` yang sama. Build akan memotong dan mengompresnya sendiri.

## Melihat hasilnya

```
python -m http.server 8899 --directory dist
```

Lalu buka `http://localhost:8899`. Jangan buka `dist/index.html` langsung dari berkas,
karena tautan antar halaman memakai alamat akar (`/portofolio/`).

Catatan Windows: build tidak menghapus folder `dist`, hanya isinya. Itu supaya build tetap
jalan walau `dist` sedang dipakai server pratinjau. Kalau ingin ganti nomor port,
pakai port lain yang bebas.

## Deploy

Situs ini statis murni. Di Cloudflare Pages, arahkan root direktori ke `portofolio-site`
dan direktori keluaran ke `dist`. Tidak ada perintah build yang perlu dijalankan di server;
`dist/` sudah berisi semua berkas.

Setelah domainnya ada, isi `url` di `data/site.json` lalu build ulang supaya
`canonical`, `og:url`, `sitemap.xml`, dan `robots.txt` terisi.

## Aturan yang dipegang

Sama dengan `DESIGN.md`: tidak ada testimoni atau statistik karangan, tidak ada emoji,
tidak ada em dash, tidak ada tombol mati. Semua tangkapan layar adalah situs klien yang
benar-benar online dan bisa dibuka.
