import glob
import os
import re

ROOT = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"
SCH = r"hardware\kicad\pcbignicao\pcbignicao"

libs = {}
for d in glob.glob(os.path.join(ROOT, "*.pretty")):
    libs[os.path.basename(d)[:-7]] = {os.path.splitext(f)[0] for f in os.listdir(d)}

seen = {}
for f in glob.glob(os.path.join(SCH, "*.kicad_sch")):
    t = open(f, encoding="utf-8").read()
    for m in re.finditer(r'\(property "Footprint" "([^"]+)"', t):
        fp = m.group(1)
        if not fp or ":" not in fp:
            continue
        seen.setdefault(fp, set()).add(os.path.basename(f))

bad = 0
for fp in sorted(seen):
    lib, name = fp.split(":", 1)
    where = ",".join(sorted(seen[fp]))
    if lib not in libs:
        verdict = "LIB DESCONHECIDA"
        bad += 1
    elif name not in libs[lib]:
        verdict = "NAO EXISTE em %s" % lib
        bad += 1
    else:
        verdict = "ok"
    print("  %-58s %-28s [%s]" % (fp, verdict, where))

print()
print("problemas:", bad)
