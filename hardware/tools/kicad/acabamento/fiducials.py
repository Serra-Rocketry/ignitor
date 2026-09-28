"""Coloca 3 fiduciais JLCPCB (1 mm cobre / 2 mm mascara) em posicoes
encontradas automaticamente: procura pontos onde um circulo de 2 mm
esteja livre de trilhas, pads, vias e courtyards.
"""

import math
import os
import sys

import pcbnew

MM = 1e6
KFP = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"
CLEAR = 1.35          # raio livre necessario
MARGIN = 1.5         # distancia minima da borda
SEP = 30.0           # separacao minima entre fiduciais


def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / l2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def bbox_dist(px, py, l, t, r, b):
    return math.hypot(max(l - px, 0.0, px - r), max(t - py, 0.0, py - b))


def main(src, out, n=3):
    b = pcbnew.LoadBoard(src)
    for i in range(1, n + 1):
        old = b.FindFootprintByReference("FID%d" % i)
        if old is not None:
            b.Remove(old)

    bore = b.GetBoardEdgesBoundingBox()
    x0 = bore.GetLeft() / MM + MARGIN
    y0 = bore.GetTop() / MM + MARGIN
    x1 = bore.GetRight() / MM - MARGIN
    y1 = bore.GetBottom() / MM - MARGIN

    tracks = []
    for t in b.GetTracks():
        cls = t.GetClass()
        if cls == "PCB_VIA":
            p = t.GetPosition()
            w = t.GetWidth(pcbnew.F_Cu)
            tracks.append((p.x / MM, p.y / MM, p.x / MM, p.y / MM, w / MM))
        elif cls == "PCB_TRACK":
            s, e = t.GetStart(), t.GetEnd()
            tracks.append((s.x / MM, s.y / MM, e.x / MM, e.y / MM, t.GetWidth() / MM))
    pads = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            pads.append((bb.GetLeft() / MM, bb.GetTop() / MM, bb.GetRight() / MM, bb.GetBottom() / MM))
    holes = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetDrillSize().x > 0:
                pos = p.GetPosition()
                holes.append((pos.x / MM, pos.y / MM, p.GetDrillSize().x / MM / 2.0 + 1.0))

    def free(x, y):
        for mhx, mhy in ((124.0, 69.0), (201.0, 69.0), (124.0, 131.0), (201.0, 131.0)):
            if abs(x - mhx) < 3.5 + CLEAR and abs(y - mhy) < 3.5 + CLEAR:
                return False
        for (a1, b1, a2, b2, w) in tracks:
            if seg_dist(x, y, a1, b1, a2, b2) < CLEAR + w / 2:
                return False
        for (l, t, r, bb_) in pads:
            if bbox_dist(x, y, l, t, r, bb_) < CLEAR:
                return False
        for (hx, hy, hr) in holes:
            if math.hypot(x - hx, y - hy) < CLEAR + hr:
                return False
        return True

    cand = []
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            if free(x, y):
                cand.append((x, y))
            x += 0.5
        y += 0.5
    print("candidatos livres:", len(cand))
    if len(cand) < n:
        raise SystemExit("poucos candidatos livres")

    # espalha: pega os cantos extremos e depois o mais distante
    xs = [c[0] for c in cand]
    ys = [c[1] for c in cand]
    picked = []
    for target in ((min(xs), min(ys)), (max(xs), max(ys)), (min(xs), max(ys))):
        if len(picked) >= n:
            break
        best = min(cand, key=lambda c: (c[0] - target[0]) ** 2 + (c[1] - target[1]) ** 2)
        if all(math.hypot(best[0] - p[0], best[1] - p[1]) >= SEP for p in picked):
            picked.append(best)
    for c in cand:
        if len(picked) >= n:
            break
        if all(math.hypot(c[0] - p[0], c[1] - p[1]) >= SEP for p in picked):
            picked.append(c)

    for i, (x, y) in enumerate(picked[:n], start=1):
        ref = "FID%d" % i
        fp = pcbnew.FootprintLoad(os.path.join(KFP, "Fiducial.pretty"), "Fiducial_1mm_Mask2mm")
        fp.SetReference(ref)
        fp.SetPosition(pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM))))
        b.Add(fp)
        print("  %s em (%.1f, %.1f)" % (ref, x, y))


    filler = pcbnew.ZONE_FILLER(b)
    filler.Fill(b.Zones())
    b.BuildListOfNets()
    b.Save(out)
    print("salvo:", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
