"""Pipeline de roteamento: DSN -> Freerouting -> SES -> placa roteada."""

import os
import shutil
import subprocess
import sys

import pcbnew

JAR = r"C:\Users\italo\Documents\KiCad\10.0\3rdparty\plugins\app_freerouting_kicad-plugin\jar\freerouting-2.2.4.jar"


def export_dsn(board_path, dsn_path):
    b = pcbnew.LoadBoard(board_path)
    ok = pcbnew.ExportSpecctraDSN(b, dsn_path)
    if not ok or not os.path.exists(dsn_path):
        raise SystemExit("falha ao exportar DSN")
    return os.path.getsize(dsn_path)


def run_freerouting(dsn_path, ses_path, passes=100, timeout=1800):
    if os.path.exists(ses_path):
        os.remove(ses_path)
    cmd = ["java", "-jar", JAR, "-de", dsn_path, "-do", ses_path, "-mp", str(passes)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    tail = [l for l in p.stdout.splitlines() if "completed" in l or "unrouted" in l]
    for l in tail[-3:]:
        print("   ", l.split("INFO")[-1].strip())
    if not os.path.exists(ses_path):
        raise SystemExit("Freerouting nao produziu SES\n" + p.stdout[-2000:] + p.stderr[-2000:])
    return os.path.getsize(ses_path)


def import_ses(src_path, ses_path, out_path):
    b = pcbnew.LoadBoard(src_path)
    before = len(b.GetTracks())
    ok = pcbnew.ImportSpecctraSES(b, ses_path)
    after = len(b.GetTracks())
    print("    trilhas: %d -> %d (ok=%s)" % (before, after, ok))
    b.BuildListOfNets()
    b.Save(out_path)
    return after


def refill(board_path):
    b = pcbnew.LoadBoard(board_path)
    filler = pcbnew.ZONE_FILLER(b)
    filler.Fill(b.Zones())
    b.Save(board_path)


if __name__ == "__main__":
    src, workdir = sys.argv[1], sys.argv[2]
    passes = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    tag = os.path.splitext(os.path.basename(src))[0]

    dsn = os.path.join(workdir, tag + ".dsn")
    ses = os.path.join(workdir, tag + ".ses")
    routed = os.path.join(workdir, tag + "_routed.kicad_pcb")

    print("[1] exportando DSN...")
    print("    DSN: %d bytes" % export_dsn(src, dsn))
    print("[2] roteando com Freerouting (mp=%d)..." % passes)
    print("    SES: %d bytes" % run_freerouting(dsn, ses, passes))
    print("[3] importando SES...")
    import_ses(src, ses, routed)
    print("[4] refazendo o preenchimento das zonas...")
    refill(routed)
    print("[5] pronto:", routed)
