"""Coloca os footprints do ignitor e verifica courtyards.

Uso:
    python place.py <board.kicad_pcb> check
    python place.py <board.kicad_pcb> apply <placement.json> [out.kicad_pcb]

O placement.json e um dict {ref: [x, y, rot]} em milimetros/graus.
"""

import json
import sys

import pcbnew

MM = 1e6


def courtyards(board):
    """ref -> SHAPE_POLY_SET (board coords) e a bbox."""
    out = {}
    for fp in board.GetFootprints():
        poly = fp.GetCourtyard(pcbnew.F_CrtYd)
        if poly.OutlineCount() == 0:
            out[fp.GetReference()] = None
        else:
            out[fp.GetReference()] = poly
    return out


def overlap_area(a, b):
    """Area da interseccao de dois SHAPE_POLY_SET (mm^2)."""
    tmp = pcbnew.SHAPE_POLY_SET()
    try:
        tmp.BooleanIntersection(a, b)
    except Exception:
        return 0.0
    return tmp.Area() / (MM * MM)


def board_rect(board):
    box = board.GetBoardEdgesBoundingBox()
    return (
        box.GetLeft() / MM,
        box.GetTop() / MM,
        box.GetRight() / MM,
        box.GetBottom() / MM,
    )


def report(board, margin=1.0):
    cys = courtyards(board)
    refs = sorted(cys.keys())
    x0, y0, x1, y1 = board_rect(board)

    problems = 0

    print("=== sobreposicoes de courtyard ===")
    found = False
    for i, ra in enumerate(refs):
        for rb in refs[i + 1 :]:
            pa, pb = cys[ra], cys[rb]
            if pa is None or pb is None:
                continue
            # atalho: bboxes que nao se tocam nao podem se sobrepor
            ba, bb_ = pa.BBox(), pb.BBox()
            if (ba.GetRight() < bb_.GetLeft() or bb_.GetRight() < ba.GetLeft()
                    or ba.GetBottom() < bb_.GetTop() or bb_.GetBottom() < ba.GetTop()):
                continue
            area = overlap_area(pa, pb)
            if area > 0.01:
                found = True
                problems += 1
                print("  %-5s <-> %-5s  %.3f mm2" % (ra, rb, area))
    if not found:
        print("  (nenhuma)")

    print()
    print("=== distancia a borda (courtyard) ===")
    bad = False
    for r in refs:
        p = cys[r]
        if p is None:
            print("  %-5s SEM COURTYARD" % r)
            bad = True
            continue
        b = p.BBox()
        dl = b.GetLeft() / MM - x0
        dr = x1 - b.GetRight() / MM
        dt = b.GetTop() / MM - y0
        db = y1 - b.GetBottom() / MM
        m = min(dl, dr, dt, db)
        flag = ""
        if m < 0:
            flag = "  <<< FORA DA PLACA"
            bad = True
        elif m < margin:
            flag = "  <<< perto"
        if flag:
            print("  %-5s esq=%.2f dir=%.2f topo=%.2f base=%.2f%s" % (r, dl, dr, dt, db, flag))
    if not bad:
        print("  (todas com >= %.1f mm)" % margin)

    print()
    print("=== resumo ===")
    print("  board: %.2f x %.2f mm" % (x1 - x0, y1 - y0))
    print("  footprints: %d" % len(refs))
    print("  sobreposicoes: %d" % problems)
    return problems


def apply_placement(board, table, out):
    for ref, (x, y, rot) in table.items():
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            print("  AVISO: %s nao existe" % ref)
            continue
        fp.SetPosition(pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM))))
        fp.SetOrientationDegrees(rot)
    board.BuildListOfNets()
    board.Save(out)
    print("salvo:", out)


def delete_refs(board, refs, out):
    for ref in refs:
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            print("  AVISO: %s nao existe" % ref)
            continue
        board.Remove(fp)
        print("  removido:", ref)
    board.BuildListOfNets()
    board.Save(out)


if __name__ == "__main__":
    mode = sys.argv[2]
    board = pcbnew.LoadBoard(sys.argv[1])

    if mode == "check":
        report(board)
    elif mode == "apply":
        table = json.load(open(sys.argv[3], encoding="utf-8"))
        out = sys.argv[4] if len(sys.argv) > 4 else sys.argv[1]
        apply_placement(board, table, out)
        report(pcbnew.LoadBoard(out))
    elif mode == "delete":
        refs = json.load(open(sys.argv[3], encoding="utf-8"))
        out = sys.argv[4] if len(sys.argv) > 4 else sys.argv[1]
        delete_refs(board, refs, out)
        report(pcbnew.LoadBoard(out))
    else:
        raise SystemExit("modo invalido: " + mode)
