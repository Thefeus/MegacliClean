"""
Indicador de Teoria dos Ciclos - MegaCLI v6.1

A Teoria dos Ciclos monitora o intervalo necessário para que todas as 60 dezenas
sejam sorteadas. Os números que "faltam" para fechar o ciclo atual têm
estatisticamente maior probabilidade de saída.

Autor: MegaCLI Team
Data: 23/01/2026
"""

import pandas as pd
from typing import List, Dict, Any

def analisar_ciclo_atual(df_historico: pd.DataFrame) -> Dict[str, Any]:
    """
    Analisa o ciclo atual da Mega-Sena.
    
    Args:
        df_historico: DataFrame com todos os sorteios
        
    Returns:
        Dict com status do ciclo e números faltantes
    """
    todos_numeros = set(range(1, 61))
    numeros_sorteados_ciclo = set()
    inicio_ciclo = None
    
    # Iterar do último para o primeiro sorteio
    for idx, row in df_historico.iloc[::-1].iterrows():
        numeros = {row[f'Bola{i}'] for i in range(1, 7)}
        
        # Se o ciclo estava vazio, este é o início (do fim para o começo)
        # Na verdade, precisamos encontrar onde o ciclo COMEÇOU.
        # Definição de ciclo: Período entre a saída da 1ª dezena até a 60ª dezena.
        # Para achar os faltantes, vamos voltando no tempo acumulando números até completar 60.
        # O momento que completou 60 no passado fecha o ciclo anterior.
        # O que temos agora é o ciclo ABERTO.
        
        numeros_sorteados_ciclo.update(numeros)
        
        if len(numeros_sorteados_ciclo) == 60:
            # Ciclo fechou aqui (no passado)
            # Então o ciclo ATUAL começou no sorteio SEGUINTE a este
            inicio_ciclo = row['Concurso'] + 1
            break
    
    # Se não fechou 60, o ciclo começou no concurso 1 ou dados insuficientes,
    # mas para lógica de faltantes, pegamos o que temos.
    
    # Recalcular faltantes baseado no ciclo atual REAL
    # Se achamos onde fechou o anterior, o atual é do (idx_fechamento + 1) até fim.
    # Se não achamos, o atual é tudo.
    
    if inicio_ciclo:
        df_ciclo_atual = df_historico[df_historico['Concurso'] >= inicio_ciclo]
    else:
        df_ciclo_atual = df_historico
        inicio_ciclo = df_historico.iloc[0]['Concurso']
        
    numeros_no_ciclo = set()
    for _, row in df_ciclo_atual.iterrows():
        numeros_no_ciclo.update({row[f'Bola{i}'] for i in range(1, 7)})
        
    faltantes = list(todos_numeros - numeros_no_ciclo)
    
    return {
        'inicio_ciclo': int(inicio_ciclo),
        'tamanho_atual': len(df_ciclo_atual),
        'numeros_sorteados': len(numeros_no_ciclo),
        'numeros_faltantes': sorted(faltantes),
        'quantidade_faltante': len(faltantes),
        'status': 'Fechado' if not faltantes else 'Aberto'
    }

def calcular_score_ciclo(numero: int, info_ciclo: Dict[str, Any]) -> float:
    """
    Calcula score baseado no ciclo.
    
    Args:
        numero: Número a avaliar
        info_ciclo: Info retornada por analisar_ciclo_atual
        
    Returns:
        Score (100 se faltante, 0 se já saiu)
    """
    if numero in info_ciclo['numeros_faltantes']:
        # Quanto menos números faltam, maior a pressão
        qnt_falta = info_ciclo['quantidade_faltante']
        # Se faltam muitos (ex: 50), peso é menor. Se faltam poucos (ex: 3), peso é enorme.
        # Mas simplificando: Faltante = Alta Prioridade.
        return 100.0
    return 0.0
