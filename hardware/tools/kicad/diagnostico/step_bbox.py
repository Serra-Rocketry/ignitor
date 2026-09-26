import re, sys, os
def bbox_step(path):
    xs=[]; ys=[]; zs=[]
    pat = re.compile(r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([-0-9.eE+]+)\s*,\s*([-0-9.eE+]+)\s*,\s*([-0-9.eE+]+)")
    with open(path, 'r', errors='ignore') as f:
        data = f.read()
    for m in pat.finditer(data):
        xs.append(float(m.group(1))); ys.append(float(m.group(2))); zs.append(float(m.group(3)))
    if not xs: return None
    return (max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs))
for p in sys.argv[1:]:
    r = bbox_step(p)
    print("%-24s  X=%8.1f Y=%8.1f Z=%8.1f mm" % ((os.path.basename(p),)+r) if r else os.path.basename(p)+" no points")
