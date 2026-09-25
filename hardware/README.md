# Hardware - Serra Rocketry Ignitor

## Arquitetura

O sistema possui duas estacoes independentes conectadas por LoRa 433 MHz:

- Estacao de Comando: operada pelo usuario em area segura.
- Estacao de Ignicao: fica proxima ao foguete e aciona o ignitor.

## Lista de Componentes (BOM)

| Item | Qtd | Aplicacao | Observacao |
| --- | --- | --- | --- |
| Raspberry Pi Pico | 1 | Estacao de Comando | MCU RP2040 |
| ESP32 NodeMCU-32S | 1 | Estacao de Ignicao (SMD) | MCU principal de ignicao |
| Modulo LoRa SX1278 433 MHz | 2 | Comando e Ignicao | Um por estacao |
| Antena LoRa 433 MHz | 2 | Comando e Ignicao | Obrigatoria antes de energizar |
| LED amarelo 5 mm | 2 | Status de link | Com resistor |
| LED vermelho 5 mm | 2 | Status de ignicao | Com resistor |
| Buzzer ativo | 2 | Feedback sonoro | Um por estacao |
| Botao de ignicao momentaneo | 1 | Comando | Segurar por 5 s |
| Rele ou MOSFET | 1 | Ignicao | Saida para ignitor |
| TP4056 com protecao | 2 | Carga de bateria | Um por estacao |
| Bateria (Li-ion/LiPo) | 2 | Alimentacao | Definir capacidade |
| Resistores 220 ohms | 4 | LEDs | Dois por estacao |

## Pinagem

### Estacao de Comando - Raspberry Pi Pico

| Pino | Funcao |
| --- | --- |
| GP0 | LoRa MISO |
| GP1 | LoRa CS (NSS) |
| GP2 | LoRa SCK |
| GP3 | LoRa MOSI |
| GP4 | LoRa RESET |
| GP15 | LoRa DIO0 |
| GP11 | LED amarelo |
| GP12 | LED vermelho |
| GP13 | Botao de ignicao |
| GP19 | Buzzer |
| GP25 | LED onboard (link) |

> O buzzer toca uma melodia via PWM ao final de um ciclo de ignicao bem-sucedido.

### Estacao de Ignicao - ESP32 NodeMCU-32S (placa SMD rev 2.1)

Pinagem da `pcbignicao_smd` (footprint DIP-38):

| Pino | Funcao | Pino | Funcao |
| --- | --- | --- | --- |
| GPIO18 | LoRa SCK | GPIO27 | LED do botao (LED_BTN_K) |
| GPIO19 | LoRa MISO | GPIO14 | Buzzer |
| GPIO23 | LoRa MOSI | GPIO13 | Botao (BTN) |
| GPIO5 | LoRa CS (NSS) | GPIO34 / 35 | CONT_A / CONT_B (so entrada) |
| GPIO17 | LoRa RESET | GPIO32 | RELE_ARM (rele ativo em baixo) |
| GPIO16 | LoRa DIO0 | GPIO21 / 22 | SDA / SCL (OLED) |
| GPIO25 / 26 | LED_Y / LED_R | GPIO4, 2, 15, 0, 12, 33 | EXP1..EXP6 |
| GPIO2 | LED interno de link | 5V / 3V3 | VSYS / 3,3 V |

> Cuidado: EXP3..EXP5 (GPIO15, GPIO0, GPIO12) sao pinos de strapping — nao
> podem ser puxados para o nivel errado durante o reset.

### Estacao de Ignicao - Raspberry Pi Pico (variante THT rev 1.3)

| Pino | Funcao |
| --- | --- |
| GP0 | LoRa MISO |
| GP1 | LoRa CS (NSS) |
| GP2 | LoRa SCK |
| GP3 | LoRa MOSI |
| GP4 | LoRa RESET |
| GP6 / GP7 | SDA / SCL (OLED) |
| GP8 / GP9 | CONT_A / CONT_B (continuidade) |
| GP11 | LED amarelo |
| GP12 | LED vermelho |
| GP16 | LED do botao (LED_BTN_K) |
| GP19 | Buzzer |
| GP21 | LoRa DIO0 |
| GP26 | Rele/MOSFET (ignitor) |
| GP25 | LED onboard (link) |

## Sequencia de Operacao

1. Comando envia `ARM_CONFIRMED` enquanto o botao e mantido.
2. Ignicao confirma com `ACK` e inicia contagem de 5 s.
3. Se houver `ABORT` ou perda de sinal > 500 ms, ciclo e cancelado.
4. Ao final da contagem, saida de ignicao ativa por 2 s.
5. Ignicao envia `IGNITION_COMPLETE`.

## Seguranca

- Sempre conectar antena LoRa antes de energizar.
- Usar botao momentaneo (sem trava).
- Testar com carga dummy antes de ignitor real.
- Manter distancia minima de 10 m em testes operacionais.

## Galeria (Tamanho Padronizado)

Todas as imagens abaixo usam largura padrao de 320 px para manter consistencia visual no documento.

<!-- markdownlint-disable MD033 -->

### Raspberry Pi Pico (Comando)

<img src="./images/pipico.png" width="320" alt="Raspberry Pi Pico" />

### Modulo LoRa SX1278

<img src="./images/lora.png" width="320" alt="Modulo LoRa SX1278" />

### Botao de Energia

<img src="./images/power-button.avif" width="320" alt="Botao de energia" />

### Botao de Ignicao

<img src="./images/ignition-button.png" width="320" alt="Botao de ignicao" />

### Esquematico - Estacao de Comando

<img src="./images/schematics/estacao-comando_bb.png" width="320" alt="Esquematico da estacao de comando" />

### Esquematico - Estacao de Ignicao

<img src="./images/schematics/estacao-ignicao_bb.png" width="320" alt="Esquematico da estacao de ignicao" />

<!-- markdownlint-enable MD033 -->

## Pastas de Hardware

- [3d_models](./3d_models): modelos 3D dos cases.
- [fritzing](./fritzing): arquivos de esquematico/layout.
- [gerbers](./gerbers): arquivos de fabricacao PCB.
- [images](./images): imagens e esquemas.
