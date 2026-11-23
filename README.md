# portofolio-site

Portofolio jasa website UMKM. Situs statis, tanpa framework, siap diunggah
ke Cloudflare Pages.

Ditulis ulang 21 November 2026: arah visual baru (kertas, tinta hijau, emas),
empat paket harga, bilah promo mingguan berhitungan waktu, blok kredensial,
bagian cerita, dan akordeon tanya jawab.

## Isi

| Halaman | Berkas | Isi |
|---|---|---|
| Beranda | `index.html` | Hero, empat fakta, enam contoh situs, tiga paket, kredensial, cerita, empat langkah, tanya jawab, ajakan penutup |
| Portofolio | `portofolio/index.html` | Enam studi kasus, tiap proyek punya tangkapan layar lebar dan telepon |
| Paket | `paket/index.html` | Empat paket, yang tidak termasuk, urutan pengerjaan, tanya jawab |
| Kontak | `kontak/index.html` | Nomor WhatsApp, hal yang perlu disebutkan, alternatif tanpa jasa |
| 404 | `404.html` | Halaman tidak ditemukan |

## Bilah promo mingguan

Bilah merah di paling atas berisi: harga promo, harga normal dicoret, hitungan
waktu, dan tautan WhatsApp yang pesannya sudah terisi niat ambil promo.

- Siklus **Senin 00.00 WIB sampai Minggu 23.59 WIB**. Hitungan memakai WIB tetap
  (UTC+7), jadi hasilnya sama untuk pengunjung dari zona waktu mana pun.
- Saat hitungan habis, ia mulai lagi untuk minggu berikutnya. Tidak ada
  perubahan berkas yang perlu dilakukan tiap minggu.
- Mematikan sementara: `"promo": { "aktif": false }` di `data/site.json`, lalu build.
  Semua elemen promo hilang, harga tampil normal, dan skema berhenti memakai
  harga promo.

Harga ada di satu tempat: `tier` di `data/site.json`. `harga` adalah harga normal,
`harga_promo` yang tampil selama promo. Kalau diskon diganti, ubah `promo.diskon`
dan `harga_promo` bersama-sama supaya angkanya konsisten.

## Kode promo

Bilah navy di paling atas berisi formulir kode. Pengunjung mengetik kode, harga
berubah seketika, dan hitungan mundur muncul.

| Kode | Paket | Harga normal | Dengan kode | Masa berlaku | Cara masuk |
|---|---|---|---|---|---|
| `UMKMMAJU` | Website UMKM | Rp500.000 | Rp250.000 | 7 hari | diketik atau tautan |
| `THREADS50` | Website UMKM | Rp500.000 | Rp250.000 | **14 hari** | **hanya tautan** |
| `MURAHBANGET` | Company Profile | Rp1.200.000 | Rp600.000 | 7 hari | diketik atau tautan |

Masa berlaku bisa beda per kode: isi `masa_hari` pada entri kode. Kode tanpa `masa_hari`
ikut nilai global `promo.masa_hari`.

### Kode khusus tautan

`THREADS50` diberi penanda `"hanya_tautan": true`. Akibatnya:

- **Tidak pernah dicetak** di halaman. Kartu paket, panel penutup, dan halaman kontak hanya
  menyebut kode yang tidak bertanda, jadi pengunjung melihat `UMKMMAJU` saja.
- **Ditolak kalau diketik** di formulir, dengan pesan yang sama seperti kode tidak dikenal.
- **Bisa** dipakai lewat `?kode=THREADS50`.
- Namanya juga tidak ditulis di bilah atas saat aktif; yang tampil "Kode promo aktif, 50%".
  Kolom formulir tidak diisi otomatis untuk kode bertanda ini.

Batas jujurnya: kode ini **tetap terbaca di view-source**, karena tanpa server kode harus
dikirim ke peramban untuk dicocokkan. Penandanya mencegah kode tampil di layar dan mencegah
disebar dari formulir, bukan mencegah orang yang sengaja mengintip. Kalau perlu benar-benar
rahasia, harus ada backend.

`THREADS50` sengaja **14 hari, bukan 7**: calon yang membuka tautan hari ini sering baru punya
dananya di hari ke-10, dan pola satu perangkat membuat promo hangus selamanya setelah lewat.

### Tautan referal: `?kode=`

Kode bisa dibawa lewat tautan, tanpa calon mengetik apa pun:

```
https://spesialis-umkm.pages.dev/?kode=THREADS50
```

Begitu halaman dibuka, `site.js` membaca `?kode=`, mencocokkannya dengan daftar yang sama,
lalu memakai jalur `klaim()` yang juga dipakai formulir. Akibatnya perilakunya identik:
hitungan 7 hari mulai saat halaman dibuka, dan satu perangkat tetap hanya sekali klaim.

Yang perlu diketahui:

- Tautan `?kode=` **tidak menulis apa pun ke riwayat** dan tidak mengubah URL. Kalau halaman
  di-refresh dengan parameter yang sama, kode yang sudah tersimpan yang dipakai, bukan klaim baru.
- Kalau perangkat itu sudah pernah klaim dan jatahnya habis, tautan `?kode=` akan menampilkan
  pesan "Jatah promo di perangkat ini sudah terpakai" dan tidak menurunkan harga. Ini konsisten
  dengan formulir.
- Kode tidak dikenal di tautan → pesan "Kode tidak dikenali", harga tidak berubah.
- Huruf besar kecil tidak berpengaruh, sama seperti formulir.

### Urutan kejadian setelah deploy

1. Pengunjung membuka situs. Bilah navy di atas menampilkan "Punya kode promo?".
2. Dia mengetik `UMKMMAJU` (huruf besar kecil tidak berpengaruh), lalu klik **Pakai**
   atau tekan Enter.
3. Sistem mencocokkan kode dengan daftar di `data/site.json`.
   - Tidak cocok: muncul pesan "Kode tidak dikenali. Coba periksa lagi hurufnya."
     Harga tidak berubah sama sekali.
   - Kosong: muncul pesan "Kode promonya diisi dulu ya."
   - Cocok: lanjut ke langkah 4.
4. Ketiga kartu langsung berganti. Harga paket yang cocok turun 50%, harga aslinya
   dicoret di bawahnya, dan penghitung "sisa 6 hari 23:59:59" muncul di kartu itu
   dan di bilah atas. Kartu paket lain tidak berubah.
5. Hitungan mundur berjalan tiap detik. Tidak ada tombol batal.

### Satu perangkat, satu kali klaim

Setelah hitungan mundur habis, **perangkat itu tidak bisa memakai harga promo lagi**.
Bukan hanya harga yang kembali normal, tapi formulirnya juga dinonaktifkan dan
pesannya tetap tampil: "Jatah promo di perangkat ini sudah terpakai."

Mekanismenya: penanda di `localStorage` **tidak dihapus** saat promo habis. Justru
penanda yang sudah kedaluwarsa itu yang membuat sistem tahu perangkat ini pernah
klaim, lalu menolak semua kode berikutnya.

Konsekuensi yang perlu diketahui:

- Satu perangkat hanya bisa mengklaim **satu** kode, sekali. Kalau sudah pakai
  `UMKMMAJU`, kode `MURAHBANGET` di perangkat yang sama akan ditolak.
- Menghapus data situs, mode privat, atau ganti peramban akan mengosongkan penanda,
  jadi promo bisa diklaim lagi. Tanpa server, ini batas yang wajar.
- Ini juga berarti orang bisa mendapat promo lagi dengan membersihkan data peramban.
  Kalau perlu benar-benar sekali per orang, harus ada backend.

### Kalau di-refresh, kodenya masih ada?

**Ya, selama masa berlaku kode itu.** Kode disimpan di `localStorage`
peramban itu dengan nama `promoWebsiteUMKM`, berisi kode, paket, waktu mulai, dan
waktu habis. Waktu habisnya dihitung dari jam sistem (`Date.now()`), bukan jam
dinding yang bisa diubah pengunjung.

Artinya:

- Refresh, tutup tab, buka lagi halaman lain → kode tetap aktif sampai waktunya habis.
- Setelah habis, refresh pun tetap terkunci. Promo tidak kembali.
- Boolean localStorage dibersihkan (mode privat, "hapus data situs", ganti peramban) →
  penanda hilang, kode bisa diklaim lagi. Ini batas wajar tanpa server.
- Perangkat yang jamnya salah bisa mendapat hitungan yang salah. Tidak berbahaya,
  hanya angkanya bergeser.

### Kalau dibuka di HP berbeda?

**Tidak ikut.** Kode tersimpan di peramban masing-masing perangkat, jadi:

- Pengunjung yang memasukkan kode di laptop tidak otomatis mendapat diskon di HP-nya.
- Dua orang berbeda harus memasukkan kode masing-masing, dan masing-masing mendapat
  masa berlakunya sendiri.
- Kode bisa dibagikan lewat tautan `?kode=`, tapi yang tersimpan tetap di perangkat
  pengunjung. Yang membuka tautan mendapat masa berlakunya sendiri.

Ini konsekuensi memilih tanpa server. Kalau nanti ingin satu kode terikat ke satu orang,
atau ingin tahu **siapa** memakai kode apa, itu perlu backend kecil (Cloudflare Worker + KV,
gratis di kuota rendah). Bilang saja kalau mau dibuatkan.

### Mematikan atau menambah kode

- Matikan semua: `"promo": { "aktif": false }` di `data/site.json`, lalu build.
  Bilah hilang, semua harga tampil normal.
- Kode baru: tambah entri di `promo.kode` (`kode`, `paket`, `diskon`, `label`),
  lalu isi `harga_promo` pada tier dengan `kunci` yang sama.

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
data/site.json      semua teks, harga, tier, daftar proyek, link WhatsApp, tanya jawab
assets/css/         style.css (token, alasan, angka kontras ada di DESIGN.md)
assets/js/          site.js (menu ponsel dan hitungan promo)
assets-src/         tangkapan layar asli enam situs klien, PNG 1280 dan 390
dist/               hasil build, yang diunggah ke hosting
build.py            penyusun halaman, pemroses gambar, sitemap, skema JSON-LD
DESIGN.md           arah visual, token, kontras terukur, bug yang sudah kena
```

## Cara mengubah

Hampir semua perubahan cukup di `data/site.json`: menambah proyek baru, mengubah
harga atau tier, mengganti teks bagian, menambah tanya jawab, atau mengubah pesan
WhatsApp. Setelah itu jalankan:

```
python build.py
```

Butuh Pillow (`pip install pillow`). Hasilnya ada di `dist/`.

Menambah proyek baru: taruh `assets-src/<slug>-desktop.png` (lebar 1280) dan
`assets-src/<slug>-mobile.png` (lebar 390), lalu tambah satu entri di `data/site.json`
dengan `slug` yang sama. Build memotong, mengompres, dan membuat dua ukuran
otomatis (1100w dan 700w untuk `srcset`).

## Melihat hasilnya

```
python -m http.server 8899 --directory dist
```

Lalu buka `http://localhost:8899`. Jangan buka `dist/index.html` langsung dari berkas,
karena tautan antar halaman memakai alamat akar (`/portofolio/`).

Catatan Windows: build tidak menghapus folder `dist`, hanya isinya. Itu supaya build tetap
jalan walau `dist` sedang dipakai server pratinjau.

## Deploy

Situs ini statis murni. Di Cloudflare Pages, arahkan root direktori ke `portofolio-site`
dan direktori keluaran ke `dist`. Tidak ada perintah build yang perlu dijalankan di server;
`dist/` sudah berisi semua berkas.

`url` di `data/site.json` sudah terisi `https://spesialis-umkm.pages.dev`, jadi
`canonical`, `og:url`, `sitemap.xml`, dan `robots.txt` ikut terbangun. Kalau pindah
domain, ubah satu nilai itu lalu build ulang.

## SEO yang sudah terpasang

- Judul dan deskripsi per halaman, panjangnya dijaga di bawah batas Google.
- `canonical` dan `og:url` per halaman, `og:image` dari tangkapan layar hero.
- `sitemap.xml` dan `robots.txt` dibangun otomatis dari `url`.
- **JSON-LD**: `ProfessionalService` (nama, telepon, alamat, area layanan, katalog
  harga) di beranda/paket/kontak, dan `FAQPage` di beranda/paket. Semua divalidasi
  sebagai JSON yang sah setiap build.
- Satu `h1` per halaman, semua `img` punya `alt` dan `width`/`height`.

## Hasil uji (21 November 2026)

Semua dijalankan, bukan diasumsikan:

- **Nol overflow horizontal** di 32 kombinasi: 4 halaman x 8 lebar (320, 360, 375,
  390, 414, 768, 1024, 1440).
- **Kontras** semua teks di atas 4.5:1, diukur dari hasil render.
- **Tap target**: tidak ada tautan yang bertumpuk di 390px.
- **Menu ponsel**: buka, tutup, Escape, aria-expanded semua benar.
- **Akordeon**: 5 pertanyaan, buka satu tidak menutup yang lain.
- **Timer**: identik di empat zona waktu; "0 hari" tidak pernah tampil.
- **Gambar responsif**: HP DPR2 ambil varian 700w, bukan 1100w.
- **Anti-slop**: P0 = 0 di keempat halaman. P1 `K7` (focus) adalah positif palsu
  alat itu, karena ia hanya membaca HTML sedangkan `:focus-visible` ada di CSS
  eksternal. Sudah dibuktikan pada render: outline emas 2px aktif.
- Nol emoji, nol em dash, nol karakter non-ASCII.

## Aturan yang dipegang

Sama dengan `DESIGN.md`: tidak ada testimoni atau statistik karangan, tidak ada emoji,
tidak ada em dash, tidak ada tombol mati. Semua tangkapan layar adalah situs klien yang
benar-benar online dan bisa dibuka.
