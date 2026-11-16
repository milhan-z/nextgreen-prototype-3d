# Prototype 3D Sistem Air Hujan Greenhouse Melon KWT Pasir Wetan

Ini prototype 3D yang aku bikin buat proposal ACC #NextGreen Leaders Challenge 2026. Isinya satu greenhouse melon KWT Pasir Wetan (Karanglewas, Banyumas), tapak 3 x 6 m, plus usulan sistem air hujan: atap greenhouse dipakai buat nampung air hujan, airnya diolah dulu, lalu jadi cadangan air baku nutrisi pas kemarau. Air sumur tetap dipakai, air hujan olahan jadi cadangan atau campuran.

Viewer online: https://milhan-z.github.io/nextgreen-prototype-3d/

Versi ini (rev 3) sudah aku sesuaikan dengan video greenhouse aktif dari WA 13 Nov 2026, dan tandonnya sudah aku ganti jadi 2 tandon Filtra 2.650 L sesuai RAB.

## Isi folder
- `index.html` : viewer 3D interaktif, bisa offline (Three.js dan model sudah ada di dalam file). Ada panel kontrol: sudut pandang (Keseluruhan, Tandon, Stasiun air, Samping, Dalam, Sudut tong), simulasi hujan, dan lapisan (label, aliran air, atap/kasa, tanaman).
  - Simulasi hujan: pilih Gerimis (5 mm/jam), Sedang (20) atau Lebat (50). Air masuk = hujan (mm) x 18 m² x 0,8, 9 L pertama dibuang first flush, sisanya mengisi 2 tandon (kapasitas nominal 5.300 L). Kalau penuh, air keluar lewat pelimpah. Toggle "Pakai air nutrisi" mengurangi 64,4 L per hari (hitungan tim) supaya kelihatan berapa hari cadangannya cukup. Ini simulasi kasar buat ilustrasi, bukan hasil ukur.
- `prototype.step` : file CAD (assembly berwarna, satuan mm)
- `prototype.stl` : mesh gabungan (mm)
- `prototype.glb` : model 3D berwarna (meter, sumbu Y ke atas)
- `gambar-teknik-A3.pdf` / `.png` : lembar gambar teknik A3 (tampak atas, samping, depan, isometri, daftar komponen, alur air, kop gambar)
- `render-1-overview.png`, `render-2-samping.png`, `render-3-dalam.png`, `render-4-stasiun-air.png`, `render-6-sudut-tong.png`, `render-7-tandon.png` : render 1920x1080 berlabel
- `render-5-iso-nomor.png` : render isometri cuma pakai nomor (dipakai di lembar A3)
- `DESIGN.md` : arah desain viewer (warna, font, dial), dan `anti-slop/` : audit antislop dan laporan perbaikannya
- `src/` : model parametrik CadQuery (`model.py`, semua ukuran di dict `P`), ekspor, proyeksi 2D, lembar A3
- `web/` : sumber viewer (Three.js) dan skrip render

## Kondisi lapangan (video 13 Nov 2026)
Ini yang aku lihat dari video greenhouse yang aktif. Semua ukuran di bawah ini perkiraan dari video, belum diukur.
- Atap plastik UV bening, miring ke dua sisi panjang. Belum ada talang dan pipa turun sama sekali.
- Rangka logam, kelihatannya baja ringan/galvanis, jarak tiang kira kira 1 sampai 1,5 m. Bambu cuma dipakai buat ajir tanaman, dengan kawat horizontal.
- Dinding kasa insect net. Lantai pakai alas mulsa anyaman hitam.
- Tinggi tepi atap kira kira 1,8 sampai 2,0 m.
- Tanaman pakai Dutch bucket yang duduk di atas pipa balik PVC putih (kira kira 2 sampai 2,5 inch) di lantai.
- Tetes pakai selang PE hitam (kira kira 16 mm) di atas tiap baris, plus selang mikro ke tiap ember.
- Di pojok dalam ada tong biru (kira kira 200 L) yang terbuka, ada pipa PVC putih masuk dari atas. Dari bawah tong ada pipa keluar lewat ball valve gagang merah ke tutup abu abu bak lantai yang tertanam.
- Pompanya nggak kelihatan langsung, tapi ada kabel listrik hitam yang turun dari rangka dan masuk ke bak, jadi aku anggap pompa celup (perkiraan).
- Ada selang taman di lantai, kemungkinan buat isi manual dari sumur atau keran (perkiraan, belum dicek).
- Di luar dinding kasa dekat pojok tong kelihatan ada area datar, jadi tandon aku taruh di situ (luasnya belum diukur).
- Aku nggak bikin klaim apa pun soal kondisi tanaman di video. Itu perlu ditanyakan langsung ke mitra.

## Yang berubah di rev 2
- Tinggi tepi atap turun dari 2,2 m jadi kira kira 1,9 m, bubungan jadi kira kira 2,6 m.
- Jarak tiang jadi kira kira 1,2 m (5 bentang).
- Batako alas ember dihapus. Ember sekarang duduk di atas pipa balik PVC putih yang mengalir ke bak lantai.
- Selang tetes biru diganti selang PE hitam 16 mm di sisi tiap baris, plus selang mikro ke tiap ember.
- Ajir bambu dan kawat horizontal ditambahkan.
- Sudut tong disusun ulang: tong biru, pipa isi PVC dari atas, ball valve gagang merah ke tutup bak lantai, pompa celup di dalam bak, kabel hitam turun dari rangka, selang taman.
- Tong digambar pakai tutup sebagai usulan perubahan (aslinya terbuka).
- Tandon dipindah ke luar dinding kasa sisi timur, dekat sudut tong. Air dari tandon lewat filter lalu masuk ke bak lantai.
- Tambah tampilan "Sudut tong" di viewer dan `render-6-sudut-tong.png`.

## Usulan sistem air hujan (warna toska)
1. Atap 18 m² (sudah ada)
2. Talang PVC + kasa kira kira 1 mm di kedua sisi panjang (baru)
3. First flush kira kira 9 L dibuang per greenhouse (0,5 L per m² x 18 m², acuan UNDP 2016)
4. Dua tandon tertutup Filtra TB 2500 (2 × 2.650 L), disambung pipa bawah, dengan pelimpah, lubang angin berkasa, kran di atas dasar (baru)
5. Filter 120 sampai 200 mesh sebelum masuk bak (baru)
6. Cek pH dan TDS (baru)
7. Campur AB mix di tong/bak yang sudah ada
8. Ke tanaman lewat pompa dan tetes yang sudah ada

Harga nggak ada di sini. Rincian biaya ada di lembar RAB terpisah.

## Asumsi & perkiraan
Semua angka ini perkiraan dari foto/video, belum diukur di lapangan:
- Tapak 3 x 6 m dan atap 18 m² dari data tim.
- Tinggi tepi kira kira 1,9 m, bubungan kira kira 2,6 m, jarak tiang kira kira 1,2 m, profil rangka 40 mm.
- Tong kira kira 200 L (Ø0,58 x 0,88 m). Bak lantai Ø0,80 m, dalam 0,60 m. Ukuran pompa celup.
- Pipa balik PVC kira kira 2 inch, selang PE 16 mm, ukuran pipa isi PVC dari atas dan dari mana asalnya.
- Dimensi tandon Filtra 2.650 L belum ditemukan, dimodelkan Ø1,40 x 1,72 m (perkiraan). Dua tandon berjajar di luar dinding kasa sisi timur.
- Diameter talang (kira kira 4 inch), pipa turun (kira kira 2,5 inch), first flush pipa Ø110 sepanjang 1,20 m (kira kira 9 L), letak filter dan meja cek air.
- Arah utara belum dicek. Jalur persis kabel pompa dan selang taman juga belum dicek.
- Ember ditampilkan 24 biar gambar jelas, aslinya sekitar 60 sampai 66 tanaman.
- Model ini ilustrasi buat proposal, bukan gambar kerja konstruksi. Satu dari tiga greenhouse.

## Catatan soal file di repo
Alat upload yang aku pakai cuma bisa kirim file teks dengan ukuran terbatas, jadi file besar (index.html, STEP) dan file biner (PNG, PDF, GLB, STL) di repo ini disimpan sebagai gzip + base64 di folder `b64/`. Workflow GitHub Actions (`.github/workflows/pages.yml`) membongkar file itu lagi waktu deploy ke GitHub Pages, jadi versi aslinya bisa diunduh langsung dari situs:
- https://milhan-z.github.io/nextgreen-prototype-3d/gambar-teknik-A3.pdf
- https://milhan-z.github.io/nextgreen-prototype-3d/render-1-overview.png
- https://milhan-z.github.io/nextgreen-prototype-3d/render-6-sudut-tong.png
- https://milhan-z.github.io/nextgreen-prototype-3d/prototype.glb
- https://milhan-z.github.io/nextgreen-prototype-3d/prototype.stl
- https://milhan-z.github.io/nextgreen-prototype-3d/prototype.step

Kalau mau bongkar sendiri: `base64 -d b64/NAMA.gz.b64 | gunzip > NAMA`

## Bangun ulang
```
python3 -m venv .venv && . .venv/bin/activate && pip install cadquery trimesh matplotlib pillow
npm install
python src/export.py      # STEP, STL, GLB dari src/model.py
python src/drawing.py     # proyeksi HLR buat gambar 2D
node web/build.mjs        # index.html
node web/render.mjs       # render PNG (butuh Chrome)
cp src/iso-sheet.png render-5-iso-nomor.png
python src/sheet.py       # lembar A3
```
