"""Gera BOM e CPL no formato da JLCPCB para a placa SMD da ignicao.

Somente os componentes SMD entram na montagem: conectores, ESP32 (socketado)
e o modulo LoRa continuam sendo soldados a mao.
"""

import csv
import io
import os

BOM_IN = r"hardware\gerbers\pcbignicao_smd\pcbignicao_smd-bom.csv"
POS_IN = r"hardware\gerbers\pcbignicao_smd\pcbignicao_smd-pos.csv"
OUT_BOM = r"hardware\gerbers\pcbignicao_smd\jlcpcb-bom.csv"
OUT_CPL = r"hardware\gerbers\pcbignicao_smd\jlcpcb-cpl.csv"

SMD_PREFIX = ("R", "C", "D", "U")
THT_REFS = {"U1"}          # Ra-02 sobre adaptador THT


def is_smd(ref):
    if ref in THT_REFS:
        return False
    return ref[:1] in SMD_PREFIX


def expand(ref):
    """'R1-R3' -> ['R1','R2','R3']"""
    if "-" in ref:
        a, b = ref.split("-")
        pa, na = a[0], int(a[1:])
        nb = int(b[1:])
        return ["%s%d" % (pa, i) for i in range(na, nb + 1)]
    return [ref]


def main():
    # ---------- BOM ----------
    rows = list(csv.DictReader(open(BOM_IN, encoding="utf-8")))
    out = []
    for r in rows:
        refs = []
        for chunk in r["Designator"].split(","):
            refs.extend(expand(chunk.strip()))
        smd = [x for x in refs if is_smd(x)]
        if not smd:
            continue
        lcsc = (r.get("LCSC") or "").strip()
        if not lcsc:
            print("  AVISO: %s sem codigo LCSC" % r["Designator"])
        out.append({
            "Comment": r["Comment"],
            "Designator": ",".join(smd),
            "Footprint": r["Footprint"].split(":")[-1],
            "LCSC Part #": lcsc,
        })
    with open(OUT_BOM, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["Comment", "Designator", "Footprint", "LCSC Part #"])
        w.writeheader()
        w.writerows(out)
    print("BOM: %d linhas, %d componentes -> %s" % (len(out), sum(len(r["Designator"].split(",")) for r in out), OUT_BOM))

    # ---------- CPL ----------
    cpl = []
    for r in csv.DictReader(open(POS_IN, encoding="utf-8")):
        ref = r["Ref"].strip('"')
        if not is_smd(ref):
            continue
        cpl.append({
            "Designator": ref,
            "Mid X": "%.4f" % float(r["PosX"]),
            "Mid Y": "%.4f" % float(r["PosY"]),
            "Layer": "Top" if r["Side"].strip('"').lower() == "top" else "Bottom",
            "Rotation": "%.6f" % float(r["Rot"]),
        })
    with open(OUT_CPL, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        w.writeheader()
        w.writerows(cpl)
    print("CPL: %d componentes -> %s" % (len(cpl), OUT_CPL))

    # conferencia: CPL e BOM tem exatamente os mesmos designadores
    bom_refs = set()
    for r in out:
        bom_refs.update(r["Designator"].split(","))
    cpl_refs = {r["Designator"] for r in cpl}
    print()
    print("  BOM x CPL: so no BOM: %s | so no CPL: %s" % (sorted(bom_refs - cpl_refs), sorted(cpl_refs - bom_refs)))


if __name__ == "__main__":
    main()
