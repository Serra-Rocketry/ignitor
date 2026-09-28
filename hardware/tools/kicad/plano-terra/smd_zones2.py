"""Recria as zonas GND da placa SMD como retangulos cheios.

O ESP32 e um modulo socketado, que fica ~11 mm acima da PCB: um keepout de
cobre sob a antena tem efeito desprezivel nessa distancia, e o recorte
anterior acabava excluindo os proprios pinos GND do modulo.
"""

import sys

import pcbnew

MM = 1e6
SRC, OUT = sys.argv[1], sys.argv[2]

X0, Y0, X1, Y1 = 120.5, 65.5, 204.5, 134.5


def main():
    b = pcbnew.LoadBoard(SRC)
    print("zonas antes:", b.GetAreaCount())
    net = b.FindNet("GND")
    if net is None:
        raise SystemExit("rede GND nao encontrada")

    outline = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(b)
        z.SetLayer(layer)
        z.SetNet(net)
        z.SetLocalClearance(int(0.25 * MM))
        z.SetMinThickness(int(0.3 * MM))
        z.SetThermalReliefGap(int(0.4 * MM))
        z.SetThermalReliefSpokeWidth(int(0.6 * MM))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        ps = z.Outline()
        ps.RemoveAllContours()
        ps.NewOutline()
        for x, y in outline:
            ps.Append(int(round(x * MM)), int(round(y * MM)))
        b.Add(z)
        print("  zona GND %s criada (%d contornos)" % (b.GetLayerName(layer), z.Outline().OutlineCount()))

    filler = pcbnew.ZONE_FILLER(b)
    filler.Fill(b.Zones())
    b.BuildListOfNets()
    b.Save(OUT)
    print("salvo:", OUT)


if __name__ == "__main__":
    main()
