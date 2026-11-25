"""Model parametrik greenhouse melon KWT + sistem air hujan (usulan).
Versi 2: disesuaikan dengan video greenhouse aktif (WA 13 Nov 2026).
Satuan mm. Sumbu: X = panjang (6 m), Y = lebar (3 m), Z = atas.
Angka bertanda EST = perkiraan dari video, belum diukur di lapangan.
"""
import math
import cadquery as cq

P = dict(
    L=6000, W=3000,             # tapak, dari data tim
    H_EAVE=1900,                # EST, video: kira kira 1,8 sampai 2,0 m
    H_RIDGE=2600,               # EST, proporsional
    BAY=1200,                   # jarak tiang, EST (video: 1 sampai 1,5 m)
    TUBE=40,                    # profil baja ringan / galvanis, EST
    ROOF_OVER=100,              # tonjolan atap melewati dinding, EST
    GUT_R=55,                   # talang PVC ~4 inch (usulan), EST
    DP_R=32,                    # pipa turun ~2,5 inch (usulan), EST
    FF_R=55, FF_LEN=1200,       # first flush pipa 110 mm, ~9 L (0,5 L/m2 x 18 m2)
    TANK_R=700, TANK_H=1720, TANK_BASE=100,  # 2 x Filtra TB 2500 (2.650 L), dimensi belum ditemukan: perkiraan Ø1,40 x 1,72 m
    TANK_XY=(7250, 2350),       # tandon 1 (masuk), di luar dinding kasa sisi timur, EST
    TANK2_Y=800,                # tandon 2, berjajar ke selatan, disambung pipa bawah, EST
    TAP_Z=400,                  # kran keluar tandon (tinggi absolut), di atas dasar
    ZC=1720,                    # tinggi pipa kolektor di luar = lubang masuk samping tandon, EST
    DRUM_R=290, DRUM_H=880,     # tong biru ~200 L, EST dari video
    DRUM_XY=(5620, 2560),       # sudut dalam greenhouse, EST
    WELL_XY=(7350, 3750), WELL_R=400,  # sumur di luar sisi utara-timur: letak dan ukuran perkiraan
    DRUM_IN_Z=180,              # lubang masuk air tandon di samping bawah tong (usulan), EST
    RES_R=400, RES_D=600,       # bak tanam di lantai bertutup abu abu, EST
    RES_XY=(5500, 1750),
    ROWS=(850, 2150), N_PER_ROW=12, X0=450, DX=380,  # 24 ember ditampilkan (aslinya ~60 sampai 66)
    BKT_TOP=300, BKT_BOT=250, BKT_H=320,
    RET_R=32,                   # pipa balik PVC putih ~2 sampai 2,5 inch, EST
    PE_R=8,                     # selang PE hitam ~16 mm
    MICRO_R=2.5,                # selang mikro ke tiap ember
    PE_Z=440,                   # tinggi selang PE di atas baris ember
    WIRE_Z=1750,                # kawat horizontal untuk ajir
)

C = dict(  # warna RGB 0..1, konsisten untuk STEP/GLB/render
    frame=(0.62, 0.65, 0.68), roof=(0.85, 0.92, 0.96), net=(0.88, 0.89, 0.90),
    mat=(0.10, 0.10, 0.11), bucket=(0.95, 0.95, 0.93), lid=(0.80, 0.80, 0.78),
    pvc=(0.96, 0.96, 0.96), pe=(0.07, 0.07, 0.08), bamboo=(0.74, 0.64, 0.40),
    plant=(0.30, 0.55, 0.25), melon=(0.80, 0.80, 0.56), drum=(0.10, 0.36, 0.78),
    reslid=(0.55, 0.57, 0.58), pumpbody=(0.38, 0.45, 0.55), cable=(0.05, 0.05, 0.05),
    valve=(0.85, 0.12, 0.10), hose=(0.95, 0.80, 0.15),
    new=(0.00, 0.62, 0.58), tank=(0.09, 0.09, 0.10), filter=(0.30, 0.72, 0.86),
    table=(0.72, 0.60, 0.45), meter=(0.95, 0.75, 0.15), ground=(0.80, 0.82, 0.78),
    concrete=(0.70, 0.70, 0.68),
)

parts = []  # (name, group, color_key, shape)
# group: frame, cover, existing, reslid, plant, new, site
A = {}      # titik acuan (mm) untuk label dan aliran air di viewer
FLOW = []   # polyline aliran air (mm)
FLOWK = []  # jenis tiap aliran: loop, rain, ff, link, out, over
SIM = {}    # angka untuk simulasi hujan di viewer


def fl(kind, pts):
    FLOW.append(pts); FLOWK.append(kind)


def add(name, group, ck, shape):
    if isinstance(shape, cq.Workplane):
        shape = shape.val() if len(shape.vals()) == 1 else cq.Compound.makeCompound(shape.vals())
    parts.append((name, group, ck, shape))


def V(*a):
    return cq.Vector(*a)


def bar(p1, p2, size, round_=False):
    p1, p2 = V(*p1), V(*p2)
    d = p2 - p1
    ln = d.Length
    n = d.normalized()
    ref = V(0, 0, 1) if abs(n.z) < 0.9 else V(1, 0, 0)
    xd = ref.cross(n).normalized()
    pl = cq.Plane(origin=p1, xDir=xd, normal=n)
    wp = cq.Workplane(pl)
    wp = wp.circle(size) if round_ else wp.rect(size, size)
    return wp.extrude(ln).val()


def pipe(pts, r, joints=True):
    """Polyline pipa dengan sambungan bola (elbow sederhana)."""
    solids = [bar(a, b, r, True) for a, b in zip(pts[:-1], pts[1:])]
    if joints:
        for p in pts[1:-1]:
            solids.append(cq.Solid.makeSphere(r * 1.15, V(*p), angleDegrees1=-90))
    return cq.Compound.makeCompound(solids)


def box(x0, y0, z0, dx, dy, dz):
    return cq.Solid.makeBox(dx, dy, dz, V(x0, y0, z0))


def cyl(x, y, z, r, h):
    return cq.Solid.makeCylinder(r, h, V(x, y, z))


def build():
    parts.clear(); A.clear(); FLOW.clear(); FLOWK.clear(); SIM.clear()
    L, W, HE, HR, T = P["L"], P["W"], P["H_EAVE"], P["H_RIDGE"], P["TUBE"]
    ym = W / 2
    rx, ry = P["RES_XY"]
    dx_, dy_ = P["DRUM_XY"]
    tx, ty = P["TANK_XY"]
    # ---------------- rangka baja ringan / galvanis ----------------
    fr = []
    n_bay = round(L / P["BAY"])
    xs = [i * L / n_bay for i in range(n_bay + 1)]
    for x in xs:
        for y in (0, W):
            fr.append(bar((x, y, 0), (x, y, HE), T))
            fr.append(bar((x, y, HE), (x, ym, HR), T))  # kuda-kuda
    for y in (0, W):
        for z in (T / 2, 950, HE):
            fr.append(bar((0, y, z), (L, y, z), T))
    fr.append(bar((0, ym, HR), (L, ym, HR), T))  # bubungan
    for x in (0, L):
        fr.append(bar((x, 0, HE), (x, W, HE), T))
        fr.append(bar((x, 0, T / 2), (x, W, T / 2), T))
        for y in (750, 2250):
            zt = HE + (HR - HE) * (1 - abs(y - ym) / ym)
            fr.append(bar((x, y, 0), (x, y, zt), T))
    fr.append(bar((L, ym, 0), (L, ym, HR), T))
    # pintu di sisi X=0
    d0, d1, dh = 1050, 1950, 1750
    for y in (d0, d1):
        fr.append(bar((0, y, 0), (0, y, HE), T))
    fr.append(bar((0, d0, dh), (0, d1, dh), T))
    fr.append(bar((-30, d0 + 40, 60), (-30, d1 - 40, dh - 60), 30))
    fr.append(bar((-30, d0 + 40, 900), (-30, d1 - 40, 900), 30))
    add("Rangka baja ringan galvanis (sudah ada)", "frame", "frame", cq.Compound.makeCompound(fr))
    add("Engsel pintu", "frame", "pumpbody", cq.Compound.makeCompound(
        [cyl(-35, d0 + 20, z, 15, 120) for z in (300, 1400)]))

    # ---------------- penutup ----------------
    ro = P["ROOF_OVER"]
    slope_dz = (HR - HE) / ym
    for side, ye in (("selatan", -ro), ("utara", W + ro)):
        ze = HE - slope_dz * ro
        pts = [V(-ro, ym, HR + T / 2), V(L + ro, ym, HR + T / 2), V(L + ro, ye, ze + T / 2), V(-ro, ye, ze + T / 2)]
        f = cq.Face.makeFromWires(cq.Wire.makePolygon(pts, close=True))
        add(f"Atap plastik UV bening ({side})", "cover", "roof", f.thicken(3))
    netf = []
    for y in (0, W):
        netf.append(cq.Face.makeFromWires(cq.Wire.makePolygon(
            [V(0, y, 0), V(L, y, 0), V(L, y, HE), V(0, y, HE)], close=True)))
    for x in (0, L):
        netf.append(cq.Face.makeFromWires(cq.Wire.makePolygon(
            [V(x, 0, 0), V(x, W, 0), V(x, W, HE), V(x, ym, HR), V(x, 0, HE)], close=True)))
    add("Dinding kasa insect net", "cover", "net", cq.Compound.makeCompound([f.thicken(1) for f in netf]))
    A["roof"] = (2400, 800, HE + (HR - HE) * 800 / ym)

    # ---------------- lantai dan bak tertanam (sudah ada) ----------------
    hole = cyl(rx, ry, -700, P["RES_R"], 800)
    add("Alas mulsa anyaman hitam", "existing", "mat", box(0, 0, 0, L, W, 5).cut(hole))
    add("Tutup bak lantai abu abu (sudah ada)", "reslid", "reslid", cyl(rx, ry, -5, P["RES_R"] + 40, 25))
    add("Bak lantai bagian tertanam", "existing", "concrete",
        cq.Workplane("XY", origin=(rx, ry, -P["RES_D"])).circle(P["RES_R"]).extrude(P["RES_D"] - 5).faces(">Z").shell(-30).val())
    A["res"] = (rx - 250, ry - 200, 20)

    # ---------------- Dutch bucket di atas pipa balik PVC ----------------
    bk, lids, rets, pe, micro, stems, leaves, melons, ties, stakes, wires = ([] for _ in range(11))
    bt, bb, bh, rr = P["BKT_TOP"], P["BKT_BOT"], P["BKT_H"], P["RET_R"]
    zr = 5 + rr                        # sumbu pipa balik
    z0 = 5 + 2 * rr                    # dasar ember duduk di atas pipa
    zl = z0 + bh + 18                  # atas tutup ember
    pez = P["PE_Z"]
    x_last = P["X0"] + (P["N_PER_ROW"] - 1) * P["DX"]
    xh = x_last + 320                  # header PE
    for ri, yr in enumerate(P["ROWS"]):
        ype = yr - 190                 # selang PE di sisi baris
        for i in range(P["N_PER_ROW"]):
            x = P["X0"] + i * P["DX"]
            b = (cq.Workplane("XY", origin=(x, yr, z0)).rect(bb, bb).workplane(offset=bh).rect(bt, bt).loft())
            bk.append(b.faces(">Z").shell(-4).val())
            lids.append(box(x - bt / 2 - 5, yr - bt / 2 - 5, z0 + bh, bt + 10, bt + 10, 18))
            # selang mikro dari PE ke ember
            micro.append(pipe([(x - 40, ype, pez), (x - 40, ype + 60, pez + 40), (x - 40, yr - 70, zl + 40), (x - 40, yr - 60, zl + 5)], P["MICRO_R"], joints=False))
            # ajir bambu + tanaman stylized
            sx = x + 95
            stakes.append(bar((sx, yr, zl - 30), (sx, yr, P["WIRE_Z"] + 40), 11, True))
            stems.append(bar((x, yr, zl), (x, yr, P["WIRE_Z"] - 20), 8, True))
            for k, zz in enumerate((620, 860, 1100, 1340, 1580)):
                ang = (k * 137 + i * 40 + ri * 90) % 360
                cx = x + 110 * math.cos(math.radians(ang))
                cy = yr + 110 * math.sin(math.radians(ang))
                e = cq.Workplane("XY", origin=(cx, cy, zz)).ellipse(105, 70).extrude(6)
                e = e.rotate((cx, cy, zz), (cx + math.sin(math.radians(ang)), cy - math.cos(math.radians(ang)), zz), 25)
                leaves.append(e.val())
            mz = 950 + (i % 3) * 80
            mx, my = x - 60, yr + (60 if ri == 0 else -60)
            melons.append(cq.Solid.makeSphere(75, V(mx, my, mz), angleDegrees1=-90))
            ties.append(bar((mx, my, mz + 75), (x, yr, mz + 330), 2, True))
        # pipa balik di bawah baris, menuju bak lantai
        xe = rx - 150
        yin = ry - 300 if ri == 0 else ry + 330
        route = [(P["X0"] - 220, yr, zr), (xe, yr, zr), (xe, yin, zr), (xe, yin, 0)]
        rets.append(pipe(route, rr))
        fl('loop', [(P["X0"] - 150, yr, zr), (xe, yr, zr), (xe, yin, zr), (xe, yin, -150)])
        # selang PE hitam di sepanjang baris + kawat
        pe.append(pipe([(xh, ype, pez), (P["X0"] - 200, ype, pez)], P["PE_R"], joints=False))
        wires.append(bar((100, yr, P["WIRE_Z"]), (L - 100, yr, P["WIRE_Z"]), 3, True))
    # header PE dari pompa celup
    px, py = rx + 20, ry + 70          # pompa celup
    ype0, ype1 = P["ROWS"][0] - 190, P["ROWS"][1] - 190
    pe.append(pipe([(px, py, -450), (px, py, pez), (xh, py, pez), (xh, ype1, pez)], P["PE_R"]))
    pe.append(pipe([(xh, py, pez), (xh, ype0, pez)], P["PE_R"], joints=False))
    for yp in (ype0, ype1):
        fl('loop', [(px, py, -450), (px, py, pez), (xh, py, pez), (xh, yp, pez), (P["X0"] - 150, yp, pez)])
    add("Ember Dutch Bucket (sudah ada)", "existing", "bucket", cq.Compound.makeCompound(bk))
    add("Tutup ember", "existing", "lid", cq.Compound.makeCompound(lids))
    add("Pipa balik PVC putih ~2 inch (sudah ada)", "existing", "pvc", cq.Compound.makeCompound(rets))
    add("Selang PE hitam 16 mm (sudah ada)", "existing", "pe", cq.Compound.makeCompound(pe))
    add("Selang mikro tetes (sudah ada)", "existing", "pe", cq.Compound.makeCompound(micro))
    add("Ajir bambu (sudah ada)", "existing", "bamboo", cq.Compound.makeCompound(stakes))
    add("Kawat penyangga", "existing", "frame", cq.Compound.makeCompound(wires + ties))
    add("Batang melon", "plant", "plant", cq.Compound.makeCompound(stems))
    add("Daun melon", "plant", "plant", cq.Compound.makeCompound(leaves))
    add("Buah melon", "plant", "melon", cq.Compound.makeCompound(melons))
    A["drip"] = (P["X0"] + 4 * P["DX"] - 40, P["ROWS"][1] - 190, pez)
    A["ret"] = (P["X0"] + 6 * P["DX"], P["ROWS"][0], zr + rr)
    A["bucket"] = (P["X0"] + 3 * P["DX"], P["ROWS"][1], zl)

    # ---------------- sudut tong (sudah ada) ----------------
    drum = cq.Workplane("XY", origin=(dx_, dy_, 5)).circle(P["DRUM_R"]).extrude(P["DRUM_H"]).faces(">Z").shell(-4)
    drum = drum.union(cq.Workplane("XY", origin=(dx_, dy_, 5 + P["DRUM_H"] - 30)).circle(P["DRUM_R"] + 8).circle(P["DRUM_R"] - 2).extrude(14))
    drum = drum.union(cq.Workplane("XY", origin=(dx_, dy_, 5 + P["DRUM_H"] * 0.45)).circle(P["DRUM_R"] + 8).circle(P["DRUM_R"] - 2).extrude(14))
    add("Tong biru ~200 L (sudah ada)", "existing", "drum", drum)
    dtop = 5 + P["DRUM_H"]
    A["drum"] = (dx_ - 150, dy_ - 150, dtop + 20)
    # pipa isi PVC putih dari atas: diduga dari sumur di luar greenhouse (Pak Aji 24 Nov: sumur di luar).
    # Letak dan ukuran sumur perkiraan, cara angkat air (pompa atau manual) belum dicek.
    wx, wy = P["WELL_XY"]
    x0, y0 = dx_ + 80, dy_ + 40
    add("Pipa air sumur ke tong, dari atas (dugaan, sudah ada)", "existing", "pvc",
        pipe([(x0, y0, dtop - 150), (x0, y0, 1500), (x0, W + 300, 1500), (x0, W + 300, 900),
              (wx, W + 300, 900), (wx, wy, 900), (wx, wy, 350)], 22))
    add("Sumur (letak dan ukuran perkiraan, sudah ada)", "existing", "concrete",
        cq.Workplane("XY", origin=(wx, wy, 0)).circle(P["WELL_R"]).circle(P["WELL_R"] - 70).extrude(700).val())
    A["well"] = (wx + P["WELL_R"], wy, 500)
    A["fillpipe"] = (x0, W + 300, 1200)
    # keluaran bawah tong -> ball valve gagang merah -> tutup bak lantai
    yv0 = dy_ - P["DRUM_R"] + 5
    yv1 = ry + P["RES_R"] - 70
    zv = 90
    add("Pipa keluar tong ke bak (sudah ada)", "existing", "pvc",
        pipe([(dx_, yv0 + 20, zv), (dx_, yv1, zv), (dx_, yv1, 10)], 18))
    yvb = (yv0 + yv1) / 2
    add("Ball valve gagang merah (sudah ada)", "existing", "valve", cq.Compound.makeCompound([
        bar((dx_, yvb - 45, zv), (dx_, yvb + 45, zv), 30, True),
        bar((dx_, yvb, zv), (dx_, yvb, zv + 50), 7, True),
        box(dx_ - 10, yvb - 8, zv + 45, 130, 16, 10)]))
    fl('loop', [(dx_, dy_, 300), (dx_, yv0 + 20, zv), (dx_, yv1, zv), (dx_, yv1, -150)])
    A["valve"] = (dx_ + 40, yvb, zv + 50)
    # pompa celup di dalam bak + kabel hitam turun dari rangka
    add("Pompa celup (perkiraan, sudah ada)", "existing", "pumpbody", cq.Compound.makeCompound([
        cyl(px, py, -P["RES_D"] + 30, 75, 140), cyl(px, py, -P["RES_D"] + 170, 20, 30)]))
    cx_, cy_ = rx + 260, ry - 150
    yc = ym + 30
    add("Kabel listrik pompa (sudah ada)", "existing", "cable",
        pipe([(px + 60, py, -P["RES_D"] + 100), (cx_, cy_, -P["RES_D"] + 100), (cx_, cy_, 22), (L - 45, cy_, 22),
              (L - 45, yc, 22), (L - 45, yc, HE - 60), (L - 45, W - 45, HE - 60), (L + 120, W - 45, HE - 60)], 5))
    A["pump"] = (px, py, -P["RES_D"] + 170)
    A["cable"] = (L - 45, yc, 1100)
    # selang taman (isi manual)
    hz = 14
    add("Selang taman (isi manual, perkiraan)", "existing", "hose",
        pipe([(dx_ - 220, dy_ + 120, dtop - 40), (dx_ - 330, dy_ + 160, 600), (dx_ - 380, dy_ + 200, hz), (5000, 2700, hz),
              (5150, 2950, hz), (5700, 2960, hz), (L + 300, W + 250, hz), (L + 800, W + 450, hz)], 9))
    A["hose"] = (L + 550, W + 350, hz)

    # ---------------- sistem air hujan BARU ----------------
    gz = HE - slope_dz * ro - P["GUT_R"] + 20
    gl, kasa = [], []
    for yg in (-ro - 10, W + ro + 10):
        g = (cq.Workplane("YZ", origin=(-ro, yg, gz)).circle(P["GUT_R"]).circle(P["GUT_R"] - 4)
             .extrude(L + 2 * ro + 150))
        g = g.cut(cq.Workplane("XY").box(L + 600, 3 * P["GUT_R"], 2 * P["GUT_R"], centered=(False, True, False))
                  .translate((-ro - 200, yg, gz)))
        gl.append(g.val())
        for xe in (-ro, L + ro + 150):
            gl.append(cyl(0, 0, 0, P["GUT_R"], 4).rotate(V(0, 0, 0), V(0, 1, 0), 90).translate(V(xe - 2, yg, gz)))
        kasa.append(box(-ro, yg - P["GUT_R"], gz - 2, L + 2 * ro + 150, 2 * P["GUT_R"], 2))
        # gantungan talang ke rangka
        for x in xs:
            kasa.append(box(x - 10, min(yg, 0) if yg < 0 else W, gz - P["GUT_R"] - 4,
                            20, abs(yg - (0 if yg < 0 else W)) + P["GUT_R"], 4))
    add("Talang PVC (baru)", "new", "new", cq.Compound.makeCompound(gl))
    add("Kasa talang ~1 mm dan gantungan (baru)", "new", "filter", cq.Compound.makeCompound(kasa))
    A["gutter"] = (3000, -ro - 10, gz)

    xdp = L + ro + 80
    ys, yn = -ro - 10, W + ro + 10
    zc = P["ZC"]
    ttop = P["TANK_BASE"] + P["TANK_H"]
    xff = tx - P["TANK_R"] - 150
    xin = tx - P["TANK_R"] + 30
    dp = [
        pipe([(xdp, yn, gz - 40), (xdp, yn, zc), (xdp, ty, zc)], P["DP_R"]),
        pipe([(xdp, ys, gz - 40), (xdp, ys, zc), (xdp, ty, zc), (xin, ty, zc)], P["DP_R"]),
    ]
    add("Pipa turun dan pipa ke tandon (baru)", "new", "new", cq.Compound.makeCompound(dp))
    for y0 in (yn, ys):
        fl('rain', [(-100, y0, gz - 25), (xdp, y0, gz - 25), (xdp, y0, zc), (xdp, ty, zc), (xin + 200, ty, zc), (xin + 260, ty, zc - 600)])
    fl('ff', [(xff, ty, zc), (xff, ty, zc - P["FF_LEN"] + 50)])
    ff = [cyl(xff, ty, zc - P["FF_LEN"], P["FF_R"], P["FF_LEN"]),
          cyl(xff, ty, zc - P["FF_LEN"] - 60, P["FF_R"] + 10, 60),
          bar((xff, ty, zc - P["FF_LEN"] - 60), (xff, ty, zc - P["FF_LEN"] - 160), 10, True),
          box(xff - 30, ty - 40, zc - P["FF_LEN"] - 140, 60, 20, 20)]
    add("First flush ~9 L (baru)", "new", "new", cq.Compound.makeCompound(ff))
    A["ff"] = (xff, ty, zc - 500)
    ty2 = P["TANK2_Y"]
    R = P["TANK_R"]
    for k, yy in enumerate((ty, ty2)):
        add(f"Dudukan tandon {k + 1} (batako + semen, baru)", "new", "concrete",
            box(tx - R - 50, yy - R - 50, 0, 2 * R + 100, 2 * R + 100, P["TANK_BASE"]))
        tank = (cq.Workplane("XY", origin=(tx, yy, P["TANK_BASE"])).circle(R).extrude(P["TANK_H"])
                .faces(">Z").edges().fillet(160))
        add(f"Tandon {k + 1} Filtra 2.650 L (baru)", "new", "tank", tank)
        add(f"Tutup tandon {k + 1}", "new", "tank", cyl(tx, yy, ttop, 230, 45))
        add(f"Lubang angin berkasa tandon {k + 1} (baru)", "new", "new", cq.Compound.makeCompound([
            bar((tx + 300, yy + 300, ttop - 140), (tx + 300, yy + 300, ttop + 120), 20, True),
            cyl(tx + 300, yy + 300, ttop + 120, 45, 30)]))
    A["tank"] = (tx + 500, ty - 500, 1000)
    A["tank2"] = (tx + 500, ty2 - 500, 1000)
    A["vent"] = (tx + 300, ty + 300, ttop + 150)
    # sambungan bawah antar tandon: dua tandon jadi satu muka air
    yl1 = ty - math.sqrt(R ** 2 - 300 ** 2)
    yl2 = ty2 + math.sqrt(R ** 2 - 300 ** 2)
    zl = P["TANK_BASE"] + 160
    add("Pipa sambung antar tandon + stop kran (baru)", "new", "new", cq.Compound.makeCompound([
        pipe([(tx + 300, yl1 + 20, zl), (tx + 300, yl2 - 20, zl)], 25),
        box(tx + 270, (yl1 + yl2) / 2 - 30, zl + 20, 60, 60, 50)]))
    A["link"] = (tx + 300, (yl1 + yl2) / 2, zl + 60)
    fl('link', [(tx + 300, yl1 - 60, zl), (tx + 300, yl2 + 60, zl)])
    xo = tx + R + 200
    add("Pipa pelimpah (baru)", "new", "new",
        pipe([(tx + R - 20, ty, ttop - 130), (xo, ty, ttop - 130), (xo, ty, 120), (xo + 150, ty, 120)], 25))
    fl('over', [(tx + R - 40, ty, ttop - 130), (xo, ty, ttop - 130), (xo, ty, 120), (xo + 260, ty, 60)])
    SIM.update(tanks=[(tx, ty), (tx, ty2)], R=R - 12, base=P["TANK_BASE"] + 8, h_over=P["TANK_H"] - 130 - 8,
               ff_l=9, roof_m2=18, coef=0.8, use_lpd=64.4, roof=dict(x0=-ro, x1=L + ro, y0=-ro, y1=W + ro, he=HE, hr=HR))
    A["over"] = (xo, ty, 900)
    # kran keluar -> filter -> masuk greenhouse -> sisi bawah tong biru (air baku, AB mix dicampur di tong)
    yt = ty - 300
    xt = tx - math.sqrt(P["TANK_R"] ** 2 - 300 ** 2)
    tz = P["TAP_Z"]
    xf, yf = L + 260, yt
    zi = P["DRUM_IN_Z"]                 # lubang masuk samping bawah tong, di bawah kran tandon supaya gravitasi jalan
    xd = dx_ + P["DRUM_R"]              # dinding timur tong
    yd = dy_
    add("Kran keluar di atas dasar (baru)", "new", "new", cq.Compound.makeCompound([
        pipe([(xt + 20, yt, tz), (xf, yt, tz)], 20),
        box(xt - 120, yt - 30, tz + 20, 40, 60, 60),
        bar((xt - 100, yt, tz + 80), (xt - 100, yt - 120, tz + 80), 8, True)]))
    A["tap"] = (xt - 100, yt, tz + 60)
    add("Housing filter 120 sampai 200 mesh (baru)", "new", "filter", cq.Compound.makeCompound([
        cyl(xf, yf, tz - 320, 70, 300), cyl(xf, yf, tz - 20, 85, 60)]))
    A["filter"] = (xf, yf, tz - 170)
    add("Pipa ke tong biru (baru)", "new", "new",
        pipe([(xf, yf, tz), (xf, yd, tz), (xd + 140, yd, tz), (xd + 140, yd, zi), (xd - 6, yd, zi)], 20))
    add("Stop kran masuk tong (baru)", "new", "new", cq.Compound.makeCompound([
        box(xd + 40, yd - 30, zi - 30, 60, 60, 60),
        bar((xd + 70, yd, zi + 30), (xd + 70, yd + 120, zi + 30), 8, True)]))
    A["drumin"] = (xd + 70, yd, zi + 40)
    add("Kran sampel (baru)", "new", "new", bar((xf, yd, tz), (xf, yd, tz - 120), 10, True))
    fl('out', [(xt + 20, yt, tz), (xf, yt, tz), (xf, yd, tz), (xd + 140, yd, tz), (xd + 140, yd, zi), (xd - 60, yd, zi)])
    # meja cek pH dan TDS, di luar sisi timur
    TX, TY = L + 150, W + 550
    tb = [box(TX, TY, 720, 600, 450, 30)]
    for lx in (TX + 20, TX + 550):
        for ly in (TY + 20, TY + 400):
            tb.append(box(lx, ly, 0, 30, 30, 720))
    tb.append(box(TX + 20, TY + 20, 250, 560, 410, 15))
    add("Meja cek air (baru)", "new", "table", cq.Compound.makeCompound(tb))
    add("pH meter, TDS pen, gelas sampel (baru)", "new", "meter", cq.Compound.makeCompound([
        box(TX + 100, TY + 100, 750, 70, 35, 170), cyl(TX + 250, TY + 120, 750, 12, 160),
        cyl(TX + 430, TY + 150, 750, 40, 100), box(TX + 200, TY + 250, 750, 250, 120, 120)]))
    A["table"] = (TX + 300, TY + 225, 870)
    # tutup tong: perubahan yang diusulkan (aslinya terbuka)
    add("Tutup tong (usulan, aslinya terbuka)", "new", "new", cq.Compound.makeCompound([
        cyl(dx_, dy_, dtop, P["DRUM_R"] + 15, 20).cut(cyl(dx_ + 80, dy_ + 40, dtop - 10, 30, 50)).cut(cyl(dx_ - 220, dy_ + 120, dtop - 10, 16, 50))]))

    ground = box(-1500, -1500, -40, 10500, 6500, 40).cut(hole)
    add("Tanah", "site", "ground", ground)
    return parts


if __name__ == "__main__":
    import time
    t = time.time()
    build()
    print(len(parts), "parts", round(time.time() - t, 1), "s")
