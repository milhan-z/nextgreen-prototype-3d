from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepLib import BRepLib
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
import cadquery as cq

def project(shape, N, Vx, hidden=False):
    hlr = HLRBRep_Algo(); hlr.Add(shape.wrapped)
    hlr.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*N), gp_Dir(*Vx))))
    hlr.Update(); hlr.Hide()
    h = HLRBRep_HLRToShape(hlr)
    comps = [h.VCompound(), h.Rg1LineVCompound(), h.OutLineVCompound()]
    if hidden:
        comps = [h.HCompound(), h.OutLineHCompound()]
    out = []
    for c in comps:
        if c.IsNull():
            continue
        BRepLib.BuildCurves3d_s(c, 1e-3)
        for e in cq.Shape.cast(c).Edges():
            cu = e._geomAdaptor()
            pts = GCPnts_QuasiUniformDeflection(cu, 0.5, cu.FirstParameter(), cu.LastParameter())
            if pts.IsDone():
                out.append([(pts.Value(i + 1).X(), pts.Value(i + 1).Y()) for i in range(pts.NbPoints())])
    return out
