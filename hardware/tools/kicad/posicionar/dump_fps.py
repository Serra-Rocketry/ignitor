import sys
import pcbnew

SRC = sys.argv[1] if len(sys.argv) > 1 else r"hardware\kicad\pcbignicao\pcbignicao\pcbignicao.kicad_pcb"
b = pcbnew.LoadBoard(SRC)


def bbox_of(fp):
    bb = fp.GetBoundingBox()
    return bb


print("%-6s %-42s %-9s %-9s %-8s %-8s %s" % ("REF", "FOOTPRINT", "X", "Y", "W", "H", "ROT"))
rows = []
for fp in b.GetFootprints():
    ref = fp.GetReference()
    fpid = fp.GetFPID().GetLibItemName()
    pos = fp.GetPosition()
    bb = bbox_of(fp)
    x = pos.x / 1e6
    y = pos.y / 1e6
    w = bb.GetWidth() / 1e6
    h = bb.GetHeight() / 1e6
    rot = fp.GetOrientationDegrees()
    rows.append((ref, fpid, x, y, w, h, rot))
    print("%-6s %-42s %9.2f %9.2f %8.2f %8.2f %s" % (ref, fpid, x, y, w, h, rot))

# courtyard-based rectangles, to place without overlaps
print()
print("=== courtyard rects (fp-local, from F.CrtYd) ===")
for fp in b.GetFootprints():
    ct = fp.GetCourtyard(pcbnew.F_CrtYd)
    if ct.OutlineCount() == 0:
        print("%-6s NO COURTYARD" % fp.GetReference())
        continue
    bb = ct.BBox()
    print("%-6s w=%6.2f h=%6.2f" % (fp.GetReference(), bb.GetWidth() / 1e6, bb.GetHeight() / 1e6))
