# Prototype 3D TIRTA MANDIRI

Prototype 3D sistem air hujan untuk greenhouse melon KWT Sukadamai, Desa Pasir Wetan (Karanglewas, Banyumas). Aku bikin ini buat proposal ACC #NextGreen Leaders Challenge 2026.

Idenya: atap greenhouse (3 x 6 m) dipakai buat nampung air hujan, airnya disaring, disimpan di 2 tandon, lalu jadi cadangan atau campuran air baku nutrisi pas kemarau. Air sumur tetap dipakai.

**Viewer online:** https://milhan-z.github.io/nextgreen-prototype-3d/

![Render overview](renders/render-1-overview.png)

## Unduh
| File | Isi |
| --- | --- |
| [Viewer 3D](https://milhan-z.github.io/nextgreen-prototype-3d/) (`dist/index.html`) | Viewer interaktif, jalan offline (Three.js, model, dan font sudah di dalam file) |
| [`gambar-teknik-A3.pdf`](https://milhan-z.github.io/nextgreen-prototype-3d/gambar-teknik-A3.pdf) | Lembar gambar teknik A3: tampak atas, samping, depan, isometri, daftar komponen, alur air |
| [`prototype.step`](https://milhan-z.github.io/nextgreen-prototype-3d/prototype.step) | CAD assembly berwarna (mm) |
| [`prototype.stl`](https://milhan-z.github.io/nextgreen-prototype-3d/prototype.stl) | Mesh gabungan (mm) |
| [`prototype.glb`](https://milhan-z.github.io/nextgreen-prototype-3d/prototype.glb) | Model 3D berwarna (meter, sumbu Y ke atas) |
| [`renders/`](renders/) | Render 1920 x 1080 berlabel dari tiap sudut pandang |

## Viewer
- **Sudut pandang:** Keseluruhan, Tandon, Stasiun air, Samping, Dalam, Sudut tong.
- **Simulasi hujan:** Gerimis (5 mm/jam), Sedang (20), Lebat (50). Air masuk = hujan (mm) x 18 m² x 0,8. Tiap kejadian hujan, 9 L pertama dibuang lewat first flush (direset kalau hujan berhenti lalu mulai lagi). Sisanya lewat tabung filter 4 inci dan mengisi 2 tandon sampai lubang masuk, bukan sampai tutup.
- **Pakai air (batch):** bak berkurang 64,4 L per hari (hitungan tim). Bak habis, kran tong dibuka, larutan turun ke bak. Tong diisi lagi dari tandon, kran tandon ditutup, lalu AB mix dan cek EC serta pH. Tandon tidak mengalir terus.
- **Lapisan:** label, aliran air, atap/kasa, tanaman.

Simulasinya kasar, buat ilustrasi, bukan hasil ukur.

## Alur air
Warna toska di model = bagian baru (ada di RAB). Biru tua dan putih = yang sudah ada di KWT. Tandon hitam.

1. Atap 18 m² (sudah ada) menampung hujan.
2. Talang PVC + kasa SS304 di kedua sisi panjang (baru). Bukaan kasa perkiraan.
3. Pipa turun 3 inci (baru) ke first flush sekitar 9 L, lalu tabung filter media 4 inci yang tidur (horizontal).
4. Dua tandon tertutup Filtra TB 2500, hitam, masing-masing 2.650 L, Ø1,415 m, tinggi 1,86 m (spek). Disambung pipa bawah jadi satu muka air. Dudukan batako. Pelimpah hanya moncong bawaan 2 inci, tanpa pipa buang. Lubang angin berkasa.
5. Kran tandon, screen filter 1 inci 120 mesh, dan kran sampel pada pipa PVC 1 inci yang pendek. Pipa masuk tong biru dari samping bawah, supaya air tandon bisa turun sendiri sampai muka airnya hampir sama dengan tong.
6. Tong biru (sudah ada, terbuka) tempat AB mix. EC dan pH dicek di sini. Ada papan SOP di sebelah tong.
7. Ball valve tong dibuka hanya saat bak habis. Larutan turun ke bak bawah tanah (sudah ada).
8. Pompa celup yang sudah ada mendorong air ke tetes, lalu kembali ke bak lewat pipa balik.

Sebagian air sumur ditambahkan ke tong. Sumurnya di luar greenhouse. Satu selang digambar dan ditandai perkiraan, karena belum dicek apakah airnya dipompa atau diangkut manual.

Harga nggak ada di sini. Rincian biaya ada di lembar RAB terpisah.

## Asumsi dan perkiraan
Yang dipakai dari sumber, bukan tebakan:
- Tapak 3 x 6 m dan atap 18 m² dari data tim.
- Kapasitas, diameter, dan tinggi tandon dari spek Filtra/Jerapah TB 2500 (2.650 L, Ø1,415 m, tinggi 1,86 m). Warna di model hitam.
- Pipa turun 3 inci, tabung filter media 4 inci, pipa 1 inci, screen filter 120 mesh, dan pelimpah 2 inci dari RAB serta keterangan KWT.
- First flush 9 L = 0,5 L per m² x 18 m² (acuan yang sudah dipakai tim, UNDP 2016).
- Pemakaian 64,4 L per hari dari hitungan tim.

Yang masih perkiraan, belum diukur di lapangan:
- Tinggi tepi sekitar 1,9 m, bubungan sekitar 2,6 m, jarak tiang sekitar 1,2 m, profil rangka 40 mm. Sumbu talang di model jatuh di sekitar 1,82 m.
- Dudukan tandon 0,40 m. Angka ini satu konstanta, `TANK_BASE` di `src/model.py`, di tengah rentang 0,3 sampai 0,5 m. Lubang masuk dihitung 0,12 m di bawah sumbu talang (sekitar 1,70 m), jadi bagian atas tandon tidak terisi. Kalau dudukan diubah, lubang masuk tetap di bawah talang selama masih mengenai badan tandon.
- Dengan dudukan 0,40 m, simulasi mengisi sampai sekitar 3.700 L dari nominal 5.300 L. Sekitar 430 L di bawah kran tidak mengalir sendiri. Dua angka ini perkiraan dari tinggi, bukan hasil ukur.
- Tong sekitar 200 L (Ø0,58 x 0,88 m). Volume bak belum diukur. Simulasi memakai 200 L sebagai satu isi bak, sama dengan satu isi tong.
- Volume air sumur yang ditambahkan tiap batch belum diukur. Simulasi menganggap tong penuh dari tandon, jadi tandon kelihatan lebih cepat habis daripada kalau dicampur air sumur.
- Panjang tabung filter 4 inci mengikuti jarak pipa turun ke tandon, bukan angka pabrik. Letak tandon, sumur, bak, dan pompa celup juga perkiraan dari video.
- Diameter talang tidak disebut di RAB. Pipa balik sekitar 2 sampai 2,5 inci, selang PE 16 mm.
- Arah utara belum dicek. Jalur kabel pompa belum dicek.
- Ember ditampilkan 24 biar gambar jelas, aslinya sekitar 60 sampai 66 tanaman.
- Model ini ilustrasi, bukan gambar kerja konstruksi. Satu dari tiga greenhouse.

Kondisi lapangan yang jadi dasar model ada di [`docs/catatan-lapangan.md`](docs/catatan-lapangan.md).

## Struktur repo
```
dist/        viewer (index.html) dan model hasil ekspor (STEP, STL, GLB)
drawings/    gambar teknik A3 (PDF, PNG)
renders/     render PNG berlabel
src/         model parametrik CadQuery (semua ukuran di dict P di model.py), ekspor, proyeksi 2D, lembar A3
web/         sumber viewer Three.js dan skrip render
docs/        arah desain viewer, catatan lapangan, riwayat perubahan, audit antislop
```

## Bangun ulang
```
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
npm install
python src/export.py      # dist/prototype.step, .stl, .glb dari src/model.py
python src/drawing.py     # proyeksi HLR buat gambar 2D
npm run build             # dist/index.html
npm run render            # renders/*.png dan src/iso-sheet.png (butuh Chrome)
cp src/iso-sheet.png renders/render-5-iso-nomor.png
python src/sheet.py       # drawings/gambar-teknik-A3.pdf dan .png
```

Setiap push ke `main`, GitHub Actions menyalin isi `dist/`, `renders/`, dan `drawings/` ke GitHub Pages.
