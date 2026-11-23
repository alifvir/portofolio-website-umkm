"""Build situs portofolio Alif Virgiawan.

Sumber data:
  data/site.json          nama, harga, tier, kode promo, teks semua bagian
  assets-src/*.png        tangkapan layar asli situs klien (desktop dan ponsel)

Hasil: dist/ siap diunggah ke Cloudflare Pages.

Jalankan: python build.py
"""

import json
import os
import shutil
import unicodedata
from datetime import date
from html import escape
from urllib.parse import quote

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "assets-src")
DIST = os.path.join(ROOT, "dist")
IMG = os.path.join(DIST, "assets", "img")

SITE = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8-sig"))

NAMA = SITE["nama"]
PERAN = SITE["peran"]
IG = SITE.get("instagram") or ""
PROYEK = {p["slug"]: p for p in SITE["proyek"]}
JUM = len(SITE["proyek"])
WA = SITE["wa"]
WA_TAMPIL = SITE["wa_tampil"]
URL = (SITE.get("url") or "").rstrip("/")
PROMO = SITE.get("promo") or {}
PROMO_AKTIF = bool(PROMO.get("aktif"))
KODE = PROMO.get("kode") or []

ANGKA = "nol satu dua tiga empat lima enam tujuh delapan sembilan".split()


def jumlah(kapital=False):
    """Jumlah proyek dalam kata, supaya teks ikut saat proyek ditambah."""
    kata = ANGKA[JUM] if JUM < len(ANGKA) else str(JUM)
    return kata.capitalize() if kapital else kata


def urutan(n):
    return "ke" + (ANGKA[n] if n < len(ANGKA) else str(n))


def rupiah(n):
    return "Rp" + format(n, ",d").replace(",", ".")


FREELANCE = bool(SITE.get("tampilkan_freelance"))
SOROT = "perfect-flowers"
TIER = SITE["tier"]
TIER_PETA = {t["kunci"]: t for t in TIER}
TIER_UTAMA = TIER_PETA["umkm"]


def tulis(path, isi):
    tujuan = os.path.join(DIST, path)
    os.makedirs(os.path.dirname(tujuan) or DIST, exist_ok=True)
    with open(tujuan, "w", encoding="utf-8", newline="\n") as f:
        f.write(isi)


def kosongkan(folder):
    """Hapus isi folder, bukan foldernya.

    Di Windows, folder yang sedang dipakai server pratinjau tidak bisa dihapus,
    padahal isinya tetap bisa diganti.
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
    """Tangkapan layar dipotong ke rasio bingkai, lalu disimpan sebagai webp.

    Tiap tangkapan dibuat dua ukuran. Pengunjung dari HP hanya mengunduh yang
    kecil, karena mayoritas pembaca UMKM membuka tautan dari WhatsApp.
    """
    kosongkan(IMG)

    hasil = {}
    for p in SITE["proyek"]:
        slug = p["slug"]

        im = Image.open(os.path.join(SRC, slug + "-desktop.png")).convert("RGB")
        im = im.crop((0, 0, im.width, round(im.width * 830 / 1280)))

        besar = im.resize((1100, round(im.height * 1100 / im.width)), Image.LANCZOS)
        besar.save(os.path.join(IMG, slug + "-desktop.webp"), "WEBP", quality=84, method=6)

        kecil = im.resize((700, round(im.height * 700 / im.width)), Image.LANCZOS)
        kecil.save(os.path.join(IMG, slug + "-desktop-700.webp"), "WEBP", quality=82, method=6)

        hasil[slug] = {
            "desktop": ("assets/img/%s-desktop.webp" % slug, besar.width, besar.height),
            "desktop700": "assets/img/%s-desktop-700.webp" % slug,
        }

        hp = Image.open(os.path.join(SRC, slug + "-mobile.png")).convert("RGB")
        hp = hp.resize((340, round(hp.height * 340 / hp.width)), Image.LANCZOS)
        hp.save(os.path.join(IMG, slug + "-mobile.webp"), "WEBP", quality=82, method=6)
        hasil[slug]["mobile"] = ("assets/img/%s-mobile.webp" % slug, hp.width, hp.height)

    return hasil


# ---------------------------------------------------------------- tautan
def wa_tautan(pesan=None):
    nomor = (WA or "").strip().replace("+", "").replace(" ", "").replace("-", "")
    return "https://wa.me/%s?text=%s" % (nomor, quote(pesan or SITE["pesan"]["umum"]))


def tombol_wa(teks, pesan=None, kelas="tombol"):
    return '<a class="%s" href="%s" target="_blank" rel="noopener">%s</a>' % (
        kelas,
        escape(wa_tautan(pesan)),
        escape(teks),
    )


# ---------------------------------------------------------------- skema SEO
def skema_umum():
    """Data terstruktur untuk mesin pencari. Hanya fakta yang ada di situs."""
    k = SITE["kredensial"]
    data = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": "%s, %s" % (SITE["nama_lengkap"], PERAN.lower()),
        "alternateName": PERAN,
        "description": (
            "Jasa pembuatan website untuk usaha mikro, kecil, dan menengah di Tangerang "
            "dan sekitarnya. Paket UMKM mulai Rp250.000 dengan kode promo, bayar setelah "
            "website jadi."
        ),
        "url": URL or None,
        "telephone": "+" + WA,
        "email": "alifvir78@gmail.com",
        "priceRange": "Rp250.000 - Rp6.000.000",
        "currenciesAccepted": "IDR",
        "paymentAccepted": "Transfer bank, dompet digital",
        "areaServed": [
            {"@type": "City", "name": "Tangerang"},
            {"@type": "City", "name": "Jakarta"},
            {"@type": "AdministrativeArea", "name": "Banten"},
            {"@type": "Country", "name": "Indonesia"},
        ],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Jl. Otista no. 36, GG Makam Pari II, Gerendeng, Karawaci",
            "addressLocality": "Tangerang",
            "addressRegion": "Banten",
            "addressCountry": "ID",
        },
        "founder": {
            "@type": "Person",
            "name": SITE["nama_lengkap"],
            "jobTitle": "Fullstack Developer",
            "sameAs": [k["tautan"]["url"]],
        },
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Paket pembuatan website",
            "itemListElement": [
                {
                    "@type": "Offer",
                    "name": t["nama"],
                    "description": t["untuk"],
                    "priceCurrency": "IDR",
                    "price": t["harga"],
                    "availability": "https://schema.org/InStock",
                }
                for t in TIER
            ],
        },
    }
    return json.dumps({k2: v for k2, v in data.items() if v is not None}, ensure_ascii=False)


def skema_tanya():
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q["tanya"],
                    "acceptedAnswer": {"@type": "Answer", "text": q["jawab"]},
                }
                for q in SITE["tanya_jawab"]
            ],
        },
        ensure_ascii=False,
    )


# ---------------------------------------------------------------- kerangka
def nav_aktif(aktif, kunci, href, teks):
    tanda = ' aria-current="page"' if aktif == kunci else ""
    return '<li><a href="%s"%s>%s</a></li>' % (href, tanda, teks)


def nav_freelance(aktif):
    if not FREELANCE:
        return ""
    return nav_aktif(aktif, "freelance", "/freelance/", "Freelance")


def data_promo():
    """Data kode promo dalam bentuk JSON, dibaca site.js."""
    if not PROMO_AKTIF or not KODE:
        return ""
    muatan = {
        "masa_hari": PROMO.get("masa_hari", 7),
        "kode": [
            {
                "kode": k["kode"],
                "paket": k["paket"],
                "diskon": k["diskon"],
                "label": k["label"],
                "masa_hari": masa_kode(k),
                "hanya_tautan": bool(k.get("hanya_tautan")),
            }
            for k in KODE
        ],
    }
    return (
        '<script type="application/json" id="data-promo">'
        + json.dumps(muatan, ensure_ascii=False)
        + "</script>"
    )


def bilah_promo():
    """Bilah kode promo di paling atas. Kosong kalau promo dimatikan."""
    if not PROMO_AKTIF or not KODE:
        return ""
    return f"""
<div class="promo" data-promo>
  <div class="wrap promo__isi">
    <form class="promo__form" data-promo-form>
      <label class="promo__label" for="kode-promo">{escape(PROMO.get('judul', 'Punya kode promo'))}?</label>
      <input class="promo__input" id="kode-promo" type="text" name="kode" data-promo-input
             placeholder="Tulis kode di sini" autocomplete="off" spellcheck="false"
             aria-describedby="promo-pesan">
      <button class="promo__tombol" type="submit">Pakai</button>
      <p class="promo__pesan" id="promo-pesan" data-promo-pesan hidden></p>
    </form>
    <p class="promo__aktif" data-promo-aktif hidden>
      <span class="promo__status">
        <span class="promo__dot" aria-hidden="true"></span>
        <span data-promo-teks></span>
      </span>
      <span class="promo__waktu" data-promo-waktu>0 hari</span>
    </p>
  </div>
</div>"""


def kepala(judul, deskripsi, aktif, path, skema=()):
    kanon = og_url = ""
    if URL:
        kanon = '<link rel="canonical" href="%s%s">' % (URL, path)
        og_url = '<meta property="og:url" content="%s%s">' % (URL, path)
    blok_skema = "".join(
        '<script type="application/ld+json">%s</script>' % s for s in skema
    )
    return f"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#fffbef">
<title>{escape(judul)}</title>
<meta name="description" content="{escape(deskripsi)}">
<meta name="author" content="{escape(SITE['nama_lengkap'])}">
<meta name="robots" content="index, follow, max-image-preview:large">
{kanon}
<meta property="og:type" content="website">
<meta property="og:locale" content="id_ID">
<meta property="og:site_name" content="{escape(NAMA)}">
<meta property="og:title" content="{escape(judul)}">
<meta property="og:description" content="{escape(deskripsi)}">
<meta property="og:image" content="/assets/img/{SOROT}-desktop.webp">
{og_url}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="/assets/css/style.css">
{blok_skema}
</head>
<body>
<a class="lewat" href="#utama">Lewati ke isi utama</a>
<div class="topbar">
{bilah_promo()}
<header class="site-head">
  <div class="wrap site-head__row">
    <a class="merek" href="/">
      <strong>{escape(NAMA)}</strong>
      <small>{escape(PERAN)}</small>
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
</div>
<main id="utama">
{data_promo()}
"""


def kaki():
    k = SITE["kredensial"]
    return f"""</main>
<footer class="site-foot">
  <div class="wrap">
    <div class="foot-baris">
      <p><a class="foot-nama" href="{escape(IG) if IG else '/'}" target="_blank" rel="noopener">{escape(NAMA)}</a> &middot; {escape(PERAN.lower())} di Tangerang</p>
      <ul class="foot-nav">
        <li><a href="/portofolio/">Portofolio</a></li>
        <li><a href="/paket/">Paket</a></li>
        {f'<li><a href="/freelance/">Freelance</a></li>' if FREELANCE else ""}
        <li><a href="/kontak/">Kontak</a></li>
      </ul>
    </div>
    <div class="foot-baris">
      <p>WhatsApp <a href="{escape(wa_tautan())}" target="_blank" rel="noopener">{escape(WA_TAMPIL)}</a> &middot; alifvir78@gmail.com</p>
      <p>&copy; <span id="tahun">{date.today().year}</span> {escape(SITE['nama_lengkap'])} &middot; <a href="{escape(k['tautan']['url'])}" target="_blank" rel="noopener">{escape(k['tautan']['nama'])}</a></p>
    </div>
  </div>
</footer>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
"""


def bingkai_desktop(p, g, kelas="", lazy=True):
    f, w, h = g[p["slug"]]["desktop"]
    f700 = g[p["slug"]]["desktop700"]
    muat = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return f"""<figure class="bingkai {kelas}">
  <figcaption class="bingkai__bar"><span class="bingkai__alamat">{escape(p["domain"])}</span><span class="bingkai__live"><span class="live__dot" aria-hidden="true"></span>live</span></figcaption>
  <a class="bingkai__isi" href="{escape(p["url"])}" target="_blank" rel="noopener">
    <img src="/{f}" srcset="/{f700} 700w, /{f} 1100w" sizes="(max-width: 660px) 92vw, (max-width: 960px) 46vw, 545px" alt="Tangkapan layar beranda {escape(p['nama'])} di layar lebar" width="{w}" height="{h}"{muat} decoding="async">
  </a>
</figure>"""


def kartu_proyek(p, g):
    return f"""<article class="kartu-proyek">
  {bingkai_desktop(p, g)}
  <div class="kartu-proyek__isi">
    <div class="kartu-proyek__meta">
      <span class="kartu-proyek__bidang">{escape(p["bidang"])}</span>
      <span class="kartu-proyek__live"><span class="live__dot" aria-hidden="true"></span>live</span>
    </div>
    <h3>{escape(p["nama"])}</h3>
    <p>{escape(p["ringkas"])}</p>
    <div class="kartu-proyek__aksi">
      <a class="tautan-garis" href="/portofolio/#{p["slug"]}">Lihat rincian</a>
      <a class="tautan-garis" href="{escape(p["url"])}" target="_blank" rel="noopener">Buka situs</a>
    </div>
  </div>
</article>"""


def blok_kasus(p, g):
    f_m, w_m, h_m = g[p["slug"]]["mobile"]
    isi = "".join("<li>%s</li>" % escape(i) for i in p["isi"])
    return f"""<article class="kasus" id="{p['slug']}">
  <div class="kasus__kepala">
    <span class="label">{escape(p["bidang"])}</span>
    <h2>{escape(p["nama"])}</h2>
    <p class="kasus__meta">{escape(p["kota"])} &middot; {escape(p["domain"])}</p>
  </div>
  <div class="kasus__gambar">
    {bingkai_desktop(p, g)}
    <figure class="telepon">
      <a class="telepon__isi" href="{escape(p["url"])}" target="_blank" rel="noopener">
        <img src="/{f_m}" alt="Beranda {escape(p['nama'])} di layar ponsel" width="{w_m}" height="{h_m}" loading="lazy" decoding="async">
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
    <a class="tombol tombol--kecil" href="{escape(p["url"])}" target="_blank" rel="noopener">Buka {escape(p["domain"])}</a>
    {tombol_wa("Mau yang seperti ini", SITE["pesan"]["klien"], "tombol tombol--putih tombol--kecil")}
  </div>
</article>"""


def masa_kode(k):
    """Durasi promo per kode. Kode tanpa `masa_hari` ikut nilai global."""
    return k.get("masa_hari") or PROMO.get("masa_hari", 7)


def kode_tampil(k):
    """True kalau kode boleh disebut di halaman.

    Kode bertanda `hanya_tautan` sengaja tidak pernah dicetak: itu kode kampanye
    yang hanya berlaku lewat tautan yang kita kirim sendiri, mis. Threads.
    """
    return not k.get("hanya_tautan")


def kode_paket(kunci):
    """Kode yang berlaku untuk satu paket dan boleh disebut di halaman."""
    return [k for k in KODE if k["paket"] == kunci and kode_tampil(k)]


def rincian_kode(daftar):
    """Kode tampil beserta durasinya, mis. `UMKMMAJU (7 hari)`."""
    return " atau ".join(
        '<span class="paket__kode">%s</span> (%d hari)' % (escape(k["kode"]), masa_kode(k))
        for k in daftar
    )


def kartu_paket(t):
    """Satu kartu harga. Semua kartu berlatar sama, tidak ada yang dibedakan warna."""
    isi = "".join("<li>%s</li>" % escape(i) for i in t["isi"])
    ada_promo = bool(t.get("harga_promo"))
    daftar = kode_paket(t["kunci"])
    diskon = daftar[0]["diskon"] if daftar else 50
    awalan = "<small>mulai</small>" if t["satuan"] == "mulai dari" else ""

    if not t.get("harga"):
        # Custom: tidak ada angka, tapi tetap memakai pola harga yang sama
        # supaya ketiga kartu seragam.
        angka = '<span class="paket__angka paket__angka--teks">Menyesuaikan kebutuhan</span>'
        hitung = ""
        catatan = (
            '<p class="paket__catatan">Harganya tergantung fitur yang dibutuhkan. '
            "Sebutkan rencanamu, saya hitung lalu kirim rincian sebelum kamu memutuskan.</p>"
        )
    elif ada_promo:
        angka = (
            '<span class="paket__angka" data-harga data-paket="%s" '
            'data-harga-promo="%d">%s%s</span>'
            '<span class="paket__coret" data-coret="%s" hidden>%s harga normal</span>'
            % (t["kunci"], t["harga_promo"], awalan, rupiah(t["harga"]), t["kunci"], rupiah(t["harga"]))
        )
        hitung = (
            '<span class="paket__hitung" data-hitung="%s" hidden>'
            '<span class="promo__dot" aria-hidden="true"></span>'
            'sisa <span data-sisa="%s">0 hari</span></span>' % (t["kunci"], t["kunci"])
        )
        # Hanya kode yang boleh disebut yang ditulis. Kode kampanye bertanda
        # `hanya_tautan` tidak pernah muncul di halaman.
        catatan = (
            "<p class=\"paket__catatan\"><strong>Pakai kode %s "
            "di atas halaman.</strong> Harga langsung turun %d%% sejak kode dipakai. "
            "Tanpa kode, harganya %s.</p>"
            % (rincian_kode(daftar), diskon, rupiah(t["harga"]))
        ) if daftar else ""
    else:
        angka = '<span class="paket__angka" data-harga data-paket="%s" data-harga-promo="0">%s%s</span>' % (
            t["kunci"],
            awalan,
            rupiah(t["harga"]),
        )
        hitung = ""
        catatan = ""

    return f"""<article class="paket">
  <div class="paket__kepala">
    <h3 class="paket__nama">{escape(t["nama"])}</h3>
    <p class="paket__sub">{escape(t["sub"])}</p>
  </div>
  <div class="paket__harga">
    {angka}
    {hitung}
    <span class="paket__satuan">{escape(t["satuan"])}</span>
  </div>
  <p class="paket__untuk">{escape(t["untuk"])}</p>
  <ul class="paket__daftar">{isi}</ul>
  {catatan}
  <div class="paket__aksi">
    {tombol_wa("Tanya paket ini", SITE["pesan"]["paket"] + " Paket: " + t["nama"], "tombol tombol--penuh")}
  </div>
</article>"""


def daftar_langkah():
    return "".join(
        """<li><div><h3>%s</h3><p>%s</p></div></li>""" % (escape(l["nama"]), escape(l["teks"]))
        for l in SITE["proses"]
    )


def daftar_tanya():
    return "".join(
        f"""<details>
      <summary>{escape(q["tanya"])}</summary>
      <p class="tanya__jawab">{escape(q["jawab"])}</p>
    </details>"""
        for q in SITE["tanya_jawab"]
    )


def blok_kredensial():
    k = SITE["kredensial"]
    butir = "".join(
        f"""<div class="kredensial__butir">
      <h3>{escape(b["nama"])}</h3>
      <p>{escape(b["teks"])}</p>
    </div>"""
        for b in k["butir"]
    )
    return f"""<section class="bagian" id="tentang">
  <div class="wrap">
    <div class="kredensial">
      <div>
        <span class="label">{escape(k["judul"])}</span>
        <h2 style="margin-top:12px"><a class="tautan-nama" href="{escape(IG) if IG else '/'}" target="_blank" rel="noopener">{escape(k["nama"])}</a></h2>
        <p class="kepala-bagian__teks" style="margin-top:16px">{escape(k["ringkas"])}</p>
        <div class="kredensial__kerja">
          <strong>Sekarang: {escape(k["kerja"]["nama"])}</strong>
          <span>{escape(k["kerja"]["teks"])}</span>
        </div>
        <p class="kredensial__tautan">
          <a class="tombol tombol--kuning" href="{escape(k["tautan"]["url"])}" target="_blank" rel="noopener">{escape(k["tautan"]["nama"])}</a>
          <a class="tombol tombol--putih" href="{escape(IG) if IG else '/'}" target="_blank" rel="noopener">Instagram</a>
        </p>
        <p class="kredensial__catatan">Kedua akun itu benar milik saya. Boleh dicek sebelum memutuskan.</p>
      </div>
      <div class="kredensial__pita">{butir}</div>
    </div>
  </div>
</section>"""


def blok_cerita():
    c = SITE["cerita"]
    return f"""<section class="cerita">
  <div class="wrap cerita__isi">
    <div>
      <span class="label label--terang">Alasan</span>
      <h2 style="margin-top:12px">{escape(c["judul"])}</h2>
      <div class="cerita__tanda" style="margin-top:24px" aria-hidden="true"></div>
    </div>
    <p>{escape(c["teks"])}</p>
  </div>
</section>"""


def blok_penutup(nomor):
    """Ajakan terakhir di panel navy, memuat harga yang berlaku sekarang."""
    t = TIER_UTAMA
    daftar = kode_paket(t["kunci"])
    diskon = daftar[0]["diskon"] if daftar else 50
    rincian = rincian_kode(daftar)
    return f"""
<section class="panel">
  <div class="wrap panel__isi">
    <div>
      <span class="label label--terang">Mulai</span>
      <h2 style="margin-top:12px">Mulai dari satu pesan.</h2>
      <p style="margin-top:16px">Sebutkan nama usaha dan bidangnya. Saya balas dengan pertanyaan yang perlu dijawab, lalu perkiraan kapan situsnya bisa dilihat.</p>
      <div class="panel__aksi">
        {tombol_wa("Tanya lewat WhatsApp", SITE["pesan"]["klien"], "tombol tombol--kuning")}
        <a class="tombol tombol--putih" href="/portofolio/">Lihat contoh dulu</a>
      </div>
    </div>
    <div class="panel__angka">
      <small>paket website umkm</small>
      <span class="panel__coret">{rupiah(t["harga"])}</span>
      <strong>{rupiah(t["harga_promo"])}</strong>
      <p class="panel__kode">Pakai kode {rincian} untuk mendapatkan harga ini. Potongan {diskon}% berlaku sejak kode dipakai.</p>
    </div>
  </div>
</section>
"""


# ---------------------------------------------------------------- halaman
def halaman_beranda(g):
    p = PROYEK[SOROT]
    f_hp, w_hp, h_hp = g[SOROT]["mobile"]
    kartu = "".join(kartu_proyek(q, g) for q in SITE["proyek"])
    paket = "".join(kartu_paket(t) for t in TIER)
    t = TIER_UTAMA

    return kepala(
        "Jasa Website UMKM Tangerang | %s" % NAMA,
        "Jasa pembuatan website UMKM di Tangerang dan Jakarta mulai %s. "
        "Bayar setelah website jadi, selesai dalam sehari, dikerjakan sendiri."
        % rupiah(t["harga_promo"]),
        "beranda",
        "/",
        skema=(skema_umum(), skema_tanya()),
    ) + f"""
<section class="hero">
  <div class="wrap hero__isi">
    <div class="hero__teks">
      <span class="label">Jasa website UMKM di Tangerang</span>
      <h1 style="margin-top:12px">Website untuk usahamu, <em>jadi dulu baru bayar.</em></h1>
      <p>Saya membuat website untuk usaha kecil seperti warung, toko kue, jamu, dan bunga. Kamu lihat hasilnya dari HP sendiri dulu, baru bicara soal bayaran.</p>
      <div class="sorot-harga">
        <span class="sorot-harga__kini" data-harga data-paket="{t["kunci"]}" data-harga-promo="{t["harga_promo"]}">{rupiah(t["harga"])}</span>
        <span class="sorot-harga__lama" data-coret="{t["kunci"]}" hidden>{rupiah(t["harga"])}</span>
        <span class="sorot-harga__label">paket umkm</span>
      </div>
      <div class="hero__aksi">
        {tombol_wa("Tanya lewat WhatsApp", SITE["pesan"]["klien"])}
        <a class="tombol tombol--putih" href="#contoh">Lihat {jumlah()} contoh</a>
      </div>
      <p class="hero__kecil">Sudah termasuk penulisan teks dan penyesuaian tampilan di HP. Tidak ada tagihan bulanan.</p>
    </div>
    <div class="hero__latar">
      {bingkai_desktop(p, g, lazy=False)}
      <div class="hero__kaki">
        <p class="hero__catatan">{escape(p["nama"])}, {escape(p["bidang"].lower())} di {escape(p["kota"])}.</p>
        <figure class="hero__telepon">
          <img src="/{f_hp}" alt="Tampilan {escape(p['nama'])} di layar ponsel" width="{w_hp}" height="{h_hp}" loading="lazy" decoding="async">
        </figure>
      </div>
    </div>
  </div>
</section>

<div class="wrap">
  <ul class="fakta">
    <li><strong>Bayar setelah jadi</strong><span>Kamu periksa hasilnya dulu. Pembayaran setelah kamu setuju.</span></li>
    <li><strong>Revisi sampai cocok</strong><span>Bagian yang mau diubah sebutkan saja, saya kerjakan.</span></li>
    <li><strong>Tanpa langganan</strong><span>Sekali bayar, situsnya tetap milikmu setelah diserahkan.</span></li>
    <li><strong>Dikerjakan sendiri</strong><span>Bukan dijual ulang ke pihak ketiga. Satu orang, dari awal sampai serah terima.</span></li>
  </ul>
</div>

<section class="bagian" id="contoh">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="label">01 Hasil kerja</span>
        <h2>{jumlah().capitalize()} situs yang sudah online.</h2>
        <p class="kepala-bagian__teks">Bukan gambar contoh. Ke{jumlah()} tautan di bawah bisa dibuka sekarang, dan isinya dipakai pemiliknya untuk berjualan.</p>
      </div>
      <a class="tombol tombol--putih tombol--kecil kepala-bagian__tautan" href="/portofolio/">Lihat rinciannya</a>
    </div>
    <div class="grid-proyek">{kartu}</div>
  </div>
</section>

<section class="bagian bagian--kertas" id="paket">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="label">02 Paket</span>
        <h2>Tiga pilihan, satu fokus.</h2>
        <p class="kepala-bagian__teks">Fokus saya website untuk UMKM. Kalau usahamu sudah berjalan atau butuh alur khusus, dua paket lain di bawah ini tersedia dengan lingkup yang jelas.</p>
      </div>
      <a class="tombol tombol--putih tombol--kecil kepala-bagian__tautan" href="/paket/">Bandingkan paket</a>
    </div>
    <div class="paket-grid paket-grid--tiga">{paket}</div>
  </div>
</section>

{blok_kredensial()}

{blok_cerita()}

<section class="bagian">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="label">04 Cara kerja</span>
        <h2>Empat langkah mudah untuk memiliki website pertamamu.</h2>
        <p class="kepala-bagian__teks">Kamu tidak perlu menyiapkan apa pun yang rapi. Yang penting ada info usaha dan nomor WhatsApp.</p>
      </div>
    </div>
    <ol class="langkah">{daftar_langkah()}</ol>
  </div>
</section>

<section class="bagian bagian--kertas">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="label">05 Pertanyaan</span>
        <h2>Yang paling sering ditanyakan.</h2>
      </div>
    </div>
    <div class="tanya">{daftar_tanya()}</div>
  </div>
</section>
{blok_penutup("06")}
""" + kaki()


def halaman_portofolio(g):
    kasus = "".join(blok_kasus(p, g) for p in SITE["proyek"])
    return kepala(
        "Portofolio website UMKM | " + NAMA,
        jumlah().capitalize()
        + " website UMKM yang sudah online, dari toko kelontong sampai dupa premium. "
        "Tampilan layar lebar dan ponsel, beserta alasan di balik susunannya.",
        "portofolio",
        "/portofolio/",
    ) + f"""
<div class="page-head">
  <div class="wrap">
    <span class="label">Portofolio</span>
    <h1 style="margin-top:12px">{jumlah().capitalize()} situs, semuanya bisa dibuka sekarang.</h1>
    <p>Tiap proyek ditampilkan dalam dua ukuran layar karena pembeli UMKM hampir selalu membuka dari HP. Tautan di tiap bagian menuju situs aslinya, bukan gambar.</p>
  </div>
</div>
<section class="bagian">
  <div class="wrap portofolio">{kasus}</div>
</section>
{blok_penutup("Berikutnya")}
""" + kaki()


def halaman_paket():
    kartu = "".join(kartu_paket(t) for t in TIER)
    tidak = "".join(
        """<li><strong>%s</strong><span>%s</span></li>""" % (escape(x["nama"]), escape(x["teks"]))
        for x in SITE["tidak_termasuk"]
    )
    return kepala(
        "Paket jasa website UMKM | " + NAMA,
        "Tiga paket website: UMKM, company profile, dan custom. Kode promo memberi "
        "potongan 50%, tujuh hari untuk kode yang diketik, empat belas hari untuk kode dari "
        "tautan. Isi tiap paket dan yang tidak termasuk ditulis terbuka.",
        "paket",
        "/paket/",
        skema=(skema_umum(), skema_tanya()),
    ) + f"""
<div class="page-head">
  <div class="wrap">
    <span class="label">Paket</span>
    <h1 style="margin-top:14px">Tiga paket, isinya ditulis lengkap.</h1>
    <p>Supaya tidak ada kejutan di tengah jalan, isi tiap paket dan yang tidak termasuk ditulis terpisah. Yang tidak termasuk bisa dikerjakan orang lain atau dibeli sendiri.</p>
  </div>
</div>
<section class="bagian">
  <div class="wrap">
    <div class="paket-grid paket-grid--tiga">{kartu}</div>
  </div>
</section>
<section class="bagian bagian--kertas">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="label">Yang tidak termasuk</span>
        <h2>Ditulis dari awal, bukan biaya tersembunyi.</h2>
        <p class="kepala-bagian__teks">Ini pekerjaan di luar pembuatan situs. Saya sebutkan supaya kamu bisa menyiapkannya sendiri atau menanyakannya terpisah.</p>
      </div>
    </div>
    <ul class="daftar-tidak">{tidak}</ul>
  </div>
</section>
<section class="bagian">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="label">Urutan pengerjaan</span>
        <h2>Pembayaran di langkah terakhir.</h2>
        <p class="kepala-bagian__teks">Itu sebabnya kamu bisa melihat hasilnya lebih dulu.</p>
      </div>
    </div>
    <ol class="langkah">{daftar_langkah()}</ol>
  </div>
</section>
<section class="bagian bagian--kertas">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="label">Pertanyaan</span>
        <h2>Sebelum kamu memutuskan.</h2>
      </div>
    </div>
    <div class="tanya">{daftar_tanya()}</div>
  </div>
</section>
{blok_penutup("Tanya")}
""" + kaki()


def halaman_freelance():
    langkah = "".join("<li><div><p>%s</p></div></li>" % escape(l) for l in SITE["freelance"]["langkah"])
    syarat = "".join("<li>%s</li>" % escape(s) for s in SITE["freelance"]["syarat"])
    return kepala(
        f"Marketing freelance website UMKM | {NAMA}",
        "Cari sampingan dengan menawarkan jasa website UMKM. Komisi Rp50.000 per klien, "
        "dibayar setelah klien melunasi. Tidak perlu bisa coding.",
        "freelance",
        "/freelance/",
    ) + f"""
<div class="page-head">
  <div class="wrap">
    <span class="label">Freelance</span>
    <h1 style="margin-top:14px">Kenalkan, lalu dapat komisi.</h1>
    <p>Banyak pemilik usaha di sekitar kita belum punya website, dan tidak tahu harus mulai dari mana. Kalau kamu yang menghubungkan mereka dengan saya, ada komisi untukmu.</p>
  </div>
</div>
<section class="bagian">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="label">01</span>
        <h2>Yang kamu kerjakan.</h2>
        <p class="kepala-bagian__teks">Bagian kamu hanya menghubungi dan menjelaskan. Menyusun situs, menulis teks, dan mengurus pembayaran saya yang kerjakan.</p>
      </div>
    </div>
    <ol class="langkah">{langkah}</ol>
  </div>
</section>
<section class="bagian bagian--kertas">
  <div class="wrap">
    <div class="kepala-bagian">
      <div>
        <span class="label">02</span>
        <h2>Yang perlu kamu tahu dulu.</h2>
        <p class="kepala-bagian__teks">Komisi dihitung per klien yang jadi, bukan per pesan yang dikirim.</p>
      </div>
    </div>
    <ul class="paket__daftar">{syarat}</ul>
  </div>
</section>
{blok_penutup("03")}
""" + kaki()


def halaman_kontak():
    t = TIER_UTAMA
    kirim = "".join(
        "<li>%s</li>" % escape(x)
        for x in [
            "Nama usaha dan bidangnya.",
            "Kota atau kecamatan tempat usahamu.",
            "Nomor WhatsApp yang dipakai berjualan.",
            "Foto produk atau tempat usaha, kalau sudah ada.",
        ]
    )
    alt = "".join(
        '<li><a href="%s" target="_blank" rel="noopener">%s</a></li>' % (escape(a["url"]), escape(a["nama"]))
        for a in SITE["buat_sendiri"]["tautan"]
    )
    # Daftar harga di kontak dibangun dari data tier + kode promo, supaya tidak
    # pernah berbeda dengan kartu paket saat harganya diubah.
    harga_pakai = "".join(
        "<li>Paket %s %s jika menggunakan kode promo %s.</li>"
        % (
            escape(TIER_PETA[k["paket"]]["nama"]),
            rupiah(TIER_PETA[k["paket"]]["harga_promo"]),
            escape(k["kode"]),
        )
        for k in KODE
        if k["paket"] in TIER_PETA
        and TIER_PETA[k["paket"]].get("harga_promo")
        and kode_tampil(k)
    )
    return kepala(
        f"Kontak | {NAMA}, jasa website UMKM Tangerang",
        "Hubungi Alif Virgiawan lewat WhatsApp di %s untuk membuat website usaha. "
        "Sebutkan nama usaha dan bidangnya untuk memulai." % WA_TAMPIL,
        "kontak",
        "/kontak/",
        skema=(skema_umum(),),
    ) + f"""
<div class="page-head">
  <div class="wrap">
    <span class="label">Kontak</span>
    <h1 style="margin-top:14px">Satu pesan sudah cukup untuk mulai.</h1>
    <p>Tidak perlu menyiapkan proposal atau daftar panjang. Saya balas dengan pertanyaan yang benar-benar dibutuhkan, sisanya saya susun sendiri.</p>
  </div>
</div>
<section>
  <div class="wrap kontak">
    <div class="kartu-info">
      <h2>WhatsApp</h2>
      <p class="kontak-nomor">{escape(WA_TAMPIL)}</p>
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
      <p>Yang ditanyakan hampir selalu sama, jadi saya jawab di sini.</p>
      <ul class="daftar-kirim">
        {harga_pakai}
        <li>Website UMKM selesai satu hari kalau logo dan foto produk sudah lengkap.</li>
        <li>Harga paket dibayar sekali, tanpa tagihan bulanan.</li>
        <li>Isi situs memakai foto dan keterangan yang kamu kirim.</li>
        <li>Perubahan setelah serah terima berbayar, kecuali kesalahan dari pihak saya.</li>
      </ul>
      <p class="catatan-kecil">Rincian tiap paket ada di <a class="tautan-garis" href="/paket/">halaman paket</a>.</p>
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
        "Halaman yang kamu cari tidak ada. Kembali ke beranda untuk melihat "
        "contoh website UMKM atau rincian paketnya.",
        "beranda",
        "/404.html",
    ) + f"""
<section class="hilang">
  <div class="wrap">
    <span class="label">404</span>
    <h1 style="margin-top:14px">Halamannya tidak ada.</h1>
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
<path d="M32 13 L52 24 L32 35 L12 24 Z" fill="#FFD23F"/>
<path d="M32 40 L52 29 L52 35 L32 46 L12 35 L12 29 Z" fill="#FFD23F" opacity="0.75"/>
<path d="M32 49 L52 38 L52 44 L32 55 L12 44 L12 38 Z" fill="#FFD23F" opacity="0.5"/>
</svg>
"""


def sitemap():
    if not URL:
        return
    halaman = [("", "1.0"), ("portofolio/", "0.9"), ("paket/", "0.9"), ("kontak/", "0.7")]
    if FREELANCE:
        halaman.insert(3, ("freelance/", "0.8"))
    baris = "".join(
        "  <url><loc>%s/%s</loc><changefreq>weekly</changefreq><priority>%s</priority></url>\n"
        % (URL, h, pr)
        for h, pr in halaman
    )
    tulis(
        "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + baris + "</urlset>\n",
    )
    tulis(
        "robots.txt",
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % URL,
    )


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

    if URL:
        sitemap()
    else:
        tulis("robots.txt", "User-agent: *\nAllow: /\n")

    berkas = sum(len(f) for _, _, f in os.walk(DIST))
    ukuran = 0
    for akar, _, isi in os.walk(DIST):
        for b in isi:
            ukuran += os.path.getsize(os.path.join(akar, b))
    print("halaman: %d" % (6 if FREELANCE else 5))
    print("berkas: %d, total %.1f KB" % (berkas, ukuran / 1024))


if __name__ == "__main__":
    main()
