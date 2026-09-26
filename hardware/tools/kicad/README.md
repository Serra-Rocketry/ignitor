# Ferramental de PCB do projeto Ignitor

Scripts Python usados para posicionar, rotear e acabar as placas dos 4 projetos
KiCad. Todos dependem do **Python embutido do KiCad 10**, que é o único que tem
o módulo `pcbnew`:

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" -u <script>.py <args>
```

Use **`-u`** sempre. Sem ele o processo morre no meio sem imprimir nada, porque
a saída fica no buffer.

Nenhum script depende do KiCad aberto: todos trabalham direto nos arquivos.

---

## posicionar/

| Script | O que faz |
| --- | --- |
| `placer.py` | Posicionador por recozimento simulado. Usa a geometria real dos courtyards (via API do KiCad) e o netlist para minimizar comprimento de trilha. Recebe um JSON com `board` (área útil), `fixed` (itens travados, por centro do courtyard) e `edge` (itens empurrados para a borda). |
| `place.py` | Aplica uma tabela de posições e reporta sobreposições de courtyard e distância à borda. Modos: `check`, `apply`, `delete`. |
| `dump_fps.py` | Lista todos os footprints com posição, tamanho e rotação. |
| `dump_one.py` | Detalha um footprint: pads (locais e absolutos), drills, redes. |
| `check_fps.py` | Confere se todo footprint referenciado no esquema existe na biblioteca do KiCad. |
| `probe_area.py` | Lista trilhas e pads num raio em volta de um ponto — diagnóstico de área congestionada. |

## rotear/

| Script | O que faz |
| --- | --- |
| `route.py` | Pipeline completo: exporta DSN, roda o Freerouting, importa o SES, refaz o preenchimento. |
| `widen.py` | Engrossa as trilhas de alimentação (VSYS, EXT_5V) para uma largura dada. |
| `strip_sexp.py` | Remove blocos S-expression de nível 1 do `.kicad_pcb` (ex.: `zone`). Evita a API SWIG, que degrada após a primeira remoção. |
| `batch.py` / `evaluate.py` | Rodam o pipeline em várias sementes / avaliam placas já roteadas. **Não rodar o `batch`** — ele dispara o Freerouting N vezes e abre N janelas Java. |

## plano-terra/

| Script | O que faz |
| --- | --- |
| `smd_zones2.py` | Cria as zonas GND (retângulo cheio) e preenche. |
| `fix_zones.py` | Ajusta clearance, espessura mínima e conexão dos pads (SÓLIDA para montagem por refluxo). |
| `stitch.py` | Vias de costura numa grade, com região e passo configuráveis. |
| `island_via.py` | Acha um ponto livre **dentro do polígono preenchido** e coloca uma via + trilha curta — resolve pad preso em ilha. |
| `fix_gnd.py` | Alternativa ao anterior: procura um caminho livre em 8 direções e coloca stub + via. |
| `sliver_via.py` | Tenta via no centro de regiões pequenas. **Cuidado**: confunde furo com ilha, use só como diagnóstico. |
| `zones.py` | Lista as zonas com camada, clearance e área. Diagnóstico. |

## acabamento/

| Script | O que faz |
| --- | --- |
| `silk.py` | Reposiciona os designadores testando 8 direções × 5 distâncias contra pads, serigrafia vizinha e borda. Segunda passada com texto menor para os que sobram. |
| `silk2.py` | Move os campos Value para F.Fab e os textos de footprint que caem sobre pads. |
| `fiducials.py` | Acha posições livres automaticamente e coloca 3 fiduciais (1 mm cobre / 2 mm máscara). |

## versao-smd/

| Script | O que faz |
| --- | --- |
| `build_smd_pcb.py` | Constrói a PCB da versão SMD a partir da THT + netlist: troca footprints, reatribui redes por nome, remove trilhas. |
| `swap_fp.py` | Troca os footprints no **esquema** (propriedade Footprint por Reference). |
| `gen_mcu_esp.py` | Gera a folha do MCU com o ESP32 NodeMCU-32S: 27 fios, 27 rótulos globais, no-connects, power flags. |
| `gen_esp32_fp.py` / `gen_esp32_sym.py` | Geram o footprint (25,4 × 48,3 mm, DIP-38, fileiras 22,86 mm) e o símbolo de 38 pinos. |
| `update_parts.py` | Atualiza MPN/LCSC/BOM Comments de cada componente no esquema. |
| `dump_mcu.py` | Mostra rótulos globais, fios e power symbols de uma folha. |

## fabricacao/

| Script | O que faz |
| --- | --- |
| `gen_jlc.py` | Gera o BOM e o CPL no formato da JLCPCB, só com os SMD, expandindo `R1-R3` em `R1,R2,R3`. |
| `check_fps.py` | (duplicado) valida footprints contra a biblioteca. |

## limpeza/

| Script | O que faz |
| --- | --- |
| `dedup_mh.py` | Remove footprints duplicados (mesma referência e mesma posição). |
| `fix_nc.py` | Remove flags de no-connect sobre pontos que têm fio. Valida o balanceamento de parênteses antes de gravar. |
| `set_netclasses.py` | Escreve as netclasses (Default, Power, IGN) nos `.kicad_pro`. |
| `set_spokes.py` | Baixa o `min_resolved_spokes` para 1 (senão o DRC acusa `starved_thermal`). |

## diagnostico/

Scripts de sondagem da API, testes pontuais e consulta à LCSC. Servem para
responder "esse método existe?" e "o que tem nesse ponto?" sem escrever nada novo.

---

# Armadilhas (não redescobrir)

| Sintoma | Causa e solução |
| --- | --- |
| `LoadBoard` chamado 2× no mesmo processo devolve objeto quebrado (`SwigPyObject`) | Use **processos separados**. Leia tudo que precisa **antes** de mutar o board. |
| `GetDrawings()` / `Zone.GetLayerSet().Seq()` falham após mutação | Idem: colete a informação primeiro. |
| Processo morre sem imprimir nada | Faltou o `-u` (saída sem buffer). |
| `zone.SetOutline()` não pega na primeira chamada | Edite `zone.Outline()` no lugar. |
| Zona com furo trava o `ZONE_FILLER` | Use polígono em "L" (sem furo) ou duas zonas. |
| Freerouting abre janela Java e trava | Rode **uma vez** com `-de`/`-do`/`-mp`. Nunca em lote. |
| GND roteado como trilha faz o roteador não terminar (30 min+) | Mantenha o GND como **plano**, não como rede roteável. |
| `sch export netlist --format` recusa `kicad` | O valor é **`kicadsexpr`**. |
| ERC acusa biblioteca do projeto não encontrada | É o **acento** em "Área de Trabalho" no caminho. Cosmético — não afeta o design. |
| Renomear projeto só trocando o nome dos arquivos perde todos os designadores | Use a ferramenta `rename_project`, que reescreve `(project "nome")` em todas as folhas. |
| `starved_thermal` no DRC | Baixe `min_resolved_spokes` para 1 no `.kicad_pro`. |
| `PCB_VIA::GetWidth` sem argumento dá assert | Use `GetWidth(pcbnew.F_Cu)`. |
| `(via` não aparece em `GetClass() == "PCB_TRACK"` | Vias são classe `PCB_VIA`. Trate as duas ao montar listas de obstáculos. |
