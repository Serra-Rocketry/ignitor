import json
import sys

PROJECTS = [
    r"hardware\kicad\pcbignicao\pcbignicao\pcbignicao.kicad_pro",
    r"hardware\kicad\pcbignicao\pcbcomando\pcbcomando.kicad_pro",
]

BASE = {
    "bus_width": 12,
    "diff_pair_gap": 0.25,
    "diff_pair_via_gap": 0.25,
    "diff_pair_width": 0.2,
    "line_style": 0,
    "microvia_diameter": 0.3,
    "microvia_drill": 0.1,
    "pcb_color": "rgba(0, 0, 0, 0.000)",
    "schematic_color": "rgba(0, 0, 0, 0.000)",
    "tuning_profile": "",
    "wire_width": 6,
}


def cls(name, priority, track, clearance, via_d, via_drill):
    d = dict(BASE)
    d.update(
        {
            "name": name,
            "priority": priority,
            "track_width": track,
            "clearance": clearance,
            "via_diameter": via_d,
            "via_drill": via_drill,
        }
    )
    # keep a stable, KiCad-like key order
    order = [
        "bus_width",
        "clearance",
        "diff_pair_gap",
        "diff_pair_via_gap",
        "diff_pair_width",
        "line_style",
        "microvia_diameter",
        "microvia_drill",
        "name",
        "pcb_color",
        "priority",
        "schematic_color",
        "track_width",
        "tuning_profile",
        "via_diameter",
        "via_drill",
        "wire_width",
    ]
    return {k: d[k] for k in order}


CLASSES = [
    # Default stays at max priority -- KiCad treats it as the fallback
    cls("Default", 2147483647, 0.2, 0.2, 0.6, 0.3),
    cls("Power", 1, 0.5, 0.25, 0.8, 0.4),
    cls("IGN", 2, 1.0, 0.3, 1.0, 0.5),
]

PATTERNS = [
    {"netclass": "Power", "pattern": "VSYS"},
    {"netclass": "Power", "pattern": "EXT_5V"},
    {"netclass": "IGN", "pattern": "IGN_A"},
    {"netclass": "IGN", "pattern": "IGN_B"},
]

for p in PROJECTS:
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    ns = d.setdefault("net_settings", {})
    old = [c.get("name") for c in ns.get("classes", [])]
    ns["classes"] = CLASSES
    ns["netclass_patterns"] = PATTERNS
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("%-42s classes %s -> %s, %d patterns" % (p.split("\\")[-1], old, [c["name"] for c in CLASSES], len(PATTERNS)))
