"""Coloca uma via de costura no centro de cada regiao pequena de cobre GND.

Percorre os poligonos preenchidos das zonas GND, calcula a area de cada
contorno e, para os que sao pequenos (lascas isoladas), tenta colocar uma via
no centro — assim a lasca se amarra ao plano da outra face.
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


def shoelace(pts):
    a = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


def main(src, out, max_area=40.0, via_d=0.6, drill=0.3):
    b = pcbnew.LoadBoard(src)

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
            pads.append((bb.GetLeft() / MM, bb.GetTop() / MM, bb.GetRight() / MM, bb.GetBottom() / MM))
    vias = []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_VIA":
            continue
        pos = t.GetPosition()
        vias.append((pos.x / MM, pos.y / MM, t.GetWidth(pcbnew.F_Cu) / MM))

    net = b.FindNet("GND")
    vr = via_d / 2.0
    added = 0

    for i in range(b.GetAreaCount()):
        z = b.GetArea(i)
        if z.GetNetname() != "GND":
            continue
        layer = z.GetLayer()
        poly = z.GetFilledPolysList(layer)
        lay_name = b.GetLayerName(layer)
        for c in range(poly.OutlineCount()):
            chain = poly.Outline(c)
            pts = [(chain.CPoint(k).x / MM, chain.CPoint(k).y / MM) for k in range(chain.PointCount())]
            if len(pts) < 3:
                continue
            area = shoelace(pts)
            if area > max_area:
                continue
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            print("  lasca em %s: %.2f mm2, centro (%.2f, %.2f)" % (lay_name, area, cx, cy))
            ok = True
            for (a1, b1, a2, b2, w) in tracks:
                if seg_dist(cx, cy, a1, b1, a2, b2) < vr + w / 2 + 0.25:
                    ok = False
                    break
            if ok:
                for (l, t, rr, bb_) in pads:
                    if bbox_dist(cx, cy, l, t, rr, bb_) < vr + 0.25:
                        ok = False
                        break
            if ok:
                for (vx, vy, vw) in vias:
                    if math.hypot(cx - vx, cy - vy) < vr + vw / 2 + 0.3:
                        ok = False
                        break
            if not ok:
                print("      centro ocupado, tentando deslocamentos...")
                found = None
                for d in (0.5, 0.8, 1.1, 1.5):
                    for k in range(12):
                        a = 2 * math.pi * k / 12
                        x, y = cx + d * math.cos(a), cy + d * math.sin(a)
                        if not poly.Contains(pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))):
                            continue
                        good = all(seg_dist(x, y, a1, b1, a2, b2) >= vr + w / 2 + 0.25
                                   for (a1, b1, a2, b2, w) in tracks)
                        if good:
                            found = (x, y)
                            break
                    if found:
                        break
                if not found:
                    print("      SEM PONTO LIVRE")
                    continue
                cx, cy = found
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pcbnew.VECTOR2I(int(round(cx * MM)), int(round(cy * MM))))
            v.SetWidth(int(round(via_d * MM)))
            v.SetDrill(int(round(drill * MM)))
            v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            v.SetNet(net)
            b.Add(v)
            added += 1

    print("vias em lascas:", added)
    filler = pcbnew.ZONE_FILLER(b)
    filler.Fill(b.Zones())
    b.BuildListOfNets()
    b.Save(out)
    print("salvo:", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
