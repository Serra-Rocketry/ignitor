"""Troca o footprint de componentes especificos na PCB, mantendo posicao e redes.

Usado para corrigir componentes cujo footprint nao bate com a peca real.
Reatribui as redes dos pads pelo netlist e remove as trilhas que tocam os pads
do componente trocado (elas deixam de fazer sentido com a nova geometria).
"""

import os
import re
import sys

import pcbnew

MM = 1e6
KFP = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"
SHARED = r"hardware\kicad\shared\lib"


def blocos(text, header):
    out = []
    for m in re.finditer(re.escape(header), text):
        i = m.start(); d = 0; j = i
        while True:
            c = text[j]
            if c == "(": d += 1
            elif c == ")":
                d -= 1
                if d == 0:
                    j += 1; break
            j += 1
        out.append(text[i:j])
    return out


def parse_netlist(path):
    t = open(path, encoding="utf-8").read()
    comps = {}
    ini, fim = t.index("\t(components"), t.index("\t(nets")
    for blk in blocos(t[ini:fim], "\t\t(comp"):
        rf = re.search(r'\(ref "([^"]+)"\)', blk)
        if not rf:
            continue
        fp = re.search(r'\(footprint "([^"]*)"\)', blk)
        vl = re.search(r'\(value "([^"]*)"\)', blk)
        comps[rf.group(1)] = {"footprint": fp.group(1) if fp else "",
                              "value": vl.group(1) if vl else ""}
    pin_net = {}
    for blk in blocos(t[fim:], "\t\t(net\n"):
        nm = re.search(r'\(name "([^"]+)"\)', blk)
        if not nm:
            continue
        for ref, pin in re.findall(r'\(ref "([^"]+)"\)\s*\n\s*\(pin "([^"]+)"\)', blk):
            pin_net.setdefault(ref, {})[pin] = nm.group(1)
    return comps, pin_net


def lib_path(lib):
    for base in (SHARED, KFP):
        p = os.path.join(base, lib + ".pretty")
        if os.path.isdir(p):
            return p
    raise SystemExit("biblioteca nao encontrada: " + lib)


def main(net, src, out, refs):
    comps, pin_net = parse_netlist(net)
    b = pcbnew.LoadBoard(src)

    # snapshot antes de mutar
    snap = {}
    for fp in b.GetFootprints():
        snap[fp.GetReference()] = {
            "obj": fp,
            "fpid": "%s:%s" % (fp.GetFPID().GetLibNickname(), fp.GetFPID().GetLibItemName()),
            "pos": fp.GetPosition(), "rot": fp.GetOrientationDegrees(),
            "layer": fp.GetLayer(),
            "pads": [(p.GetPosition().x / MM, p.GetPosition().y / MM, p.GetNetname())
                     for p in fp.Pads()],
        }

    trocados = []
    for ref in refs:
        if ref not in snap or ref not in comps:
            print("  %s: nao encontrado no netlist ou na placa" % ref)
            continue
        novo = comps[ref]["footprint"]
        s = snap[ref]
        if s["fpid"] == novo:
            print("  %s: ja esta com %s" % (ref, novo))
            continue
        lib, nome = novo.split(":", 1)
        fp = pcbnew.FootprintLoad(lib_path(lib), nome)
        if fp is None:
            print("  %s: falha ao carregar %s" % (ref, novo))
            continue
        b.Remove(s["obj"])
        b.Add(fp)
        fp.SetReference(ref)
        fp.SetValue(comps[ref]["value"])
        fp.SetPosition(s["pos"])
        fp.SetOrientationDegrees(s["rot"])
        if fp.GetLayer() != s["layer"]:
            fp.SetLayer(s["layer"])
        pn = pin_net.get(ref, {})
        for pad in fp.Pads():
            nn = pn.get(pad.GetNumber())
            net_obj = b.FindNet(nn) if nn else None
            pad.SetNet(net_obj if net_obj is not None else b.FindNet(""))
        print("  %s: %s -> %s" % (ref, s["fpid"].split(":")[-1], novo.split(":")[-1]))
        trocados.append(ref)

    # remove as trilhas que terminavam nos pads ANTIGOS (a geometria mudou)
    alvo = []
    for ref in trocados:
        alvo.extend(snap[ref]["pads"])
    removidas = 0
    for t in list(b.GetTracks()):
        if t.GetClass() != "PCB_TRACK":
            continue
        s, e = t.GetStart(), t.GetEnd()
        sx, sy, ex, ey = s.x / MM, s.y / MM, e.x / MM, e.y / MM
        for ax, ay, an in alvo:
            if (abs(sx - ax) < 0.05 and abs(sy - ay) < 0.05) or (abs(ex - ax) < 0.05 and abs(ey - ay) < 0.05):
                b.Remove(t)
                removidas += 1
                break
    print("  trilhas removidas nos pads antigos:", removidas)

    b.BuildListOfNets()
    b.Save(out)
    print("salvo:", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
