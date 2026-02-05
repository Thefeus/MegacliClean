"""
Indicadores Numerológicos para Mega-Sena

Módulo com 2 indicadores focados em padrões numerológicos:
1. SomaDigitos - Soma simples dos dígitos (não-recursiva)
2. PadraoModular - Análise de restos (mod 4, mod 7, mod 11)

Autor: MegaCLI v4.0
Data: 27/12/2024
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from collections import Counter


def calcular_soma_digitos(historico: pd.DataFrame,
                           numeros: List[int]) -> float:
    """
    Soma de todos os dígitos individuais (não-recursiva).
    Exemplo: 23 = 2+3 = 5, 58 = 5+8 = 13
    
    Diferente de RaizDigital que é recursivo (23 → 5, 58 → 13 → 4)
    
    Args:
        historico: DataFrame
        numeros: Lista de 6 números
        
    Returns:
        Score 0-100 baseado no padrão histórico de somas
    """
    def soma_digitos_numero(n):
        return sum(int(d) for d in str(n))
    
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Calcular soma de dígitos para cada sorteio histórico
    somas_historicas = []
    
    for _, row in historico.iterrows():
        nums = [int(row[col]) for col in ball_cols if pd.notna(row[col])]
        soma_total = sum(soma_digitos_numero(n) for n in nums)
        somas_historicas.append(soma_total)
    
    # Estatísticas
    media = np.mean(somas_historicas)
    desvio = np.std(somas_historicas)
    
    # Calcular para o jogo proposto
    soma_jogo = sum(soma_digitos_numero(n) for n in numeros)
    
    # Score baseado em quão próximo está da média
    if desvio > 0:
        z_score = abs((soma_jogo - media) / desvio)
        
        # Dentro de 1 desvio padrão = bom
        if z_score < 0.5:
            score = 100
        elif z_score < 1.0:
            score = 90 - (z_score - 0.5) * 20
        elif z_score < 1.5:
            score = 70 - (z_score - 1.0) * 20
        elif z_score < 2.0:
            score = 50 - (z_score - 1.5) * 20
        else:
            score = max(30 - (z_score - 2.0) * 10, 10)
    else:
        score = 50.0
    
    return min(max(score, 0), 100)


def calcular_padrao_modular(historico: pd.DataFrame,
                             numeros: List[int]) -> float:
    """
    Análise de restos de divisão por diferentes módulos.
    Módulos testados: 4, 7, 11
    
    Complementa Div3, Div6, Div9
    
    Args:
        historico: DataFrame
        numeros: Lista de 6 números
        
    Returns:
        Score 0-100 baseado na distribuição modular
    """
    modulos = [4, 7, 11]
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Para cada módulo, calcular distribuição histórica dos restos
    distribuicoes_historicas = {mod: Counter() for mod in modulos}
    
    for _, row in historico.iterrows():
        nums = [int(row[col]) for col in ball_cols if pd.notna(row[col])]
        
        for mod in modulos:
            restos = [n % mod for n in nums]
            distribuicoes_historicas[mod].update(restos)
    
    # Calcular score para o jogo proposto
    score = 0
    
    for mod in modulos:
        restos_jogo = Counter([n % mod for n in numeros])
        dist_hist = distribuicoes_historicas[mod]
        
        # Total de ocorrências
        total = sum(dist_hist.values())
        
        # Para cada resto presente no jogo
        for resto, count in restos_jogo.items():
            # Frequência esperada deste resto
            freq_esperada = dist_hist.get(resto, 0) / total if total > 0 else 1/mod
            
            # Quantos números com este resto temos
            # Frequência esperada normalizada: ~6/mod números com cada resto
            nums_esperados = 6 / mod
            
            # Score baseado em quão próximo está do esperado
            if count <= nums_esperados * 1.5:
                score += count * (freq_esperada * 100)
            else:
                # Penalidade por ter muitos números com mesmo resto
                score += count * (freq_esperada * 50)
        
        # Bonus por diversidade de restos
        num_restos_diferentes = len(restos_jogo)
        if num_restos_diferentes >= mod - 1:  # Quase todos os restos
            score += 10
        elif num_restos_diferentes >= mod // 2:
            score += 5
    
    # Normalizar score (máximo teórico: ~300)
    score_normalizado = (score / 300) * 100
    
    return min(max(score_normalizado, 0), 100)


def criar_todos_indicadores_numerologicos(historico: pd.DataFrame,
                                          numeros: List[int]) -> Dict[str, float]:
    """
    Calcula todos os 2 indicadores numerológicos de uma vez.
    
    Args:
        historico: DataFrame com histórico completo
        numeros: Lista de 6 números para análise
        
    Returns:
        Dict com scores de cada indicador
    """
    return {
        'SomaDigitos': calcular_soma_digitos(historico, numeros),
        'PadraoModular': calcular_padrao_modular(historico, numeros)
    }
