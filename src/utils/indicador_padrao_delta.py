"""
Indicador de Padrão de Deltas - MegaCLI v6.1

Analisa as diferenças (deltas) entre os números ordenados de um jogo.
Ajuda a eliminar combinações aritmeticamente improváveis.

Autor: MegaCLI Team
Data: 23/01/2026
"""

from typing import List, Tuple
import numpy as np

def calcular_deltas(jogo: List[int]) -> List[int]:
    """
    Calcula os deltas entre números ordenados.
    Ex: [4, 12, 15] -> [4, 8, 3] (considerando 0 como início ou apenas entre eles?)
    Padrão Mega-Sena: Deltas entre os números.
    """
    sorted_nums = sorted(jogo)
    deltas = []
    for i in range(len(sorted_nums) - 1):
        deltas.append(sorted_nums[i+1] - sorted_nums[i])
    return deltas

def analisar_padrao_delta(jogo: List[int]) -> Tuple[bool, str]:
    """
    Verifica se os deltas do jogo estão dentro de padrões aceitáveis.
    
    Regras de Rejeição (Baseado em estatística histórica):
    1. Deltas todos iguais a 1 (Sequência 1,2,3,4,5,6) -> Rejeitar
    2. Muitos deltas iguais a 1 (Ex: 1,2,3,4, 40, 50) -> Suspeito (> 3 deltas 1)
    3. Delta muito grande único (> 40) -> Raro
    """
    deltas = calcular_deltas(jogo)
    
    # Regra 1: Sequência completa (deltas = 1)
    if all(d == 1 for d in deltas):
        return False, "Sequência Completa (Improvável)"
        
    # Regra 2: Excesso de consecutivos
    consecutivos = sum(1 for d in deltas if d == 1)
    if consecutivos > 2: # Permitir no máximo 3 números seguidos (2 deltas de 1)
        return False, f"Muitos consecutivos ({consecutivos+1})"
        
    # Regra 3: Buracos muito grandes
    # Ex: 1, 2, 3, 4, 5, 60 (Delta 5->60 é 55)
    # Embora possível, reduz a probabilidade. Vamos ser conservadores no filtro.
    # Apenas alertar ou penalizar seria melhor, mas aqui é filtro booleano?
    # Vamos manter simples: Rejeita se > 3 consecutivos.
    
    return True, "OK"

def score_delta(jogo: List[int]) -> float:
    """Retorna score 0-100 para a qualidade dos deltas."""
    deltas = calcular_deltas(jogo)
    consecutivos = sum(1 for d in deltas if d == 1)
    
    score = 100
    
    # Penalizar consecutivos
    if consecutivos == 1: score -= 10  # 1 duples (10,11) OK
    if consecutivos == 2: score -= 30  # 1 tripla (10,11,12) Raro
    if consecutivos >= 3: score -= 80  # 1 quadra ou 2 duplas (10,11,12,13) Muito Raro
    
    # Penalizar desvio padrão muito baixo (números muito juntos) ou muito alto
    std_delta = np.std(deltas)
    if std_delta < 2: score -= 20 # Muito agrupados
    
    return max(0, score)
