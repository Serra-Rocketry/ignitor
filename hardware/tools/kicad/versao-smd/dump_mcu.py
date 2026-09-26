import re
import sys

p = r"hardware\kicad\pcbignicao\pcbignicao_smd\mcu_pico.kicad_sch"
t = open(p, encoding="utf-8").read()

print("=== contagens ===")
for k in ["global_label", "label ", "hierarchical_label", "wire", "junction", "symbol", "no_connect"]:
    print("  %-20s %d" % (k, len(re.findall(r"\(" + re.escape(k.strip()) + r"[\s\n]", t))))

print()
print("=== rotulos globais e posicoes ===")
for m in re.finditer(r'\(global_label "([^"]+)"\s*\n\s*\(shape (\w+)\)\s*\n\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\)', t):
    print("  %-14s shape=%-10s at=(%7.2f,%7.2f) rot=%s" % (m.group(1), m.group(2),
          float(m.group(3)), float(m.group(4)), m.group(5)))

print()
print("=== instancias de simbolo (nao-power) ===")
for m in re.finditer(r'\(symbol\s*\n\s*\(lib_id "([^"]+)"\)\s*\n\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\)\s*\n\s*\(unit (\d+)\)\s*\n\s*\([^\n]*\n\s*\(uuid "([^"]+)"\)', t):
    print("  lib_id=%-40s at=(%7.2f,%7.2f) rot=%s unit=%s uuid=%s" % (
        m.group(1), float(m.group(2)), float(m.group(3)), m.group(4), m.group(5), m.group(6)))

print()
print("=== power symbols ===")
for m in re.finditer(r'\(lib_id "power:([^"]+)"\)\s*\n\s*\(at ([-\d.]+) ([-\d.]+) (\d+)\)', t):
    print("  %-10s at=(%7.2f,%7.2f) rot=%s" % (m.group(1), float(m.group(2)), float(m.group(3)), m.group(4)))
