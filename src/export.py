import sys, json, numpy as np, trimesh, cadquery as cq
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import model
from model import C, P
parts = model.build()
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "")

asm = cq.Assembly(name="greenhouse_air_hujan")
for i, (n, g, ck, s) in enumerate(parts):
    if g == "site":
        continue
    asm.add(s, name=f"{i:02d}_{n}".replace(" ", "_"), color=cq.Color(*C[ck]))
asm.save(OUT + "dist/prototype.step")
allc = cq.Compound.makeCompound([s for n, g, ck, s in parts if g != "site"])
cq.exporters.export(allc, OUT + "dist/prototype.stl", tolerance=2, angularTolerance=0.3)

scene = trimesh.Scene()
meta = []
for i, (n, g, ck, s) in enumerate(parts):
    tol = 3 if g in ("plant",) else 1.5
    v, f = s.tessellate(tol, 0.3)
    v = np.array([(p.x, p.z, -p.y) for p in v]) / 1000.0
    m = trimesh.Trimesh(v, np.array(f), process=False)
    col = (np.array(list(C[ck]) + [1.0]) * 255).astype(np.uint8)
    alpha = {"roof": 0.30, "net": 0.22, "filter": 0.85}.get(ck, 1.0)
    mat = trimesh.visual.material.PBRMaterial(name=ck, baseColorFactor=[*(c ** 2.2 for c in C[ck]), alpha],
                                              metallicFactor=0.6 if ck == "frame" else 0.0,
                                              roughnessFactor=0.45 if ck == "frame" else 0.7,
                                              alphaMode="BLEND" if alpha < 1 else "OPAQUE", doubleSided=True)
    m.visual = trimesh.visual.TextureVisuals(material=mat)
    nm = f"{g}|{ck}|{i:02d} {n}"
    scene.add_geometry(m, node_name=nm, geom_name=nm)
    meta.append(dict(name=n, group=g, color=ck))
scene.export(OUT + "dist/prototype.glb", include_normals=True)
json.dump(dict(anchors=model.A, flow=model.FLOW, flowk=model.FLOWK, sim=model.SIM), open(OUT + "web/geom.json", "w"))
json.dump(dict(params=P, parts=meta), open(OUT + "src/parts.json", "w"), indent=1, ensure_ascii=False)
print("ok")
