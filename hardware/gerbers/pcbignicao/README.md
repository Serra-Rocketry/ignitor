# PCB Ignição — arquivos de fabricação (revisão 2.0)

## Arquivos

| Arquivo | Camada |
| --- | --- |
| `pcbignicao-F_Cu.gtl` | Cobre, face superior |
| `pcbignicao-B_Cu.gbl` | Cobre, face inferior |
| `pcbignicao-F_Mask.gts` | Máscara de solda, face superior |
| `pcbignicao-B_Mask.gbs` | Máscara de solda, face inferior |
| `pcbignicao-F_Silkscreen.gto` | Serigrafia, face superior |
| `pcbignicao-B_Silkscreen.gbo` | Serigrafia, face inferior |
| `pcbignicao-Edge_Cuts.gm1` | Contorno da placa |
| `pcbignicao.drl` | Furos (Excellon, mm, absoluto) |
| `pcbignicao-job.gbrjob` | Metadados Gerber X2 |
| `pcbignicao_jlcpcb.zip` | Pacote pronto para upload |

## Especificação de fabricação

| Parâmetro | Valor |
| --- | --- |
| Dimensões | 66,05 × 64,05 mm |
| Camadas | 2 |
| Espessura | 1,6 mm |
| Cobre | 1 oz |
| Furo mínimo | 0,3 mm (via) |
| Menor trilha | 0,2 mm (sinal) / 0,35 mm (alimentação) |
| Menor anel anular | 0,15 mm |
| Cobre–borda | ≥ 0,5 mm |
| Furos de fixação | 4 × M3 (3,2 mm, NPTH) |

Tudo dentro das capacidades **standard** da JLCPCB (trilha/espaço mín. 0,127 mm,
via mín. 0,45/0,2 mm, anel mín. 0,125 mm).

## Ordem sugerida na JLCPCB

1. Suba `pcbignicao_jlcpcb.zip` em <https://cart.jlcpcb.com/quote>
2. 2 camadas, 1,6 mm, **sem** montagem (a placa é THT e é soldada à mão)
3. Peça o **stencil emoldurado** junto se for soldar em pasta (opcional para THT)

## Detalhes de montagem

- **A1 (Raspberry Pi Pico)** — módulo em 2 fileiras de 20 pinos, soquetado ou soldado direto.
  O conector micro-USB fica virado para a borda inferior.
- **U1 (RA-02)** — adaptador THT plugável (2×8, 2,54 mm). **Conectar a antena
  IPEX antes de energizar.**
- **J10 (ARM)** — jumper físico de armar. Sem ele o relê não pode ser acionado.
- **J13 (SAÍDA IGNIÇÃO)** — pinos 1+2 = contato NO do relê, pinos 3+4 = BAT−.
  A corrente do ignitor circula por fiação **externa**, não pela placa.
- **J8 (RELÉ)** — VCC=VSYS, GND, IN. Módulo de relê 5 V ativo em nível baixo.
- **J7 (EXT_PWR)** — entrada 5 V, protegida por D3 (1N5819).

## Plano de terra

Zona GND contínua nas duas faces, com **110 vias de costura** distribuídas
automaticamente (124 vias no total). Alívio térmico nos pads THT para facilitar
a solda manual.
