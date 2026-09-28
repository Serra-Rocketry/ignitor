# Envio JLCPCB — Ignição SMD (rev 2.2)

> **⚠️ Antes de pedir:** o esquema e a PCB já trocaram U2/U3 (PC817) de SOP-4
> para **DIP-4 (THT, solda manual)**. Este pacote ainda é da rev 2.2 com U2/U3
> no BOM/CPL — **remova as linhas de U2/U3 do BOM e do CPL no upload** (ou
> regenere o pacote) para a JLCPCB não montar SOP-4 no lugar errado.

Pacote pronto para o site da JLCPCB. Use **somente** estes 3 arquivos:

| Arquivo | Onde entra no site |
| --- | --- |
| `pcbignicao_smd_jlcpcb.zip` | Fabricação — "Add gerber file" em <https://cart.jlcpcb.com/quote> |
| `jlcpcb-bom.csv` | Montagem — "Add BOM file" |
| `jlcpcb-cpl.csv` | Montagem — "Add CPL file" |

O zip já inclui os gerbers das 2 faces, máscaras, serigrafias, contorno,
furos (`.drl`) e o job Gerber X2.

## Passo a passo

1. **PCB**: suba o zip e configure **2 camadas, 1,6 mm, 1 oz**, cor padrão.
2. Ative **PCB Assembly → Economic** (SMD, lado Top).
3. Suba `jlcpcb-bom.csv` e `jlcpcb-cpl.csv` **sem U2/U3** (ver aviso acima).
4. **Confira na pré-visualização de posicionamento** — a convenção de rotação
   da JLCPCB difere da do KiCad em alguns encapsulamentos:

   | Item | Encapsulamento | O que conferir |
   | --- | --- | --- |
   | D3, D5 | SMA | catodo (offset típico 180°) |
   | D4 | SOD-123 | catodo |
   | D1, D2 | LED 0805 | polaridade |
   | C1, C2, R1..R7 | 0805 | simétricos, sem risco |

5. **Não estão no BOM/CPL** (são THT e você solda depois): A1 (ESP32
   NodeMCU-32S), U1 (RA-02), U2/U3 (PC817 DIP-4) e J3..J13 — a lista completa
   está no `README.md` da pasta acima.

## Especificação

- 85 × 70 mm, 2 camadas, 1,6 mm, 4 furos M3
- Fiduciais FID1..FID3 para a montagem
- Montagem: lado Top, 14 componentes SMD (com U2/U3 fora do BOM/CPL)
- Total de vias: 24 (rev 2.2, sem malha de costura)
