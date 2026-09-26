import json, sys, collections
d = json.load(open(sys.argv[1], encoding="utf-8"))
want = sys.argv[2].split(",") if len(sys.argv)>2 else None
for f in d.get("findings", []):
    if want and f.get("rule_id") not in want: continue
    print("[%s/%s/%s] %s" % (f.get("rule_id"), f.get("severity"), f.get("confidence"), f.get("summary")))
    if f.get("recommendation"): print("     -> %s" % f["recommendation"])
