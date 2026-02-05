"""
Indicadores Básicos - MegaCLI

12 indicadores básicos clássicos da Mega-Sena
"""

import pandas as pd
import numpy as np
from typing import List


def calcular_quadrantes(historico: pd.DataFrame, numeros: List[int]) -> float:
    """Score baseado em distribuição por quadrantes (1-15, 16-30, 31-45, 46-60)"""
    quadrantes = {1: 0, 2: 0, 3: 0, 4: 0}
    for n in numeros:
        if n <= 15:
            quadrantes[1] += 1
        elif n <= 30:
            quadrantes[2] += 1
        elif n <= 45:
            quadrantes[3] += 1
        else:
            quadrantes[4] += 1
    
    # Ideal: 1-2 números por quadrante
    desvios = sum(abs(q - 1.5) for q in quadrantes.values())
    return max(0, 100 - desvios * 15)


def calcular_div9(historico: pd.DataFrame, numeros: List[int]) -> float:
    """Score baseado em divisibilidade por 9"""
    div9 = sum(1 for n in numeros if n % 9 == 0)
    # Ideal: 0-1 divisíveis por 9
    if div9 <= 1:
        return 80
    elif div9 == 2:
        return 50
    else:
        return 20


def calcular_fibonacci(historico: pd.DataFrame, numeros: List[int]) -> float:
    """Score baseado em números de Fibonacci"""
    fib = [1, 2, 3, 5, 8, 13, 21, 34, 55]
    fib_count = sum(1 for n in numeros if n in fib)
    # Ideal: 1-3 números Fibonacci
    if 1 <= fib_count <= 3:
        return 80
    elif fib_count == 0 or fib_count == 4:
        return 50
    else:
        return 30


def calcular_div6(historico: pd.DataFrame, numeros: List[int]) -> float:
    """Score baseado em divisibilidade por 6"""
    div6 = sum(1 for n in numeros if n % 6 == 0)
    # Ideal: 0-2 divisíveis por 6
    if div6 <= 2:
        return 75
    elif div6 == 3:
        return 50
    else:
        return 25


def calcular_mult5(historico: pd.DataFrame, numeros: List[int]) -> float:
    """Score baseado em múltiplos de 5"""
    mult5 = sum(1 for n in numeros if n % 5 == 0)
    # Ideal: 1-2 múltiplos de 5
    if 1 <= mult5 <= 2:
        return 70
    elif mult5 == 0 or mult5 == 3:
        return 45
    else:
        return 20


def calcular_div3(historico: pd.DataFrame, numeros: List[int]) -> float:
    """Score baseado em divisibilidade por 3"""
    div3 = sum(1 for n in numeros if n % 3 == 0)
    # Ideal: 2-3 divisíveis por 3
    if 2 <= div3 <= 3:
        return 65
    elif div3 == 1 or div3 == 4:
        return 45
    else:
        return 25


def calcular_gap(historico: pd.DataFrame, numeros: List[int]) -> float:
    """Score baseado em gaps (distâncias) entre números consecutivos"""
    nums_sorted = sorted(numeros)
    gaps = [nums_sorted[i+1] - nums_sorted[i] for i in range(5)]
    gap_medio = np.mean(gaps)
    # Ideal: gap médio entre 8-12
    if 8 <= gap_medio <= 12:
        return 62
    elif 6 <= gap_medio <= 14:
        return 45
    else:
        return 30


def calcular_primos(historico: pd.DataFrame, numeros: List[int]) -> float:
    """Score baseado em números primos"""
    primos = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59]
    primos_count = sum(1 for n in numeros if n in primos)
    # Ideal: 2-3 primos
    if 2 <= primos_count <= 3:
        return 60
    elif primos_count == 1 or primos_count == 4:
        return 40
    else:
        return 25


def calcular_simetria(historico: pd.DataFrame, numeros: List[int]) -> float:
    """Score baseado em simetria (números menores vs maiores que 30)"""
    menores = sum(1 for n in numeros if n <= 30)
    maiores = 6 - menores
    diff = abs(menores - maiores)
    # Ideal: 3-3 ou 4-2
    if diff == 0:
        return 58
    elif diff <= 2:
        return 45
    else:
        return 25


def calcular_par_impar(historico: pd.DataFrame, numeros: List[int]) -> float:
    """Score baseado em distribuição par/ímpar"""
    pares = sum(1 for n in numeros if n % 2 == 0)
    impares = 6 - pares
    diff = abs(pares - impares)
    # Ideal: 3-3 ou 4-2
    if diff == 0:
        return 58
    elif diff <= 2:
        return 42
    else:
        return 25


def calcular_amplitude(historico: pd.DataFrame, numeros: List[int]) -> float:
    """Score baseado na amplitude (max - min)"""
    amplitude = max(numeros) - min(numeros)
    # Ideal: amplitude entre 30-45
    if 30 <= amplitude <= 45:
        return 45
    elif 25 <= amplitude <= 50:
        return 35
    else:
        return 20


def calcular_soma(historico: pd.DataFrame, numeros: List[int]) -> float:
    """Score baseado na soma total"""
    soma = sum(numeros)
    # Ideal: soma entre 140-220
    if 140 <= soma <= 220:
        return 30
    elif 120 <= soma <= 240:
        return 20
    else:
        return 10


# Dict com todos os 12 básicos
INDICADORES_BASICOS = {
    'Quadrantes': calcular_quadrantes,
    'Div9': calcular_div9,
    'Fibonacci': calcular_fibonacci,
    'Div6': calcular_div6,
    'Mult5': calcular_mult5,
    'Div3': calcular_div3,
    'Gap': calcular_gap,
    'Primos': calcular_primos,
    'Simetria': calcular_simetria,
    'ParImpar': calcular_par_impar,
    'Amplitude': calcular_amplitude,
    'Soma': calcular_soma
}
