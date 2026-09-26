"""Corrige violacoes de isolamento usando o proprio DRC do KiCad como medida.

Em vez de recalcular geometria (sujeito a divergencia), roda o DRC, le o UUID
de cada trilha culpada e o valor real de isolamento que o KiCad reportou, e
atua sobre exatamente aquele item:

  1. afina a trilha o minimo necessario para atingir o alvo
  2. se afinar ate o minimo do netclass ainda nao bastar, desloca a trilha
     perpendicularmente, para longe do pad

Repete ate zerar ou atingir o limite de iteracoes. Só muda largura/posicao de
trilhas existentes: nenhuma conexao e criada ou removida.
"""

import json
import os
import re
import shutil
import subprocess
import sys

import pcbnew

MM = 1e6
KCLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
ALVO = 0.15        # margem de seguranca sobre o minimo de 0.127 mm
LARG_MIN = 0.2     # piso do netclass


def rodar_drc(board_path, out_json):
    if os.path.exists(out_json):
        os.remove(out_json)
    subprocess.run([KCLI, "pcb", "drc", "--format", "json", "--severity-all",
                    "--output", out_json, board_path],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
    return json.load(open(out_json, encoding="utf-8"))


def violacoes_de_trilha(drc):
    """[(uuid_trilha, isolamento_atual, pos_trilha, pos_outro)] das violacoes de clearance."""
    out = []
    for v in drc.get("violations", []):
        if v.get("severity") != "error" or v.get("type") != "clearance":
            continue
        m = re.search(r"atual ([\d,\.]+) mm", v.get("description") or "")
        if not m:
            continue
        atual = float(m.group(1).replace(",", "."))
        trilhas = [i for i in v.get("items", []) if (i.get("description") or "").startswith("Trilha")]
        outros = [i for i in v.get("items", []) if not (i.get("description") or "").startswith("Trilha")]
        for t in trilhas:
            out.append((t.get("uuid"), atual, t.get("pos"), outros[0].get("pos") if outros else None))
    return out


def violacoes_de_borda(drc):
    """[(uuid_do_cobre, isolamento_atual)] para violacoes de cobre-borda."""
    out = []
    for v in drc.get("violations", []):
        if v.get("severity") != "error" or v.get("type") != "copper_edge_clearance":
            continue
        m = re.search(r"atual ([\d,\.]+) mm", v.get("description") or "")
        if not m:
            continue
        atual = float(m.group(1).replace(",", "."))
        for i in v.get("items", []):
            d = i.get("description") or ""
            if d.startswith("Trilha") or d.startswith("Via"):
                out.append((i.get("uuid"), atual))
    return out


def achar(board, uuid):
    for t in board.GetTracks():
        if t.m_Uuid.AsString() == uuid:
            return t
    return None


def mover_para_dentro(board, item, deficit):
    """Move uma via/trilha na direcao do centro da placa."""
    bb = board.GetBoardEdgesBoundingBox()
    cx = (bb.GetLeft() + bb.GetRight()) / 2.0
    cy = (bb.GetTop() + bb.GetBottom()) / 2.0
    passo = deficit + 0.05

    if item.GetClass() == "PCB_VIA":
        p = item.GetPosition()
        x, y = p.x / MM, p.y / MM
        dx, dy = cx / MM - x, cy / MM - y
        L = (dx * dx + dy * dy) ** 0.5 or 1.0
        item.SetPosition(pcbnew.VECTOR2I(int(round((x + dx / L * passo) * MM)),
                                         int(round((y + dy / L * passo) * MM))))
        return True

    s, e = item.GetStart(), item.GetEnd()
    ax, ay, bx, by = s.x / MM, s.y / MM, e.x / MM, e.y / MM
    mx, my = (ax + bx) / 2, (ay + by) / 2
    dx, dy = cx / MM - mx, cy / MM - my
    L = (dx * dx + dy * dy) ** 0.5 or 1.0
    item.SetStart(pcbnew.VECTOR2I(int(round((ax + dx / L * passo) * MM)),
                                  int(round((ay + dy / L * passo) * MM))))
    item.SetEnd(pcbnew.VECTOR2I(int(round((bx + dx / L * passo) * MM)),
                                int(round((by + dy / L * passo) * MM))))
    return True


def main(src, out, max_iter=8):
    board_path = src
    tmp_drc = out + ".drc.json"
    shutil.copyfile(src, out)

    for it in range(1, max_iter + 1):
        drc = rodar_drc(out, tmp_drc)
        viol = violacoes_de_trilha(drc)
        borda = violacoes_de_borda(drc)
        unc = len(drc.get("unconnected_items", []))
        print("--- iteracao %d: %d de isolamento | %d de borda | %d desconectados"
              % (it, len(viol), len(borda), unc))
        if not viol and not borda:
            print("LIMPO")
            break

        b = pcbnew.LoadBoard(out)
        agido = 0
        for uuid, atual in borda:
            t = achar(b, uuid)
            if t is None:
                continue
            mover_para_dentro(b, t, 0.5 - atual)
            print("   borda: %-6s afastado %.3f mm do limite"
                  % (t.GetNetname(), 0.5 - atual + 0.05))
            agido += 1
        for uuid, atual, pos_t, pos_o in viol:
            t = achar(b, uuid)
            if t is None:
                print("   uuid %s nao encontrado" % (uuid or "?"))
                continue
            w = t.GetWidth() / MM
            precisa = ALVO - atual
            nova = w - 2 * precisa
            s, e = t.GetStart(), t.GetEnd()
            if nova >= LARG_MIN:
                nova = round(nova, 3)
                t.SetWidth(int(round(nova * MM)))
                print("   %-6s (%.2f,%.2f)->(%.2f,%.2f) folga=%.4f  largura %.2f -> %.2f"
                      % (t.GetNetname(), s.x / MM, s.y / MM, e.x / MM, e.y / MM, atual, w, nova))
            else:
                t.SetWidth(int(LARG_MIN * MM))
                # desloca perpendicularmente, para longe do outro item
                if pos_o:
                    ax, ay = s.x / MM, s.y / MM
                    bx, by = e.x / MM, e.y / MM
                    dx, dy = bx - ax, by - ay
                    L = (dx * dx + dy * dy) ** 0.5 or 1.0
                    nx, ny = -dy / L, dx / L
                    ox, oy = pos_o.get("x", 0), pos_o.get("y", 0)
                    mx, my = (ax + bx) / 2, (ay + by) / 2
                    sinal = 1.0 if (ox - mx) * nx + (oy - my) * ny > 0 else -1.0
                    falta = ALVO - atual - (w - LARG_MIN) / 2
                    passo = max(0.05, min(falta, 0.25))
                    t.SetStart(pcbnew.VECTOR2I(int(round((ax - sinal * nx * passo) * MM)),
                                               int(round((ay - sinal * ny * passo) * MM))))
                    t.SetEnd(pcbnew.VECTOR2I(int(round((bx - sinal * nx * passo) * MM)),
                                             int(round((by - sinal * ny * passo) * MM))))
                    print("   %-6s (%.2f,%.2f)->(%.2f,%.2f) folga=%.4f  largura->%.2f + desloc %.3f"
                          % (t.GetNetname(), ax, ay, bx, by, atual, LARG_MIN, passo))
            agido += 1
        if not agido:
            print("nada a fazer")
            break
        f = pcbnew.ZONE_FILLER(b)
        f.Fill(b.Zones())
        b.BuildListOfNets()
        b.Save(out)
    else:
        print("atingiu o limite de iteracoes")

    drc = rodar_drc(out, tmp_drc)
    print()
    print("FINAL: %d desconectados, %d erros"
          % (len(drc.get("unconnected_items", [])),
             len([v for v in drc.get("violations", []) if v["severity"] == "error"])))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
