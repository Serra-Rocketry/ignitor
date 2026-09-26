import json
import sys

for p in sys.argv[1:]:
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    r = d["board"]["design_settings"]["rules"]
    old = r.get("min_resolved_spokes")
    r["min_resolved_spokes"] = 1
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("%-46s min_resolved_spokes %s -> 1" % (p.split("\\")[-1], old))
