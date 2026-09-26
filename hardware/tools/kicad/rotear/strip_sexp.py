"""Utilitario: remove blocos S-expression de nivel 1 do .kicad_pcb.

Usado para tirar as zonas antigas sem depender da API SWIG do pcbnew.
"""

import re
import sys

path = sys.argv[1]
out = sys.argv[2]
kinds = sys.argv[3].split(",")

text = open(path, encoding="utf-8").read()
removed = 0
for kind in kinds:
    pat = re.compile(r"^\t\(%s[\s\n]" % re.escape(kind), re.MULTILINE)
    while True:
        m = pat.search(text)
        if not m:
            break
        i = m.start()
        depth = 0
        j = i
        while True:
            c = text[j]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        while j < len(text) and text[j] in "\r\n":
            j += 1
        text = text[:i] + text[j:]
        removed += 1

if text.count("(") != text.count(")"):
    raise SystemExit("ABORTADO: parenteses desbalanceados (%d vs %d)" % (text.count("("), text.count(")")))

open(out, "w", encoding="utf-8", newline="\n").write(text)
print("removidos %d blocos %s -> %s" % (removed, kinds, out))
