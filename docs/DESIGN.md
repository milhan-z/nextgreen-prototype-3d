# DESIGN.md: viewer prototype 3D TIRTA MANDIRI

Arah desain ini diambil dari bahan proyek yang sudah ada (deck lomba dan gambar teknik), bukan gaya baru.

## Untuk siapa dan untuk apa
- Juri ACC #NextGreen dan anggota KWT Sukadamai yang membuka link dari slide.
- Tugas layar: melihat di mana tiap komponen sistem air hujan dipasang, lalu mencoba simulasi hujan untuk melihat berapa liter yang masuk ke 2 tandon dan cukup untuk berapa hari.
- Satu hal yang harus menang di layar: model 3D. Panel hanya alat bantu.

## Dial
Dial: ENERGY 1 / RHYTHM 1 / MOTION 2
- ENERGY 1: ini lampiran teknis proposal, tenang seperti lembar gambar teknik.
- RHYTHM 1: panel kontrol satu kolom yang seragam, sengaja, supaya cepat dipindai.
- MOTION 2: gerak cuma untuk isi simulasi (titik aliran air, hujan, muka air naik). UI sendiri tidak beranimasi kecuali transisi panel di HP.

## Warna (token)
- Ink #16212b: teks utama.
- Navy #004890: warna navy logo ACC, dipakai untuk tombol sudut pandang yang aktif.
- Teal #00857e: warna "komponen baru" yang sudah dipakai di model sejak rev 1. Sengaja bukan hijau supaya tidak tertukar dengan daun melon.
- Hitam #1a1c1e: kedua tandon Filtra TB 2500. Pengukur isi di panel memakai garis tepi hitam yang sama. Air di dalam tetap biru.
- Biru air #0b6aa8: hanya untuk hal yang berhubungan dengan air hujan (tombol hujan aktif, isi tandon). Versi lebih gelap dari biru aliran supaya teks putih lolos kontras.
- Latar #e9ecef rata: abu muda netral seperti kertas gambar, tanpa gradasi atau sorotan.

## Huruf
- Mitr (judul dan angka besar): font judul yang sama dengan deck tim, jadi viewer terasa satu keluarga dengan slide.
- Carlito (teks): font isi deck tim, terbaca baik di ukuran kecil.
- File font ditanam di index.html supaya tetap jalan offline.

## Motif
- Callout bernomor 1 sampai 8 yang sama dengan nomor di gambar teknik A3, jadi orang bisa pindah dari lembar A3 ke viewer tanpa belajar ulang.

## Yang tidak dipakai
- Label kecil huruf kapital di atas judul, garis warna di tepi kiri, bayangan besar, gradasi latar, ikon dekoratif.
