"""Atualiza MPN/LCSC dos componentes que viraram SMD na versao _smd.

Os conectores, o ESP32 e o modulo LoRa continuam THT e serao soldados a mao,
entao saem da montagem da JLCPCB.
"""

import glob
import os
import re
import sys

SMD = r"hardware\kicad\pcbignicao\pcbignicao_smd"

# ref -> (MPN, LCSC, observed)
PARTS = {
    "R1": ("0805W8F3300T5E", "C17630", "330R 0805 1% Basic"),
    "R2": ("0805W8F3300T5E", "C17630", "330R 0805 1% Basic"),
    "R3": ("0805W8F3300T5E", "C17630", "330R 0805 1% Basic"),
    "R4": ("0805W8F1001T5E", "C17513", "1k 0805 1% Basic"),
    "R5": ("0805W8F1002T5E", "C17414", "10k 0805 1% Basic"),
    "R6": ("0805W8F1002T5E", "C17414", "10k 0805 1% Basic"),
    "R7": ("0805W8F1002T5E", "C17414", "10k 0805 1% Basic"),
    "C1": ("CC0805KRX7R9BB104", "C49678", "100nF 50V X7R 0805 Basic"),
    "C2": ("CL21A106KAYNNNE", "C15850", "10uF 25V X5R 0805 Basic"),
    "D1": ("KT-0805Y", "C2296", "LED amarelo 0805 Basic"),
    "D2": ("NCD0805R1", "C84256", "LED vermelho 0805 Basic"),
    "D3": ("SS14", "C2480", "Schottky 1A 40V SMA (equiv. 1N5819) Basic"),
    "D4": ("1N4148W", "C81598", "1N4148 SOD-123 Basic"),
    "D5": ("1N4007", "C727081", "1N4007 SMA Extended"),
    "U2": ("PC817C", "C3025164", "PC817C SMD-4P Extended - CONFERIR passo do footprint"),
    "U3": ("PC817C", "C3025164", "PC817C SMD-4P Extended - CONFERIR passo do footprint"),
}


def blocks(text):
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


def set_prop(blk, name, value, at):
    """Substitui ou insere a propriedade `name` dentro do bloco do simbolo."""
    pat = re.compile(r'\(property "%s" "([^"]*)"\s*\n(\s*\(at [^)]*\)\n)(\s*\(hide yes\)\n)?(\s*\(show_name no\)\n)?' % re.escape(name))
    m = pat.search(blk)
    if m:
        return blk[:m.start(1)] + value + blk[m.end(1):], True
    # insere antes de (instances ou do fim
    ins = ('\t\t(property "%s" "%s"\n\t\t\t(at %s)\n\t\t\t(hide yes)\n\t\t\t(effects (font (size 1.27 1.27)))\n\t\t)\n'
           % (name, value, at))
    k = blk.find("\t\t(instances")
    if k < 0:
        k = blk.rfind(")")
    return blk[:k] + ins + blk[k:], False


def main(apply=False):
    changed = 0
    for path in sorted(glob.glob(os.path.join(SMD, "*.kicad_sch"))):
        text = open(path, encoding="utf-8").read()
        edits = []
        for a, b in blocks(text):
            blk = text[a:b]
            mr = re.search(r'\(property "Reference" "([^"]+)"', blk)
            if not mr:
                continue
            ref = mr.group(1)
            if ref not in PARTS:
                continue
            mpn, lcsc, note = PARTS[ref]
            ma = re.search(r'\(property "Reference" "[^"]+"\s*\n\s*\(at ([^)]*)\)', blk)
            at = ma.group(1) if ma else "0 0 0"
            new = blk
            new, _ = set_prop(new, "MPN", mpn, at)
            new, _ = set_prop(new, "LCSC", lcsc, at)
            new, _ = set_prop(new, "BOM Comments", note, at)
            if new != blk:
                edits.append((a, b, new, ref, mpn, lcsc))
        if not edits:
            continue
        print("%s: %d componentes" % (os.path.basename(path), len(edits)))
        for a, b, new, ref, mpn, lcsc in edits:
            print("   %-4s -> %-18s %s" % (ref, mpn, lcsc))
        changed += len(edits)
        if apply:
            for a, b, new, *_ in sorted(edits, key=lambda t: -t[0]):
                text = text[:a] + new + text[b:]
            if text.count("(") != text.count(")"):
                raise SystemExit("ABORTADO %s desbalanceado" % path)
            open(path, "w", encoding="utf-8", newline="\n").write(text)
    print()
    print("total:", changed, "(aplicado)" if apply else "(dry-run)")


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
