"""Build situs portofolio Alif Virgiawan.

Sumber data:
  data/site.json          nama, harga, komisi, teks semua bagian, daftar proyek
  assets-src/*.png        tangkapan layar asli tiga situs klien (desktop dan telepon)

Hasil: dist/ siap diunggah ke Cloudflare Pages.

Jalankan: python build.py
"""

import json
import os
import shutil
from html import escape
from urllib.parse import quote

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "assets-src")
DIST = os.path.join(ROOT, "dist")
IMG = os.path.join(DIST, "assets", "img")

SITE = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8-sig"))

NAMA = SITE["nama"]
PROYEK = {p["slug"]: p for p in SITE["proyek"]}

# Halaman freelance bisa dilepas dari situs tanpa dihapus, cukup lewat data/site.json.
FREELANCE = bool(SITE.get("tampilkan_freelance"))

# Proyek yang tangkapan layarnya dipakai di hero beranda.
SOROT = "perfect-flowers"


def rupiah(n):
    return "Rp" + format(n, ",d").replace(",", ".")


def tulis(path, isi):
    tujuan = os.path.join(DIST, path)
    os.makedirs(os.path.dirname(tujuan) or DIST, exist_ok=True)
    with open(tujuan, "w", encoding="utf-8", newline="\n") as f:
        f.write(isi)


def kosongkan(folder):
    """Hapus isi folder, tapi bukan foldernya.

    Di Windows, folder yang sedang dipakai server pratinjau tidak bisa dihapus,
    padahal isinya tetap bisa diganti. Jadi folder dipertahankan.
    """
    if not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)
        return
    for nama in os.listdir(folder):
        jalur = os.path.join(folder, nama)
        if os.path.isdir(jalur):
            shutil.rmtree(jalur)
        else:
            os.remove(jalur)


# ---------------------------------------------------------------- gambar
def siapkan_gambar():
    """Tangkapan layar dipotong ke rasio bingkai, lalu disimpan sebagai webp."""
    kosongkan(IMG)

    hasil = {}
    for p in SITE["proyek"]:
        slug = p["slug"]

        # desktop: 1280x900 dipotong ke 1280x830 supaya sama dengan rasio bingkai
        im = Image.open(os.path.join(SRC, slug + "-desktop.png")).convert("RGB")
        im = im.crop((0, 0, im.width, round(im.width * 830 / 1280)))
        im = im.resize((1100, round(im.height * 1100 / im.width)), Image.LANCZOS)
        im.save(os.path.join(IMG, slug + "-desktop.webp"), "WEBP", quality=84, method=6)
        hasil[slug] = {"desktop": ("assets/img/%s-desktop.webp" % slug, im.width, im.height)}

        # telepon: 390x844, dipakai di halaman portofolio
        hp = Image.open(os.path.join(SRC, slug + "-mobile.png")).convert("RGB")
        hp = hp.resize((340, round(hp.height * 340 / hp.width)), Image.LANCZOS)
        hp.save(os.path.join(IMG, slug + "-mobile.webp"), "WEBP", quality=82, method=6)
        hasil[slug]["mobile"] = ("assets/img/%s-mobile.webp" % slug, hp.width, hp.height)

    return hasil


# ---------------------------------------------------------------- tautan
def wa_tautan(pesan=None):
    nomor = (SITE.get("wa") or "").strip().replace("+", "").replace(" ", "").replace("-", "")
    return "https://wa.me/%s?text=%s" % (nomor, quote(pesan or SITE["pesan"]["umum"]))


def tombol_wa(teks, pesan=None, kelas="tombol"):
    return ('<a class="%s" href="%s" target="_blank" rel="noopener">%s</a>'
            % (kelas, escape(wa_tautan(pesan)), escape(teks)))


# ---------------------------------------------------------------- kerangka
def nav_aktif(aktif, kunci, href, teks):
    tanda = ' aria-current="page"' if aktif == kunci else ""
    return '<li><a href="%s"%s>%s</a></li>' % (href, tanda, teks)


def nav_freelance(aktif):
    if not FREELANCE:
        return ""
    return nav_aktif(aktif, "freelance", "/freelance/", "Freelance")


def kepala(judul, deskripsi, aktif, path):
    kanon = og_url = ""
    if SITE.get("url"):
        akar = SITE["url"].rstrip("/")
        kanon = '<link rel="canonical" href="%s%s">' % (akar, path)
        og_url = '<meta property="og:url" content="%s%s">' % (akar, path)
    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#FFD23F">
<title>{escape(judul)}</title>
<meta name="description" content="{escape(deskripsi)}">
{kanon}
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(judul)}">
<meta property="og:description" content="{escape(deskripsi)}">
<meta property="og:image" content="/assets/img/{SOROT}-desktop.webp">
{og_url}
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
<a class="skip" href="#utama">Lewati ke isi utama</a>
<header class="site-head">
  <div class="wrap site-head__row">
    <a class="merek" href="/">
      <strong>{escape(NAMA)}</strong>
      <small>{escape(SITE["peran"])}</small>
    </a>
    <button class="nav-tombol" type="button" data-nav-tombol aria-expanded="false" aria-controls="nav-utama">
      <span class="nav-tombol__garis" aria-hidden="true"></span> Menu
    </button>
    <nav class="nav" id="nav-utama" data-nav data-terbuka="false" aria-label="Navigasi utama">
      <ul>
        {nav_aktif(aktif, "portofolio", "/portofolio/", "Portofolio")}
        {nav_aktif(aktif, "paket", "/paket/", "Paket")}
        {nav_freelance(aktif)}
        {nav_aktif(aktif, "kontak", "/kontak/", "Kontak")}
      </ul>
    </nav>
    <div class="head-cta">
      {tombol_wa("Tanya lewat WhatsApp", SITE["pesan"]["umum"], "tombol tombol--kecil")}
    </div>
  </div>
</header>
<main id="utama">
"""


def kaki():
    return f"""</main>
<footer class="site-foot">
  <div class="wrap">
    <div class="foot-baris">
      <p>{escape(NAMA)}, {escape(SITE["peran"].lower())} di Tangerang.</p>
      <ul class="foot-nav">
        <li><a href="/portofolio/">Portofolio</a></li>
        <li><a href="/paket/">Paket {rupiah(SITE["harga"])}</a></li>
        {f'<li><a href="/freelance/">Freelance</a></li>' if FREELANCE else ""}
        <li><a href="/kontak/">Kontak</a></li>
      </ul>
    </div>
    <div class="foot-baris">
      <p>WhatsApp <a href="{escape(wa_tautan())}" target="_blank" rel="noopener">{escape(SITE["wa_tampil"])}</a></p>
      <p>&copy; <span id="tahun">2026</span> {escape(NAMA)}.</p>
    </div>
  </div>
</footer>
<script src="/assets/js/site.js" defer></script>
<script>document.getElementById("tahun").textContent = new Date().getFullYear();</script>
</body>
</html>
"""


def bingkai_desktop(p, g, kelas="", lazy=True):
    f, w, h = g[p["slug"]]["desktop"]
    muat = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return f"""<figure class="bingkai {kelas}">
  <figcaption class="bingkai__bar"><span>{escape(p["domain"])}</span></figcaption>
  <a class="bingkai__isi" href="{escape(p["url"])}" target="_blank" rel="noopener">
    <img src="/{f}" alt="Tangkapan layar beranda {escape(p["nama"])} di layar lebar" width="{w}" height="{h}"{muat} decoding="async">
  </a>
</figure>"""


def kartu_proyek(p, g):
    return f"""<article class="kartu-proyek">
  {bingkai_desktop(p, g)}
  <div class="kartu-proyek__isi">
    <span class="kartu-proyek__bidang">{escape(p["bidang"])}</span>
    <h3>{escape(p["nama"])}</h3>
    <p>{escape(p["ringkas"])}</p>
    <div class="kartu-proyek__aksi">
      <a class="tombol tombol--kecil" href="/portofolio/#{p["slug"]}">Lihat rincian</a>
      <a class="tautan-garis" href="{escape(p["url"])}" target="_blank" rel="noopener">Buka situs</a>
    </div>
  </div>
</article>"""


def blok_kasus(p, g):
    f_m, w_m, h_m = g[p["slug"]]["mobile"]
    isi = "".join("<li>%s</li>" % escape(i) for i in p["isi"])
    return f"""<article class="kasus" id="{p['slug']}">
  <div class="kasus__kepala">
    <h2>{escape(p["nama"])}</h2>
    <p class="kasus__meta">{escape(p["bidang"])} &middot; {escape(p["kota"])} &middot; {escape(p["domain"])}</p>
  </div>
  <div class="kasus__gambar">
    {bingkai_desktop(p, g)}
    <figure class="telepon">
      <a class="telepon__isi" href="{escape(p["url"])}" target="_blank" rel="noopener">
        <img src="/{f_m}" alt="Beranda {escape(p["nama"])} di layar telepon" width="{w_m}" height="{h_m}" loading="lazy" decoding="async">
      </a>
    </figure>
  </div>
  <div class="kasus__teks">
    <div class="kasus__blok">
      <h3>Keadaannya</h3>
      <p>{escape(p["masalah"])}</p>
    </div>
    <div class="kasus__blok">
      <h3>Yang dikerjakan</h3>
      <p>{escape(p["solusi"])}</p>
    </div>
    <div class="kasus__blok">
      <h3>Isi situsnya</h3>
      <ul class="kasus__daftar">{isi}</ul>
    </div>
    <div class="kasus__blok">
      <h3>Catatan</h3>
      <p class="kasus__fakta">{escape(p["fakta"])}</p>
    </div>
  </div>
  <div class="kasus__aksi">
    <a class="tombol" href="{escape(p["url"])}" target="_blank" rel="noopener">Buka {escape(p["domain"])}</a>
    {tombol_wa("Mau yang seperti ini", SITE["pesan"]["klien"], "tombol tombol--putih")}
  </div>
</article>"""


# ---------------------------------------------------------------- halaman
def halaman_beranda(g):
    p = PROYEK[SOROT]
    f_hp, w_hp, h_hp = g[SOROT]["mobile"]
    kartu = "".join(kartu_proyek(q, g) for q in SITE["proyek"])
    langkah = "".join(
        """<li><div><h3>%s</h3><p>%s</p></div></li>""" % (escape(l["nama"]), escape(l["teks"]))
        for l in SITE["proses"]
    )
    paket = "".join(
        """<li><strong>%s</strong><span>%s</span></li>""" % (escape(x["nama"]), escape(x["teks"]))
        for x in SITE["paket"]
    )
    # Nomor bagian menyesuaikan: saat freelance dilepas, penutup naik jadi 04.
    nomor_tutup = "05" if FREELANCE else "04"
    return kepala(
        f"{NAMA} | Jasa website UMKM {rupiah(SITE['harga'])}, bayar setelah jadi",
        "Jasa pembuatan website untuk UMKM. Harga satu paket Rp250.000, revisi sampai cocok, "
        "bayar setelah website jadi, tanpa tagihan bulanan. Tiga contoh hasil kerja bisa dibuka langsung.",
        "beranda",
        "/",
    ) + f"""
<section class="hero">
  <div class="wrap hero__isi">
    <div class="hero__teks">
      <h1>Website untuk usahamu, <span>jadi dulu baru bayar.</span></h1>
      <p>Saya membuat website untuk usaha kecil: warung, toko bunga, jamu, dan sejenisnya. Kamu lihat hasilnya dari HP sendiri dulu, baru bicara soal bayaran.</p>
      <div class="hero__aksi">
        {tombol_wa("Tanya lewat WhatsApp")}
        <a class="tombol tombol--putih" href="#contoh">Lihat tiga contoh</a>
      </div>
      <div class="pita-harga">
        <small>satu paket</small>
        <strong>{rupiah(SITE["harga"])}</strong>
      </div>
      <p class="hero__kecil">Sudah termasuk penulisan teks dan penyesuaian tampilan di HP. Tidak ada tagihan bulanan.</p>
    </div>
    <div class="hero__latar">
      {bingkai_desktop(p, g, lazy=False)}
      <div class="hero__kaki">
        <p class="hero__catatan">{escape(p["nama"])}, {escape(p["bidang"].lower())} di {escape(p["kota"])}.</p>
        <figure class="hero__telepon">
          <img src="/{f_hp}" alt="Tampilan {escape(p["nama"])} di layar telepon" width="{w_hp}" height="{h_hp}" loading="lazy" decoding="async">
        </figure>
      </div>
    </div>
  </div>
</section>

<div class="wrap">
  <ul class="fakta">
    <li><strong>Satu harga</strong><span>{rupiah(SITE["harga"])} untuk satu website, bukan per halaman yang dihitung terpisah.</span></li>
    <li><strong>Bayar setelah jadi</strong><span>Kamu periksa hasilnya dulu. Pembayaran dilakukan setelah kamu setuju.</span></li>
    <li><strong>Revisi sampai cocok</strong><span>Bagian yang mau diubah sebutkan saja, saya kerjakan.</span></li>
    <li><strong>Tanpa langganan</strong><span>Sekali bayar, situsnya tetap milikmu setelah diserahkan.</span></li>
  </ul>
</div>

<section class="bagian bagian--kertas" id="contoh">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="nomor">01</span>
        <h2>Tiga situs yang sudah online.</h2>
      </div>
      <p class="kepala-bagian__teks">Bukan gambar contoh. Ketiga tautan di bawah bisa dibuka sekarang, dan isinya dipakai pemiliknya untuk berjualan.</p>
      <a class="tombol tombol--kecil kepala-bagian__tautan" href="/portofolio/">Lihat rinciannya</a>
    </div>
    <div class="grid-proyek">{kartu}</div>
  </div>
</section>

<section class="bagian">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="nomor">02</span>
        <h2>Apa saja yang termasuk.</h2>
      </div>
      <p class="kepala-bagian__teks">Satu paket untuk semua. Yang membedakan hanya berapa banyak isi yang perlu ditampilkan.</p>
      <a class="tombol tombol--kecil kepala-bagian__tautan" href="/paket/">Rincian paket</a>
    </div>
    <ul class="daftar-paket">{paket}</ul>
  </div>
</section>

<section class="bagian bagian--kertas">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="nomor">03</span>
        <h2>Empat langkah, tanpa istilah rumit.</h2>
      </div>
      <p class="kepala-bagian__teks">Kamu tidak perlu menyiapkan apa pun yang rapi. Yang penting ada info usaha dan nomor WhatsApp.</p>
    </div>
    <ol class="langkah">{langkah}</ol>
  </div>
</section>
{panel_freelance()}
{blok_penutup(nomor_tutup)}
""" + kaki()


def panel_freelance():
    """Bagian ajakan marketing freelance. Kosong kalau dilepas dari situs."""
    if not FREELANCE:
        return ""
    syarat = "".join("<li>%s</li>" % escape(s) for s in SITE["freelance"]["syarat"])
    return f"""
<section class="panel">
  <div class="wrap panel__isi">
    <div>
      <span class="nomor">04</span>
      <h2>Punya kenalan pemilik usaha? Bisa dapat komisi.</h2>
      <p>Kalau kamu mempertemukan saya dengan pemilik UMKM yang jadi membuat website, ada komisi untukmu. Tidak perlu bisa coding, tidak perlu menyiapkan modal.</p>
      <ul class="periksa">{syarat}</ul>
      <div class="panel__aksi">
        <a class="tombol tombol--kuning" href="/freelance/">Cara ikutnya</a>
        {tombol_wa("Daftar lewat WhatsApp", SITE["pesan"]["freelance"], "tombol tombol--putih")}
      </div>
    </div>
    <div class="angka-bungkus">
      <div class="angka-pita">
        <small>komisi per klien</small>
        <strong>{rupiah(SITE["komisi"])}</strong>
        <span>dibayar setelah klien melunasi</span>
      </div>
    </div>
  </div>
</section>
"""


def blok_penutup(nomor):
    """Ajakan terakhir. Jadi panel navy saat bagian freelance dilepas, supaya
    ritme terang-gelap halaman tidak hilang dan tidak ada dua panel gelap berdempet."""
    isi = f"""
      <span class="nomor">{nomor}</span>
      <h2>Mulai dari satu pesan.</h2>
      <p>Sebutkan nama usaha dan bidangnya. Saya balas dengan pertanyaan yang perlu dijawab, lalu perkiraan kapan situsnya bisa dilihat.</p>
      <div class="panel__aksi">
        {tombol_wa("Tanya lewat WhatsApp", SITE["pesan"]["klien"], "tombol tombol--kuning")}
        <a class="tombol tombol--putih" href="/portofolio/">Lihat contoh dulu</a>
      </div>"""
    if FREELANCE:
        return f"""
<section class="bagian">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>{isi}
      </div>
      <a class="tombol kepala-bagian__tautan" href="/kontak/">Halaman kontak</a>
    </div>
  </div>
</section>
"""
    return f"""
<section class="panel">
  <div class="wrap panel__isi">
    <div>{isi}
    </div>
    <div class="angka-bungkus">
      <div class="angka-pita">
        <small>satu paket</small>
        <strong>{rupiah(SITE["harga"])}</strong>
        <span>dibayar setelah situsnya jadi</span>
      </div>
    </div>
  </div>
</section>
"""


def halaman_portofolio(g):
    kasus = "".join(blok_kasus(p, g) for p in SITE["proyek"])
    return kepala(
        f"Portofolio website UMKM | {NAMA}",
        "Tiga website UMKM yang sudah online: toko kelontong, toko bunga, dan jamu botolan. "
        "Tampilan layar lebar dan telepon, beserta alasan di balik susunannya.",
        "portofolio",
        "/portofolio/",
    ) + f"""
<div class="page-head">
  <div class="wrap">
    <span class="nomor">Portofolio</span>
    <h1>Tiga situs, semuanya bisa dibuka sekarang.</h1>
    <p>Tiap proyek ditampilkan dalam dua ukuran layar karena pembeli UMKM hampir selalu membuka dari HP. Tautan di tiap bagian menuju situs aslinya, bukan gambar.</p>
  </div>
</div>
<section class="bagian">
  <div class="wrap portofolio">{kasus}</div>
</section>
<section class="panel">
  <div class="wrap panel__isi">
    <div>
      <span class="nomor">Berikutnya</span>
      <h2>Usahamu bisa jadi yang keempat.</h2>
      <p>Ceritakan daganganmu lewat WhatsApp. Saya bantu menentukan apa saja yang perlu ada di situs, tanpa istilah teknis yang membingungkan.</p>
      <div class="panel__aksi">
        {tombol_wa("Ceritakan usahamu", SITE["pesan"]["klien"], "tombol tombol--kuning")}
        <a class="tombol tombol--putih" href="/paket/">Lihat paket {rupiah(SITE["harga"])}</a>
      </div>
    </div>
    <div class="angka-bungkus">
      <div class="angka-pita">
        <small>harga satu paket</small>
        <strong>{rupiah(SITE["harga"])}</strong>
        <span>dibayar setelah situsnya jadi</span>
      </div>
    </div>
  </div>
</section>
""" + kaki()


def halaman_paket():
    paket = "".join(
        """<li><strong>%s</strong><span>%s</span></li>""" % (escape(x["nama"]), escape(x["teks"]))
        for x in SITE["paket"]
    )
    tidak = "".join(
        """<li><strong>%s</strong><span>%s</span></li>""" % (escape(x["nama"]), escape(x["teks"]))
        for x in SITE["tidak_termasuk"]
    )
    langkah = "".join(
        """<li><div><h3>%s</h3><p>%s</p></div></li>""" % (escape(l["nama"]), escape(l["teks"]))
        for l in SITE["proses"]
    )
    return kepala(
        f"Paket website UMKM {rupiah(SITE['harga'])} | {NAMA}",
        "Satu paket Rp250.000 untuk website UMKM: teks ditulis, tampilan di HP disesuaikan, "
        "revisi sampai cocok, bayar setelah jadi. Termasuk dan tidak termasuk dijelaskan terbuka.",
        "paket",
        "/paket/",
    ) + f"""
<div class="page-head">
  <div class="wrap">
    <span class="nomor">Paket</span>
    <h1>Satu harga, isinya ditulis lengkap di sini.</h1>
    <p>Supaya tidak ada kejutan di tengah jalan, bagian yang termasuk dan yang tidak termasuk ditulis terpisah. Yang tidak termasuk bisa dikerjakan orang lain atau dibeli sendiri.</p>
  </div>
</div>
<section class="bagian">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="nomor">01</span>
        <h2>Yang termasuk.</h2>
      </div>
      <div class="harga-besar">
        <strong>{rupiah(SITE["harga"])}</strong>
        <span>sekali bayar, setelah situsnya jadi</span>
      </div>
    </div>
    <ul class="daftar-paket">{paket}</ul>
  </div>
</section>
<section class="bagian bagian--kertas">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="nomor">02</span>
        <h2>Yang tidak termasuk.</h2>
      </div>
      <p class="kepala-bagian__teks">Ini bukan biaya tersembunyi, hanya pekerjaan di luar pembuatan situs. Saya sebutkan dari awal supaya kamu bisa menyiapkannya sendiri atau menanyakannya terpisah.</p>
    </div>
    <ul class="daftar-tidak">{tidak}</ul>
  </div>
</section>
<section class="bagian">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="nomor">03</span>
        <h2>Urutan pengerjaannya.</h2>
      </div>
      <p class="kepala-bagian__teks">Pembayaran ada di langkah terakhir, bukan di awal. Itu sebabnya kamu bisa melihat hasilnya lebih dulu.</p>
    </div>
    <ol class="langkah">{langkah}</ol>
  </div>
</section>
<section class="panel">
  <div class="wrap panel__isi">
    <div>
      <span class="nomor">04</span>
      <h2>Masih ada yang mau ditanyakan?</h2>
      <p>Pertanyaan yang paling sering masuk soal domain, biaya tahunan, dan siapa yang memperbarui isinya. Semuanya bisa dijawab lewat chat sebelum kamu memutuskan.</p>
      <div class="panel__aksi">
        {tombol_wa("Tanya paketnya", SITE["pesan"]["paket"], "tombol tombol--kuning")}
        <a class="tombol tombol--putih" href="/portofolio/">Lihat contoh dulu</a>
      </div>
    </div>
    <div class="angka-bungkus">
      <div class="angka-pita">
        <small>satu paket</small>
        <strong>{rupiah(SITE["harga"])}</strong>
        <span>tanpa tagihan bulanan</span>
      </div>
    </div>
  </div>
</section>
""" + kaki()


def halaman_freelance():
    langkah = "".join("<li><div><p>%s</p></div></li>" % escape(l) for l in SITE["freelance"]["langkah"])
    syarat = "".join("<li>%s</li>" % escape(s) for s in SITE["freelance"]["syarat"])
    return kepala(
        f"Marketing freelance website UMKM | {NAMA}",
        "Cari sampingan tanpa modal dengan menawarkan jasa website UMKM. Komisi Rp50.000 per klien, "
        "dibayar setelah klien melunasi. Tidak perlu bisa coding.",
        "freelance",
        "/freelance/",
    ) + f"""
<div class="page-head">
  <div class="wrap">
    <span class="nomor">Freelance</span>
    <h1>Cari sampingan tanpa modal, cukup kenalkan.</h1>
    <p>Banyak pemilik usaha di sekitar kita belum punya website, dan tidak tahu harus mulai dari mana. Kalau kamu yang menghubungkan mereka dengan saya, ada komisi untukmu.</p>
  </div>
</div>
<section class="bagian">
  <div class="wrap panel__isi">
    <div>
      <span class="nomor">01</span>
      <h2>Yang kamu kerjakan.</h2>
      <p>Bagian kamu hanya menghubungi dan menjelaskan. Menyusun situs, menulis teks, dan mengurus pembayaran saya yang kerjakan.</p>
      <ol class="langkah">{langkah}</ol>
    </div>
    <div class="angka-bungkus">
      <div class="angka-pita">
        <small>komisi per klien</small>
        <strong>{rupiah(SITE["komisi"])}</strong>
        <span>dibayar setelah klien melunasi</span>
      </div>
      <ul class="periksa">{syarat}</ul>
      <div class="panel__aksi">
        {tombol_wa("Daftar lewat WhatsApp", SITE["pesan"]["freelance"], "tombol")}
      </div>
      <p class="catatan-kecil">Format pesannya sudah terisi nama, umur, dan domisili. Cukup dilengkapi.</p>
    </div>
  </div>
</section>
<section class="bagian bagian--kertas">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="nomor">02</span>
        <h2>Yang perlu kamu tahu dulu.</h2>
      </div>
      <p class="kepala-bagian__teks">Komisi dihitung per klien yang jadi, bukan per pesan yang dikirim. Kalau klien belum jadi, tidak ada kewajiban apa pun untukmu.</p>
    </div>
    <div class="daftar-tidak">
      <li>
        <strong>Komisi dibayar setelah klien melunasi</strong>
        <span>Bukan di awal, bukan saat klien setuju. Supaya tidak ada uang yang berpindah sebelum pekerjaan selesai.</span>
      </li>
      <li>
        <strong>Klien tetap diurus saya</strong>
        <span>Kamu tidak perlu menjawab pertanyaan teknis atau menampung revisi. Cukup teruskan kontaknya.</span>
      </li>
    </div>
  </div>
</section>
""" + kaki()


def halaman_kontak():
    kirim = "".join("<li>%s</li>" % escape(x) for x in [
        "Nama usaha dan bidangnya.",
        "Kota atau kecamatan tempat usahamu.",
        "Nomor WhatsApp yang dipakai berjualan.",
        "Foto produk atau tempat usaha, kalau sudah ada.",
    ])
    alt = "".join(
        '<li><a href="%s" target="_blank" rel="noopener">%s</a></li>' % (escape(a["url"]), escape(a["nama"]))
        for a in SITE["buat_sendiri"]["tautan"]
    )
    return kepala(
        f"Kontak | {NAMA}, jasa website UMKM",
        "Hubungi Alif Virgiawan lewat WhatsApp di 0812-2384-4841 untuk membuat website usaha. "
        "Sebutkan nama usaha dan bidangnya untuk memulai.",
        "kontak",
        "/kontak/",
    ) + f"""
<div class="page-head">
  <div class="wrap">
    <span class="nomor">Kontak</span>
    <h1>Satu pesan sudah cukup untuk mulai.</h1>
    <p>Tidak perlu menyiapkan proposal atau daftar panjang. Saya balas dengan pertanyaan yang benar-benar dibutuhkan, sisanya saya susun sendiri.</p>
  </div>
</div>
<section>
  <div class="wrap kontak">
    <div class="kartu-info">
      <h2>WhatsApp</h2>
      <p class="kontak-nomor">{escape(SITE["wa_tampil"])}</p>
      <p>Cara paling cepat. Pesan di bawah sudah terisi pembuka, kamu tinggal menambahkan nama usaha.</p>
      <p><a class="tombol" href="{escape(wa_tautan(SITE["pesan"]["klien"]))}" target="_blank" rel="noopener">Buka WhatsApp</a></p>
      <p class="catatan-kecil">Nomor ini juga dipakai untuk klien yang sedang dikerjakan. Balasan mengikuti jam wajar, biasanya di hari yang sama.</p>
    </div>
    <div class="kartu-info">
      <h2>Yang perlu disebutkan</h2>
      <p>Kalau empat hal ini ada di pesan pertama, balasan saya bisa langsung berisi perkiraan, bukan pertanyaan balik.</p>
      <ul class="daftar-kirim">{kirim}</ul>
    </div>
    <div class="kartu-info">
      <h2>Sebelum menghubungi</h2>
      <p>Yang ditanyakan hampir selalu sama, jadi saya jawab di sini:</p>
      <ul class="daftar-kirim">
        <li>Harga tetap {rupiah(SITE["harga"])} untuk satu situs, dibayar setelah jadi.</li>
        <li>Alamat situs gratis dari saya. Nama domain sendiri dibeli terpisah atas namamu.</li>
        <li>Isi situs memakai foto dan keterangan yang kamu kirim.</li>
        <li>Perubahan setelah serah terima berbayar, kecuali kesalahan dari pihak saya.</li>
      </ul>
      <p class="catatan-kecil">Rinciannya ada di <a class="tautan-garis" href="/paket/">halaman paket</a>.</p>
    </div>
    <div class="kartu-info">
      <h2>{escape(SITE["buat_sendiri"]["judul"])}</h2>
      <p>{escape(SITE["buat_sendiri"]["teks"])}</p>
      <ul class="baris-alt">{alt}</ul>
      <p class="catatan-kecil">Kalau kamu lebih suka mengerjakan sendiri, tidak masalah. Saya sebutkan supaya pilihannya jelas, bukan karena terpaksa memakai jasa.</p>
    </div>
  </div>
</section>
""" + kaki()


def halaman_404():
    return kepala(
        f"Halaman tidak ditemukan | {NAMA}",
        "Halaman yang kamu cari tidak ada.",
        "beranda",
        "/404.html",
    ) + f"""
<section class="hilang">
  <div class="wrap">
    <span class="nomor">404</span>
    <h1>Halamannya tidak ada.</h1>
    <p>Mungkin tautannya salah ketik atau sudah dipindahkan. Dari sini kamu bisa langsung melihat contoh situs yang sudah jadi, atau membaca rincian paketnya.</p>
    <div class="hero__aksi">
      <a class="tombol" href="/portofolio/">Lihat portofolio</a>
      <a class="tombol tombol--putih" href="/">Kembali ke beranda</a>
    </div>
  </div>
</section>
""" + kaki()


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="8" fill="#1B2A4A"/>
<rect x="6" y="6" width="52" height="52" rx="4" fill="none" stroke="#FFD23F" stroke-width="3"/>
<text x="32" y="43" text-anchor="middle" font-family="Plus Jakarta Sans, Segoe UI, sans-serif" font-size="27" font-weight="800" fill="#FFD23F">AV</text>
</svg>
"""


def main():
    kosongkan(DIST)
    os.makedirs(IMG, exist_ok=True)
    g = siapkan_gambar()

    tulis("index.html", halaman_beranda(g))
    tulis("portofolio/index.html", halaman_portofolio(g))
    tulis("paket/index.html", halaman_paket())
    if FREELANCE:
        tulis("freelance/index.html", halaman_freelance())
    tulis("kontak/index.html", halaman_kontak())
    tulis("404.html", halaman_404())
    tulis("assets/favicon.svg", FAVICON)

    for nama in ("style.css", "site.js"):
        sub = "css" if nama.endswith(".css") else "js"
        tujuan = os.path.join(DIST, "assets", sub, nama)
        os.makedirs(os.path.dirname(tujuan), exist_ok=True)
        shutil.copy(os.path.join(ROOT, "assets", sub, nama), tujuan)

    if SITE.get("url"):
        halaman = ["", "portofolio/", "paket/", "kontak/"]
        if FREELANCE:
            halaman.insert(3, "freelance/")
        akar = SITE["url"].rstrip("/")
        urls = "".join("  <url><loc>%s/%s</loc></url>\n" % (akar, h) for h in halaman)
        tulis("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
              + urls + "</urlset>\n")
        tulis("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % akar)
    else:
        tulis("robots.txt", "User-agent: *\nAllow: /\n")

    jumlah = sum(len(f) for _, _, f in os.walk(DIST))
    ukuran = 0
    for akar, _, berkas in os.walk(DIST):
        for b in berkas:
            ukuran += os.path.getsize(os.path.join(akar, b))
    print("halaman: %d" % (6 if FREELANCE else 5))
    print("berkas: %d, total %.1f KB" % (jumlah, ukuran / 1024))


if __name__ == "__main__":
    main()
