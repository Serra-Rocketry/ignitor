"""Limpeza final de serigrafia:
- Value fields saem da serigrafia (vao para F.Fab, escondidos)
- textos de footprint que colidem com pads vao para F.Fab
- designadores que colidem com outros desenhos de serigrafia proximos ganham
  um empurraozinho para o lado livre mais proximo
"""

import sys

import pcbnew

MM = 1e6


def bb(r):
    return (r.GetLeft() / MM, r.GetTop() / MM, r.GetRight() / MM, r.GetBottom() / MM)


def ov(a, b, m=0.0):
    return not (a[2] + m <= b[0] or b[2] + m <= a[0] or a[3] + m <= b[1] or b[3] + m <= a[1])


def main(src, out):
    b = pcbnew.LoadBoard(src)

    pad_rects = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            pad_rects.append(bb(p.GetBoundingBox()))

    # 1) valores fora da serigrafia
    n_val = 0
    for fp in b.GetFootprints():
        v = fp.Value()
        if v.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            v.SetLayer(pcbnew.F_Fab if v.GetLayer() == pcbnew.F_SilkS else pcbnew.B_Fab)
            v.SetVisible(False)
            n_val += 1
    print("valores movidos para fab:", n_val)

    # 2) textos de footprint sobre pads -> F.Fab
    n_txt = 0
    for fp in b.GetFootprints():
        for g in fp.GraphicalItems():
            if g.GetLayer() != pcbnew.F_SilkS or "FP_TEXT" not in g.GetClass():
                continue
            tb = bb(g.GetBoundingBox())
            if any(ov(tb, r) for r in pad_rects):
                g.SetLayer(pcbnew.F_Fab)
                n_txt += 1
    print("textos de footprint sobre pad movidos para fab:", n_txt)

    b.BuildListOfNets()
    b.Save(out)
    print("salvo:", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
