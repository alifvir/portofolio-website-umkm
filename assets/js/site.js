// Menu ponsel dan kode promo.
//
// Aturan promo: satu perangkat hanya boleh mengklaim satu kode, sekali.
// Setelah hitungan mundur habis, perangkat itu tidak bisa memakai harga promo
// lagi selamanya. Penandanya disimpan di localStorage, bukan hanya dihapus,
// jadi memuat ulang halaman tidak mengembalikan promo.
//
// Tidak ada server, jadi tidak ada data pribadi yang dikirim ke mana pun.

(function () {
  "use strict";

  var HARI = 24 * 60 * 60 * 1000;
  var SIMPAN = "promoWebsiteUMKM";

  /* ------------------------------------------------------- menu ponsel */

  var tombol = document.querySelector("[data-nav-tombol]");
  var nav = document.querySelector("[data-nav]");

  if (tombol && nav) {
    var tutupNav = function () {
      nav.setAttribute("data-terbuka", "false");
      tombol.setAttribute("aria-expanded", "false");
    };

    tombol.addEventListener("click", function () {
      var terbuka = nav.getAttribute("data-terbuka") === "true";
      nav.setAttribute("data-terbuka", terbuka ? "false" : "true");
      tombol.setAttribute("aria-expanded", terbuka ? "false" : "true");
    });

    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) tutupNav();
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        tutupNav();
        tombol.focus();
      }
    });

    document.addEventListener("click", function (e) {
      if (!nav.contains(e.target) && !tombol.contains(e.target)) tutupNav();
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth >= 960) tutupNav();
    });
  }

  /* ------------------------------------------------------- penjaga gulir

     Input kode promo tinggal di bilah yang menempel di atas. Posisi tata
     letaknya ada di paling atas dokumen, jadi saat difokus peramban mengira
     elemen itu jauh di atas layar dan menggulir halaman ke atas. Akibatnya
     layar melompat begitu pengunjung mulai mengetik. Gulirnya dikembalikan. */

  (function () {
    var bilah = document.querySelector("[data-promo]");
    if (!bilah) return;

    var tenang =
      window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    var pulihkan = function (y) {
      var asal = document.documentElement.style.scrollBehavior;
      document.documentElement.style.scrollBehavior = "auto";
      window.scrollTo(0, y);
      document.documentElement.style.scrollBehavior = asal;
    };

    bilah.addEventListener(
      "focusin",
      function () {
        var y = window.scrollY;
        if (tenang) {
          pulihkan(y);
          return;
        }
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            pulihkan(y);
          });
        });
        setTimeout(function () {
          pulihkan(y);
        }, 60);
      },
      true
    );
  })();

  /* ------------------------------------------------------- kode promo */

  var wadah = document.querySelector("[data-promo]");
  var sumber = document.getElementById("data-promo");
  if (!wadah || !sumber) return;

  var data;
  try {
    data = JSON.parse(sumber.textContent);
  } catch (e) {
    return;
  }

  var daftarKode = data.kode || [];
  var masaHari = data.masa_hari || 7;
  var form = wadah.querySelector("[data-promo-form]");
  var input = wadah.querySelector("[data-promo-input]");
  var pesan = wadah.querySelector("[data-promo-pesan]");
  var aktif = wadah.querySelector("[data-promo-aktif]");
  var teksAktif = wadah.querySelector("[data-promo-teks]");
  var waktu = wadah.querySelector("[data-promo-waktu]");

  function rupiah(n) {
    return "Rp" + n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  }

  function dua(n) {
    return n < 10 ? "0" + n : String(n);
  }

  function sisaTeks(habis) {
    var sisa = habis - Date.now();
    if (sisa < 0) sisa = 0;
    var h = Math.floor(sisa / 3600000);
    var m = Math.floor((sisa % 3600000) / 60000);
    var s = Math.floor((sisa % 60000) / 1000);
    if (h >= 24) return Math.floor(h / 24) + " hari " + dua(h % 24) + ":" + dua(m) + ":" + dua(s);
    return dua(h) + ":" + dua(m) + ":" + dua(s);
  }

  /* Tiga keadaan yang disimpan:
       belum pernah klaim  -> tidak ada apa-apa di localStorage
       sedang berjalan     -> {habis} masih di depan
       sudah pernah klaim  -> {habis} sudah lewat, dan penandanya SENGAJA
                              dibiarkan ada supaya tidak bisa klaim ulang */
  function baca() {
    try {
      var teks = localStorage.getItem(SIMPAN);
      if (!teks) return null;
      var d = JSON.parse(teks);
      if (!d || !d.kode || !d.habis) return null;
      return d;
    } catch (e) {
      return null;
    }
  }

  function simpan(d) {
    try {
      localStorage.setItem(SIMPAN, JSON.stringify(d));
    } catch (e) {
      /* mode privat: promo tetap jalan selama halaman terbuka */
    }
  }

  /* Semua harga di halaman ditandai data-harga + data-paket.
     Teks aslinya disimpan sekali di awal supaya selalu bisa dipulihkan. */
  var semuaHarga = Array.prototype.slice.call(document.querySelectorAll("[data-harga]"));
  semuaHarga.forEach(function (el) {
    el.setAttribute("data-asli", el.innerHTML);
  });

  var semuaCoret = Array.prototype.slice.call(document.querySelectorAll("[data-coret]"));
  var semuaHitung = Array.prototype.slice.call(document.querySelectorAll("[data-hitung]"));

  function terapkan(aktifkah, paketKode) {
    semuaHarga.forEach(function (el) {
      var paket = el.getAttribute("data-paket");
      var promo = Number(el.getAttribute("data-harga-promo") || 0);
      var asli = el.getAttribute("data-asli");

      if (!promo) {
        el.innerHTML = asli;
        return;
      }

      if (aktifkah && paketKode === paket) {
        el.innerHTML = rupiah(promo);
      } else {
        el.innerHTML = asli;
      }
    });

    semuaCoret.forEach(function (el) {
      el.hidden = !(aktifkah && el.getAttribute("data-coret") === paketKode);
    });

    semuaHitung.forEach(function (el) {
      el.hidden = !(aktifkah && el.getAttribute("data-hitung") === paketKode);
    });
  }

  var jeda = null;

  function segarkanHitungan(habis) {
    var teks = sisaTeks(habis);
    if (waktu) waktu.textContent = teks;
    semuaHitung.forEach(function (el) {
      var isi = el.querySelector("[data-sisa]");
      if (isi) isi.textContent = teks;
    });
  }

  function tampilkanAktif(d, cocok) {
    if (form) form.hidden = true;
    if (aktif) aktif.hidden = false;
    if (pesan) pesan.hidden = true;

    if (teksAktif) {
      teksAktif.textContent = "Kode " + cocok.kode + " aktif, " + cocok.diskon + "%";
      teksAktif.setAttribute("title", "Berlaku untuk " + cocok.label);
    }

    terapkan(true, cocok.paket);
    segarkanHitungan(d.habis);

    if (jeda) clearInterval(jeda);
    jeda = setInterval(function () {
      var masih = baca();
      if (!masih || Date.now() >= masih.habis) {
        if (jeda) {
          clearInterval(jeda);
          jeda = null;
        }
        habiskan();
        return;
      }
      segarkanHitungan(masih.habis);
    }, 1000);
  }

  /* Hitungan selesai: harga kembali normal, dan kode TIDAK dihapus dari
     localStorage. Justru penandanya yang mencegah perangkat ini memakai
     harga promo lagi. Formulirnya dinonaktifkan, bukan disembunyikan, karena
     pesan penjelasnya ada di dalam formulir itu. */
  function habiskan() {
    terapkan(false, null);
    if (input) input.value = "";
    if (aktif) aktif.hidden = true;
    if (form) {
      var isi = form.querySelectorAll("input, button");
      for (var i = 0; i < isi.length; i++) {
        isi[i].disabled = true;
        isi[i].setAttribute("aria-disabled", "true");
      }
    }
    tulisPesan(
      "Jatah promo di perangkat ini sudah terpakai. Harga promo tidak bisa dipakai lagi di sini.",
      true
    );
  }

  function tulisPesan(teks, salah) {
    if (!pesan) return;
    pesan.hidden = false;
    pesan.textContent = teks;
    pesan.setAttribute("data-salah", salah ? "true" : "false");
  }

  function cariKode(isi) {
    for (var i = 0; i < daftarKode.length; i++) {
      if (daftarKode[i].kode === isi) return daftarKode[i];
    }
    return null;
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      /* Sudah pernah klaim di perangkat ini? Tolak, apa pun kodenya. */
      var lama = baca();
      if (lama) {
        if (Date.now() >= lama.habis) {
          habiskan();
          return;
        }
        var lamaCocok = cariKode(lama.kode);
        if (lamaCocok) {
          tampilkanAktif(lama, lamaCocok);
          return;
        }
      }

      var isi = (input && input.value ? input.value : "").trim().toUpperCase();

      if (!isi) {
        tulisPesan("Kode promonya diisi dulu ya.", true);
        return;
      }

      var cocok = cariKode(isi);
      if (!cocok) {
        tulisPesan("Kode tidak dikenali. Coba periksa lagi hurufnya.", true);
        return;
      }

      var sekarang = Date.now();
      var d = {
        kode: cocok.kode,
        paket: cocok.paket,
        mulai: sekarang,
        habis: sekarang + masaHari * HARI,
      };
      simpan(d);
      tampilkanAktif(d, cocok);
    });
  }

  /* Keadaan saat halaman dibuka. */
  var tersimpan = baca();
  if (!tersimpan) {
    terapkan(false, null);
  } else if (Date.now() >= tersimpan.habis) {
    // Sudah pernah klaim dan waktunya lewat: tetap tertutup.
    habiskan();
  } else {
    var cocokAwal = cariKode(tersimpan.kode);
    if (cocokAwal) {
      tampilkanAktif(tersimpan, cocokAwal);
    } else {
      terapkan(false, null);
    }
  }
})();
