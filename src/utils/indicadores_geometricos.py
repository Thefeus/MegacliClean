"""
Indicadores de Padrões Geométricos para Mega-Sena

Módulo com 3 novos indicadores focados em padrões espaciais/geométricos:
1. MatrizPosicional - Posição relativa (1ª, 2ª, ..., 6ª bola)
2. ClusterEspacial - "Zonas quentes" na sequência 1-60
3. SimetriaCentral - Balanceamento em torno da mediana (30.5)

Autor: MegaCLI v4.0
Data: 27/12/2024
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter, defaultdict


def calcular_matriz_posicional(historico: pd.DataFrame,
                                numeros: List[int]) -> float:
    """
    Analisa a posição relativa dos números (1ª bola, 2ª bola, etc).
    Números baixos tendem a sair nas primeiras posições?
    
    Args:
        historico: DataFrame com histórico
        numeros: Lista de 6 números já ordenados
        
    Returns:
        Score 0-100 (maior = melhor alinhamento com padrão histórico)
    """
    if len(numeros) != 6:
        return 50.0
    
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Analisar distribuição por posição
    # Para cada posição (1-6), qual a faixa típica de valores?
    ranges_por_posicao = {}
    
    for i, col in enumerate(ball_cols, 1):
        valores = historico[col].dropna().astype(int).tolist()
        if len(valores) > 0:
            ranges_por_posicao[i] = {
                'min': np.percentile(valores, 10),
                'q1': np.percentile(valores, 25),
                'mediana': np.median(valores),
                'q3': np.percentile(valores, 75),
                'max': np.percentile(valores, 90)
            }
    
    # Calcular score baseado em quão bem os números propostos
    # se encaixam nas posições esperadas
    score = 0
    
    for i, num in enumerate(numeros, 1):
        if i in ranges_por_posicao:
            r = ranges_por_posicao[i]
            
            # Pontuação máxima se está dentro do IQR (25%-75%)
            if r['q1'] <= num <= r['q3']:
                score += 20
            # Boa pontuação se está dentro de 10%-90%
            elif r['min'] <= num <= r['max']:
                score += 12
            # Pontuação menor se está próximo, mas fora
            elif r['min'] - 10 <= num <= r['max'] + 10:
                score += 5
            # Sem pontos se está muito fora do padrão
    
    # Bonus: se números estão em ordem crescente consistente
    # (natural para sorteios ordenados)
    if all(numeros[i] < numeros[i+1] for i in range(5)):
        score *= 1.1
    
    return min(max(score, 0), 100)


def calcular_cluster_espacial(historico: pd.DataFrame,
                               numeros: List[int],
                               tamanho_zona: int = 10) -> float:
    """
    Agrupa números próximos e detecta "zonas quentes".
    Divide 1-60 em 6 zonas de 10 números cada.
    
    Zonas:
    - Z1: 1-10
    - Z2: 11-20  
    - Z3: 21-30
    - Z4: 31-40
    - Z5: 41-50
    - Z6: 51-60
    
    Args:
        historico: DataFrame
        numeros: Lista de 6 números
        tamanho_zona: Tamanho de cada zona (padrão: 10)
        
    Returns:
        Score 0-100 baseado em frequência das zonas
    """
    def numero_para_zona(n):
        return (n - 1) // tamanho_zona + 1
    
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Calcular frequência de cada zona historicamente
    freq_zonas = Counter()
    
    for _, row in historico.iterrows():
        nums = [int(row[col]) for col in ball_cols if pd.notna(row[col])]
        zonas = [numero_para_zona(n) for n in nums]
        freq_zonas.update(zonas)
    
    # Normalizar frequência (quantos números por zona em média)
    total_numeros = sum(freq_zonas.values())
    freq_normalizada = {z: (freq_zonas.get(z, 0) / total_numeros * 100) 
                        for z in range(1, 7)}
    
    # Calcular score para o jogo proposto
    zonas_jogo = Counter([numero_para_zona(n) for n in numeros])
    
    score = 0
    
    # Avaliar cada zona do jogo
    for zona, count in zonas_jogo.items():
        freq_zona = freq_normalizada.get(zona, 0)
        
        # Se a zona é "quente" (frequência > 17%), bom ter números dela
        if freq_zona > 17:  # Acima da média uniforme (100/6 ≈ 16.67%)
            score += count * 18
        # Se é zona "morna" (próximo da média)
        elif 15 <= freq_zona <= 17:
            score += count * 15
        # Zona "fria"
        else:
            score += count * 10
    
    # Penalidade se muitos números na mesma zona (falta diversidade)
    max_por_zona = max(zonas_jogo.values())
    if max_por_zona > 3:
        score *= 0.7
    elif max_por_zona == 3:
        score *= 0.9
    
    # Bonus por diversidade (números em várias zonas)
    nums_zonas_diferentes = len(zonas_jogo)
    if nums_zonas_diferentes >= 5:
        score *= 1.2
    elif nums_zonas_diferentes >= 4:
        score *= 1.1
    
    return min(max(score, 0), 100)


def calcular_simetria_central(historico: pd.DataFrame,
                               numeros: List[int]) -> float:
    """
    Balanceamento em torno da mediana (30.5).
    Quantos números < 30 vs > 30.
    
    Padrão ideal detectado historicamente: 3-3 ou 2-4
    
    Args:
        historico: DataFrame
        numeros: Lista de 6 números
        
    Returns:
        Score 0-100 (maior = balanceamento ideal)
    """
    MEDIANA = 30.5
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Analisar distribuição histórica
    distribuicoes = []
    
    for _, row in historico.iterrows():
        nums = [int(row[col]) for col in ball_cols if pd.notna(row[col])]
        baixos = len([n for n in nums if n <= MEDIANA])
        altos = len([n for n in nums if n > MEDIANA])
        distribuicoes.append((baixos, altos))
    
    # Calcular padrão mais comum
    dist_counter = Counter(distribuicoes)
    padroes_comuns = dist_counter.most_common(3)
    
    # Analisar jogo proposto
    baixos_jogo = len([n for n in numeros if n <= MEDIANA])
    altos_jogo = len([n for n in numeros if n > MEDIANA])
    dist_jogo = (baixos_jogo, altos_jogo)
    
    # Score baseado em quão comum é essa distribuição
    score = 0
    
    # Se é um dos 3 padrões mais comuns, score alto
    if dist_jogo in [p[0] for p in padroes_comuns]:
        # Posição no ranking
        for i, (padrao, freq) in enumerate(padroes_comuns):
            if padrao == dist_jogo:
                if i == 0:  # Padrão mais comum
                    score = 100
                elif i == 1:  # 2º mais comum
                    score = 85
                else:  # 3º mais comum
                    score = 70
                break
    else:
        # Se não é comum, pontuar baseado em balanceamento
        diferenca = abs(baixos_jogo - altos_jogo)
        
        if diferenca == 0:  # 3-3 perfeito
            score = 90
        elif diferenca == 1:  # 2-4 ou 4-2
            score = 75
        elif diferenca == 2:  # 1-5 ou 5-1
            score = 50
        else:  # 0-6 ou 6-0 (muito desequilibrado)
            score = 20
    
    # Calcular também a média dos números
    # Idealmente deve estar próxima de 30.5
    media_jogo = np.mean(numeros)
    
    # Bonus se média está próxima da mediana teórica
    distancia_media = abs(media_jogo - MEDIANA)
    if distancia_media < 3:
        score = min(score * 1.15, 100)
    elif distancia_media < 5:
        score = min(score * 1.05, 100)
    
    return min(max(score, 0), 100)


def criar_todos_indicadores_geometricos(historico: pd.DataFrame,
                                        numeros: List[int]) -> Dict[str, float]:
    """
    Calcula todos os 3 indicadores geométricos de uma vez.
    
    Args:
        historico: DataFrame com histórico completo
        numeros: Lista de 6 números para análise
        
    Returns:
        Dict com scores de cada indicador
    """
    return {
        'MatrizPosicional': calcular_matriz_posicional(historico, numeros),
        'ClusterEspacial': calcular_cluster_espacial(historico, numeros),
        'SimetriaCentral': calcular_simetria_central(historico, numeros)
    }
