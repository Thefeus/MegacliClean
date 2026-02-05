"""
Indicadores baseados em Machine Learning para Mega-Sena

Módulo com 3 indicadores focados em técnicas de ML:
1. ScoreAnomalia - Isolation Forest para detectar jogos anormais
2. ProbabilidadeCondicional - P(número | números já no jogo)
3. ImportanciaFeature - Peso de cada número por Random Forest

Autor: MegaCLI v4.0
Data: 27/12/2024
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from collections import Counter


def calcular_score_anomalia(historico: pd.DataFrame,
                             numeros: List[int]) -> float:
    """
    Detecta jogos "anormais" estatisticamente usando conceitos de Isolation Forest.
    
    Um jogo anômalo tem características muito diferentes da maioria:
    - Soma muito alta/baixa
    - Amplitude extrema
    - Todos pares ou todos ímpares
    - Todos em um quadrante
    
    Args:
        historico: DataFrame
        numeros: Lista de 6 números
        
    Returns:
        Score 0-100 (maior = mais "normal", menor = anômalo)
    """
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Extrair features de cada sorteio histórico
    features_historicas = []
    
    for _, row in historico.iterrows():
        nums = [int(row[col]) for col in ball_cols if pd.notna(row[col])]
        
        features = {
            'soma': sum(nums),
            'amplitude': max(nums) - min(nums),
            'pares': sum(1 for n in nums if n % 2 == 0),
            'primeiros_15': sum(1 for n in nums if n <= 15),
            'ultimos_15': sum(1 for n in nums if n > 45)
        }
        features_historicas.append(features)
    
    # Calcular estatísticas
    df_features = pd.DataFrame(features_historicas)
    medias = df_features.mean()
    desvios = df_features.std()
    
    # Features do jogo proposto
    features_jogo = {
        'soma': sum(numeros),
        'amplitude': max(numeros) - min(numeros),
        'pares': sum(1 for n in numeros if n % 2 == 0),
        'primeiros_15': sum(1 for n in numeros if n <= 15),
        'ultimos_15': sum(1 for n in numeros if n > 45)
    }
    
    # Calcular "anomalia" como distância média normalizada
    anomalias = []
    
    for feat in features_jogo.keys():
        if desvios[feat] > 0:
            dist = abs((features_jogo[feat] - medias[feat]) / desvios[feat])
            anomalias.append(dist)
    
    # Média das distâncias
    anomalia_media = np.mean(anomalias) if anomalias else 0
    
    # Score invertido: menor anomalia = melhor
    # Anomalia típica: 0-2
    if anomalia_media < 0.5:
        score = 100
    elif anomalia_media < 1.0:
        score = 90 - (anomalia_media - 0.5) * 20
    elif anomalia_media < 1.5:
        score = 70 - (anomalia_media - 1.0) * 20
    elif anomalia_media < 2.0:
        score = 50 - (anomalia_media - 1.5) * 20
    else:
        score = max(30 - (anomalia_media - 2.0) * 10, 10)
    
    return min(max(score, 0), 100)


def calcular_probabilidade_condicional(historico: pd.DataFrame,
                                        numeros: List[int]) -> float:
    """
    P(número X | números já sorteados no jogo).
    Análise Bayesiana simplificada.
    
    Dado que já temos certos números, qual a probabilidade dos outros?
    
    Args:
        historico: DataFrame
        numeros: Lista de 6 números
        
    Returns:
        Score 0-100 baseado em probabilidades condicionais
    """
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Contar co-ocorrências: dado número N1, quantas vezes N2 aparece junto?
    co_ocorrencias = {}
    freq_individual = Counter()
    
    for _, row in historico.iterrows():
        nums = [int(row[col]) for col in ball_cols if pd.notna(row[col])]
        
        # Atualizar frequências individuais
        freq_individual.update(nums)
        
        # Atualizar co-ocorrências
        for n1 in nums:
            if n1 not in co_ocorrencias:
                co_ocorrencias[n1] = Counter()
            
            for n2 in nums:
                if n2 != n1:
                    co_ocorrencias[n1][n2] += 1
    
    # Calcular score baseado em probabilidades condicionais
    score = 0
    numeros_sorted = sorted(numeros)
    
    # Para cada par de números no jogo
    for i, n1 in enumerate(numeros_sorted):
        for n2 in numeros_sorted[i+1:]:
            # P(n2 | n1) = count(n1 AND n2) / count(n1)
            if n1 in co_ocorrencias and freq_individual[n1] > 0:
                prob_cond = co_ocorrencias[n1].get(n2, 0) / freq_individual[n1]
                
                # Probabilidade esperada uniforme: 5/59 (já temos n1, restam 59)
                prob_esperada = 5 / 59
                
                # Score baseado em quão maior é a probabilidade real vs esperada
                if prob_cond >= prob_esperada:
                    score += min((prob_cond / prob_esperada) * 10, 15)
                else:
                    score += (prob_cond / prob_esperada) * 8
    
    # Normalizar (máximo de 15 pares)
    score_normalizado = (score / (15 * 15)) * 100
    
    return min(max(score_normalizado, 0), 100)


def calcular_importancia_feature(historico: pd.DataFrame,
                                  numeros: List[int]) -> float:
    """
    Peso de cada número baseado em "importância" histórica.
    Simula conceito de feature importance do Random Forest.
    
    Números "importantes" são aqueles que:
    - Aparecem em sorteios com padrões consistentes
    - Têm alta frequência em jogos "típicos"
    
    Args:
        historico: DataFrame
        numeros: Lista de 6 números
        
    Returns:
        Score 0-100 baseado na importância acumulada
    """
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Calcular "importância" de cada número
    # Baseado em: frequência ponderada por padrões típicos
    
    importancias = {}
    
    for n in range(1, 61):
        # Frequência bruta
        freq = 0
        
        # Contextos em que aparece (pares/ímpares, quadrantes, etc)
        contextos = {
            'com_pares': 0,
            'com_impares': 0,
            'soma_normal': 0,  # Sorteios com soma 160-190
            'amplitude_normal': 0  # Amplitude 40-55
        }
        
        for _, row in historico.iterrows():
            nums = [int(row[col]) for col in ball_cols if pd.notna(row[col])]
            
            if n in nums:
                freq += 1
                
                # Analisar contexto
                pares = sum(1 for x in nums if x % 2 == 0)
                soma = sum(nums)
                amplitude = max(nums) - min(nums)
                
                if pares >= 2:
                    contextos['com_pares'] += 1
                if pares <= 4:
                    contextos['com_impares'] += 1
                if 160 <= soma <= 190:
                    contextos['soma_normal'] += 1
                if 40 <= amplitude <= 55:
                    contextos['amplitude_normal'] += 1
        
        # Importância = frequência * peso_contextos
        if freq > 0:
            peso_contexto = (
                contextos['soma_normal'] / freq * 0.4 +
                contextos['amplitude_normal'] / freq * 0.3 +
                min(contextos['com_pares'], contextos['com_impares']) / freq * 0.3
            )
        else:
            peso_contexto = 0
        
        importancias[n] = freq * (1 + peso_contexto)
    
    # Normalizar importâncias
    max_imp = max(importancias.values()) if importancias else 1
    importancias_norm = {k: v/max_imp for k, v in importancias.items()}
    
    # Score do jogo: média das importâncias
    importancia_jogo = np.mean([importancias_norm.get(n, 0) for n in numeros])
    
    # Converter para 0-100
    score = importancia_jogo * 100
    
    # Bonus se todos números têm importância > 0.5
    if all(importancias_norm.get(n, 0) > 0.5 for n in numeros):
        score = min(score * 1.15, 100)
    
    return min(max(score, 0), 100)


def criar_todos_indicadores_ml(historico: pd.DataFrame,
                                numeros: List[int]) -> Dict[str, float]:
    """
    Calcula todos os 3 indicadores ML de uma vez.
    
    Args:
        historico: DataFrame com histórico completo
        numeros: Lista de 6 números para análise
        
    Returns:
        Dict com scores de cada indicador
    """
    return {
        'ScoreAnomalia': calcular_score_anomalia(historico, numeros),
        'ProbabilidadeCondicional': calcular_probabilidade_condicional(historico, numeros),
        'ImportanciaFeature': calcular_importancia_feature(historico, numeros)
    }
