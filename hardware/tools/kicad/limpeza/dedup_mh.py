"""Remove os furos de montagem duplicados (mesma referencia e mesma posicao)."""

import sys
import pcbnew

src = sys.argv[1]
out = sys.argv[2]

board = pcbnew.LoadBoard(src)

seen = {}
to_remove = []
for fp in board.GetFootprints():
    ref = fp.GetReference()
    key = (ref, fp.GetPosition().x, fp.GetPosition().y)
    if key in seen:
        to_remove.append(fp)
    else:
        seen[key] = fp

for fp in to_remove:
    print("removendo duplicata: %-5s uuid=%s at=(%.2f, %.2f)" % (
        fp.GetReference(), fp.m_Uuid.AsString(),
        fp.GetPosition().x / 1e6, fp.GetPosition().y / 1e6))
    board.Remove(fp)

print("footprints: %d -> %d" % (len(seen) + len(to_remove) + sum(1 for _ in []), len(board.GetFootprints())))
board.BuildListOfNets()
board.Save(out)
print("salvo:", out)
