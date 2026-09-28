import sys
sys.path.insert(0, r"C:\Users\italo\tools\kicad-happy\skills\kicad\scripts")
import sexp_parser as sp
p = r"hardware\kicad\shared\lib\ignitor.kicad_sym"
d = sp.parse_file(p)
syms = [x for x in d if isinstance(x, list) and x and x[0] == "symbol"]
print("symbols:", [s[1] for s in syms])
for s in syms:
    subs = [y for y in s if isinstance(y, list) and y and y[0] == "symbol"]
    n = sum(len([z for z in sub if isinstance(z, list) and z and z[0] == "pin"]) for sub in subs)
    print("  %-22s pins=%d" % (s[1], n))
p2 = r"hardware\kicad\shared\lib\ignitor.pretty\ESP32_NodeMCU-32S.kicad_mod"
d2 = sp.parse_file(p2)
print("footprint pads:", len(sp.find_all(d2, "pad")))
