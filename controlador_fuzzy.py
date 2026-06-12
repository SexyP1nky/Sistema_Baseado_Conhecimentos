"""
Controlador Fuzzy Mamdani para Triagem de Resíduos
====================================================

Este módulo implementa um controlador fuzzy tipo Mamdani usando scikit-fuzzy
para determinar a urgência de tratamento de resíduos sólidos urbanos.

Domínio:
--------
O sistema avalia dois fatores críticos na triagem de resíduos:
1. Contaminação (%): nível de sujeira/impurezas no material
2. Umidade (%): teor de água presente no resíduo

A saída é a Urgência de Tratamento, que indica quão rapidamente o resíduo
deve ser processado para evitar degradação ou contaminação cruzada.

Justificativa dos Termos Linguísticos:
--------------------------------------
- Contaminação: baixa (<30%), média (20-70%), alta (>60%)
  → Materiais pouco contaminados podem aguardar; altamente contaminados exigem ação imediata
  
- Umidade: seca (<30%), úmida (20-70%), molhada (>60%)
  → Alta umidade acelera degradação (especialmente em papel/orgânicos)
  
- Urgência: baixa, média, alta
  → Define prioridade na fila de tratamento

Autor: Yuri Silva Bezerra de Lima
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def criar_sistema_fuzzy():
    """
    Cria e configura o sistema de inferência fuzzy Mamdani.
    
    Retorna:
        ctrl.ControlSystemSimulation: Sistema configurado pronto para simulação
    """
    
    # ========================================================================
    # VARIÁVEIS DE ENTRADA E SAÍDA
    # ========================================================================
    
    # Entrada 1: Contaminação (0-100%)
    contaminacao = ctrl.Antecedent(np.arange(0, 101, 1), 'contaminacao')
    
    # Entrada 2: Umidade (0-100%)
    umidade = ctrl.Antecedent(np.arange(0, 101, 1), 'umidade')
    
    # Saída: Urgência de Tratamento (0-100%)
    urgencia = ctrl.Consequent(np.arange(0, 101, 1), 'urgencia')
    
    # ========================================================================
    # FUNÇÕES DE PERTINÊNCIA (3 termos por variável)
    # ========================================================================
    
    # Contaminação: triangular para simplicidade e eficiência computacional
    contaminacao['baixa'] = fuzz.trimf(contaminacao.universe, [0, 0, 30])
    contaminacao['media'] = fuzz.trimf(contaminacao.universe, [20, 50, 80])
    contaminacao['alta'] = fuzz.trimf(contaminacao.universe, [60, 100, 100])
    
    # Umidade: triangular para consistência
    umidade['seca'] = fuzz.trimf(umidade.universe, [0, 0, 30])
    umidade['umida'] = fuzz.trimf(umidade.universe, [20, 50, 80])
    umidade['molhada'] = fuzz.trimf(umidade.universe, [60, 100, 100])
    
    # Urgência: triangular para saída suave
    urgencia['baixa'] = fuzz.trimf(urgencia.universe, [0, 0, 40])
    urgencia['media'] = fuzz.trimf(urgencia.universe, [30, 50, 70])
    urgencia['alta'] = fuzz.trimf(urgencia.universe, [60, 100, 100])
    
    # ========================================================================
    # BASE DE REGRAS FUZZY (9 regras - cobrindo todo espaço de entradas)
    # ========================================================================
    
    # Regra 1: Se contaminação é baixa E umidade é seca → urgência baixa
    regra1 = ctrl.Rule(contaminacao['baixa'] & umidade['seca'], 
                       urgencia['baixa'])
    
    # Regra 2: Se contaminação é baixa E umidade é úmida → urgência baixa
    regra2 = ctrl.Rule(contaminacao['baixa'] & umidade['umida'], 
                       urgencia['baixa'])
    
    # Regra 3: Se contaminação é baixa E umidade é molhada → urgência média
    regra3 = ctrl.Rule(contaminacao['baixa'] & umidade['molhada'], 
                       urgencia['media'])
    
    # Regra 4: Se contaminação é média E umidade é seca → urgência baixa
    regra4 = ctrl.Rule(contaminacao['media'] & umidade['seca'], 
                       urgencia['baixa'])
    
    # Regra 5: Se contaminação é média E umidade é úmida → urgência média
    regra5 = ctrl.Rule(contaminacao['media'] & umidade['umida'], 
                       urgencia['media'])
    
    # Regra 6: Se contaminação é média E umidade é molhada → urgência alta
    regra6 = ctrl.Rule(contaminacao['media'] & umidade['molhada'], 
                       urgencia['alta'])
    
    # Regra 7: Se contaminação é alta E umidade é seca → urgência média
    regra7 = ctrl.Rule(contaminacao['alta'] & umidade['seca'], 
                       urgencia['media'])
    
    # Regra 8: Se contaminação é alta E umidade é úmida → urgência alta
    regra8 = ctrl.Rule(contaminacao['alta'] & umidade['umida'], 
                       urgencia['alta'])
    
    # Regra 9: Se contaminação é alta E umidade é molhada → urgência alta
    regra9 = ctrl.Rule(contaminacao['alta'] & umidade['molhada'], 
                       urgencia['alta'])
    
    # ========================================================================
    # CRIAR SISTEMA DE CONTROLE
    # ========================================================================
    
    sistema_controle = ctrl.ControlSystem([
        regra1, regra2, regra3, regra4, regra5, 
        regra6, regra7, regra8, regra9
    ])
    
    return sistema_controle


def simular_controlador(contaminacao_valor, umidade_valor, sistema=None):
    """
    Simula o controlador fuzzy para valores específicos de entrada.
    
    Args:
        contaminacao_valor (float): Percentual de contaminação (0-100)
        umidade_valor (float): Percentual de umidade (0-100)
        sistema (ctrl.ControlSystem, optional): Sistema pré-criado
    
    Returns:
        dict: Resultados da simulação incluindo urgência e detalhes
    """
    if sistema is None:
        sistema = criar_sistema_fuzzy()
    
    # Criar instância de simulação
    simulador = ctrl.ControlSystemSimulation(sistema)
    
    # Atribuir valores de entrada
    simulador.input['contaminacao'] = contaminacao_valor
    simulador.input['umidade'] = umidade_valor
    
    # Computar saída
    simulador.compute()
    
    # Obter resultado
    urgencia_resultado = simulador.output['urgencia']
    
    # Determinar categoria linguística dominante
    if urgencia_resultado <= 40:
        categoria = 'baixa'
    elif urgencia_resultado <= 70:
        categoria = 'media'
    else:
        categoria = 'alta'
    
    return {
        'contaminacao': contaminacao_valor,
        'umidade': umidade_valor,
        'urgencia_valor': urgencia_resultado,
        'urgencia_categoria': categoria,
        'simulador': simulador
    }


def visualizar_funcoes_pertinencia(sistema=None):
    """
    Gera visualizações das funções de pertinência (requer matplotlib).
    
    Args:
        sistema (ctrl.ControlSystem, optional): Sistema pré-criado
    """
    try:
        import matplotlib.pyplot as plt
        
        if sistema is None:
            sistema = criar_sistema_fuzzy()
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        
        # Plotar função de pertinência da contaminação
        contaminacao_var = sistema.variables['contaminacao']
        contaminacao_var.view(ax=axes[0])
        axes[0].set_title('Contaminação')
        
        # Plotar função de pertinência da umidade
        umidade_var = sistema.variables['umidade']
        umidade_var.view(ax=axes[1])
        axes[1].set_title('Umidade')
        
        # Plotar função de pertinência da urgência
        urgencia_var = sistema.variables['urgencia']
        urgencia_var.view(ax=axes[2])
        axes[2].set_title('Urgência de Tratamento')
        
        plt.tight_layout()
        plt.savefig('funcoes_pertinencia.png', dpi=150)
        print("Gráfico salvo como 'funcoes_pertinencia.png'")
        plt.show()
        
    except ImportError:
        print("matplotlib não disponível. Instale com: pip install matplotlib")


def testar_casos_exemplo():
    """
    Executa testes com casos exemplo demonstrativos.
    """
    print("=" * 60)
    print("TESTES DO CONTROLADOR FUZZY MAMDANI")
    print("=" * 60)
    
    sistema = criar_sistema_fuzzy()
    
    # Casos de teste representativos
    casos = [
        (10, 15, "Resíduo limpo e seco"),
        (25, 45, "Resíduo levemente contaminado e úmido"),
        (75, 80, "Resíduo muito contaminado e molhado"),
        (50, 50, "Resíduo com contaminação e umidade médias"),
        (90, 20, "Resíduo muito contaminado mas seco"),
        (15, 85, "Resíduo limpo mas muito molhado"),
        (65, 55, "Resíduo contaminado e úmido"),
        (40, 30, "Resíduo moderadamente contaminado e seco"),
        (80, 70, "Resíduo crítico: alta contaminação e molhado"),
    ]
    
    print("\nExecutando casos de teste:\n")
    
    for contaminacao, umidade, descricao in casos:
        resultado = simular_controlador(contaminacao, umidade, sistema)
        print(f"Caso: {descricao}")
        print(f"  Entradas: contaminação={contaminacao}%, umidade={umidade}%")
        print(f"  Saída: urgência={resultado['urgencia_valor']:.2f}% ({resultado['urgencia_categoria']})")
        print()
    
    print("=" * 60)
    print("Todos os testes concluídos!")
    print("=" * 60)


if __name__ == '__main__':
    # Executar testes quando o script é chamado diretamente
    testar_casos_exemplo()
    
    # Opcional: visualizar funções de pertinência
    # visualizar_funcoes_pertinencia()
