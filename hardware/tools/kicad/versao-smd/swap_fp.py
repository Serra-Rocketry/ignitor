"""Troca os footprints THT pelos SMD nos esquemas da versao _smd.

Atua na propriedade "Footprint" de cada instancia de simbolo, identificada
pela propriedade "Reference". Nao mexe em nada mais.
"""

import glob
import os
import re
import sys

SMD = r"hardware\kicad\pcbignicao\pcbignicao_smd"

# referencia -> novo footprint
MAP = {
    "A1": "ignitor:ESP32_NodeMCU-32S",
    "R1": "Resistor_SMD:R_0805_2012Metric",
    "R2": "Resistor_SMD:R_0805_2012Metric",
    "R3": "Resistor_SMD:R_0805_2012Metric",
    "R4": "Resistor_SMD:R_0805_2012Metric",
    "R5": "Resistor_SMD:R_0805_2012Metric",
    "R6": "Resistor_SMD:R_0805_2012Metric",
    "R7": "Resistor_SMD:R_0805_2012Metric",
    "C1": "Capacitor_SMD:C_0805_2012Metric",
    "C2": "Capacitor_SMD:C_0805_2012Metric",
    "D1": "LED_SMD:LED_0805_2012Metric",
    "D2": "LED_SMD:LED_0805_2012Metric",
    "D3": "Diode_SMD:D_SMA",
    "D4": "Diode_SMD:D_SOD-123",
    "D5": "Diode_SMD:D_SMA",
    "U2": "Package_SO:SOP-4_4.4x2.6mm_P1.27mm",
    "U3": "Package_SO:SOP-4_4.4x2.6mm_P1.27mm",
    # U1 (RA-02_THT) e todos os conectores continuam THT
}


def blocks(text):
    """(start, end) de cada instancia de simbolo no corpo da folha (1 tab)."""
    out = []
    for m in re.finditer(r"^\t\(symbol\n", text, re.MULTILINE):
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
        out.append((i, j))
    return out


def main(dry=False):
    total = 0
    for path in sorted(glob.glob(os.path.join(SMD, "*.kicad_sch"))):
        text = open(path, encoding="utf-8").read()
        edits = []
        for a, b in blocks(text):
            blk = text[a:b]
            mr = re.search(r'\(property "Reference" "([^"]+)"', blk)
            if not mr:
                continue
            ref = mr.group(1)
            if ref not in MAP:
                continue
            new = MAP[ref]
            mf = re.search(r'\(property "Footprint" "([^"]*)"', blk)
            if not mf:
                continue
            old = mf.group(1)
            if old == new:
                continue
            s = a + mf.start(1)
            e = a + mf.end(1)
            edits.append((s, e, old, new, ref))
        if not edits:
            continue
        print("%s: %d trocas" % (os.path.basename(path), len(edits)))
        for s, e, old, new, ref in edits:
            print("   %-4s %-58s -> %s" % (ref, old, new))
        total += len(edits)
        if not dry:
            for s, e, old, new, ref in sorted(edits, key=lambda t: -t[0]):
                text = text[:s] + new + text[e:]
            if text.count("(") != text.count(")"):
                raise SystemExit("ABORTADO %s: parenteses desbalanceados" % path)
            open(path, "w", encoding="utf-8", newline="\n").write(text)
    print()
    print("total de trocas:", total, "(dry-run)" if dry else "(aplicado)")


if __name__ == "__main__":
    main(dry="--apply" not in sys.argv)
