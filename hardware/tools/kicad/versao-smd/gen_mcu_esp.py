"""Gera mcu_esp32.kicad_sch: folha do MCU com o ESP32 NodeMCU-32S.

Substitui a folha do Pico. A interface com o resto do projeto e feita
exclusivamente por rotulos globais, entao basta manter os mesmos nomes de rede.

Nao altera o resto do projeto.
"""

import re
import uuid

SRC = r"hardware\kicad\pcbignicao\pcbignicao\mcu_pico.kicad_sch"
SYMLIB = r"hardware\kicad\shared\lib\ignitor.kicad_sym"
OUT = r"hardware\kicad\pcbignicao\pcbignicao_smd\mcu_esp32.kicad_sch"

SHEET_UUID = "01bc44fd-6e97-4a31-88f0-c10670563229"
ROOT_UUID = "b6806db8-0023-44ae-8b35-5692cafd6852"
PROJECT = "pcbignicao_smd"

SYM_X, SYM_Y = 105.41, 90.17
HALF_W = 17.78          # distancia da origem do simbolo ate o ponto de conexao do pino
STUB = 5.08
XYP = 22.86

# pino fisico do NodeMCU-32S -> rede
PIN_NET = {
    1: "3.3V",
    5: "CONT_A",
    6: "CONT_B",
    7: "RELE_ARM",
    8: "EXP6",
    9: "LED_Y",
    10: "LED_R",
    11: "LED_BTN_K",
    12: "BUZZ",
    13: "EXP5",
    14: "GND",
    15: "BTN",
    19: "VSYS",
    23: "EXP3",
    24: "EXP2",
    25: "EXP4",
    26: "EXP1",
    27: "LORA_DIO0",
    28: "LORA_RST",
    29: "LORA_NSS",
    30: "LORA_SCK",
    31: "LORA_MISO",
    32: "GND",
    33: "SDA",
    36: "SCL",
    37: "LORA_MOSI",
    38: "GND",
}
# pinos visiveis que ficam soltos -> flag de no-connect
NC_PINS = [2, 3, 4, 34, 35]

# nome da rede -> nome do rotulo (renomeia os antigos GPxx para EXPx)
NET_LABEL = {
    "GP14": "EXP1", "GP15": "EXP2", "GP17": "EXP3",
    "GP18": "EXP4", "GP20": "EXP5", "GP22": "EXP6",
}


def pin_xy(n):
    """Posicao absoluta do ponto de conexao do pino n, no espaco do esquema.

    A biblioteca de simbolos usa +Y para cima; o esquema usa +Y para baixo,
    entao a coordenada Y local e NEGADA ao posicionar no esquema.
    """
    if 1 <= n <= 19:
        local_y = XYP - (n - 1) * 2.54
        return (SYM_X - HALF_W, SYM_Y - local_y)
    local_y = -XYP + (n - 20) * 2.54
    return (SYM_X + HALF_W, SYM_Y - local_y)


def f(v):
    s = "%.4f" % v
    s = s.rstrip("0").rstrip(".")
    return s if s else "0"


def indent(block, extra="\t"):
    return "\n".join(extra + ln if ln.strip() else ln for ln in block.splitlines())


def extract_power_symbols(text):
    """Pega os blocos de 3.3V, GND e PWR_FLAG de dentro de (lib_symbols ...).

    Delimita o bloco lib_symbols por balanceamento de parenteses, senao os
    junction/no_connect que vem depois acabam entrando junto.
    """
    start = text.index("\t(lib_symbols")
    depth = 0
    i = start
    while True:
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                i += 1
                break
        i += 1
    block = text[start:i]
    lines = block.splitlines()
    starts = [k for k, ln in enumerate(lines) if re.match(r'^\t\t\(symbol "', ln)]
    out = {}
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(lines)
        name = re.match(r'^\t\t\(symbol "([^"]+)"', lines[s]).group(1)
        blk = "\n".join(lines[s:e]).rstrip()
        if blk.endswith("\n\t)"):
            blk = blk[:-3].rstrip()
        if blk.count("(") != blk.count(")"):
            raise SystemExit("bloco %s desbalanceado (%d vs %d)" % (name, blk.count("("), blk.count(")")))
        out[name] = blk
    return out


def extract_esp32(text):
    """Pega o simbolo ESP32_NodeMCU-32S da biblioteca compartilhada."""
    i = text.index('\t(symbol "ESP32_NodeMCU-32S"')
    depth = 0
    j = i
    while True:
        ch = text[j]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                j += 1
                break
        j += 1
    block = text[i:j]
    block = block.replace('(symbol "ESP32_NodeMCU-32S"',
                          '(symbol "ignitor:ESP32_NodeMCU-32S"', 1)
    return indent(block, "\t\t")


def sym_instance(lib_id, at, ref, value, uid, extra_hide_value=False):
    x, y = at
    p = []
    p.append("\t(symbol")
    p.append('\t\t(lib_id "%s")' % lib_id)
    p.append("\t\t(at %s %s 0)" % (f(x), f(y)))
    p.append("\t\t(unit 1)")
    p.append("\t\t(exclude_from_sim no)")
    p.append("\t\t(in_bom yes)")
    p.append("\t\t(on_board yes)")
    p.append("\t\t(dnp no)")
    p.append("\t\t(uuid \"%s\")" % uid)
    hid = "\n\t\t\t(hide yes)" if ref.startswith("#") or extra_hide_value else ""
    p.append('\t\t(property "Reference" "%s"' % ref)
    p.append("\t\t\t(at %s %s 0)%s" % (f(x), f(y - 3.5), hid))
    p.append("\t\t\t(effects (font (size 1.27 1.27)))")
    p.append("\t\t)")
    hidv = "\n\t\t\t(hide yes)" if ref.startswith("#") else ""
    p.append('\t\t(property "Value" "%s"' % value)
    p.append("\t\t\t(at %s %s 0)%s" % (f(x), f(y + 30.0), hidv))
    p.append("\t\t\t(effects (font (size 1.27 1.27)))")
    p.append("\t\t)")
    p.append('\t\t(property "Footprint" ""')
    p.append("\t\t\t(at %s %s 0)" % (f(x), f(y)))
    p.append("\t\t\t(hide yes)")
    p.append("\t\t\t(effects (font (size 1.27 1.27)))")
    p.append("\t\t)")
    p.append('\t\t(property "Datasheet" ""')
    p.append("\t\t\t(at %s %s 0)" % (f(x), f(y)))
    p.append("\t\t\t(hide yes)")
    p.append("\t\t\t(effects (font (size 1.27 1.27)))")
    p.append("\t\t)")
    p.append("\t\t(instances")
    p.append('\t\t\t(project "%s"' % PROJECT)
    p.append('\t\t\t\t(path "/%s"' % ROOT_UUID)
    p.append('\t\t\t\t\t(reference "%s")' % ref)
    p.append("\t\t\t\t\t(unit 1)")
    p.append("\t\t\t\t)")
    p.append("\t\t\t)")
    p.append("\t\t)")
    p.append("\t)")
    return "\n".join(p)


def main():
    src = open(SRC, encoding="utf-8").read()
    symlib = open(SYMLIB, encoding="utf-8").read()

    powers = extract_power_symbols(src)
    esp32 = extract_esp32(symlib)

    L = []
    A = L.append
    A("(kicad_sch")
    A("\t(version 20260306)")
    A('\t(generator "eeschema")')
    A('\t(generator_version "10.0")')
    A('\t(uuid "%s")' % SHEET_UUID)
    A('\t(paper "A4")')
    A("\t(title_block")
    A('\t\t(title "Estacao de Ignicao - MCU (ESP32 NodeMCU-32S)")')
    A('\t\t(date "2026-09-24")')
    A('\t\t(rev "2.0")')
    A('\t\t(company "Serra Rocketry")')
    A("\t)")

    A("\t(lib_symbols")
    A(esp32)
    for n in ("PCM_SparkFun-PowerSymbol:3.3V", "PCM_SparkFun-PowerSymbol:GND", "power:PWR_FLAG"):
        A(powers[n])
    A("\t)")

    # fios + rotulos
    wires = []
    labels = []
    for n, net in sorted(PIN_NET.items()):
        px, py = pin_xy(n)
        left = n <= 19
        ex = px - STUB if left else px + STUB
        wires.append(
            "\t(wire\n\t\t(pts\n\t\t\t(xy %s %s) (xy %s %s)\n\t\t)\n\t\t(stroke (width 0) (type default))\n\t\t(uuid \"%s\")\n\t)"
            % (f(px), f(py), f(ex), f(py), uuid.uuid4())
        )
        lab = NET_LABEL.get(net, net)
        rot = 180 if left else 0
        just = "right" if left else "left"
        labels.append(
            '\t(global_label "%s"\n\t\t(shape input)\n\t\t(at %s %s %d)\n\t\t(fields_autoplaced yes)\n'
            '\t\t(effects (font (size 1.27 1.27)) (justify %s))\n\t\t(uuid "%s")\n\t\t(property "Intersheetrefs" "${INTERSHEET_REFS}"\n'
            '\t\t\t(at %s %s %d)\n\t\t\t(hide yes)\n\t\t\t(effects (font (size 1.27 1.27)) (justify %s))\n\t\t)\n\t)'
            % (lab, f(ex), f(py), rot, just, uuid.uuid4(), f(ex), f(py), rot, just)
        )

    A("\n".join(wires))
    A("\n".join(labels))

    # simbolo do MCU
    A(sym_instance("ignitor:ESP32_NodeMCU-32S", (SYM_X, SYM_Y), "A1", "ESP32_NodeMCU-32S", uuid.uuid4()))

    # power symbols + PWR_FLAG nas redes de alimentacao
    n_pwr = 0
    for n, net in sorted(PIN_NET.items()):
        if net not in ("3.3V", "GND"):
            continue
        px, py = pin_xy(n)
        left = n <= 19
        ex = px - STUB if left else px + STUB
        n_pwr += 1
        lib = "PCM_SparkFun-PowerSymbol:" + net
        A(sym_instance(lib, (ex, py), "#PWR1%02d" % n_pwr, net, uuid.uuid4()))

    # PWR_FLAG nas redes de alimentacao que ainda nao tem uma no projeto.
    # A folha Radio_LoRa ja traz um PWR_FLAG no 3.3V.
    ja_tem = {"3.3V"}
    flag_pins = []
    for pin in PIN_NET:
        net = PIN_NET[pin]
        if net in ("3.3V", "VSYS", "GND") and net not in ja_tem:
            ja_tem.add(net)
            flag_pins.append(pin)
    for i, pin in enumerate(flag_pins, start=1):
        px, py = pin_xy(pin)
        ex = px - STUB if pin <= 19 else px + STUB
        A(sym_instance("power:PWR_FLAG", (ex, py), "#FLG1%02d" % i, "PWR_FLAG", uuid.uuid4()))

    # no-connects
    for n in NC_PINS:
        px, py = pin_xy(n)
        A('\t(no_connect\n\t\t(at %s %s)\n\t\t(uuid "%s")\n\t)' % (f(px), f(py), uuid.uuid4()))

    A("\t(embedded_fonts no)")
    A("\t(sheet_instances")
    A('\t\t(path "/"')
    A('\t\t\t(page "1")')
    A("\t\t)")
    A("\t)")
    A(")")

    txt = "\n".join(L) + "\n"
    if txt.count("(") != txt.count(")"):
        raise SystemExit("ABORTADO: parenteses desbalanceados (%d vs %d)" % (txt.count("("), txt.count(")")))
    open(OUT, "w", encoding="utf-8", newline="\n").write(txt)
    print("gerado:", OUT, len(txt), "bytes")
    print("  fios:", len(wires), " rotulos:", len(labels), " nc:", len(NC_PINS), " power:", n_pwr + 2)


if __name__ == "__main__":
    main()
