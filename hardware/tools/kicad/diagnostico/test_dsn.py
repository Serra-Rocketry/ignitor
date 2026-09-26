import sys, os, shutil
import pcbnew, wx

src = r"hardware\kicad\pcbignicao\pcbignicao\pcbignicao.kicad_pcb"
work = r"C:\Users\italo\AppData\Local\Temp\opencode\ignitor_analysis\dsn_test"
os.makedirs(work, exist_ok=True)
tmp = os.path.join(work, "test.kicad_pcb")
shutil.copyfile(src, tmp)

b = pcbnew.LoadBoard(tmp)
print("loaded, footprints:", len(b.GetFootprints()))
print("tracks:", len(b.GetTracks()), " zones:", b.GetAreaCount())
dsn = os.path.join(work, "test.dsn")
try:
    ok = pcbnew.ExportSpecctraDSN(b, dsn)
    print("ExportSpecctraDSN ->", ok, " exists:", os.path.exists(dsn), os.path.getsize(dsn) if os.path.exists(dsn) else 0)
except Exception as e:
    print("DSN export FAILED:", type(e).__name__, e)
