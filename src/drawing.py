import sys, time, pickle, os
sys.path.insert(0, os.path.dirname(__file__))
import cadquery as cq
import model
from model import P
from hlr import project

parts = model.build()
def comp(pred):
    return cq.Compound.makeCompound([s for n, g, ck, s in parts if pred(n, g, ck)])
is_res = lambda n: n.startswith("Bak lantai bagian tertanam") or n.startswith("Pompa celup")
G = {
    "exist": comp(lambda n, g, ck: g in ("frame", "existing", "reslid") and not is_res(n)),
    "new": comp(lambda n, g, ck: g == "new"),
    "res": comp(lambda n, g, ck: is_res(n)),
}
VIEWS = {"atas": ((0, 0, 1), (1, 0, 0)), "samping": ((0, -1, 0), (1, 0, 0)), "depan": ((1, 0, 0), (0, 1, 0))}
res = {}
for vn, (N, Vx) in VIEWS.items():
    for gn, sh in G.items():
        t = time.time()
        res[(vn, gn)] = project(sh, N, Vx)
        if gn == "res":
            res[(vn, "res_h")] = project(sh, N, Vx, hidden=True)
        print(vn, gn, len(res[(vn, gn)]), round(time.time() - t, 1), "s", flush=True)
pickle.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hlr_cache.pkl"), "wb"))
