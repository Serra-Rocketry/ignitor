"""Gera vias de costura GND nas areas livres da placa.

Testa uma grade de candidatos e aceita cada ponto cujo circulo de via
(via + clearance) nao colida com trilhas, pads, furos nem com a borda.
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
    dx = max(l - px, 0.0, px - r)
    dy = max(t - py, 0.0, py - b)
    return math.hypot(dx, dy)


def main(src, out, pitch=4.0, via_d=0.8, drill=0.4, clearance=0.3, edge=1.2, region=None):
    b = pcbnew.LoadBoard(src)
    bore = b.GetBoardEdgesBoundingBox()
    x0, y0 = bore.GetLeft() / MM + edge, bore.GetTop() / MM + edge
    x1, y1 = bore.GetRight() / MM - edge, bore.GetBottom() / MM - edge

    if region:
        x0, y0, x1, y1 = region

    vr = via_d / 2.0

    tracks = []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK":
            continue
        s, e = t.GetStart(), t.GetEnd()
        tracks.append((s.x / MM, s.y / MM, e.x / MM, e.y / MM, t.GetWidth() / MM,
                       t.GetNetname(), t.GetLayer()))

    pads = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            pads.append((bb.GetLeft() / MM, bb.GetTop() / MM, bb.GetRight() / MM, bb.GetBottom() / MM,
                         p.GetNetname(), fp.GetReference() + "." + p.GetNumber()))
    holes = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetDrillSize().x > 0:
                pos = p.GetPosition()
                holes.append((pos.x / MM, pos.y / MM, p.GetDrillSize().x / MM / 2.0 + 0.35,
                              fp.GetReference()))
    # as vias ja existentes tambem sao furos: sem isso, grades finas geram
    # avisos de hole_to_hole e holes_co_located
    for t in b.GetTracks():
        if t.GetClass() != "PCB_VIA":
            continue
        pos = t.GetPosition()
        holes.append((pos.x / MM, pos.y / MM, t.GetDrillValue() / MM / 2.0 + 0.35, "via"))

    placed = 0
    tried = 0
    y = y0
    row = 0
    while y <= y1:
        x = x0 + (pitch / 2 if row % 2 else 0)
        while x <= x1:
            tried += 1
            ok = True
            for tx1, ty1, tx2, ty2, tw, tn, tl in tracks:
                if seg_dist(x, y, tx1, ty1, tx2, ty2) < vr + tw / 2 + clearance:
                    ok = False
                    break
            if ok:
                for pl, pt, pr, pb, pn, pid in pads:
                    if bbox_dist(x, y, pl, pt, pr, pb) < vr + clearance:
                        ok = False
                        break
            if ok:
                for hx, hy, hr, href in holes:
                    if math.hypot(x - hx, y - hy) < vr + hr + 0.2:
                        ok = False
                        break
            if ok:
                v = pcbnew.PCB_VIA(b)
                v.SetPosition(pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM))))
                v.SetWidth(int(round(via_d * MM)))
                v.SetDrill(int(round(drill * MM)))
                v.SetViaType(pcbnew.VIATYPE_THROUGH)
                v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                net = b.FindNet("GND")
                v.SetNet(net)
                b.Add(v)
                placed += 1
            x += pitch
        y += pitch
        row += 1

    print("candidatos: %d   vias de costura colocadas: %d" % (tried, placed))
    filler = pcbnew.ZONE_FILLER(b)
    filler.Fill(b.Zones())
    b.BuildListOfNets()
    b.Save(out)
    print("salvo:", out)


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    pitch = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
    reg = None
    if len(sys.argv) > 4:
        reg = tuple(float(v) for v in sys.argv[4].split(','))
    main(src, out, pitch=pitch, region=reg)
