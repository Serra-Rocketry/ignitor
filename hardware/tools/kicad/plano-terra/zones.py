import sys
import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
print("zonas:", b.GetAreaCount())
for i in range(b.GetAreaCount()):
    z = b.GetArea(i)
    print("  [%d] net=%s layers=%s priority=%s clearance=%s min_width=%s thermal_gap=%s spoke=%s pad_conn=%s filled=%s"
          % (
              i,
              z.GetNetname(),
              [b.GetLayerName(l) for l in z.GetLayerSet().Seq()],
              z.GetAssignedPriority(),
              z.GetLocalClearance() / 1e6,
              z.GetMinThickness() / 1e6,
              z.GetThermalReliefGap() / 1e6,
              z.GetThermalReliefSpokeWidth() / 1e6,
              z.GetPadConnection(),
              z.IsFilled(),
          ))
    bb = z.GetBoundingBox()
    print("      bbox=(%.2f, %.2f)..(%.2f, %.2f)" % (
        bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6))
