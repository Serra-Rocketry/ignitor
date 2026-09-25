# Biblioteca compartilhada do projeto Ignitor

Biblioteca unica de simbolos e footprints usada pelos quatro projetos KiCad:

| Projeto | Caminho |
| --- | --- |
| Ignicao THT | `hardware/kicad/pcbignicao/pcbignicao/` |
| Ignicao SMD | `hardware/kicad/pcbignicao/pcbignicao_smd/` |
| Comando THT | `hardware/kicad/pcbignicao/pcbcomando/` |
| Comando SMD | `hardware/kicad/pcbignicao/pcbcomando_smd/` |

Os projetos registram esta biblioteca com o apelido **`ignitor`**:

```text
sym-lib-table -> ${KIPRJMOD}/../../shared/lib/ignitor.kicad_sym
fp-lib-table  -> ${KIPRJMOD}/../../shared/lib/ignitor.pretty
```

Antes existia uma pasta `lib/` duplicada dentro de cada projeto, o que causava os
erros de ERC `lib_symbol_mismatch` e "biblioteca de simbolos nao encontrada".
Ela foi removida.

## Simbolos

| Simbolo | Uso |
| --- | --- |
| `Ra-02` | Modulo LoRa Ai-Thinker RA-02 (SX1278, 433 MHz, soquete IPEX) |
| `ESP32_NodeMCU-32S` | Modulo ESP32-WROOM-32 em placa de desenvolvimento, DIP-38 |

## Footprints

### `RA-02`

Modulo RA-02 soldado direto na placa. Pads SMD castellated de 2,0 mm de passo,
3,0 x 1,4 mm, estendidos 1,5 mm alem da borda do modulo para facilitar a solda
manual. Modulo real: 17 x 16 mm.

Numeracao dos pads segue o pinout fisico do modulo:

- Coluna esquerda (topo -> base) = pads 1-8: `GND, GND, 3V3, RESET, DIO0, DIO1, DIO2, DIO3`
- Coluna direita (topo -> base) = pads 16-9: `GND, NSS, MOSI, MISO, SCK, DIO5, DIO4, GND`

### `RA-02_THT`

Adaptador plugavel (carrier) para o RA-02, 2 fileiras de 8 pinos, passo 2,54 mm,
fileiras a 25,4 mm, placa de 33 x 24 mm. Corresponde ao projeto
[kevinta893/LoRa-Breakout-Board](https://github.com/kevinta893/LoRa-Breakout-Board).

- Fileira esquerda (topo -> base) = pads 9,10,11,12,13,14,15,16
- Fileira direita (topo -> base) = pads 8,7,6,5,4,3,2,1

> O part de Fritzing original rotula o slot do pino 1 como `ANT` (off-by-one na
> serigrafia). O test point de antena **nao** e levado ao adaptador.

### `ESP32_NodeMCU-32S`

Modulo ESP32-WROOM-32 em placa, soquetado com 2 conectores femea 1x19 (furo 1,0 mm).

Especificacao Ai-Thinker confirmada no datasheet: **25,4 x 48,3 mm (±0,2),
DIP-38, passo 2,54 mm, fileiras a 22,86 mm (0,9")**.

> Cuidado: existem clones de 38 pinos com fileiras a **22,86 mm** (NodeMCU-32S,
> a variante adotada aqui) e a placa oficial ESP32-DevKitC V4, que usa
> **25,4 mm (1,0")**. Sao fisicamente incompativeis entre si. Se trocar de
> modulo, o footprint precisa ser refeito.

Numeracao DIP-38 (pin 1 no topo da fileira esquerda, sentido anti-horario):

| Pino | Sinal | Pino | Sinal | Pino | Sinal | Pino | Sinal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3V3 | 11 | GPIO27 | 21 | GPIO7 (flash) | 31 | GPIO19 |
| 2 | EN | 12 | GPIO14 | 22 | GPIO8 (flash) | 32 | GND |
| 3 | GPIO36 | 13 | GPIO12 | 23 | GPIO15 | 33 | GPIO21 |
| 4 | GPIO39 | 14 | GND | 24 | GPIO2 | 34 | GPIO3 (RX0) |
| 5 | GPIO34 | 15 | GPIO13 | 25 | GPIO0 | 35 | GPIO1 (TX0) |
| 6 | GPIO35 | 16 | GPIO9 (flash) | 26 | GPIO4 | 36 | GPIO22 |
| 7 | GPIO32 | 17 | GPIO10 (flash) | 27 | GPIO16 | 37 | GPIO23 |
| 8 | GPIO33 | 18 | GPIO11 (flash) | 28 | GPIO17 | 38 | GND |
| 9 | GPIO25 | 19 | 5V | 29 | GPIO5 | | |
| 10 | GPIO26 | 20 | GPIO6 (flash) | 30 | GPIO18 | | |

**Uso dos pinos — restricoes**

- `GPIO6` a `GPIO11` (pinos 16-18 e 20-22): ligados a flash SPI, **nao usar**.
  Estao marcados como `no_connect` no simbolo.
- `GPIO34`, `GPIO35`, `GPIO36`, `GPIO39`: **somente entrada**, sem pull-up
  interno. Otimos para ADC, ruins para saida.
- Pinos de strapping `GPIO0`, `GPIO2`, `GPIO12`, `GPIO15`: funcionam como I/O
  normal depois do boot, mas **nao podem ser puxados para o nivel errado durante
  o reset** ou o modulo entra em modo de download. Na placa de ignicao eles
  ficam no header de expansao J12 — a serigrafia avisa.
- `GPIO1` / `GPIO3` (pinos 34/35) sao tambem UART0 (TX/RX) — usar como I/O
  normal so se a serial de debug nao estiver em uso.

**Orientacao mecanica** (importante para RF e para acessar o USB):

- `+Y` = lado da **antena** do WROOM-32 -> manter **sem cobre** embaixo.
- `-Y` = lado do **micro-USB** -> precisa ficar acessivel, virado para a borda.

O footprint ja traz a marcacao `ANT` / `USB`, a seta de pino 1 e um courtyard que
inclui os 2,6 mm do conector USB.
