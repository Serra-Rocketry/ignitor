"""Reposiciona os designadores (Reference) na serigrafia para nao colidir.

Para cada footprint, testa posicoes candidatas ao redor do corpo e escolhe a
primeira livre de: pads, serigrafia de outros footprints, borda da placa e
outros designadores ja posicionados. Se nenhuma servir, esconde o texto.
"""

import math
import sys

import pcbnew

MM = 1e6

CANDS = [
    ("abaixo", 0.0, 1.0),
    ("acima", 0.0, -1.0),
    ("direita", 1.0, 0.0),
    ("esquerda", -1.0, 0.0),
    ("sudeste", 0.7, 0.7),
    ("sudoeste", -0.7, 0.7),
    ("nordeste", 0.7, -0.7),
    ("noroeste", -0.7, -0.7),
]


def rects_overlap(a, b, m=0.15):
    return not (a[2] + m <= b[0] or b[2] + m <= a[0] or a[3] + m <= b[1] or b[3] + m <= a[1])


def bb(r):
    return (r.GetLeft() / MM, r.GetTop() / MM, r.GetRight() / MM, r.GetBottom() / MM)


def main(src, out, text_h=1.0, text_w=0.15):
    b = pcbnew.LoadBoard(src)
    bo = bb(b.GetBoardEdgesBoundingBox())
    inset = 0.3

    # obstaculos: pads (aberturas de mascara) e serigrafia dos footprints
    pad_rects = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            pad_rects.append(bb(p.GetBoundingBox()))

    silk_rects = []
    for fp in b.GetFootprints():
        for g in fp.GraphicalItems():
            if g.GetLayer() != pcbnew.F_SilkS:
                continue
            if g.GetClass() in ("PCB_TEXT", "FP_TEXT"):
                continue
            try:
                silk_rects.append(bb(g.GetBoundingBox()))
            except Exception:
                pass

    placed = []
    hidden = []
    hidden_n = 0
    moved = 0

    fps = list(b.GetFootprints())
    fps.sort(key=lambda f: -f.GetBoundingBox().GetWidth())

    for fp in fps:
        t = fp.Reference()
        if t.GetLayer() != pcbnew.F_SilkS:
            continue
        t.SetTextSize(pcbnew.VECTOR2I(int(text_h * MM), int(text_h * MM)))
        t.SetTextThickness(int(text_w * MM))
        try:
            t.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))
        except Exception:
            pass
        t.SetKeepUpright(False)

        fb = bb(fp.GetBoundingBox())
        best = None
        orig = (t.GetPosition().x / MM, t.GetPosition().y / MM)

        for name, dx, dy in CANDS:
            for dist in (0.8, 1.4, 2.0, 2.8, 3.8):
                cx = (fb[0] + fb[2]) / 2 + dx * (fb[2] - fb[0]) / 2 + dx * dist
                cy = (fb[1] + fb[3]) / 2 + dy * (fb[3] - fb[1]) / 2 + dy * dist
                t.SetPosition(pcbnew.VECTOR2I(int(cx * MM), int(cy * MM)))
                tb = bb(t.GetBoundingBox())
                if (tb[0] < bo[0] + inset or tb[1] < bo[1] + inset
                        or tb[2] > bo[2] - inset or tb[3] > bo[3] - inset):
                    continue
                bad = False
                for r in pad_rects:
                    if rects_overlap(tb, r):
                        bad = True
                        break
                if not bad:
                    for r in silk_rects:
                        if rects_overlap(tb, r, 0.1):
                            bad = True
                            break
                if not bad:
                    for r in placed:
                        if rects_overlap(tb, r, 0.2):
                            bad = True
                            break
                if not bad:
                    best = (name, cx, cy, tb)
                    break
            if best:
                break

        if best:
            name, cx, cy, tb = best
            t.SetPosition(pcbnew.VECTOR2I(int(cx * MM), int(cy * MM)))
            placed.append(tb)
            if abs(cx - orig[0]) > 0.05 or abs(cy - orig[1]) > 0.05:
                moved += 1
        else:
            t.SetVisible(False)
            hidden.append((fp, t))
            continue

    # segunda passada: texto menor e margem apertada para os que sobraram
    for fp, t in hidden:
        t.SetVisible(True)
        t.SetTextSize(pcbnew.VECTOR2I(int(0.85 * MM), int(0.85 * MM)))
        t.SetTextThickness(int(0.13 * MM))
        fb = bb(fp.GetBoundingBox())
        best = None
        for name, dx, dy in CANDS:
            for dist in (0.7, 1.1, 1.6, 2.2, 3.0, 4.0, 5.2):
                cx = (fb[0] + fb[2]) / 2 + dx * (fb[2] - fb[0]) / 2 + dx * dist
                cy = (fb[1] + fb[3]) / 2 + dy * (fb[3] - fb[1]) / 2 + dy * dist
                t.SetPosition(pcbnew.VECTOR2I(int(cx * MM), int(cy * MM)))
                tb = bb(t.GetBoundingBox())
                if (tb[0] < bo[0] + 0.1 or tb[1] < bo[1] + 0.1
                        or tb[2] > bo[2] - 0.1 or tb[3] > bo[3] - 0.1):
                    continue
                bad = False
                for r in pad_rects:
                    if rects_overlap(tb, r, 0.05):
                        bad = True
                        break
                if not bad:
                    for r in placed:
                        if rects_overlap(tb, r, 0.05):
                            bad = True
                            break
                if not bad:
                    best = (cx, cy, tb)
                    break
            if best:
                break
        if best:
            cx, cy, tb = best
            t.SetPosition(pcbnew.VECTOR2I(int(cx * MM), int(cy * MM)))
            placed.append(tb)
            moved += 1
        else:
            t.SetVisible(False)
            hidden_n += 1

    print("designadores: %d posicionados (%d movidos), %d escondidos" % (len(placed), moved, hidden_n))

    # valores nunca na serigrafia
    for fp in b.GetFootprints():
        v = fp.Value()
        if v.GetLayer() == pcbnew.F_SilkS:
            v.SetLayer(pcbnew.F_Fab)
            v.SetVisible(False)

    # textos soltos de footprint na serigrafia (ex: marcacao "K" do catodo)
    # que colidem com pads viram F.Fab
    for fp in b.GetFootprints():
        for g in fp.GraphicalItems():
            if g.GetLayer() != pcbnew.F_SilkS:
                continue
            if "FP_TEXT" not in g.GetClass():
                continue
            try:
                tb = bb(g.GetBoundingBox())
            except Exception:
                continue
            for r in pad_rects:
                if rects_overlap(tb, r, 0.05):
                    g.SetLayer(pcbnew.F_Fab)
                    print("  texto de silks (%s) movido para F.Fab: colide com pad" % fp.GetReference())
                    break

    # textos soltos da placa na serigrafia: reposiciona se colidirem com pads
    n_bt = 0
    for g in b.GetDrawings():
        if "PCB_TEXT" not in g.GetClass():
            continue
        lay = g.GetLayer()
        if lay not in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            continue
        try:
            tb = bb(g.GetBoundingBox())
        except Exception:
            continue
        clash = any(rects_overlap(tb, r, 0.05) for r in pad_rects)
        if not clash:
            continue
        pos = g.GetPosition()
        w = tb[2] - tb[0]
        h = tb[3] - tb[1]
        done = False
        for cy in (y for y in [bo[1] + 4, bo[3] - 4, (bo[1] + bo[3]) / 2]):
            for cx in (bo[0] + 6, bo[2] - w - 6, (bo[0] + bo[2]) / 2):
                nt = (cx, cy, cx + w, cy + h)
                if (nt[0] < bo[0] + 0.5 or nt[2] > bo[2] - 0.5
                        or nt[1] < bo[1] + 0.5 or nt[3] > bo[3] - 0.5):
                    continue
                if any(rects_overlap(nt, r, 0.05) for r in pad_rects):
                    continue
                if any(rects_overlap(nt, r, 0.05) for r in placed):
                    continue
                g.SetPosition(pcbnew.VECTOR2I(int((cx + w / 2) * MM), int((cy + h / 2) * MM)))
                n_bt += 1
                done = True
                break
            if done:
                break
        if not done:
            g.SetLayer(pcbnew.F_Fab if lay == pcbnew.F_SilkS else pcbnew.B_Fab)
            print("  texto de placa movido para fab: sem espaco livre")
    if n_bt:
        print("  textos de placa reposicionados:", n_bt)

    b.BuildListOfNets()
    b.Save(out)
    print("salvo:", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
