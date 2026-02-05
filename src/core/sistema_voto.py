"""
Sistema de Votação Rastreável - MegaCLI

Inverte a lógica dos indicadores: em vez de apenas validar um jogo pronto,
cada indicador "vota" em um conjunto de números.
Gera rastreabilidade completa de por que um número foi escolhido.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Set
from collections import Counter

# --- Helpers de Indicadores ---
def obter_votos_quadrantes(df_historico: pd.DataFrame) -> List[int]:
    """Retorna números que equilibram os quadrantes baseados no histórico recente."""
    # Lógica simplificada: favorece quadrantes "atrasados" ou equilibrados
    # Por padrão, retorna todos 1-60 mas com peso distribuído se refinado
    return list(range(1, 61))

def obter_votos_primos() -> List[int]:
    return [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59]

def obter_votos_fibonacci() -> List[int]:
    return [1, 2, 3, 5, 8, 13, 21, 34, 55]

def obter_votos_frequencia(df_historico: pd.DataFrame, top_n: int = 30) -> List[int]:
    """Retorna os N números mais frequentes dos últimos 100 jogos."""
    ultimo_ciclo = df_historico.tail(100)
    todos_numeros = []
    for _, row in ultimo_ciclo.iterrows():
        numeros = [row[f'Bola{i}'] for i in range(1, 7)]
        todos_numeros.extend(numeros)
    
    contador = Counter(todos_numeros)
    mais_comuns = [num for num, _ in contador.most_common(top_n)]
    return mais_comuns

def obter_votos_atraso(df_historico: pd.DataFrame, top_n: int = 20) -> List[int]:
    """Retorna os números mais atrasados."""
    todos_numeros = set(range(1, 61))
    atrasos = {}
    
    # Percorrer de trás para frente para achar último sorteio de cada número
    df_invertido = df_historico.iloc[::-1]
    
    for num in todos_numeros:
        count = 0
        encontrou = False
        for _, row in df_invertido.iterrows():
            linha_nums = [row[f'Bola{i}'] for i in range(1, 7)]
            if num in linha_nums:
                encontrou = True
                break
            count += 1
        atrasos[num] = count if encontrou else 1000
    
    # Retorna os top_n mais atrasados
    ordenados = sorted(atrasos.items(), key=lambda x: x[1], reverse=True)
    return [num for num, _ in ordenados[:top_n]]

# Mapeamento de Nome do Indicador -> Função de Voto
MAPA_VOTO_INDICADORES = {
    'Primos': obter_votos_primos,
    'Fibonacci': obter_votos_fibonacci,
    'FrequenciaRelativa': obter_votos_frequencia, # Exemplo genérico
    'FrequenciaMensal': obter_votos_frequencia,
    'Atraso': obter_votos_atraso # Exemplo genérico
    # Adicionar outros conforme necessidade de implementação detalhada
}

def coletar_votos_indicadores(
    df_historico: pd.DataFrame,
    ranking_pesos: List[Dict[str, float]]
) -> Tuple[Dict[int, float], List[Dict]]:
    """
    Coleta votos de todos os indicadores ponderados pelos pesos da IA.
    
    Args:
        df_historico: Base de dados
        ranking_pesos: Lista [{'indicador': 'Nome', 'relevancia': 80.0}, ...]
        
    Returns:
        Tuple:
            - Dict {numero: score_total}
            - List [ {indicador, peso, numeros_votados} ] (Rastreabilidade)
    """
    scores_finais = Counter()
    rastreabilidade = []
    
    # Processar cada indicador do ranking
    for item in ranking_pesos:
        nome_ind = item.get('indicador')
        peso = float(item.get('relevancia', 0))
        
        if peso <= 0:
            continue
            
        numeros_votados = []
        
        # 1. Tentar mapeamento direto específico
        if nome_ind in MAPA_VOTO_INDICADORES:
            func = MAPA_VOTO_INDICADORES[nome_ind]
            # Algumas funções pedem df, outras não
            try:
                numeros_votados = func(df_historico)
            except TypeError:
                numeros_votados = func()
                
        # 2. Logica Genérica (Fallback Inteligente)
        elif 'Frequencia' in nome_ind:
            numeros_votados = obter_votos_frequencia(df_historico, top_n=25)
        elif 'Atraso' in nome_ind:
            numeros_votados = obter_votos_atraso(df_historico, top_n=20)
        else:
            # Padrão para indicadores geométricos/complexos não mapeados ainda:
            # Usa frequência geral como proxy temporário para não zerar participação
            numeros_votados = obter_votos_frequencia(df_historico, top_n=30)
            
        # Adicionar votos ao Score Total
        # Cada número recebe o PESO do indicador como pontos
        for num in numeros_votados:
            scores_finais[num] += peso
            
        # Registrar Rastreabilidade
        rastreabilidade.append({
            'Indicador': nome_ind,
            'Peso_IA': peso,
            'Qtd_Votos': len(numeros_votados),
            'Numeros_Sugeridos': sorted(numeros_votados)
        })
        
    return scores_finais, rastreabilidade

def gerar_analise_intersecao(
    numeros_selecionados: List[int],
    rastreabilidade: List[Dict]
) -> List[Dict]:
    """
    Gera o relatório reverso: Para cada número selecionado, quem votou nele?
    """
    analise_numeros = []
    
    for num in numeros_selecionados:
        votos_recebidos = []
        score_acumulado = 0
        
        for r in rastreabilidade:
            if num in r['Numeros_Sugeridos']:
                votos_recebidos.append(f"{r['Indicador']} ({r['Peso_IA']})")
                score_acumulado += r['Peso_IA']
                
        analise_numeros.append({
            'Numero': num,
            'Score_Total': score_acumulado,
            'Fontes_Voto': ', '.join(votos_recebidos)
        })
        
    return sorted(analise_numeros, key=lambda x: x['Score_Total'], reverse=True)
