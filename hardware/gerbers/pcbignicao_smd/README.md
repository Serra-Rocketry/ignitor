# PCB Ignição SMD — arquivos de fabricação (revisão 2.2)

Versão com componentes SMD e **ESP32 NodeMCU-32S** no lugar do Raspberry Pi Pico.

## Arquivos

| Arquivo | Uso |
| --- | --- |
| `pcbignicao_smd_jlcpcb.zip` | Gerbers + drill — upload na JLCPCB |
| `jlcpcb-bom.csv` | BOM para a montagem (só SMD) |
| `jlcpcb-cpl.csv` | Pick-and-place para a montagem (só SMD) |
| `pcbignicao_smd-bom.csv` | BOM completa, incluindo os THT |
| `pcbignicao_smd-pos.csv` | Posições completas (todos os footprints) |

## Especificação

| Parâmetro | Valor |
| --- | --- |
| Dimensões | 85 × 70 mm |
| Camadas | 2 |
| Espessura | 1,6 mm |
| Cobre | 1 oz |
| Menor trilha | 0,2 mm |
| Via | 0,8 / 0,4 mm (padrão) e 0,6 / 0,3 mm (sinal) |
| Vias GND | 6 (4 funcionais em trilha + 2 de amarração do plano) |
| Fiduciais | 3 × FID1..FID3 (1 mm cobre, 2 mm máscara) |
| Furos de fixação | 4 × M3 (3,2 mm, NPTH) |

## Como pedir

1. Gerbers em <https://cart.jlcpcb.com/quote> — 2 camadas, 1,6 mm
2. Ative **PCB Assembly → Economic**
3. Suba `jlcpcb-bom.csv` e `jlcpcb-cpl.csv`
4. **Confira na pré-visualização de posicionamento** os itens abaixo — a
   convenção de rotação da JLCPCB difere da do KiCad em alguns encapsulamentos:

   | Item | Encapsulamento | O que conferir |
   | --- | --- | --- |
   | U2, U3 (PC817C) | SOP-4 | Pino 1 / orientação (offset típico ±90°) |
   | D3, D5 | SMA | Catodo (offset típico 180°) |
   | D4 | SOD-123 | Catodo |
   | D1, D2 | LED 0805 | Polaridade |
   | R1..R7, C1, C2 | 0805 | Simétricos, sem risco |

5. **Não** inclua no BOM/CPL: A1 (ESP32), U1 (RA-02), J3..J13 — são THT e você
   solda depois.

## Montagem híbrida — o que você solda

| Ref | Componente | Observação |
| --- | --- | --- |
| A1 | ESP32 NodeMCU-32S | Socketado em 2× 1×19 fêmea — troca em segundos |
| U1 | Módulo LoRa RA-02 | Sobre o adaptador THT, 2× 8 pinos. **Antena antes de energizar** |
| J3, J4 | Buzzer (+) e (−) | Terminais |
| J5, J6 | Botão NO / COM | Terminais do botão |
| J7 | EXT_PWR 5 V | Entrada, protegida por D3 |
| J8 | RELÉ | VCC=VSYS, GND, IN (módulo 5 V ativo em baixo) |
| J9 | LED_BTN | |
| J10 | ARM | Jumper físico de armar |
| J11 | OLED | I2C |
| J12 | EXPANSÃO | 6 GPIO + 3,3 V + GND |
| J13 | SAÍDA IGNIÇÃO | Pinos 1+2 = contato NO do relê, 3+4 = BAT− |

## ⚠️ Aviso sobre o header de expansão J12

Os pinos EXP2, EXP3, EXP4 e EXP5 são **pinos de strapping** do ESP32
(GPIO2, GPIO15, GPIO0 e GPIO12). Funcionam como I/O normal depois do boot, mas
**não podem ser puxados para o nível errado durante o reset** — em especial o
EXP4 (GPIO0), que em nível baixo entra em modo de download.

Deixe-os soltos (ou em alta impedância) na energização.

## Mapa de pinos do ESP32

| Rede | GPIO | Rede | GPIO |
| --- | --- | --- | --- |
| LORA_SCK | 18 | LED_BTN_K | 27 |
| LORA_MISO | 19 | BUZZ | 14 |
| LORA_MOSI | 23 | BTN | 13 |
| LORA_NSS | 5 | CONT_A / CONT_B | 34 / 35 *(só entrada)* |
| LORA_RST | 17 | RELE_ARM | 32 |
| LORA_DIO0 | 16 | SDA / SCL | 21 / 22 |
| LED_Y / LED_R | 25 / 26 | 3,3 V | 3V3 (pino 1) |
| EXP1..EXP6 | 4, 2, 15, 0, 12, 33 | VSYS | 5V (pino 19) |

## Alimentação

```
EXT_5V ──[ D3 SS14 ]── VSYS ── pino 5V do ESP32 ── AMS1117 do módulo ── 3,3 V
                                                                        │
                              RA-02, PC817, LEDs, OLED ────────────────┘
```

O regulador do próprio módulo ESP32 gera os 3,3 V (500 mA), o que cobre o
RA-02 (~120 mA em transmissão) com folga.

## Plano de terra

Zona GND nas duas faces com conexão **sólida** (não alívio térmico) nos pads —
recomendado para montagem por refluxo. Sem malha de costura: o plano fecha com
as 4 vias funcionais de GND e 2 vias de amarração (24 vias no total, contra
406 na revisão 2.0; as centenas de vias de costura foram eliminadas nas
revisões 2.1 e 2.2).

> Nota: as ilhas de cobre que sobraram perto de J9/J11 estão amarradas ao plano
> com 2 vias de ponte e o DRC fecha com 0 itens desconectados.
