"""Engrossa as trilhas das redes de alimentacao (VSYS, EXT_5V) para 0,5 mm."""

import sys

import pcbnew

MM = 1e6
TARGETS = {"VSYS": 0.5, "EXT_5V": 0.5}
WIDTHS = [0.5, 0.45, 0.4, 0.35, 0.3, 0.25]

src, out = sys.argv[1], sys.argv[2]
width = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
b = pcbnew.LoadBoard(src)

tracks = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]

changed = 0
for t in tracks:
    n = t.GetNetname()
    if n not in TARGETS:
        continue
    t.SetWidth(int(width * MM))
    changed += 1
print("trilhas de alimentacao em %.2f mm: %d" % (width, changed))

filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.BuildListOfNets()
b.Save(out)
print("salvo:", out)
