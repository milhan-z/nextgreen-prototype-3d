import pickle, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
from matplotlib.lines import Line2D
from PIL import Image
from model import P

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "")
res = pickle.load(open(D + "src/hlr_cache.pkl", "rb"))
plt.rcParams["font.family"] = "DejaVu Sans"
S = 50.0  # skala 1:50, mm model -> mm kertas
TEAL, INK, GREY = "#00857e", "#1d2327", "#7b838b"

fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.axis("off")
ax.add_patch(Rectangle((10, 10), 400, 277, fill=False, lw=1.4, ec=INK))
ax.add_patch(Rectangle((7, 7), 406, 283, fill=False, lw=0.4, ec=INK))

def T(ox, oy):
    return lambda u, v: (ox + u / S, oy + v / S)

def draw(view, f):
    for gn, kw in (("exist", dict(color=INK, lw=0.45)), ("res", dict(color=INK, lw=0.45)),
                   ("res_h", dict(color=GREY, lw=0.4, ls=(0, (3, 2)))), ("new", dict(color=TEAL, lw=0.85))):
        for pl in res.get((view, gn), []):
            xs, ys = zip(*[f(u, v) for u, v in pl])
            ax.plot(xs, ys, solid_capstyle="round", **kw)

def arrow(p, q):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", lw=0.5, color=INK, mutation_scale=6, shrinkA=0, shrinkB=0))

def dim(p1, p2, off, text, f, horiz=True, fs=7, est=False):
    (x1, y1), (x2, y2) = f(*p1), f(*p2)
    if horiz:
        yd = y1 + off
        ax.plot([x1, x1], [y1, yd + (1.5 if off > 0 else -1.5)], color=INK, lw=0.3)
        ax.plot([x2, x2], [y2, yd + (1.5 if off > 0 else -1.5)], color=INK, lw=0.3)
        ax.plot([x1, x2], [yd, yd], color=INK, lw=0.45)
        arrow(((x1 + x2) / 2, yd), (x1, yd)); arrow(((x1 + x2) / 2, yd), (x2, yd))
        ax.text((x1 + x2) / 2, yd + (1.0 if off > 0 else -1.2), text, ha="center", va="bottom" if off > 0 else "top", fontsize=fs, color=INK,
                bbox=dict(fc="white", ec="none", pad=0.4))
    else:
        xd = x1 + off
        ax.plot([x1, xd + (1.5 if off > 0 else -1.5)], [y1, y1], color=INK, lw=0.3)
        ax.plot([x2, xd + (1.5 if off > 0 else -1.5)], [y2, y2], color=INK, lw=0.3)
        ax.plot([xd, xd], [y1, y2], color=INK, lw=0.45)
        arrow((xd, (y1 + y2) / 2), (xd, y1)); arrow((xd, (y1 + y2) / 2), (xd, y2))
        ax.text(xd + (-1.0 if off < 0 else 1.0), (y1 + y2) / 2, text, ha="right" if off < 0 else "left", va="center", fontsize=fs, color=INK,
                rotation=90 if not est else 0, bbox=dict(fc="white", ec="none", pad=0.4))

def balloon(anchor, at, n, f, new=True):
    ax_, ay_ = f(*anchor)
    ax.plot([ax_, at[0]], [ay_, at[1]], color=INK, lw=0.35)
    ax.add_patch(Circle((ax_, ay_), 0.55, color=INK))
    ax.add_patch(Circle(at, 2.6, fc=TEAL if new else "white", ec=INK, lw=0.6, zorder=5))
    ax.text(at[0], at[1], str(n), ha="center", va="center", fontsize=7.5, color="white" if new else INK, weight="bold", zorder=6)

def vtitle(x, y, t, sub):
    ax.text(x, y, t, fontsize=10, weight="bold", color=INK, ha="left", va="bottom")
    ax.text(x, y - 1.2, sub, fontsize=6.5, color=GREY, ha="left", va="top")

L, W, HE, HR = P["L"], P["W"], P["H_EAVE"], P["H_RIDGE"]
# ---------------- TAMPAK ATAS ----------------
fa = T(35, 200)
draw("atas", fa)
x0, y0 = fa(-P["ROOF_OVER"], -P["ROOF_OVER"]); x1, y1 = fa(L + P["ROOF_OVER"], W + P["ROOF_OVER"])
ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, lw=0.35, ec=GREY, ls=(0, (6, 2, 1, 2))))
ax.plot([fa(-300, W / 2)[0], fa(L + 300, W / 2)[0]], [fa(0, W / 2)[1]] * 2, color=GREY, lw=0.3, ls=(0, (8, 2, 1, 2)))
dim((0, 0), (L, 0), -9, "6,00 m", fa)
dim((0, 0), (0, W), -9, "3,00 m", fa, horiz=False)
dim((P["TANK_XY"][0] - P["TANK_R"], P["TANK_XY"][1] + P["TANK_R"] + 80),
    (P["TANK_XY"][0] + P["TANK_R"], P["TANK_XY"][1] + P["TANK_R"] + 80), 6, "Ø 1,415 m", fa, fs=5.5)
vtitle(35, 281, "TAMPAK ATAS", "skala 1:50, garis titik-strip = tepi atap dan bubungan, tanaman tidak digambar")
for n, anc, yy in ((7, (5620, 2560), 3600), (6, (5100, 2520), 3100), (3, (6450, 2350), 2500), (5, (6380, 2100), 1500), (4, (7600, 1800), 700)):
    balloon(anc, fa(9300, yy), n, fa)
ax.text(*fa(5200, 3900), "ke sumur, di luar greenhouse (perkiraan)", fontsize=5.2, color=GREY, va="center", ha="center")

# ---------------- TAMPAK SAMPING ----------------
fs_ = T(27, 112)
draw("samping", fs_)
gx0, _ = fs_(-1000, 0); gx1, gy = fs_(8600, 0)
ax.plot([gx0, gx1], [gy, gy], color=INK, lw=1.0)
for i in range(40):
    xx = gx0 + i * (gx1 - gx0) / 40
    ax.plot([xx, xx - 1.2], [gy, gy - 1.2], color=GREY, lw=0.25)
dim((0, 0), (L, 0), -13.5, "6,00 m", fs_)
dim((0, 0), (0, HE), -6, "1,90 m (perkiraan)", fs_, horiz=False, fs=6)
dim((0, 0), (0, HR), -12, "2,60 m (perkiraan)", fs_, horiz=False, fs=6)
dim((6400 - 150, P["ZC"] - P["FF_LEN"]), (6400 - 150, P["ZC"]), 0, "", fs_, horiz=False)
ax.text(*fs_(5900, -180), "first flush Ø110 (~9 L) lalu tabung 4 inci horizontal", fontsize=5.3, ha="left", va="top", color=INK,
        bbox=dict(fc="white", ec="none", pad=0.3))
dim((8600, 0), (8600, P["TANK_BASE"] + P["TANK_H"]), 6, "2,26 m (0,40 dudukan perkiraan + 1,86 spek)", fs_, horiz=False, fs=5.5)
vtitle(27, 181, "TAMPAK SAMPING (dari selatan)", "skala 1:50, garis putus = bak lantai dan pompa celup tertanam")
balloon((2400, 2450), fs_(3600, 3050), 1, fs_)
balloon((3800, 1800), fs_(4700, 3050), 2, fs_)
balloon((6450, 1600), fs_(5600, 3050), 3, fs_)
balloon((7500, 1400), fs_(7200, 3050), 4, fs_)
balloon((2800, 440), (fs_(2300, -1250)[0], fs_(0, -1250)[1]), 8, fs_, new=False)

# ---------------- TAMPAK DEPAN ----------------
fd = T(218, 112)
draw("depan", fd)
gx0, gy = fd(-1100, 0); gx1, _ = fd(3600, 0)
ax.plot([gx0, gx1], [gy, gy], color=INK, lw=1.0)
for i in range(22):
    xx = gx0 + i * (gx1 - gx0) / 22
    ax.plot([xx, xx - 1.2], [gy, gy - 1.2], color=GREY, lw=0.25)
dim((0, 0), (W, 0), -13.5, "3,00 m", fd)
dim((W, 0), (W, HR), 14, "2,60 m (perkiraan)", fd, horiz=False, fs=6)
vtitle(205, 181, "TAMPAK DEPAN (dari timur)", "skala 1:50, sisi stasiun air")
balloon((-110, 1800), fd(-900, 2800), 2, fd)
balloon((2200, 2250), fd(2900, 3050), 1, fd)

# ---------------- ISO ----------------
im = Image.open(D + "src/iso-sheet.png").convert("RGB")
w, h = im.size
im = im.crop((int(w * 0.07), int(h * 0.07), int(w * 0.90), int(h * 0.88)))
iw, ih = im.size
X0, Y0, WW = 252, 193, 152
HH = WW * ih / iw
ax.imshow(im, extent=(X0, X0 + WW, Y0, Y0 + HH), zorder=1, interpolation="lanczos")
ax.add_patch(Rectangle((X0, Y0), WW, HH, fill=False, lw=0.5, ec=GREY))
ax.text(X0, Y0 + HH + 1.2, "TAMPAK ISOMETRI (render 3D, tanpa skala)", fontsize=10, weight="bold", color=INK, va="bottom")

# ---------------- DAFTAR KOMPONEN ----------------
BX, BY, BW = 300, 186, 110
rows = [
    ("1", "Atap 18 m²", "plastik UV bening, 3 x 6 m,\nsudah ada, belum ada talang", "Ada"),
    ("2", "Talang + kasa SS304", "PVC, dua sisi panjang,\nbukaan kasa perkiraan", "Baru"),
    ("3", "First flush + tabung 4 inci", "9 L dibuang, lalu tabung\nmedia 4 inci horizontal", "Baru"),
    ("4", "2 tandon Filtra TB 2500", "2 x 2.650 L, hitam, Ø1,415 x 1,86 m,\npipa bawah, pelimpah 2 inci bawaan", "Baru"),
    ("5", "Pipa 1 inci ke tong biru", "kran tandon, screen filter 120 mesh,\nkran sampel, masuk samping bawah", "Baru"),
    ("6", "Cek EC dan pH di tong biru", "meter + papan SOP di sebelah tong,\nbukan meja di luar", "Baru"),
    ("7", "Campur AB mix di tong biru", "tong terbuka (sudah ada),\nball valve ke bak saat bak habis", "Ada"),
    ("8", "Ke tanaman (Dutch Bucket, tetes)", "pompa celup + PE 16 mm yang ada,\nbalik lewat pipa PVC ~2 inch", "Ada"),
]
ax.text(BX, BY + 2, "DAFTAR KOMPONEN", fontsize=10, weight="bold", color=INK, va="bottom")
cols = [BX, BX + 7, BX + 52, BX + 98, BX + BW]
y = BY
rh = 5.2
ax.add_patch(Rectangle((BX, y - rh), BW, rh, fc="#e9edf0", ec=INK, lw=0.5))
for t, cx in zip(("No", "Komponen", "Keterangan", "Status"), cols):
    ax.text(cx + 1.2, y - rh / 2, t, fontsize=6.5, weight="bold", va="center")
y -= rh
for no, k, ket, st in rows:
    hh = rh * (1.7 if "\n" in ket or len(k) > 26 else 1.15)
    ax.add_patch(Rectangle((BX, y - hh), BW, hh, fc="white", ec=INK, lw=0.4))
    ax.add_patch(Circle((BX + 3.5, y - hh / 2), 2.1, fc=TEAL if st == "Baru" else "white", ec=INK, lw=0.5))
    ax.text(BX + 3.5, y - hh / 2, no, fontsize=6.5, ha="center", va="center", weight="bold", color="white" if st == "Baru" else INK)
    kk = k if len(k) <= 26 else k.replace(" di tong", "\ndi tong").replace(" (Dutch", "\n(Dutch")
    ax.text(cols[1] + 1.2, y - hh / 2, kk, fontsize=6.0, va="center", linespacing=1.15)
    ax.text(cols[2] + 1.2, y - hh / 2, ket, fontsize=5.4, va="center", color="#333a40", linespacing=1.15)
    ax.text(cols[3] + 1.2, y - hh / 2, st, fontsize=6.0, va="center", color=TEAL if st == "Baru" else INK, weight="bold")
    y -= hh
for cx in cols[1:4]:
    ax.plot([cx, cx], [BY, y], color=INK, lw=0.4)
ax.text(BX, y - 2, "Tanpa harga. Rincian biaya ada di lembar RAB terpisah.", fontsize=5.5, color=GREY, va="top")
ax.text(BX, y - 5.5, "Air sumur tetap dipakai, air hujan olahan jadi cadangan kemarau.", fontsize=5.5, color=GREY, va="top")

# ---------------- CATATAN ----------------
NX, NY = 14, 64
ax.text(NX + 4, NY, "CATATAN", fontsize=9, weight="bold", va="bottom")
notes = [
    "Tapak 3,00 x 6,00 m dan atap 18 m² dari data tim. Tinggi tepi ±1,90 m dan bubungan ±2,60 m perkiraan dari video 13 Nov 2026.",
    "Kondisi yang ada mengikuti video: rangka baja ringan, ember di atas pipa balik PVC, tetes PE 16 mm, tong, bak lantai, pompa.",
    "Jarak tiang ±1,20 m. Tong (~200 L), bak, pompa, letak tandon dan sumur masih perkiraan. Spek tandon TB 2500: Ø1,415 m, tinggi 1,86 m. Dudukan 0,40 m (perkiraan).",
    "First flush 0,5 L per m² x 18 m² = 9 L (UNDP 2016), direset tiap kejadian hujan. Tabung filter 4 inci horizontal, panjangnya perkiraan.",
    "Ember ditampilkan 24 buah agar gambar jelas (aslinya sekitar 60 sampai 66 tanaman). Tanaman tidak digambar di tampak 2D.",
    "Warna toska = sistem air hujan usulan baru. Warna hitam/abu = kondisi yang sudah ada di lokasi.",
    "Model ilustratif untuk proposal, bukan gambar kerja konstruksi. Satu dari tiga greenhouse, tandon diletakkan di luar dinding kasa.",
]
for i, n in enumerate(notes):
    ax.text(NX + 4, NY - 4 - i * 4.4, f"{i + 1}.  {n}", fontsize=6.2, va="top", color="#2b3136")

# legenda garis
LX, LY = 18, 22
ax.add_line(Line2D([LX, LX + 10], [LY, LY], color=INK, lw=0.45)); ax.text(LX + 12, LY, "sudah ada", fontsize=6, va="center")
ax.add_line(Line2D([LX + 35, LX + 45], [LY, LY], color=TEAL, lw=0.9)); ax.text(LX + 47, LY, "baru (usulan)", fontsize=6, va="center")
ax.add_line(Line2D([LX + 78, LX + 88], [LY, LY], color=GREY, lw=0.4, ls=(0, (3, 2)))); ax.text(LX + 90, LY, "tersembunyi / di bawah tanah", fontsize=6, va="center")
ax.add_line(Line2D([LX + 132, LX + 142], [LY, LY], color=GREY, lw=0.35, ls=(0, (6, 2, 1, 2)))); ax.text(LX + 144, LY, "tepi atap / sumbu", fontsize=6, va="center")
ax.add_patch(Rectangle((14, 16), 196, 12, fill=False, ec=INK, lw=0.4))

# ---------------- ALUR AIR ----------------
FX, FY = 214, 98
ax.text(FX, FY + 1.5, "ALUR AIR HUJAN", fontsize=9, weight="bold", va="bottom")
steps = ["Atap 18 m²", "Talang + kasa", "First flush +\ntabung 4 inci", "2 tandon hitam\n2 x 2.650 L", "Pipa 1 inci\nke tong biru", "Cek EC + pH\ndi tong biru", "Campur AB mix\ndi tong biru", "Ke tanaman\n(tetes)"]
bw_, bh_, gap = 42, 11, 7
for i, t in enumerate(steps):
    r, c = divmod(i, 4)
    x = FX + c * (bw_ + gap); y = FY - 4 - r * (bh_ + 7) - bh_
    new = i in (1, 2, 3, 4, 5)
    ax.add_patch(FancyBboxPatch((x, y), bw_, bh_, boxstyle="round,pad=0,rounding_size=1.5", fc="#e6f4f3" if new else "white", ec=TEAL if new else INK, lw=0.7))
    ax.add_patch(Circle((x + 4.5, y + bh_ / 2), 2.4, fc=TEAL if new else "white", ec=INK, lw=0.5))
    ax.text(x + 4.5, y + bh_ / 2, str(i + 1), ha="center", va="center", fontsize=6.5, weight="bold", color="white" if new else INK)
    ax.text(x + 8.5, y + bh_ / 2, t, va="center", fontsize=6.2, linespacing=1.1)
    if c < 3:
        arrow((x + bw_ + 0.5, y + bh_ / 2), (x + bw_ + gap - 0.5, y + bh_ / 2))
    elif r == 0:
        ax.annotate("", xy=(FX + 4.5, y - 6.5 + 0.2), xytext=(x + bw_ / 2, y), arrowprops=dict(arrowstyle="-|>", lw=0.5, color=INK, mutation_scale=6, connectionstyle="angle,angleA=-90,angleB=180,rad=0"))
ax.text(FX, FY - 4 - 2 * (bh_ + 7) + 4, "Kotak toska = bagian baru. Air diisi per batch. Air sumur ke tong ditandai perkiraan (pompa atau manual).", fontsize=5.6, color=GREY, va="top")

# ---------------- KOP GAMBAR ----------------
TX, TY, TW, THh = 250, 10, 160, 46
ax.add_patch(Rectangle((TX, TY), TW, THh, fill=False, ec=INK, lw=1.0))
ax.plot([TX, TX + TW], [TY + 30, TY + 30], color=INK, lw=0.5)
ax.plot([TX, TX + TW], [TY + 20, TY + 20], color=INK, lw=0.5)
ax.plot([TX, TX + TW], [TY + 10, TY + 10], color=INK, lw=0.5)
for cx in (TX + 55, TX + 105):
    ax.plot([cx, cx], [TY, TY + 20], color=INK, lw=0.5)
ax.text(TX + 3, TY + 40.5, "Prototype Sistem Air Hujan Greenhouse Melon KWT, Pasir Wetan", fontsize=8.6, weight="bold", va="center")
ax.text(TX + 3, TY + 34, "Karanglewas, Banyumas. ACC #NextGreen Leaders Challenge 2026", fontsize=6.3, va="center", color="#333a40")
ax.text(TX + 3, TY + 25, "Catatan: semua ukuran perkiraan dari video 13 Nov 2026, belum diukur", fontsize=6.0, va="center", color="#b3471d")
cells = [("SKALA", "1:50 (A3)"), ("TANGGAL", "24 Nov 2026"), ("SATUAN", "meter")]
cells2 = [("LEMBAR", "1 dari 1"), ("STATUS", "Konsep proposal, rev 4"), ("MITRA", "KWT Pasir Wetan")]
for (k, v), cx in zip(cells, (TX, TX + 55, TX + 105)):
    ax.text(cx + 2, TY + 17.5, k, fontsize=5, color=GREY, va="center"); ax.text(cx + 2, TY + 13, v, fontsize=7.2, weight="bold", va="center")
for (k, v), cx in zip(cells2, (TX, TX + 55, TX + 105)):
    ax.text(cx + 2, TY + 7.5, k, fontsize=5, color=GREY, va="center"); ax.text(cx + 2, TY + 3, v, fontsize=7.2, weight="bold", va="center")

# panah utara di tampak atas
NXa, NYa = 238, 212
ax.annotate("", xy=(NXa, NYa + 8), xytext=(NXa, NYa), arrowprops=dict(arrowstyle="-|>", lw=0.8, color=INK))
ax.text(NXa, NYa + 9, "U", ha="center", va="bottom", fontsize=7, weight="bold")
ax.text(NXa, NYa - 1.5, "arah utara\nbelum dicek", ha="center", va="top", fontsize=4.8, color=GREY)

fig.savefig(D + "drawings/gambar-teknik-A3.pdf")
fig.savefig(D + "drawings/gambar-teknik-A3.png", dpi=200)
print("saved")
