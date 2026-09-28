import pcbnew
MM = 1e6
b = pcbnew.LoadBoard(r"C:\Users\italo\AppData\Local\Temp\opencode\ignitor_analysis\p_8_z.kicad_pcb")
targets = {"A1.8": (147.90, 108.32), "C2.2": (152.5355, 108.7658)}
R = 6.0
print("=== trilhas num raio de %.1fmm ===" % R)
for name, (tx, ty) in targets.items():
    print("--", name)
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK":
            continue
        s, e = t.GetStart(), t.GetEnd()
        sx, sy, ex, ey = s.x/MM, s.y/MM, e.x/MM, e.y/MM
        if (abs(sx-tx) < R and abs(sy-ty) < R) or (abs(ex-tx) < R and abs(ey-ty) < R):
            print("   %s w=%.2f net=%-10s (%.2f,%.2f)->(%.2f,%.2f)" % (
                b.GetLayerName(t.GetLayer()), t.GetWidth()/MM, t.GetNetname(), sx, sy, ex, ey))
    print("   pads por perto:")
    for fp in b.GetFootprints():
        for p in fp.Pads():
            px, py = p.GetPosition().x/MM, p.GetPosition().y/MM
            if abs(px-tx) < 3.0 and abs(py-ty) < 3.0 and not (fp.GetReference()=="A1" and p.GetNumber()=="8"):
                print("      %s.%s net=%-10s (%.2f,%.2f)" % (fp.GetReference(), p.GetNumber(), p.GetNetname(), px, py))
