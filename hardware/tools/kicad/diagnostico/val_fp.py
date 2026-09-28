import sys, os
sys.path.insert(0, r"C:\Users\italo\tools\kicad-happy\skills\kicad\scripts")
try:
    from sexp_parser import parse_sexp
except Exception as e:
    from sexp_parser import parse as parse_sexp
p = r"hardware\kicad\shared\lib\ignitor.pretty\ESP32_NodeMCU-32S.kicad_mod"
d = parse_sexp(open(p, encoding="utf-8").read())
pads = [x for x in d if isinstance(x, list) and x and x[0] == "pad"]
print("OK parse. top-level nodes:", len(d), " pads:", len(pads))
nums = [x[1] for x in pads]
print("pad numbers 1..38 present:", sorted(nums, key=lambda s: int(s)) == [str(i) for i in range(1, 39)])
def padxy(x):
    at = [y for y in x if isinstance(y, list) and y[0] == "at"][0]
    return float(at[1]), float(at[2])
print("pad 1  ->", padxy([x for x in pads if x[1]=='1'][0]))
print("pad 19 ->", padxy([x for x in pads if x[1]=='19'][0]))
print("pad 20 ->", padxy([x for x in pads if x[1]=='20'][0]))
print("pad 38 ->", padxy([x for x in pads if x[1]=='38'][0]))
