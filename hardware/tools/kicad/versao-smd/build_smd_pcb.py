"""Constroi a PCB da versao SMD a partir da PCB THT + netlist do esquema novo.

- parte de uma copia da PCB THT (aproveita a posicao dos conectores)
- troca cada footprint pelo SMD equivalente indicado no netlist
- reatribui as redes de cada pad pelo nome
- por ultimo remove trilhas e vias; as zonas GND ficam e serao repreenchidas
"""

import os
import re
import sys

import pcbnew

MM = 1e6
KFP = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"
SHARED = r"hardware\kicad\shared\lib"

NET, SRC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]


def blocks(text, header):
    out = []
    for m in re.finditer(re.escape(header), text):
        i = m.start()
        depth = 0
        j = i
        while True:
            c = text[j]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        out.append(text[i:j])
    return out


def parse_netlist(path):
    t = open(path, encoding="utf-8").read()
    comps = {}
    start, end = t.index("\t(components"), t.index("\t(nets")
    for blk in blocks(t[start:end], "\t\t(comp"):
        ref = re.search(r'\(ref "([^"]+)"\)', blk)
        if not ref:
            continue
        val = re.search(r'\(value "([^"]*)"\)', blk)
        fp = re.search(r'\(footprint "([^"]*)"\)', blk)
        comps[ref.group(1)] = {"value": val.group(1) if val else "",
                               "footprint": fp.group(1) if fp else ""}
    nets = {}
    for blk in blocks(t[end:], "\t\t(net\n"):
        nm = re.search(r'\(name "([^"]+)"\)', blk)
        if nm:
            nets[nm.group(1)] = re.findall(r'\(ref "([^"]+)"\)\s*\n\s*\(pin "([^"]+)"\)', blk)
    pin_net = {}
    for name, nodes in nets.items():
        for ref, pin in nodes:
            pin_net.setdefault(ref, {})[pin] = name
    return comps, nets, pin_net


def lib_path(lib):
    for base in (SHARED, KFP):
        p = os.path.join(base, lib + ".pretty")
        if os.path.isdir(p):
            return p
    raise SystemExit("biblioteca nao encontrada: " + lib)


def main():
    comps, nets, pin_net = parse_netlist(NET)
    print("netlist: %d componentes, %d redes" % (len(comps), len(nets)))

    b = pcbnew.LoadBoard(SRC)
    print("PCB de partida: %d footprints, %d trilhas/vias, %d zonas"
          % (len(b.GetFootprints()), len(b.GetTracks()), b.GetAreaCount()))

    # snapshot de tudo que precisamos LER, antes de qualquer mutacao no board
    snap = {}
    for fp in b.GetFootprints():
        d = {"obj": fp, "fpid": "%s:%s" % (fp.GetFPID().GetLibNickname(),
                                           fp.GetFPID().GetLibItemName()),
             "pos": fp.GetPosition(), "rot": fp.GetOrientationDegrees(),
             "layer": fp.GetLayer(), "props": {}}
        for k in ("MPN", "Manufacturer", "LCSC", "BOM Comments"):
            try:
                d["props"][k] = fp.GetProperty(k) or ""
            except Exception:
                d["props"][k] = ""
        snap[fp.GetReference()] = d
    print("  snapshot: %d footprints" % len(snap))

    for name in nets:
        if b.FindNet(name) is None:
            b.Add(pcbnew.NETINFO_ITEM(b, name))
    b.BuildListOfNets()

    trocados, mantidos = 0, 0
    for ref in sorted(comps):
        info = comps[ref]
        fpid = info["footprint"]
        if not fpid:
            print("  %-5s SEM FOOTPRINT no netlist" % ref)
            continue
        if ref not in snap:
            print("  %-5s NAO EXISTE na PCB de partida" % ref)
            continue
        s = snap[ref]
        old, cur = s["obj"], s["fpid"]
        lib, name = fpid.split(":", 1)

        if cur == fpid:
            fp = old
            mantidos += 1
        else:
            fp = pcbnew.FootprintLoad(lib_path(lib), name)
            if fp is None:
                print("  %-5s FALHA ao carregar %s" % (ref, fpid))
                continue
            b.Remove(old)
            b.Add(fp)
            trocados += 1

        fp.SetReference(ref)
        fp.SetValue(info["value"])
        fp.SetPosition(s["pos"])
        fp.SetOrientationDegrees(s["rot"])
        if fp.GetLayer() != s["layer"]:
            fp.SetLayer(s["layer"])
        for k, v in s["props"].items():
            try:
                fp.SetProperty(k, v)
            except Exception:
                pass

        pn = pin_net.get(ref, {})
        for pad in fp.Pads():
            nn = pn.get(pad.GetNumber())
            net = b.FindNet(nn) if nn else None
            pad.SetNet(net if net is not None else b.FindNet(""))

    print("  footprints trocados: %d   mantidos: %d" % (trocados, mantidos))

    removed = 0
    for t in list(b.GetTracks()):
        b.Remove(t)
        removed += 1
    print("  trilhas/vias removidos: %d" % removed)

    b.BuildListOfNets()
    b.Save(OUT)
    print("salvo:", OUT)

    b2 = pcbnew.LoadBoard(OUT)
    sem = sum(1 for fp in b2.GetFootprints() for pad in fp.Pads()
              if not pad.GetNetname() and pad.GetNumber())
    print("pads sem rede: %d   footprints finais: %d" % (sem, len(b2.GetFootprints())))


if __name__ == "__main__":
    main()
