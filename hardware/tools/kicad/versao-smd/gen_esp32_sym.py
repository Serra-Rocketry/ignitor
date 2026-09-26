import re

LIB = r"hardware\kicad\shared\lib\ignitor.kicad_sym"

# physical pin -> (display name, etype)
# etype: passive / input / output / bidirectional / power_in / no_connect
P = {
    1: ("3V3", "power_in"),
    2: ("EN", "input"),
    3: ("GPIO36", "input"),
    4: ("GPIO39", "input"),
    5: ("GPIO34", "input"),
    6: ("GPIO35", "input"),
    7: ("GPIO32", "bidirectional"),
    8: ("GPIO33", "bidirectional"),
    9: ("GPIO25", "bidirectional"),
    10: ("GPIO26", "bidirectional"),
    11: ("GPIO27", "bidirectional"),
    12: ("GPIO14", "bidirectional"),
    13: ("GPIO12", "bidirectional"),
    14: ("GND", "power_in"),
    15: ("GPIO13", "bidirectional"),
    16: ("GPIO9", "no_connect"),
    17: ("GPIO10", "no_connect"),
    18: ("GPIO11", "no_connect"),
    19: ("5V", "power_in"),
    20: ("GPIO6", "no_connect"),
    21: ("GPIO7", "no_connect"),
    22: ("GPIO8", "no_connect"),
    23: ("GPIO15", "bidirectional"),
    24: ("GPIO2", "bidirectional"),
    25: ("GPIO0", "bidirectional"),
    26: ("GPIO4", "bidirectional"),
    27: ("GPIO16", "bidirectional"),
    28: ("GPIO17", "bidirectional"),
    29: ("GPIO5", "bidirectional"),
    30: ("GPIO18", "bidirectional"),
    31: ("GPIO19", "bidirectional"),
    32: ("GND", "power_in"),
    33: ("GPIO21", "bidirectional"),
    34: ("GPIO3", "bidirectional"),
    35: ("GPIO1", "bidirectional"),
    36: ("GPIO22", "bidirectional"),
    37: ("GPIO23", "bidirectional"),
    38: ("GND", "power_in"),
}

PITCH = 2.54
BODY_HX = 15.24
PIN_LEN = 2.54
XYP = 22.86          # (19-1)*2.54/2


def f(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return s if s else "0"


def pin_y(n):
    if 1 <= n <= 19:
        return XYP - (n - 1) * PITCH
    return -XYP + (n - 20) * PITCH


L = []
A = L.append
A('\t(symbol "ESP32_NodeMCU-32S"')
A('\t\t(exclude_from_sim no)')
A('\t\t(in_bom yes)')
A('\t\t(on_board yes)')
A('\t\t(in_pos_files yes)')
A('\t\t(duplicate_pin_numbers_are_jumpers no)')
A('\t\t(property "Reference" "A"')
A('\t\t\t(at 0 28 0)')
A('\t\t\t(show_name no)')
A('\t\t\t(do_not_autoplace no)')
A('\t\t\t(effects (font (size 1.27 1.27)))')
A('\t\t)')
A('\t\t(property "Value" "ESP32_NodeMCU-32S"')
A('\t\t\t(at 0 -28 0)')
A('\t\t\t(show_name no)')
A('\t\t\t(do_not_autoplace no)')
A('\t\t\t(effects (font (size 1.27 1.27)))')
A('\t\t)')
A('\t\t(property "Footprint" "ignitor:ESP32_NodeMCU-32S"')
A('\t\t\t(at 0 0 0)')
A('\t\t\t(show_name no)')
A('\t\t\t(do_not_autoplace no)')
A('\t\t\t(hide yes)')
A('\t\t\t(effects (font (size 1.27 1.27)))')
A('\t\t)')
A('\t\t(property "Datasheet" "https://component.aithinker.com/_media/esp32/docs/nodemcu-32s_product_specification.pdf"')
A('\t\t\t(at 0 0 0)')
A('\t\t\t(show_name no)')
A('\t\t\t(do_not_autoplace no)')
A('\t\t\t(hide yes)')
A('\t\t\t(effects (font (size 1.27 1.27)))')
A('\t\t)')
A('\t\t(property "Description" "ESP32-WROOM-32 dev board module, DIP-38, 2.54mm, socketed (NodeMCU-32S / 38-pin clone)"')
A('\t\t\t(at 0 0 0)')
A('\t\t\t(show_name no)')
A('\t\t\t(do_not_autoplace no)')
A('\t\t\t(hide yes)')
A('\t\t\t(effects (font (size 1.27 1.27)))')
A('\t\t)')
A('\t\t(property "ki_keywords" "ESP32 WROOM-32 NodeMCU devkit module"')
A('\t\t\t(at 0 0 0)')
A('\t\t\t(show_name no)')
A('\t\t\t(do_not_autoplace no)')
A('\t\t\t(hide yes)')
A('\t\t\t(effects (font (size 1.27 1.27)))')
A('\t\t)')
A('\t\t(property "ki_description" "ESP32-WROOM-32 development board module, 38-pin DIP header, socketed"')
A('\t\t\t(at 0 0 0)')
A('\t\t\t(show_name no)')
A('\t\t\t(do_not_autoplace no)')
A('\t\t\t(hide yes)')
A('\t\t\t(effects (font (size 1.27 1.27)))')
A('\t\t)')

# ---- graphics unit (0_1) ----
A('\t\t(symbol "ESP32_NodeMCU-32S_0_1"')
A('\t\t\t(rectangle')
A('\t\t\t\t(start %s %s)' % (f(-BODY_HX), f(25.4)))
A('\t\t\t\t(end %s %s)' % (f(BODY_HX), f(-25.4)))
A('\t\t\t\t(stroke (width 0.254) (type default))')
A('\t\t\t\t(fill (type background))')
A('\t\t\t)')
# USB end marker (bottom)
A('\t\t\t(rectangle')
A('\t\t\t\t(start -3.81 -25.4)')
A('\t\t\t\t(end 3.81 -27.94)')
A('\t\t\t\t(stroke (width 0.254) (type default))')
A('\t\t\t\t(fill (type none))')
A('\t\t\t)')
A('\t\t\t(text "USB"')
A('\t\t\t\t(at 0 -26.67 0)')
A('\t\t\t\t(effects (font (size 1.016 1.016))))')
# antenna end marker (top)
A('\t\t\t(polyline')
A('\t\t\t\t(pts (xy -10.16 25.4) (xy -7.62 27.94) (xy 7.62 27.94) (xy 10.16 25.4))')
A('\t\t\t\t(stroke (width 0.254) (type default))')
A('\t\t\t\t(fill (type none))')
A('\t\t\t)')
A('\t\t\t(text "ANT"')
A('\t\t\t\t(at 0 26.67 0)')
A('\t\t\t\t(effects (font (size 1.016 1.016))))')
A('\t\t)')

# ---- pins unit (1_1) ----
A('\t\t(symbol "ESP32_NodeMCU-32S_1_1"')
for n in range(1, 39):
    name, etype = P[n]
    y = pin_y(n)
    if n <= 19:
        x, ang = -(BODY_HX + PIN_LEN), 0
    else:
        x, ang = (BODY_HX + PIN_LEN), 180
    hide = " hide" if etype == "no_connect" else ""
    A('\t\t\t(pin %s line (at %s %s %d) (length %s)%s' % (etype, f(x), f(y), ang, f(PIN_LEN), hide))
    A('\t\t\t\t(name "%s"' % name)
    A('\t\t\t\t\t(effects (font (size 1.27 1.27))))')
    A('\t\t\t\t(number "%d"' % n)
    A('\t\t\t\t\t(effects (font (size 1.27 1.27))))')
    A('\t\t\t)')
A('\t\t)')

A('\t)')

new_sym = "\n".join(L) + "\n"

txt = open(LIB, encoding="utf-8").read()
if '"ESP32_NodeMCU-32S"' in txt:
    raise SystemExit("symbol already present, aborting")

# append before the final closing paren of the (kicad_symbol_lib ...) form
idx = txt.rstrip().rfind("\n)")
if idx < 0:
    raise SystemExit("could not locate closing paren")
txt = txt[: idx + 1] + new_sym + txt[idx + 1 :]
open(LIB, "w", encoding="utf-8", newline="\n").write(txt)
print("appended ESP32_NodeMCU-32S symbol to", LIB)
print("file size now", len(txt), "bytes")
