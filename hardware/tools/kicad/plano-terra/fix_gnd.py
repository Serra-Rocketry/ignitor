"""Liga pads GND isolados a um ponto com plano, com um stub curto + via."""

import math
import sys

import pcbnew

MM = 1e6
DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1), (0.707, 0.707), (0.707, -0.707), (-0.707, 0.707), (-0.707, -0.707)]


def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / l2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def seg_seg_dist(a, b, c, d):
    def ccw(p, q, r):
        return (r[1] - p[1]) * (q[0] - p[0]) - (q[1] - p[1]) * (r[0] - p[0])
    d1, d2 = ccw(c, d, a), ccw(c, d, b)
    d3, d4 = ccw(a, b, c), ccw(a, b, d)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    return min(seg_dist(a[0], a[1], c[0], c[1], d[0], d[1]),
               seg_dist(b[0], b[1], c[0], c[1], d[0], d[1]),
               seg_dist(c[0], c[1], a[0], a[1], b[0], b[1]),
               seg_dist(d[0], d[1], a[0], a[1], b[0], b[1]))


def main(src, out, targets, track_w=0.25, via_d=0.6, drill=0.3):
    b = pcbnew.LoadBoard(src)
    bore = b.GetBoardEdgesBoundingBox()
    bx0, by0 = bore.GetLeft() / MM, bore.GetTop() / MM
    bx1, by1 = bore.GetRight() / MM, bore.GetBottom() / MM

    obstacles = []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK":
            continue
        s, e = t.GetStart(), t.GetEnd()
        obstacles.append(((s.x / MM, s.y / MM), (e.x / MM, e.y / MM), t.GetWidth() / MM, t.GetLayer()))
    pads = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            pads.append((bb.GetLeft() / MM, bb.GetTop() / MM, bb.GetRight() / MM, bb.GetBottom() / MM,
                         p.GetNetname(), fp.GetReference() + "." + p.GetNumber()))

    def clear_point(x, y, r):
        if x < bx0 + 1.0 or x > bx1 - 1.0 or y < by0 + 1.0 or y > by1 - 1.0:
            return False
        for (a, c, w, lay) in obstacles:
            if seg_dist(x, y, a[0], a[1], c[0], c[1]) < r + w / 2 + 0.22:
                return False
        for (l, t, rr, bb_, n, pid) in pads:
            dx = max(l - x, 0, x - rr)
            dy = max(t - y, 0, y - bb_)
            if math.hypot(dx, dy) < r + 0.22:
                return False
        return True

    def clear_seg(a, c, w, layer):
        for (p, q, ww, lay) in obstacles:
            if lay != layer:
                continue
            if seg_seg_dist(a, c, p, q) < w / 2 + ww / 2 + 0.22:
                return False
        for (l, t, rr, bb_, n, pid) in pads:
            # caixa do pad como 4 segmentos
            corners = [(l, t), (rr, t), (rr, bb_), (l, bb_)]
            for k in range(4):
                if seg_seg_dist(a, c, corners[k], corners[(k + 1) % 4]) < w / 2 + 0.22:
                    return False
        return True

    net = b.FindNet("GND")
    added = 0
    for ref, padnum in targets:
        fp = b.FindFootprintByReference(ref)
        pad = [p for p in fp.Pads() if p.GetNumber() == padnum][0]
        pos = pad.GetPosition()
        px, py = pos.x / MM, pos.y / MM
        done = False
        for L in (1.0, 1.3, 1.6, 2.0, 2.5, 3.0, 3.6, 4.4, 5.5, 7.0, 9.0):
            for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
                for dx, dy in DIRS:
                    ex, ey = px + dx * L, py + dy * L
                    if not clear_point(ex, ey, via_d / 2):
                        continue
                    if not clear_seg((px, py), (ex, ey), track_w, layer):
                        continue
                    t = pcbnew.PCB_TRACK(b)
                    t.SetStart(pcbnew.VECTOR2I(int(round(px * MM)), int(round(py * MM))))
                    t.SetEnd(pcbnew.VECTOR2I(int(round(ex * MM)), int(round(ey * MM))))
                    t.SetWidth(int(round(track_w * MM)))
                    t.SetLayer(layer)
                    t.SetNet(net)
                    b.Add(t)
                    v = pcbnew.PCB_VIA(b)
                    v.SetPosition(pcbnew.VECTOR2I(int(round(ex * MM)), int(round(ey * MM))))
                    v.SetWidth(int(round(via_d * MM)))
                    v.SetDrill(int(round(drill * MM)))
                    v.SetViaType(pcbnew.VIATYPE_THROUGH)
                    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                    v.SetNet(net)
                    b.Add(v)
                    print("  %s.%s (%.2f,%.2f) -> stub %.1fmm em %s dir(%+0.0f,%+0.0f) + via" % (
                        ref, padnum, px, py, L, b.GetLayerName(layer), dx, dy))
                    added += 1
                    done = True
                    break
                if done:
                    break
            if done:
                break
        if not done:
            print("  %s.%s (%.2f,%.2f) SEM SOLUCAO" % (ref, padnum, px, py))

    print("stubs adicionados:", added)
    filler = pcbnew.ZONE_FILLER(b)
    filler.Fill(b.Zones())
    b.BuildListOfNets()
    b.Save(out)
    print("salvo:", out)


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    tg = []
    for a in sys.argv[3:]:
        r, p = a.split(".")
        tg.append((r, p))
    main(src, out, tg)
