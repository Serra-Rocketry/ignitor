import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding="utf-8"))
print("=== NETS ===")
for n, info in d["nets"].items():
    pins = info.get("pins", [])
    s = ", ".join("%s.%s" % (x.get("component"), x.get("pin_name") or x.get("pin_number")) for x in pins)
    print("  %-26s (%2d) %s" % (n, len(pins), s[:170]))
