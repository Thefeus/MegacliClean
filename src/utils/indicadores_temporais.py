"""
Indicadores de Análise Temporal para Mega-Sena

Módulo com 4 novos indicadores focados em padrões temporais:
1. TendenciaQuadrantes - Migração entre quadrantes
2. CiclosSemanais - Padrões por dia da semana
3. AcumulacaoConsecutiva - Números "atrasados"
4. JanelaDeslizante - Frequência em janelas móveis

Autor: MegaCLI v4.0
Data: 27/12/2024
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter, defaultdict
from datetime import datetime


def calcular_tendencia_quadrantes(historico: pd.DataFrame, 
                                   numeros: List[int],
                                   janela: int = 10) -> float:
    """
    Analisa a migração de números entre quadrantes nos últimos N sorteios.
    
    Quadrantes:
    - Q1: 1-15
    - Q2: 16-30
    - Q3: 31-45
    - Q4: 46-60
    
    Detecta se há movimento de baixo→alto, dispersão ou concentração
    
    Args:
        historico: DataFrame com histórico completo
        numeros: Lista de 6 números para análise
        janela: Quantidade de sorteios recentes a considerar
        
    Returns:
        Score 0-100 (100 = tendência forte e positiva)
    """
    def numero_para_quadrante(n):
        if n <= 15: return 1
        elif n <= 30: return 2
        elif n <= 45: return 3
        else: return 4
    
    # Pegar últimos N sorteios
    if len(historico) < janela:
        janela = len(historico)
    
    ultimos = historico.tail(janela)
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Analisar distribuição histórica de quadrantes
    quadrantes_historicos = []
    for _, row in ultimos.iterrows():
        nums_sorteio = [int(row[col]) for col in ball_cols if pd.notna(row[col])]
        quads = [numero_para_quadrante(n) for n in nums_sorteio]
        quadrantes_historicos.append(Counter(quads))
    
    # Calcular tendência: últimos 3 vs primeiros 3 sorteios da janela
    if len(quadrantes_historicos) >= 6:
        primeiros_3 = Counter()
        ultimos_3 = Counter()
        
        for i in range(3):
            primeiros_3.update(quadrantes_historicos[i])
            ultimos_3.update(quadrantes_historicos[-(i+1)])
        
        # Detectar movimento
        movimento = 0
        for q in [1, 2, 3, 4]:
            diff = ultimos_3.get(q, 0) - primeiros_3.get(q, 0)
            # Dar peso positivo se movimento for para distribuição equilibrada
            if q in [2, 3]:  # Quadrantes centrais
                movimento += abs(diff) * 1.2
            else:
                movimento += abs(diff) * 0.8
    else:
        movimento = 5  # Valor neutro se não há histórico suficiente
    
    # Analisar jogo proposto
    quads_jogo = Counter([numero_para_quadrante(n) for n in numeros])
    
    # Calcular balanceamento (ideal: 1-2 números por quadrante)
    balanceamento = 0
    for q in [1, 2, 3, 4]:
        count = quads_jogo.get(q, 0)
        if count in [1, 2]:  # Ideal
            balanceamento += 30
        elif count == 3:
            balanceamento += 10
        # 0 ou 4+ números: sem pontos
    
    # Score final: combina balanceamento com tendência detectada
    score = (balanceamento * 0.7) + (min(movimento * 3, 30) * 0.3)
    
    return min(max(score, 0), 100)


def calcular_ciclos_semanais(historico: pd.DataFrame, 
                              numeros: List[int],
                              dia_semana: int = None) -> float:
    """
    Analisa padrões baseados no dia da semana do sorteio.
    Mega-Sena sorteia quartas (3) e sábados (6).
    
    Args:
        historico: DataFrame com histórico completo
        numeros: Lista de 6 números
        dia_semana: 3=quarta, 6=sábado (None = detectar automaticamente)
        
    Returns:
        Score 0-100 baseado em frequência desses números nesse dia
    """
    if 'Data' not in historico.columns:
        return 50.0  # Neutro se não há data
    
    # Se não especificado, assumir próximo sábado (mais comum)
    if dia_semana is None:
        dia_semana = 6
    
    # Filtrar sorteios do mesmo dia da semana
    historico_dia = historico.copy()
    historico_dia['DiaSemana'] = pd.to_datetime(historico_dia['Data']).dt.dayofweek
    mesmo_dia = historico_dia[historico_dia['DiaSemana'] == dia_semana]
    
    if len(mesmo_dia) == 0:
        return 50.0
    
    # Calcular frequência de cada número neste dia
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    freq_dia = Counter()
    
    for _, row in mesmo_dia.iterrows():
        nums = [int(row[col]) for col in ball_cols if pd.notna(row[col])]
        freq_dia.update(nums)
    
    # Total de números sorteados neste dia
    total_sorteios_dia = len(mesmo_dia) * 6
    
    # Calcular score baseado na frequência dos números propostos
    score = 0
    for num in numeros:
        freq = freq_dia.get(num, 0)
        # Frequência esperada: total_sorteios_dia / 60
        freq_esperada = total_sorteios_dia / 60
        
        # Normalizar: quanto mais próximo ou acima da esperada, melhor
        if freq >= freq_esperada:
            score += min((freq / freq_esperada) * 20, 25)
        else:
            score += (freq / freq_esperada) * 15
    
    return min(max(score, 0), 100)


def calcular_acumulacao_consecutiva(historico: pd.DataFrame,
                                     numeros: List[int]) -> float:
    """
    Quantos sorteios seguidos cada número ficou ausente.
    Teoria: "Números atrasados" tendem a aparecer (lei dos grandes números).
    
    Args:
        historico: DataFrame com histórico
        numeros: Lista de 6 números
        
    Returns:
        Score 0-100 (maior = números mais "atrasados")
    """
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Calcular ausência de cada número (de trás para frente)
    ausencias = {}
    
    for n in range(1, 61):
        ausencias[n] = 0
        
        for i in range(len(historico)-1, -1, -1):
            row = historico.iloc[i]
            nums_sorteio = [int(row[col]) for col in ball_cols if pd.notna(row[col])]
            
            if n in nums_sorteio:
                break
            else:
                ausencias[n] += 1
    
    # Calcular score baseado na ausência dos números propostos
    score = 0
    ausencias_jogo = [ausencias[n] for n in numeros]
    
    # Média de ausência
    media_ausencia = np.mean(ausencias_jogo)
    
    # Ausências muito longas (>30) ou muito curtas (<5) são ruins
    # Ideal: 10-25 sorteios
    if 10 <= media_ausencia <= 25:
        score = 100
    elif 5 <= media_ausencia < 10:
        score = 60 + (media_ausencia - 5) * 8
    elif 25 < media_ausencia <= 40:
        score = 100 - (media_ausencia - 25) * 2.5
    elif media_ausencia > 40:
        score = max(20, 100 - (media_ausencia - 25) * 2.5)
    else:  # < 5
        score = media_ausencia * 10
    
    # Bônus se há diversidade (alguns atrasados + alguns recentes)
    desvio = np.std(ausencias_jogo)
    if 5 < desvio < 15:
        score = min(score * 1.1, 100)
    
    return min(max(score, 0), 100)


def calcular_janela_deslizante(historico: pd.DataFrame,
                                numeros: List[int],
                                janelas: List[int] = [10, 20, 50, 100]) -> float:
    """
    Frequência em janelas móveis de diferentes tamanhos.
    Detecta tendências de curto vs longo prazo.
    
    Args:
        historico: DataFrame
        numeros: Lista de 6 números
        janelas: Tamanhos de janela a analisar
        
    Returns:
        Score 0-100 baseado em consistência entre janelas
    """
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Calcular frequência em cada janela
    frequencias_por_janela = {}
    
    for janela in janelas:
        if len(historico) < janela:
            continue
            
        ultimos = historico.tail(janela)
        freq = Counter()
        
        for _, row in ultimos.iterrows():
            nums = [int(row[col]) for col in ball_cols if pd.notna(row[col])]
            freq.update(nums)
        
        frequencias_por_janela[janela] = freq
    
    if len(frequencias_por_janela) == 0:
        return 50.0
    
    # Calcular score para os números propostos
    scores_janelas = []
    
    for janela, freq in frequencias_por_janela.items():
        score_janela = 0
        for num in numeros:
            # Frequência esperada: janela * 6 / 60
            freq_esperada = (janela * 6) / 60
            freq_real = freq.get(num, 0)
            
            # Quanto mais próximo da esperada, melhor
            if freq_real > 0:
                ratio = freq_real / freq_esperada
                if 0.8 <= ratio <= 1.2:  # Dentro do esperado
                    score_janela += 20
                elif 0.5 <= ratio < 0.8 or 1.2 < ratio <= 1.5:
                    score_janela += 12
                else:
                    score_janela += 5
        
        scores_janelas.append(score_janela)
    
    # Consistência: se scores parecidos em todas as janelas = bom
    if len(scores_janelas) > 1:
        media_scores = np.mean(scores_janelas)
        desvio_scores = np.std(scores_janelas)
        
        # Bonus por consistência
        if desvio_scores < 15:
            score_final = min(media_scores * 1.2, 100)
        else:
            score_final = media_scores * 0.9
    else:
        score_final = scores_janelas[0] if scores_janelas else 50.0
    
    return min(max(score_final, 0), 100)


def criar_todos_indicadores_temporais(historico: pd.DataFrame,
                                       numeros: List[int]) -> Dict[str, float]:
    """
    Calcula todos os 4 indicadores temporais de uma vez.
    
    Args:
        historico: DataFrame com histórico completo
        numeros: Lista de 6 números para análise
        
    Returns:
        Dict com scores de cada indicador
    """
    return {
        'TendenciaQuadrantes': calcular_tendencia_quadrantes(historico, numeros),
        'CiclosSemanais': calcular_ciclos_semanais(historico, numeros),
        'AcumulacaoConsecutiva': calcular_acumulacao_consecutiva(historico, numeros),
        'JanelaDeslizante': calcular_janela_deslizante(historico, numeros)
    }
