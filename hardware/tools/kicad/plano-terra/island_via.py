"""Coloca uma via de costura DENTRO da ilha de cobre do pad problemático.

Diferente do stub+via, aqui a via e' procurada dentro do proprio poligono
preenchido da zona GND — garante que ela cai sobre cobre e amarra a ilha
isolada ao plano da outra face.
"""

import math
import sys

import pcbnew

MM = 1e6


def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / l2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def bbox_dist(px, py, l, t, r, b):
    return math.hypot(max(l - px, 0.0, px - r), max(t - py, 0.0, py - b))


def main(src, out, targets, via_d=0.6, drill=0.3, reach=9.0):
    b = pcbnew.LoadBoard(src)

    zones = [b.GetArea(i) for i in range(b.GetAreaCount())]
    fzone = [z for z in zones if b.GetLayerName(z.GetLayer()) == "F.Cu"]
    if not fzone:
        raise SystemExit("zona F.Cu nao encontrada")
    poly = fzone[0].GetFilledPolysList(pcbnew.F_Cu)
    print("poligono preenchido: %d contornos, area %.1f mm2" % (poly.OutlineCount(), poly.Area() / (MM * MM)))

    tracks = []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK":
            continue
        s, e = t.GetStart(), t.GetEnd()
        tracks.append((s.x / MM, s.y / MM, e.x / MM, e.y / MM, t.GetWidth() / MM))
    pads = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            pads.append((bb.GetLeft() / MM, bb.GetTop() / MM, bb.GetRight() / MM, bb.GetBottom() / MM,
                         fp.GetReference() + "." + p.GetNumber()))

    vr = via_d / 2.0
    net = b.FindNet("GND")
    added = 0

    for ref, pnum in targets:
        fp = b.FindFootprintByReference(ref)
        pad = [p for p in fp.Pads() if p.GetNumber() == pnum][0]
        px, py = pad.GetPosition().x / MM, pad.GetPosition().y / MM
        best = None
        d = 0.95
        while d <= reach and best is None:
            n = max(8, int(2 * math.pi * d / 0.35))
            for k in range(n):
                a = 2 * math.pi * k / n
                x, y = px + d * math.cos(a), py + d * math.sin(a)
                if not poly.Contains(pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))):
                    continue
                ok = True
                for (a1, b1, a2, b2, w) in tracks:
                    if seg_dist(x, y, a1, b1, a2, b2) < vr + w / 2 + 0.22:
                        ok = False
                        break
                if ok:
                    for (l, t, rr, bb_, pid) in pads:
                        if pid == "%s.%s" % (ref, pnum):
                            continue
                        if bbox_dist(x, y, l, t, rr, bb_) < vr + 0.22:
                            ok = False
                            break
                if ok:
                    best = (x, y)
                    break
            d += 0.30
        if best is None:
            print("  %s.%s (%.2f,%.2f) SEM PONTO LIVRE na ilha" % (ref, pnum, px, py))
            continue
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(int(round(best[0] * MM)), int(round(best[1] * MM))))
        v.SetWidth(int(round(via_d * MM)))
        v.SetDrill(int(round(drill * MM)))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(net)
        b.Add(v)
        # trilha curta do pad ate a via, garantindo a conexao mesmo que a via
        # caia numa ilha diferente
        tr = pcbnew.PCB_TRACK(b)
        tr.SetStart(pcbnew.VECTOR2I(int(round(px * MM)), int(round(py * MM))))
        tr.SetEnd(pcbnew.VECTOR2I(int(round(best[0] * MM)), int(round(best[1] * MM))))
        tr.SetWidth(int(round(0.25 * MM)))
        tr.SetLayer(pcbnew.F_Cu)
        tr.SetNet(net)
        b.Add(tr)
        print("  %s.%s -> via em (%.2f, %.2f) a %.2f mm + trilha" % (ref, pnum, best[0], best[1], math.hypot(best[0] - px, best[1] - py)))
        added += 1

    print("vias colocadas:", added)
    filler = pcbnew.ZONE_FILLER(b)
    filler.Fill(b.Zones())
    b.BuildListOfNets()
    b.Save(out)
    print("salvo:", out)


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    tg = [a.split(".") for a in sys.argv[3:]]
    main(src, out, tg)
