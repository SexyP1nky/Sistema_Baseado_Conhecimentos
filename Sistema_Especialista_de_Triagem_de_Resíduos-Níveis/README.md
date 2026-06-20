# Sistema Especialista de Triagem de Resíduos

Sistema de regras para classificar resíduos sólidos urbanos e indicar o destino correto. Desenvolvido com `experta`, um port Python do CLIPS.

Entrada: material, percentual de contaminação e umidade. O motor encadeia três níveis de regras e chega na decisão final: tipo de lixeira + rota de tratamento.

---

## Domínio

A triagem de resíduos tem alguns conflitos não óbvios. Papel reciclável com muita umidade não vale mais do que lixo comum porque as fibras se degradam e contaminam o lote inteiro. Um material tecnicamente reciclável com contaminação acima de 60% vai pro aterro. Resíduos perigosos — pilha, bateria, medicamento — têm tratamento completamente separado, não importa o restante das condições.

O sistema resolve esses conflitos usando `salience` para ordenar qual regra tem prioridade e `NOT(Estado())` para impedir que mais de uma classificação de estado seja aplicada ao mesmo item. As cores de lixeira seguem o padrão CONAMA 275/2001.

---

## Regras

12 regras em 3 níveis de encadeamento:

### Nível 1 — Faixa de contaminação (R01–R03)

Converte o valor numérico de contaminação num nível qualitativo. Disparam com salience 110, antes de todas as regras do Nível 2.

| Regra | Condição | Resultado |

| R01 | contaminacao ≥ 60% | NivelContaminacao = alta |
| R02 | 20% ≤ contaminacao < 60% | NivelContaminacao = media |
| R03 | contaminacao < 20% | NivelContaminacao = baixa |

### Nível 2 — Estado do resíduo (R04–R08)

Depende dos fatos declarados no Nível 1. Quando mais de uma regra se aplica ao mesmo item, o conflito é resolvido por `salience` + `NOT(Estado())`.

| Regra | Salience | Condição | Resultado |

| R04 | 100 | material ∈ {pilha, bateria, eletrônico, lâmpada, remédio} | Estado = perigoso |
| R05 | 90 | material = papel **e** umidade > 50% | Estado = rejeito |
| R06 | 80 | material reciclável **e** NivelContaminacao = alta | Estado = rejeito |
| R07 | 70 | material = orgânico | Estado = compostável |
| R08 | 10 | material reciclável **e** NivelContaminacao = baixa ou média | Estado = reciclável |

### Nível 3 — Destino final (R09–R12)

Lê o `Estado` do Nível 2 e emite a decisão: lixeira + rota de tratamento.

| Regra | Condição | Lixeira | Rota |

| R09 | Estado = reciclável | Varia por material (CONAMA) | coleta seletiva |
| R10 | Estado = compostável | MARROM | compostagem |
| R11 | Estado = rejeito | CINZA | aterro sanitário |
| R12 | Estado = perigoso | LARANJA | logística reversa |

---

## Resolução de conflito

Dois mecanismos são usados em conjunto:

`salience` — define qual regra do Nível 2 dispara primeiro quando o item ativa mais de uma condição. Exemplo concreto: papel com umidade 70% e contaminação 10% satisfaz R05 (salience 90) e R08 (salience 10) ao mesmo tempo. R05 ganha e o papel vai pro rejeito, não pra coleta seletiva.

`NOT(Estado())` — depois que uma regra de estado disparou, as demais não conseguem mais disparar pro mesmo item. Funciona como um mutex: garante que o salience, sozinho, não basta — a segunda regra está bloqueada estruturalmente.

---

## Casos de teste

### Caso 1 — Garrafa PET limpa e seca


material=plastico | contaminacao=5% | umidade=10%


- R03 → NivelContaminacao = baixa
- R08 (salience 10) → Estado = reciclável
- R09 → lixeira VERMELHA, coleta seletiva

**Decisão:** Descartar na lixeira VERMELHA para reciclagem.

---

### Caso 2 — Papel limpo mas molhado (conflito de regras)


material=papel | contaminacao=10% | umidade=70%


- R03 → NivelContaminacao = baixa
- R05 (salience 90) e R08 (salience 10) são ambas aplicáveis; R05 vence e `NOT(Estado())` bloqueia R08
- R11 → lixeira CINZA, aterro sanitário

**Decisão:** Descartar como rejeito (lixeira CINZA).

---

### Caso 3 — Pilha usada


material=pilha | contaminacao=0% | umidade=0%


- R03 → NivelContaminacao = baixa
- R04 (salience 100) → Estado = perigoso, descarta qualquer outra regra de estado
- R12 → lixeira LARANJA, logística reversa

**Decisão:** Levar a ponto de coleta especial (logística reversa).

---

## Como rodar

Abrir `triagem_reciclagem.ipynb` no Google Colab e executar as células em ordem. A primeira célula instala as dependências.

## Equipe

- Yuri Silva Bezerra de Lima
