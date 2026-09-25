# PCB Comando — arquivos de fabricação (revisão 1.2)

## Arquivos

| Arquivo | Camada |
| --- | --- |
| `pcbcomando-F_Cu.gtl` | Cobre, face superior |
| `pcbcomando-B_Cu.gbl` | Cobre, face inferior |
| `pcbcomando-F_Mask.gts` | Máscara de solda, face superior |
| `pcbcomando-B_Mask.gbs` | Máscara de solda, face inferior |
| `pcbcomando-F_Silkscreen.gto` | Serigrafia, face superior |
| `pcbcomando-B_Silkscreen.gbo` | Serigrafia, face inferior |
| `pcbcomando-Edge_Cuts.gm1` | Contorno da placa |
| `pcbcomando.drl` | Furos (Excellon, mm, absoluto) |
| `pcbcomando-job.gbrjob` | Metadados Gerber X2 |
| `pcbcomando_jlcpcb.zip` | Pacote pronto para upload |

## Especificação de fabricação

| Parâmetro | Valor |
| --- | --- |
| Dimensões | 60 × 58 mm |
| Camadas | 2 |
| Espessura | 1,6 mm |
| Cobre | 1 oz |
| Via | 0,8 / 0,4 mm (costura) e 0,6 / 0,3 mm (sinal) |
| Furo mínimo | 0,3 mm (via) |
| Menor trilha | 0,2 mm |
| Menor anel anular | 0,15 mm |

## Ordem sugerida na JLCPCB

1. Suba `pcbcomando_jlcpcb.zip` em <https://cart.jlcpcb.com/quote>
2. 2 camadas, 1,6 mm, **sem** montagem (a placa é THT e é soldada à mão)

## Detalhes de montagem

- **A1 (Raspberry Pi Pico)** — módulo soquetado (2× 20 pinos).
- **U1 (RA-02)** — adaptador THT plugável (2×8, 2,54 mm). **Conectar a antena
  IPEX antes de energizar.**
- **J3/J4** — buzzer (+) e (−).
- **J5/J6** — botão momentâneo NO / COM.
- **J7** — entrada EXT_PWR 5 V (protegida por D3).

## Pinagem do Pico (revisada na 1.2)

| Sinal | GPIO | Sinal | GPIO |
| --- | --- | --- | --- |
| LORA_MISO | GP0 | LED_Y | GP11 |
| LORA_NSS | GP1 | LED_R | GP12 |
| LORA_SCK | GP2 | BTN | GP13 |
| LORA_MOSI | GP3 | BUZZ | GP19 |
| LORA_RST | GP4 | LORA_DIO0 | GP15 |
| LED de link | GP25 (onboard) | | |

## Plano de terra

Zona GND nas duas faces, com **12 vias de costura** (22 vias no total),
alívio térmico nos pads THT para facilitar a solda manual.
