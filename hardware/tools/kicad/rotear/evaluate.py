"""Avalia placas ja roteadas: zonas -> costura -> DRC. NAO roda o Freerouting."""

import collections
import json
import os
import subprocess
import sys

W = os.path.dirname(os.path.abspath(__file__))
KPY = r"C:\Program Files\KiCad\10.0\bin\python.exe"
KCLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"


def run(args):
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or ""), (p.stderr or "")


rows = []
for base in sys.argv[1:]:
    tag = os.path.splitext(os.path.basename(base))[0]
    z = os.path.join(W, tag + "_z2.kicad_pcb")
    s = os.path.join(W, tag + "_s2.kicad_pcb")
    d = os.path.join(W, "drc_" + tag + "_2.json")

    rc, out, err = run([KPY, os.path.join(W, "fix_zones.py"), base, z])
    if rc != 0:
        print("%-16s zonas FALHOU rc=%d %s" % (tag, rc, err[-200:]))
        continue
    rc, out, err = run([KPY, os.path.join(W, "stitch.py"), z, s, "4.0"])
    if rc != 0:
        print("%-16s stitch FALHOU rc=%d %s" % (tag, rc, err[-200:]))
        continue
    stitches = ""
    for line in out.splitlines():
        if "vias de costura" in line:
            stitches = line.strip()
    run([KCLI, "pcb", "drc", "--format", "json", "--severity-all", "--output", d, s])
    if not os.path.exists(d):
        print("%-16s DRC sem saida" % tag)
        continue
    data = json.load(open(d, encoding="utf-8"))
    unc = data.get("unconnected_items", [])
    errs = [v for v in data.get("violations", []) if v["severity"] == "error"]
    c = collections.Counter(v["type"] for v in errs)
    warn = collections.Counter(v["type"] for v in data.get("violations", []) if v["severity"] == "warning")
    rows.append((len(unc), len(errs), tag, s, dict(c), dict(warn), stitches))
    print("%-16s unconnected=%-3d errors=%-3d %s | warns %s | %s" % (
        tag, len(unc), len(errs), dict(c), dict(warn), stitches))

print()
print("=== ordenado por (unconnected, errors) ===")
for u, e, tag, s, c, w, st in sorted(rows):
    print("  %-16s unc=%-3d err=%-3d %s" % (tag, u, e, c))
