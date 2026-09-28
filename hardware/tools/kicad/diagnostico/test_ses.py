import os, shutil
import pcbnew

work = r"C:\Users\italo\AppData\Local\Temp\opencode\ignitor_analysis\dsn_test"
board_p = os.path.join(work, "test.kicad_pcb")
ses_p   = os.path.join(work, "test.ses")

b = pcbnew.LoadBoard(board_p)
print("before import: tracks =", len(b.GetTracks()))
try:
    ok = pcbnew.ImportSpecctraSES(b, ses_p)
    print("ImportSpecctraSES ->", ok)
except Exception as e:
    print("SES import FAILED:", type(e).__name__, e)
print("after import: tracks =", len(b.GetTracks()))
out = os.path.join(work, "test_routed.kicad_pcb")
b.Save(out)
print("saved:", out, os.path.getsize(out))
