# Sistema Especialista de Triagem de Resíduos — Fuzzy

Versão fuzzy do projeto original em `../Sistema_Especialista_de_Triagem_de_Resíduos-Níveis`. O domínio continua sendo a triagem de resíduos sólidos urbanos, mas as faixas rígidas de contaminação e umidade foram substituídas por um **controlador Mamdani**, implementado com `scikit-fuzzy`.

O resultado é mais apropriado para situações limítrofes: um resíduo com 34% de contaminação não muda abruptamente de destino ao passar para 35%; as regras dos termos linguísticos vizinhos participam com graus diferentes.

## Domínio e premissas

O sistema recebe o material, a contaminação (%) e a umidade (%). Para materiais recicláveis (`plastico`, `papel`, `vidro` e `metal`), o controlador estima a **destinação da fração reciclável**. Materiais perigosos (`pilha`, `bateria`, `eletronico`, `lampada`, `remedio`) sempre seguem para logística reversa, e `organico` sempre segue para compostagem. Essas duas exceções permanecem explícitas porque são regras de segurança e de sanidade, não uma decisão gradual de qualidade.

| Variável | Papel no domínio | Termos linguísticos | Justificativa |
|---|---|---|---|
| `contaminacao` (0–100%) | Entrada | baixa, média, alta | Sujidade ou mistura com outros materiais reduz o aproveitamento do lote. |
| `umidade` (0–100%) | Entrada | seca, moderada, alta | A água degrada fibras, aumenta o peso e pode inviabilizar a separação e a reciclagem. |
| `destinacao` (0–100) | Saída | rejeito, triagem, reciclagem | Representa a qualidade/rota mais adequada do material reciclável. |

As funções de pertinência se sobrepõem: por exemplo, uma contaminação de 30% pode ser parcialmente **baixa** e **média**. Essa sobreposição representa incerteza de inspeção e evita cortes artificiais.

## Arquitetura

```text
material + contaminação + umidade
              |
              +--> perigoso  --> logística reversa (regra de segurança)
              +--> orgânico  --> compostagem (regra de domínio)
              +--> reciclável --> Mamdani: fuzzificação
                                  --> 9 regras
                                  --> agregação + centroide
                                  --> rejeito / triagem / reciclagem
```

O controlador usa inferência **Mamdani**, conjunção `AND` pelo mínimo, agregação das consequências e defuzzificação pelo **centroide** (comportamento padrão do `scikit-fuzzy`). A execução também mostra quais regras contribuíram e sua intensidade.

## Base de regras fuzzy

A base contém as nove combinações possíveis das três faixas de cada entrada. Assim, todo o espaço de entrada é coberto sem lacunas.

| Regra | Se contaminação é | E umidade é | Então destinação é |
|---|---|---|---|
| R01 | baixa | seca | reciclagem |
| R02 | baixa | moderada | triagem |
| R03 | baixa | alta | rejeito |
| R04 | média | seca | reciclagem |
| R05 | média | moderada | triagem |
| R06 | média | alta | rejeito |
| R07 | alta | seca | rejeito |
| R08 | alta | moderada | rejeito |
| R09 | alta | alta | rejeito |

Após a defuzzificação, o escore operacional é interpretado como: **70–100 reciclável**, **40–69 triagem/limpeza** e **0–39 rejeito**. Esses limites são uma política de encaminhamento; a inferência anterior é gradual.

## Instalação e execução

O artefato principal é o notebook autocontido [Triagem_Residuos_Fuzzy.ipynb](Triagem_Residuos_Fuzzy.ipynb). Abra-o no Jupyter Notebook, JupyterLab ou Google Colab e execute as células na ordem. A primeira célula instala todas as dependências necessárias; portanto, o notebook não depende de nenhum arquivo `.py` para funcionar.

Para executar localmente, requer Python 3.10 ou superior e Jupyter:

```bash
cd Sistema_Especialista_de_Triagem_de_Resíduos-Fuzzy
python -m venv .venv
```

Ative o ambiente virtual no Windows:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
jupyter notebook Triagem_Residuos_Fuzzy.ipynb
```

No Google Colab, envie o arquivo `Triagem_Residuos_Fuzzy.ipynb`, abra-o e execute as células na ordem. Não é necessário instalar ou importar arquivos adicionais.

## Verificação

A própria célula **Verificação programática** do notebook confirma que há nove regras e percorre uma grade de contaminação e umidade de 0% a 100%, verificando que existe pelo menos uma regra ativa em cada ponto testado. A célula de demonstração reproduz PET limpa, papel molhado e pilha usada.

## Comparação com o projeto original por níveis

| Aspecto | Projeto original (regras por níveis) | Esta versão fuzzy |
|---|---|---|
| Representação | Limites rígidos, como `contaminacao < 20` | Termos linguísticos com sobreposição |
| Decisão perto do limite | Pode mudar de uma classe para outra por 1 ponto percentual | Combina as interpretações vizinhas gradualmente |
| Conflitos | `salience` e `NOT(Estado())` definem uma única regra vencedora | Várias regras podem contribuir simultaneamente; centroide compõe a saída |
| Complexidade | Simples para regras exatas, mas cresce com exceções e faixas intermediárias | Exige projetar funções de pertinência e validar a base, mas expressa incerteza de modo mais natural |
| Poder de expressividade | Ótimo para prioridades absolutas (por exemplo, resíduos perigosos) | Melhor para qualidade contínua e casos ambíguos |

Por isso, o projeto mantém regras clássicas apenas para segurança e compostagem, enquanto aplica fuzzy à decisão que realmente é gradual: a qualidade de recuperação dos recicláveis.

## Estrutura

```text
Sistema_Especialista_de_Triagem_de_Resíduos-Fuzzy/
├── Triagem_Residuos_Fuzzy.ipynb  # entrega principal, autocontida e executável
├── requirements.txt
├── README.md
└── ROTEIRO_VIDEO.md
```

## Equipe

- Yuri Silva Bezerra de Lima
