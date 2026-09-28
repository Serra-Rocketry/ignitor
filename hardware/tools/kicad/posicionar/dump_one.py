import sys
import pcbnew

SRC = sys.argv[1]
REF = sys.argv[2]
b = pcbnew.LoadBoard(SRC)
fp = b.FindFootprintByReference(REF)
print("ref", fp.GetReference(), "pos", fp.GetPosition(), "rot", fp.GetOrientationDegrees(),
      "layer", fp.GetLayerName())
print()
print("--- pads ---")
for p in fp.Pads():
    pos = p.GetPosition()
    sz = p.GetSize()
    print("  pad %-4s local=(%7.3f,%7.3f) board=(%8.3f,%8.3f) size=(%.2f,%.2f) shape=%s drill=%s net=%s"
          % (p.GetNumber(), p.GetFPRelativePosition().x / 1e6, p.GetFPRelativePosition().y / 1e6,
             pos.x / 1e6, pos.y / 1e6, sz.x / 1e6, sz.y / 1e6,
             p.GetShape(), p.GetDrillSize().x / 1e6, p.GetNetname()))
print()
print("--- graphics on F.Fab / F.SilkS ---")
for d in fp.GraphicalItems():
    ln = fp.GetLayerName(d.GetLayer())
    if ln not in ("F.Fab", "F.SilkS"):
        continue
    cls = d.GetClass()
    try:
        s = d.GetStart(); e = d.GetEnd()
        print("  %-12s %-8s start=(%7.2f,%7.2f) end=(%7.2f,%7.2f)" % (cls, ln, s.x / 1e6, s.y / 1e6, e.x / 1e6, e.y / 1e6))
    except Exception:
        print("  %-12s %-8s (no start/end)" % (cls, ln))
