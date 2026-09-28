"""Roda o pipeline completo para varias sementes e reporta o resultado do DRC."""

import json
import os
import subprocess
import sys

W = os.path.dirname(os.path.abspath(__file__))
KPY = r"C:\Program Files\KiCad\10.0\bin\python.exe"
KCLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"


def run(args, label):
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        print("   [%s] FALHOU rc=%d" % (label, p.returncode))
        print("   ", (p.stdout or "")[-800:])
        print("   ", (p.stderr or "")[-800:])
        return None
    return p.stdout


def pipeline(seed, base, plan, tag):
    out = os.path.join(W, "s%d.kicad_pcb" % seed)
    if not run([KPY, os.path.join(W, "placer.py"), base, plan, out, str(seed)], "placer"):
        return None
    r = os.path.join(W, "s%d_r.kicad_pcb" % seed)
    if not run([KPY, os.path.join(W, "route.py"), out, W, "100"], "route"):
        return None
    z = os.path.join(W, "s%d_z.kicad_pcb" % seed)
    if not run([KPY, os.path.join(W, "fix_zones.py"), r, z], "zones"):
        return None
    s = os.path.join(W, "s%d_s.kicad_pcb" % seed)
    if not run([KPY, os.path.join(W, "stitch.py"), z, s, "4.0"], "stitch"):
        return None
    drc = os.path.join(W, "drc_s%d.json" % seed)
    run([KCLI, "pcb", "drc", "--format", "json", "--severity-all", "--output", drc, s], "drc")
    if not os.path.exists(drc):
        return None
    d = json.load(open(drc, encoding="utf-8"))
    unc = d.get("unconnected_items", [])
    errs = [v for v in d.get("violations", []) if v["severity"] == "error"]
    import collections
    c = collections.Counter(v["type"] for v in errs)
    return {"seed": seed, "board": s, "unconnected": len(unc), "errors": len(errs), "by_type": dict(c)}


if __name__ == "__main__":
    base = sys.argv[1]
    plan = sys.argv[2]
    seeds = [int(x) for x in sys.argv[3:]]
    results = []
    for sd in seeds:
        print("=== seed %d ===" % sd)
        r = pipeline(sd, base, plan, "")
        if r:
            print("   -> unconnected=%d  errors=%d  %s" % (r["unconnected"], r["errors"], r["by_type"]))
            results.append(r)
    print()
    print("=== resumo ===")
    for r in sorted(results, key=lambda x: (x["unconnected"], x["errors"])):
        print("  seed %-3d unconnected=%-3d errors=%-3d %s" % (r["seed"], r["unconnected"], r["errors"], r["by_type"]))
