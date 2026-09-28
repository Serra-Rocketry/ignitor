"""Busca no LCSC os equivalentes SMD dos componentes que mudaram de THT para SMD."""

import json
import subprocess
import sys

SCRIPT = r"C:\Users\italo\tools\kicad-happy\skills\lcsc\scripts\search_lcsc.py"

QUERIES = [
    ("R 330R 0805", ["330R 0805 resistor", "-p", "0805", "--basic", "--in-stock"]),
    ("R 1k 0805", ["1K 0805 resistor", "-p", "0805", "--basic", "--in-stock"]),
    ("R 10k 0805", ["10K 0805 resistor", "-p", "0805", "--basic", "--in-stock"]),
    ("C 100nF 0805", ["100nF 0805 capacitor X7R", "-p", "0805", "--basic", "--in-stock"]),
    ("C 10uF 0805", ["10uF 0805 capacitor X5R 25V", "-p", "0805", "--in-stock"]),
    ("LED amarelo 0805", ["yellow LED 0805", "-p", "0805", "--basic", "--in-stock"]),
    ("LED vermelho 0805", ["red LED 0805", "-p", "0805", "--basic", "--in-stock"]),
    ("D 1N5819 SMA", ["SS14 SMA schottky", "-p", "SMA", "--basic", "--in-stock"]),
    ("D 1N4007 SMA", ["1N4007 SMA rectifier", "-p", "SMA", "--in-stock"]),
    ("D 1N4148 SOD-123", ["1N4148W SOD-123", "--basic", "--in-stock"]),
    ("U PC817 SOP-4", ["PC817 SOP-4 optocoupler", "--in-stock"]),
]

for label, args in QUERIES:
    print("=" * 70)
    print(label)
    p = subprocess.run([sys.executable, SCRIPT] + args + ["-n", "4"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (p.stdout or "").strip()
    print(out[:1200] if out else ("(sem saida) " + (p.stderr or "")[-300:]))
