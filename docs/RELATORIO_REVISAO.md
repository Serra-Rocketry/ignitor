# Relatório — Revisão de hardware e firmware (2026-09)

Revisão executada nas branches `feat/pcb-smd-e-organizacao` (hardware) e
`feat/firmware-esp32` (firmware), ambas a partir da `dev`. A `main` não foi
tocada e nada foi enviado (`push`) para o remoto.

## Resumo dos commits

### `feat/pcb-smd-e-organizacao`

| Commit | Passo | Conteúdo |
| --- | --- | --- |
| `f4991c0` | 0 | Consolida projetos de ignição THT/SMD, move gerbers para `hardware/gerbers/`, exceções de CSV no `.gitignore`, ignora `*.bak`/`*.kicad_prl` |
| `dfdba0f` | 1 | Títulos/rev 2.0 do projeto SMD (era cópia do THT) |
| `461abd8` | 1 | Sufixo (THT) nos títulos do projeto de ignição THT |
| `5722519` | 1 | Comando hierarquizado: `alimentacao`, `mcu_pico`, `radio_lora`, `interface` |
| `730f454` | 2 | Vias de costura THT 112 → 43 (rev 1.3) |
| `0391487` | 2 | Vias de costura SMD 388 → 101 (rev 2.1) + 2 vias de ponte |
| `ca783c6` | 3 | Paths de folha dos footprints sincronizados (THT/SMD) |
| `b5f0227` | 3 | Pacote de fabricação do comando padronizado (rev 1.2) + README |
| — | 2b | Vias de costura SMD eliminadas: 101 → 6 GND (rev 2.2) |

### `feat/firmware-esp32`

| Commit | Passo | Conteúdo |
| --- | --- | --- |
| `2762fd9` | 5 | Pinagem do firmware alinhada ao hardware revisado |

## Passo 1 — Organização dos esquemas

- THT e SMD já eram hierárquicos e espelhados; apenas os títulos foram
  normalizados (o SMD era cópia fiel do THT, inclusive comentários).
- O comando estava plano (12 componentes, 14 nets) e foi dividido em 4
  subfolhas, com as coordenadas ancoradas na grade de 1,27 mm.
- **Validação:** netlist exportado antes/depois em todos os projetos —
  componentes e nets idênticos (comando 14/41, THT 29/47, SMD 29/50).

## Passo 2 — Redução das vias de costura

| Placa | Antes | Depois | Espaçamento | DRC |
| --- | --- | --- | --- | --- |
| Ignição THT (rev 1.3) | 124 (112 GND) | 55 (43 GND) | ~6–8 mm | 0 desconexões |
| Ignição SMD (rev 2.2) | 406 (388 GND) | 24 (6 GND) | sem costura | 0 desconexões |
| Comando THT | 22 | 22 (já esparso) | ~4–10 mm | 0 desconexões |

- As vias funcionais (em trilha) foram preservadas; o critério da THT foi
  distância mínima de 6 mm na borda e 6–8 mm no miolo.
- Na SMD, a pedido, **toda** a malha de costura foi removida (rev 2.2): o
  plano GND fecha com as 4 vias funcionais e **2 vias de ponte** que amarram
  as ilhas de cobre perto de J9/J11. O DRC confirma 0 itens desconectados e
  nenhuma violação nova de cobre.
- Gerbers, drill e pacotes JLCPCB regenerados; READMEs corrigidos, incluindo a
  inversão de tamanhos de via (0,8/0,4 = costura; 0,6/0,3 = sinal).

## Passo 3 — Comando THT (rev 1.2)

- Pacote de fabricação padronizado como as ignições: extensões Protel, drill
  único, job Gerber X2 e zip para JLCPCB (os arquivos antigos `.gbr` e drills
  NPTH/PTH separados foram removidos).
- Criado `hardware/gerbers/pcbcomando/README.md` (especificação, pinagem,
  plano de terra).
- Paths de folha dos footprints sincronizados com a hierarquia nova.
- `hardware/README.md` atualizado: pinagem real do comando, da ignição THT
  (DIO0 = GP21, LED do botão, SDA/SCL, continuidade) e da ignição SMD
  (ESP32 NodeMCU-32S).

### Paridade esquema ↔ PCB (pendência conhecida)

| Placa | Antes | Depois | Resíduo |
| --- | --- | --- | --- |
| Comando THT | 43 | 43 | 29 pads NC/auto-net + 14 campos (MPN etc.) |
| Ignição THT | 80 | 76 | idem |
| Ignição SMD | 82 | 75 | idem |

A sincronização de paths reduziu parte dos avisos, mas o restante exige o
comando **Ferramentas → Atualizar PCB a partir do esquema** no KiCad (GUI),
que também preenche os campos de BOM (MPN, fabricante) nos footprints. São
avisos de severidade *warning*; a conectividade elétrica e o DRC de cobre
estão limpos nas 3 placas. **Recomendação:** abrir os 3 projetos no KiCad,
rodar o update e regravar os gerbers se algo mudar.

## Passo 4 — Comando SMD (não executado)

Decisão aprovada: manter o **Raspberry Pi Pico**. O projeto é uma placa nova
inteira e ficou pendente, com o seguinte plano proposto:

1. Criar `hardware/kicad/pcbignicao/pcbcomando_smd/` copiando a estrutura
   hierárquica do comando THT.
2. Migrar passivos para 0805 e registrar a lib compartilhada `ignitor`
   (o README da lib já lista o projeto).
3. Layout 2 camadas (mesmas dimensões do THT, 60 × 58 mm) e DRC limpo.
4. Gerbers + BOM/CPL JLCPCB + README, rev 1.0, e validação de netlist como
   nos demais projetos.

## Passo 5 — Firmware (`feat/firmware-esp32`)

Pinagem conferida contra o netlist das 3 placas — **0 divergências**:

| Estação | MCU | LoRa (SCK/MISO/MOSI/NSS/RST/DIO0) | Atuadores |
| --- | --- | --- | --- |
| Comando THT | Pico | 2/0/3/1/4/15 | LED_Y 11, LED_R 12, BTN 13, BUZZ 19, link 25 |
| Ignição THT | Pico | 2/0/3/1/4/21 | RELE 26 (ativo baixo), BUZZ 19, LED_R 12, LED_Y 11 |
| Ignição SMD | NodeMCU-32S | 18/19/23/5/17/16 | RELE 32 (ativo baixo), BUZZ 14, LED_R 26, LED_Y 25, link 2 |

- `estacao_ignicao_esp.py` foi reescrito para o **ESP32 NodeMCU-32S** (antes
  era ESP32-C3, incompatível com a placa SMD); SPI passa a usar o VSPI (id 2).
- `estacao_ignicao.py` (Pico THT): DIO0 = GP21, relê ativo em baixo, driver
  nativo por padrão e retry de boot do LoRa.
- `estacao_comando.py`: as alterações pendentes eram todas incorretas
  (DIO0 = 21, LED_BTN inexistente e docstring corrompido); foram revertidas e
  o arquivo ficou idêntico ao commit anterior.

### Pendências de firmware

- A placa SMD tem `LED_BTN_K` (GPIO27) e `BTN` (GPIO13) que o firmware de
  ignição ainda não usa — o comando é quem arma, então não é bloqueante.
- O README da estação de comando cita um LED de botão que não existe na placa
  (removido da tabela de pinagem).

## Estado final

- `feat/pcb-smd-e-organizacao` com 10 commits; `feat/firmware-esp32` com 1.
- Working tree limpo; nenhum push; `main` intacta na `e5424de`.
- Pendências: Passo 4 (comando SMD) e paridade via GUI nos 3 projetos.
