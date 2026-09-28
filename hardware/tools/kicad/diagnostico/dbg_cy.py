import pcbnew
MM = 1e6
b = pcbnew.LoadBoard(r"C:\Users\italo\AppData\Local\Temp\opencode\ignitor_analysis\work.kicad_pcb")
print("footprints:", len(b.GetFootprints()))
seen = {}
for fp in b.GetFootprints():
    r = fp.GetReference()
    seen.setdefault(r, []).append(fp)
dups = {k: len(v) for k, v in seen.items() if len(v) > 1}
print("refs duplicados:", dups)
print("refs unicos:", len(seen))

for ref in ("R2", "A1", "U3", "J8"):
    f = b.FindFootprintByReference(ref)
    cy = f.GetCourtyard(pcbnew.F_CrtYd)
    print("%-4s outlines=%d area=%.2f mm2 bbox=%s" % (
        ref, cy.OutlineCount(), cy.Area()/(MM*MM),
        (cy.BBox().GetLeft()/MM, cy.BBox().GetTop()/MM, cy.BBox().GetRight()/MM, cy.BBox().GetBottom()/MM)))

ra = b.FindFootprintByReference("R2").GetCourtyard(pcbnew.F_CrtYd)
aa = b.FindFootprintByReference("A1").GetCourtyard(pcbnew.F_CrtYd)
tmp = pcbnew.SHAPE_POLY_SET(ra)
tmp.BooleanIntersection(aa, pcbnew.SHAPE_POLY_SET.PM_FAST)
print("R2 ^ A1 area direta =", tmp.Area()/(MM*MM))
