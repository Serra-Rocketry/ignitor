import os

OUT = r"hardware\kicad\shared\lib\ignitor.pretty\ESP32_NodeMCU-32S.kicad_mod"

# Ai-Thinker NodeMCU-32S : 25.4 (W) x 48.3 (H) mm, DIP-38, 2.54mm pitch header
# DIP numbering: pin 1 top-left, down to 19 bottom-left, 20 bottom-right, up to 38 top-right
ROW_X = 11.43          # +-11.43 -> 22.86mm between rows
PITCH = 2.54
Y_TOP = 22.86          # (19-1)*2.54/2 = 22.86
PAD_D = 1.7
DRILL = 1.0

DESCR = (
    "Ai-Thinker NodeMCU-32S ESP32 dev board, DIP-38, 2.54mm header, module 25.4x48.3mm, "
    "pin rows 22.86mm apart. DIP numbering: 1=3V3 top-left down to 19=5V bottom-left, "
    "20=GPIO6 bottom-right up to 38=GND top-right. Socketed with 2x 1x19 female headers "
    "(1.0mm drill). Placed so the micro-USB is at the -Y end and the WROOM-32 PCB antenna "
    "at the +Y end (keep copper out of the antenna area)."
)


def pad_xy(n):
    if 1 <= n <= 19:
        return (-ROW_X, Y_TOP - (n - 1) * PITCH)
    return (ROW_X, -Y_TOP + (n - 20) * PITCH)


def f(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return s if s else "0"


L = []
A = L.append
A('(footprint "ESP32_NodeMCU-32S"')
A('\t(version 20260206)')
A('\t(generator "ignitor")')
A('\t(generator_version "10.0")')
A('\t(layer "F.Cu")')
A('\t(descr "%s")' % DESCR)
A('\t(tags "ESP32 NodeMCU-32S WROOM-32 devkit module socket")')
A('\t(attr through_hole)')

A('\t(property "Reference" "A"')
A('\t\t(at 0 -28.5 0)')
A('\t\t(layer "F.SilkS")')
A('\t\t(effects')
A('\t\t\t(font')
A('\t\t\t\t(size 1 1)')
A('\t\t\t\t(thickness 0.15)')
A('\t\t\t)')
A('\t\t)')
A('\t)')
A('\t(property "Value" "ESP32_NodeMCU-32S"')
A('\t\t(at 0 -31 0)')
A('\t\t(layer "F.Fab")')
A('\t\t(effects')
A('\t\t\t(font')
A('\t\t\t\t(size 1 1)')
A('\t\t\t\t(thickness 0.15)')
A('\t\t\t)')
A('\t\t)')
A('\t)')
A('\t(property "Datasheet" "https://component.aithinker.com/_media/esp32/docs/nodemcu-32s_product_specification.pdf"')
A('\t\t(at 0 0 0)')
A('\t\t(unlocked yes)')
A('\t\t(layer "F.Fab")')
A('\t\t(hide yes)')
A('\t\t(effects')
A('\t\t\t(font')
A('\t\t\t\t(size 1.27 1.27)')
A('\t\t\t\t(thickness 0.15)')
A('\t\t\t)')
A('\t\t)')
A('\t)')
A('\t(property "Description" "ESP32-WROOM-32 dev board module, DIP-38, socketed"')
A('\t\t(at 0 0 0)')
A('\t\t(unlocked yes)')
A('\t\t(layer "F.Fab")')
A('\t\t(hide yes)')
A('\t\t(effects')
A('\t\t\t(font')
A('\t\t\t\t(size 1.27 1.27)')
A('\t\t\t\t(thickness 0.15)')
A('\t\t\t)')
A('\t\t)')
A('\t)')

HX, HY = 12.7, 24.15
SX, SY = 12.45, 23.9

A('\t(fp_rect (start %s %s) (end %s %s)' % (f(-SX), f(-SY), f(SX), f(SY)))
A('\t\t(stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS")')
A('\t\t(uuid "00000000-0000-0000-0000-00000000e001"))')

# antenna-side corner brackets (top / +Y)
for idx, sx in enumerate((-1, 1)):
    A('\t(fp_line (start %s %s) (end %s %s)' % (f(sx * SX), f(SY - 11.9), f(sx * SX), f(SY)))
    A('\t\t(stroke (width 0.12) (type solid)) (layer "F.SilkS")')
    A('\t\t(uuid "00000000-0000-0000-0000-00000000e1%02d"))' % idx)
    A('\t(fp_line (start %s %s) (end %s %s)' % (f(sx * SX), f(SY), f(sx * (SX - 5.0)), f(SY)))
    A('\t\t(stroke (width 0.12) (type solid)) (layer "F.SilkS")')
    A('\t\t(uuid "00000000-0000-0000-0000-00000000e2%02d"))' % idx)

A('\t(fp_text user "ANT"')
A('\t\t(at 0 20.5 0)')
A('\t\t(layer "F.SilkS")')
A('\t\t(effects (font (size 1 1) (thickness 0.15))))')
A('\t(fp_text user "USB"')
A('\t\t(at 0 -21.9 0)')
A('\t\t(layer "F.SilkS")')
A('\t\t(effects (font (size 1 1) (thickness 0.15))))')
A('\t(fp_text user "CPU"')
A('\t\t(at 0 -2 0)')
A('\t\t(layer "F.Fab")')
A('\t\t(effects (font (size 0.8 0.8) (thickness 0.12))))')

A('\t(fp_poly (pts (xy %s %s) (xy %s %s) (xy %s %s) (xy %s %s))' % (
    f(-SX), f(SY - 2.0), f(-SX + 2.0), f(SY - 1.0), f(-SX), f(SY), f(-SX), f(SY - 2.0)))
A('\t\t(stroke (width 0.12) (type solid)) (fill yes) (layer "F.SilkS")')
A('\t\t(uuid "00000000-0000-0000-0000-00000000e300"))')

A('\t(fp_rect (start %s %s) (end %s %s)' % (f(-HX), f(-HY), f(HX), f(HY)))
A('\t\t(stroke (width 0.05) (type solid)) (fill none) (layer "F.Fab")')
A('\t\t(uuid "00000000-0000-0000-0000-00000000f001"))')
A('\t(fp_rect (start -3.7 %s) (end 3.7 %s)' % (f(-HY - 2.6), f(-HY)))
A('\t\t(stroke (width 0.05) (type solid)) (fill none) (layer "F.Fab")')
A('\t\t(uuid "00000000-0000-0000-0000-00000000f002"))')

A('\t(fp_rect (start -13.3 %s) (end 13.3 %s)' % (f(-HY - 3.6), f(HY + 0.5)))
A('\t\t(stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd")')
A('\t\t(uuid "00000000-0000-0000-0000-00000000fd01"))')

for n in range(1, 39):
    x, y = pad_xy(n)
    shape = "rect" if n == 1 else "circle"
    A('\t(pad "%d" thru_hole %s (at %s %s) (size %s %s)' % (n, shape, f(x), f(y), f(PAD_D), f(PAD_D)))
    A('\t\t(drill %s) (layers "*.Cu" "*.Mask")' % f(DRILL))
    A('\t\t(uuid "00000000-0000-0000-0000-0000000%05d"))' % (1000 + n))

A(')')

txt = "\n".join(L) + "\n"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(txt)
print("written:", OUT, len(txt), "bytes,", len(L), "lines")
