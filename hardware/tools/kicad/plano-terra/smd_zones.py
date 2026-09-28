"""Cria as zonas GND da placa SMD no tamanho novo (85x70), deixando a area
da antena do ESP32 sem cobre.

O preenchimento NAO e feito aqui: sera refeito depois do roteamento.
"""

import sys

import pcbnew

MM = 1e6
SRC, OUT = sys.argv[1], sys.argv[2]

X0, Y0, X1, Y1 = 120.5, 65.5, 204.5, 134.5   # placa menos 0.5mm
AX, AY = 155.5, 82.0                          # canto superior esquerdo livre (antena)


def main():
    b = pcbnew.LoadBoard(SRC)
    print("zonas antes:", b.GetAreaCount())

    net = b.FindNet("GND")
    if net is None:
        raise SystemExit("rede GND nao encontrada")

    # poligono em L: comeca abaixo da area da antena
    outline = [
        (X0, AY), (AX, AY), (AX, Y0), (X1, Y0), (X1, Y1), (X0, Y1),
    ]

    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(b)
        z.SetLayer(layer)
        z.SetNet(net)
        z.SetLocalClearance(int(0.3 * MM))
        z.SetMinThickness(int(0.25 * MM))
        z.SetThermalReliefGap(int(0.4 * MM))
        z.SetThermalReliefSpokeWidth(int(0.6 * MM))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        # edita o contorno da propria zona (evita problema de posse do SHAPE_POLY_SET)
        ps = z.Outline()
        ps.RemoveAllContours()
        ps.NewOutline()
        for x, y in outline:
            ps.Append(int(round(x * MM)), int(round(y * MM)))
        b.Add(z)
        print("  zona GND criada em %s com %d pontos, contornos=%d"
              % (b.GetLayerName(layer), len(outline), z.Outline().OutlineCount()))

    b.BuildListOfNets()
    b.Save(OUT)
    print("salvo:", OUT)


if __name__ == "__main__":
    main()
