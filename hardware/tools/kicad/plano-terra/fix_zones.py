"""Ajusta os parametros das zonas GND e refaz o preenchimento."""

import sys

import pcbnew

src, out = sys.argv[1], sys.argv[2]

b = pcbnew.LoadBoard(src)
n = b.GetAreaCount()
for i in range(n):
    z = b.GetArea(i)
    if z.GetNetname() != "GND":
        continue
    z.SetLocalClearance(int(0.25 * 1e6))
    z.SetMinThickness(int(0.2 * 1e6))
    z.SetThermalReliefGap(int(0.4 * 1e6))
    z.SetThermalReliefSpokeWidth(int(0.6 * 1e6))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)

filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
b.BuildListOfNets()
b.Save(out)
print("zonas ajustadas e preenchidas:", n)
