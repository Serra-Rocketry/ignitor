"""Remove flags de no-connect falsos (sobre um ponto que tem fio).

Um no_connect so e valido quando o ponto NAO tem nenhuma outra conexao.
Se houver um fio terminando no mesmo ponto, o flag e contraditorio e sai.

Remove o bloco S-expression COMPLETO, incluindo o ')' de fechamento, e valida
o balanceamento de parenteses antes de gravar.
"""

import re
import sys

TOL = 0.01

BLOCK = re.compile(
    r"[ \t]*\(no_connect\s*\n\s*\(at ([-\d.]+) ([-\d.]+)\)\s*\n\s*\(uuid \"([^\"]+)\"\)\s*\n\s*\)\n?",
    re.MULTILINE,
)


def wire_points(text):
    pts = []
    for m in re.finditer(
        r"\(wire\s*\n\s*\(pts\s*\n\s*\(xy ([-\d.]+) ([-\d.]+)\)\s*\n\s*\(xy ([-\d.]+) ([-\d.]+)\)",
        text,
    ):
        pts.append((float(m.group(1)), float(m.group(2))))
        pts.append((float(m.group(3)), float(m.group(4))))
    return pts


def junction_points(text):
    return [
        (float(m.group(1)), float(m.group(2)))
        for m in re.finditer(r"\(junction\s*\n\s*\(at ([-\d.]+) ([-\d.]+)\)", text)
    ]


def label_points(text):
    pts = []
    for m in re.finditer(r"\(label \"[^\"]*\"\s*\n\s*\(at ([-\d.]+) ([-\d.]+)\)", text):
        pts.append((float(m.group(1)), float(m.group(2))))
    return pts


def main(path, dry=True):
    text = open(path, encoding="utf-8").read()
    wires = wire_points(text)
    juncs = junction_points(text)
    labels = label_points(text)

    hits = []
    for m in BLOCK.finditer(text):
        x, y = float(m.group(1)), float(m.group(2))
        w = any(abs(x - a) < TOL and abs(y - b) < TOL for a, b in wires)
        j = any(abs(x - a) < TOL and abs(y - b) < TOL for a, b in juncs)
        l = any(abs(x - a) < TOL and abs(y - b) < TOL for a, b in labels)
        if w or j or l:
            hits.append((x, y, m.group(3), m.start(), m.end(), w, j, l))

    name = path.split("\\")[-1]
    print("%s: %d no_connect, %d extremos de fio" % (name, len(BLOCK.findall(text)), len(wires)))
    for x, y, uuid, _, _, w, j, l in hits:
        print("   CONFLITO (%.2f, %.2f) uuid=%s fio=%s juncao=%s rotulo=%s" % (x, y, uuid, w, j, l))

    if not hits:
        print("   nada a remover")
        return

    if dry:
        print("   [dry-run] %d seriam removidos" % len(hits))
        return

    for x, y, uuid, start, end, *_ in sorted(hits, key=lambda t: -t[3]):
        text = text[:start] + text[end:]

    if text.count("(") != text.count(")"):
        raise SystemExit("ABORTADO: parenteses desbalanceados (%d vs %d)" % (text.count("("), text.count(")")))
    if len(BLOCK.findall(text)) != 16 - len(hits):
        raise SystemExit("ABORTADO: sobrou numero inesperado de no_connect")

    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("   removidos: %d  (parenteses balanceados, restam %d no_connect)"
          % (len(hits), len(BLOCK.findall(text))))


if __name__ == "__main__":
    dry = "--apply" not in sys.argv
    for p in sys.argv[1:]:
        if p == "--apply":
            continue
        main(p, dry=dry)
