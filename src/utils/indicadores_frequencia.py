"""
Indicadores de Análise de Frequência Avançada para Mega-Sena

Módulo com 4 novos indicadores focados em estatística avançada de frequência:
1. FrequenciaRelativa - Normalização temporal (histórico completo vs recente)
2. DesvioFrequencia - Z-score de cada número
3. EntrópiaDistribuicao - Medida de aleatoriedade (Shannon entropy)
4. CorrelacaoTemporal - Números que aparecem juntos

Autor: MegaCLI v4.0
Data: 27/12/2024
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter, defaultdict
from itertools import combinations
import math


def calcular_frequencia_relativa(historico: pd.DataFrame,
                                  numeros: List[int],
                                  janela_recente: int = 100) -> float:
    """
    Normalização da frequência: completo vs últimos N sorteios.
    Detecta se números estão "em alta" ou "em baixa".
    
    Args:
        historico: DataFrame com histórico
        numeros: Lista de 6 números
        janela_recente: Tamanho da janela recente (padrão: 100)
        
    Returns:
        Score 0-100 (maior = frequência relativa favorável)
    """
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Frequência total (histórico completo)
    freq_total = Counter()
    for col in ball_cols:
        freq_total.update(historico[col].dropna().astype(int).tolist())
    
    # Frequência recente
    if len(historico) < janela_recente:
        janela_recente = len(historico)
    
    recente = historico.tail(janela_recente)
    freq_recente = Counter()
    for col in ball_cols:
        freq_recente.update(recente[col].dropna().astype(int).tolist())
    
    # Calcular frequência esperada (uniforme)
    total_sorteios = len(historico)
    freq_esperada_total = (total_sorteios * 6) / 60
    
    total_recente = janela_recente
    freq_esperada_recente = (total_recente * 6) / 60
    
    # Calcular score para cada número proposto
    score = 0
    
    for num in numeros:
        # Frequência normalizada no histórico total
        freq_norm_total = freq_total.get(num, 0) / freq_esperada_total if freq_esperada_total > 0 else 1.0
        
        # Frequência normalizada recente
        freq_norm_recente = freq_recente.get(num, 0) / freq_esperada_recente if freq_esperada_recente > 0 else 1.0
        
        # Razão: quão "quente" está o número recentemente
        if freq_norm_total > 0:
            razao = freq_norm_recente / freq_norm_total
        else:
            razao = 1.0
        
        # Score baseado na razão
        # Razão > 1: número está "em alta" (mais frequente recentemente)
        # Razão < 1: número está "em baixa"
        # Ideal: próximo de 1 (consistente) ou > 1 (tendência positiva)
        
        if 0.9 <= razao <= 1.1:  # Consistente
            score += 18
        elif razao > 1.1:  # Em alta
            score += min(20 * razao, 25)  # Máximo 25 pontos
        elif 0.7 <= razao < 0.9:  # Ligeiramente abaixo
            score += 12
        else:  # Muito abaixo
            score += 5
    
    return min(max(score, 0), 100)


def calcular_desvio_frequencia(historico: pd.DataFrame,
                                numeros: List[int]) -> float:
    """
    Z-score de cada número (quão longe está da frequência esperada).
    
    Args:
        historico: DataFrame
        numeros: Lista de 6 números
        
    Returns:
        Score 0-100 (menor desvio absoluto médio = melhor)
    """
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Calcular frequência de todos os números
    freq = Counter()
    for col in ball_cols:
        freq.update(historico[col].dropna().astype(int).tolist())
    
    # Frequência esperada (distribuição uniforme)
    total_numeros = len(historico) * 6
    freq_esperada = total_numeros / 60
    
    # Calcular frequências de todos os 60 números
    frequencias_todas = [freq.get(n, 0) for n in range(1, 61)]
    
    # Média e desvio padrão
    media = np.mean(frequencias_todas)
    desvio_padrao = np.std(frequencias_todas)
    
    if desvio_padrao == 0:
        return 50.0  # Todas as frequências iguais (improvável)
    
    # Calcular Z-score para os números propostos
    z_scores = []
    for num in numeros:
        freq_num = freq.get(num, 0)
        z_score = abs((freq_num - media) / desvio_padrao)
        z_scores.append(z_score)
    
    # Média dos Z-scores (quanto menor, mais "normal" é o conjunto)
    media_z = np.mean(z_scores)
    
    # Score invertido: menor desvio = melhor
    # Z-score típico: 0-2 (dentro de 2 desvios padrões)
    # Z-score > 2: outlier
    
    if media_z < 0.5:  # Muito próximo da média
        score = 100
    elif media_z < 1.0:  # Dentro de 1 desvio
        score = 90 - (media_z - 0.5) * 20
    elif media_z < 1.5:
        score = 70 - (media_z - 1.0) * 20
    elif media_z < 2.0:
        score = 50 - (media_z - 1.5) * 20
    else:  # Outliers
        score = max(30 - (media_z - 2.0) * 10, 10)
    
    return min(max(score, 0), 100)


def calcular_entropia_distribuicao(historico: pd.DataFrame,
                                    numeros: List[int]) -> float:
    """
    Mede "aleatoriedade" do jogo usando entropia de Shannon.
    
    Entropia alta = jogo imprevisível (bom)
    Entropia baixa = jogo muito previsível (ruim)
    
    Args:
        historico: DataFrame
        numeros: Lista de 6 números
        
    Returns:
        Score 0-100 baseado na entropia
    """
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Calcular frequência histórica
    freq = Counter()
    for col in ball_cols:
        freq.update(historico[col].dropna().astype(int).tolist())
    
    total = sum(freq.values())
    
    # Probabilidade de cada número no jogo proposto
    probabilidades = []
    for num in numeros:
        # Probabilidade empírica baseada no histórico
        prob = freq.get(num, 1) / total if total > 0 else 1/60
        probabilidades.append(prob)
    
    # Calcular entropia de Shannon: H = -Σ(p * log2(p))
    entropia = 0
    for p in probabilidades:
        if p > 0:
            entropia += -p * math.log2(p)
    
    # Normalizar entropia
    # Entropia máxima para 6 números: log2(6) ≈ 2.585
    # Entropia mínima: 0 (todos iguais - impossível aqui)
    entropia_max = math.log2(len(numeros))
    entropia_normalizada = entropia / entropia_max if entropia_max > 0 else 0
    
    # Score baseado na entropia normalizada
    # Queremos entropia alta (próxima de 1.0)
    score = entropia_normalizada * 100
    
    # Bonus se a distribuição é bem balanceada
    # (todas as probabilidades similares)
    variancia_prob = np.var(probabilidades)
    if variancia_prob < 0.0001:  # Muito uniforme
        score = min(score * 1.15, 100)
    
    return min(max(score, 0), 100)


def calcular_correlacao_temporal(historico: pd.DataFrame,
                                  numeros: List[int]) -> float:
    """
    Números que tendem a aparecer juntos historicamente.
    Analisa pares e trios que são sorteados juntos com frequência.
    
    Args:
        historico: DataFrame
        numeros: Lista de 6 números
        
    Returns:
        Score 0-100 baseado em correlações positivas
    """
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Mapear co-ocorrências de pares
    pares_freq = Counter()
    
    for _, row in historico.iterrows():
        nums_sorteio = [int(row[col]) for col in ball_cols if pd.notna(row[col])]
        # Gerar todos os pares possíveis
        for par in combinations(nums_sorteio, 2):
            pares_freq[tuple(sorted(par))] += 1
    
    # Calcular score baseado nos pares presentes no jogo proposto
    pares_jogo = list(combinations(sorted(numeros), 2))
    
    # Frequência média de pares
    if len(pares_freq) > 0:
        freq_media_pares = np.mean(list(pares_freq.values()))
        freq_max_pares = max(pares_freq.values())
    else:
        freq_media_pares = 1
        freq_max_pares = 1
    
    score = 0
    
    for par in pares_jogo:
        freq_par = pares_freq.get(tuple(sorted(par)), 0)
        
        # Normalizar pela frequência média
        if freq_media_pares > 0:
            ratio = freq_par / freq_media_pares
        else:
            ratio = 0
        
        # Score por par
        if ratio >= 1.5:  # Par muito frequente
            score += 8
        elif ratio >= 1.0:  # Acima da média
            score += 6
        elif ratio >= 0.5:  # Próximo da média
            score += 4
        else:  # Abaixo da média ou nunca ocorreu
            score += 2
    
    # Máximo de 15 pares (C(6,2) = 15)
    # Normalizar para 0-100
    score_normalizado = (score / (15 * 8)) * 100
    
    # Bonus: se temos pelo menos 1 trio que apareceu junto
    trios_freq = Counter()
    for _, row in historico.iterrows():
        nums_sorteio = [int(row[col]) for col in ball_cols if pd.notna(row[col])]
        for trio in combinations(nums_sorteio, 3):
            trios_freq[tuple(sorted(trio))] += 1
    
    trios_jogo = list(combinations(sorted(numeros), 3))
    tem_trio_forte = False
    
    for trio in trios_jogo:
        if trios_freq.get(tuple(sorted(trio)), 0) >= 2:  # Trio apareceu 2+ vezes
            tem_trio_forte = True
            break
    
    if tem_trio_forte:
        score_normalizado = min(score_normalizado * 1.2, 100)
    
    return min(max(score_normalizado, 0), 100)


def criar_todos_indicadores_frequencia(historico: pd.DataFrame,
                                       numeros: List[int]) -> Dict[str, float]:
    """
    Calcula todos os 4 indicadores de frequência avançada de uma vez.
    
    Args:
        historico: DataFrame com histórico completo
        numeros: Lista de 6 números para análise
        
    Returns:
        Dict com scores de cada indicador
    """
    return {
        'FrequenciaRelativa': calcular_frequencia_relativa(historico, numeros),
        'DesvioFrequencia': calcular_desvio_frequencia(historico, numeros),
        'EntrópiaDistribuicao': calcular_entropia_distribuicao(historico, numeros),
        'CorrelacaoTemporal': calcular_correlacao_temporal(historico, numeros)
    }
