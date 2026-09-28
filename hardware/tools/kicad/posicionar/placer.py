"""Posicionador automatico para o PCB do ignitor.

- Fixa os itens mecanicos (furos M3), o MCU, o modulo LoRa e os conectores de borda.
- Otimiza os passivos/semicondutores restantes por recozimento simulado.
- Custo = sobreposicao de courtyard + fora da placa + comprimento de trilha (HPWL).

Uso:
    python placer.py <board.kicad_pcb> <plan.json> <out.kicad_pcb> [seed]
"""

import json
import math
import random
import sys

import pcbnew

MM = 1e6
ROTS = (0, 90, 180, 270)


def ref_of(fp):
    return fp.GetReference()


def rel_bbox_at(fp, rot):
    """BBox do courtyard em coords locais (independente de posicao), para uma rotacao."""
    old_rot = fp.GetOrientationDegrees()
    old_pos = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(0, 0))
    fp.SetOrientationDegrees(rot)
    cy = fp.GetCourtyard(pcbnew.F_CrtYd)
    if cy.OutlineCount() == 0:
        res = None
    else:
        bb = cy.BBox()
        res = (bb.GetLeft() / MM, bb.GetTop() / MM, bb.GetRight() / MM, bb.GetBottom() / MM)
    fp.SetOrientationDegrees(old_rot)
    fp.SetPosition(old_pos)
    return res


def pad_offsets_at(fp, rot):
    """[(net, dx, dy)] dos pads, em coords locais para uma rotacao."""
    old_rot = fp.GetOrientationDegrees()
    old_pos = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(0, 0))
    fp.SetOrientationDegrees(rot)
    out = []
    for p in fp.Pads():
        n = p.GetNetname()
        if not n:
            continue
        pos = p.GetPosition()
        out.append((n, pos.x, pos.y))
    fp.SetOrientationDegrees(old_rot)
    fp.SetPosition(old_pos)
    return out


class Item:
    def __init__(self, fp, geom, pads, fixed_rot=None):
        self.ref = fp.GetReference()
        self.fp = fp
        self.geom = geom                 # rot -> (l,t,r,b) local
        self.pads = pads                 # rot -> [(net, dx, dy)]
        self.fixed_rot = fixed_rot
        self.rots = [fixed_rot] if fixed_rot is not None else [0, 90, 180, 270]
        self.x = 0.0
        self.y = 0.0
        self.rot = 0

    def bbox(self):
        l, t, r, b = self.geom[self.rot]
        return (self.x + l, self.y + t, self.x + r, self.y + b)

    def pad_positions(self):
        return [(n, self.x + dx, self.y + dy) for n, dx, dy in self.pads[self.rot]]

    def area(self):
        l, t, r, b = self.geom[self.rot]
        return (r - l) * (b - t)


def overlap(a, b):
    dx = min(a[2], b[2]) - max(a[0], b[0])
    dy = min(a[3], b[3]) - max(a[1], b[1])
    if dx <= 0 or dy <= 0:
        return 0.0
    return dx * dy


def outside(bb, rect):
    dx = max(0.0, rect[0] - bb[0]) + max(0.0, bb[2] - rect[2])
    dy = max(0.0, rect[1] - bb[1]) + max(0.0, bb[3] - rect[3])
    return dx + dy


def cost(items, net_items, rect, movable_mask, edge_mask=None, w_ov=6.0, w_out=40.0,
         w_hpwl=0.05, w_edge=3.0):
    c = 0.0
    boxes = [(it, it.bbox()) for it in items]
    n = len(boxes)
    for i in range(n):
        bi = boxes[i][1]
        for j in range(i + 1, n):
            bj = boxes[j][1]
            if (bi[2] < bj[0] or bj[2] < bi[0] or bi[3] < bj[1] or bj[3] < bi[1]):
                continue
            c += w_ov * overlap(bi, bj)
    for k, (it, bb) in enumerate(boxes):
        if movable_mask[k]:
            c += w_out * outside(bb, rect)
        if edge_mask and edge_mask[k]:
            d = min(bb[0] - rect[0], rect[2] - bb[2], bb[1] - rect[1], rect[3] - bb[3])
            c += w_edge * max(0.0, d)

    hp = 0.0
    for net, idxs in net_items.items():
        if len(idxs) < 2:
            continue
        xs = [items[i].x for i in idxs]
        ys = [items[i].y for i in idxs]
        hp += (max(xs) - min(xs)) + (max(ys) - min(ys))
    c += w_hpwl * hp
    return c


def anneal(items, net_items, rect, movable_mask, edge_mask=None, seed=1, iters=80000):
    rnd = random.Random(seed)
    for k, it in enumerate(items):
        if not movable_mask[k]:
            continue
        it.rot = rnd.choice(it.rots)
        l, t, r, b = it.geom[it.rot]
        w, h = r - l, b - t
        cx = rnd.uniform(rect[0] + w / 2, rect[2] - w / 2)
        cy = rnd.uniform(rect[1] + h / 2, rect[3] - h / 2)
        it.x = cx - (l + r) / 2
        it.y = cy - (t + b) / 2
    cur = cost(items, net_items, rect, movable_mask, edge_mask)
    best = cur
    best_state = [(it.x, it.y, it.rot) for it in items]

    pool = [it for k, it in enumerate(items) if movable_mask[k]]
    T0, T1 = 12.0, 0.02
    for k in range(iters):
        T = T0 * (T1 / T0) ** (k / iters)
        it = rnd.choice(pool)
        ox, oy, orot = it.x, it.y, it.rot
        move = rnd.random()
        if move < 0.12 and len(it.rots) > 1:
            it.rot = rnd.choice(it.rots)
        else:
            step = 1.0 + 12.0 * T / T0
            it.x = ox + rnd.uniform(-step, step)
            it.y = oy + rnd.uniform(-step, step)
        new = cost(items, net_items, rect, movable_mask, edge_mask)
        if new <= cur or rnd.random() < math.exp(-(new - cur) / max(T, 1e-9)):
            cur = new
            if new < best:
                best = new
                best_state = [(i.x, i.y, i.rot) for i in items]
        else:
            it.x, it.y, it.rot = ox, oy, orot

    for it, (x, y, rot) in zip(items, best_state):
        it.x, it.y, it.rot = x, y, rot
    return best


def main():
    board_p, plan_p, out_p = sys.argv[1], sys.argv[2], sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1

    plan = json.load(open(plan_p, encoding="utf-8"))
    rect = tuple(plan["board"])          # (x0, y0, x1, y1) area utilizavel

    board = pcbnew.LoadBoard(board_p)
    board.BuildListOfNets()

    fps = {}
    for fp in board.GetFootprints():
        fps.setdefault(fp.GetReference(), []).append(fp)

    items_all = []
    for ref, lst in fps.items():
        fp = lst[0]
        geom = {r: rel_bbox_at(fp, r) for r in ROTS}
        if geom[0] is None:
            print("  sem courtyard, ignorado:", ref)
            continue
        pads = {r: pad_offsets_at(fp, r) for r in ROTS}
        items_all.append((ref, Item(fp, geom, pads)))

    # netlist: ref -> indices de itens, somente redes com 2+ itens
    ref_to_idx = {ref: i for i, (ref, it) in enumerate(items_all)}
    net_items = {}
    for ref, it in items_all:
        for n, x, y in it.pads[0]:
            net_items.setdefault(n, set()).add(ref_to_idx[ref])
    net_items = {n: sorted(v) for n, v in net_items.items() if len(v) >= 2}

    fixed = {}
    movable = []
    for ref, it in items_all:
        spec = plan["fixed"].get(ref)
        if spec is None:
            movable.append(it)
            continue
        if spec == "keep":
            it.rot = round(it.fp.GetOrientationDegrees()) % 360
            it.x = it.fp.GetPosition().x / MM
            it.y = it.fp.GetPosition().y / MM
        else:
            cx, cy, rot = spec
            l, t, r, b = it.geom[rot]
            it.x = cx - (l + r) / 2
            it.y = cy - (t + b) / 2
            it.rot = rot
        it.rots = [it.rot]
        fixed[ref] = it

    items = list(fixed.values()) + movable
    movable_mask = [False] * len(fixed) + [True] * len(movable)
    print("fixos: %d   moveis: %d   redes: %d" % (len(fixed), len(movable), len(net_items)))

    edge_mask = [ref in set(plan.get('edge', [])) for ref in ([r for r in fixed] + [it.ref for it in movable])]
    best = anneal(items, net_items, rect, movable_mask, edge_mask, seed=seed)
    print("custo final: %.2f" % best)

    for it in items:
        it.fp.SetOrientationDegrees(it.rot)
        it.fp.SetPosition(pcbnew.VECTOR2I(int(round(it.x * MM)), int(round(it.y * MM))))

    board.BuildListOfNets()
    board.Save(out_p)
    print("salvo:", out_p)


if __name__ == "__main__":
    main()
