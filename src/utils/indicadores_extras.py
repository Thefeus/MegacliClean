"""
Indicadores Extras - Fase 6

5 novos indicadores para melhorar previsibilidade:
1. Sequências - Números consecutivos
2. Distância Média - Espaçamento entre números
3. Números Extremos - Presença de extremos (<10 ou >50)
4. Padrão de Dezenas - Análise de terminações
5. Ciclo de Aparição - Frequência temporal
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from collections import Counter


class SequenciasIndicador:
    """
    Analisa presença de números consecutivos
    Jogos com 2-3 números em sequência são comuns
    """
    
    @staticmethod
    def calcular_score(numeros: List[int], historico: pd.DataFrame = None) -> float:
        """
        Score baseado em sequências
        - 2 consecutivos: +30 pontos
        - 3+ consecutivos: +50 pontos
        """
        numeros_sorted = sorted(numeros)
        sequencias = 0
        max_seq = 1
        seq_atual = 1
        
        for i in range(len(numeros_sorted) - 1):
            if numeros_sorted[i+1] == numeros_sorted[i] + 1:
                seq_atual += 1
                max_seq = max(max_seq, seq_atual)
            else:
                seq_atual = 1
        
        if max_seq >= 3:
            return 50
        elif max_seq == 2:
            return 30
        return 10


class DistanciaMediaIndicador:
    """
    Analisa distância média entre números consecutivos
    Ideal: 8-12 (distribuição equilibrada)
    """
    
    @staticmethod
    def calcular_score(numeros: List[int], historico: pd.DataFrame = None) -> float:
        """
        Score baseado na distância média
        Ideal: 8-12 (60 números / 6 = 10)
        """
        numeros_sorted = sorted(numeros)
        distancias = []
        
        for i in range(len(numeros_sorted) - 1):
            distancias.append(numeros_sorted[i+1] - numeros_sorted[i])
        
        media_dist = np.mean(distancias)
        
        # Score máximo se distância média entre 8-12
        if 8 <= media_dist <= 12:
            return 60
        elif 6 <= media_dist <= 14:
            return 40
        else:
            return 20


class NumerosExtremosIndicador:
    """
    Analisa presença de números extremos
    - Baixos: 1-10
    - Altos: 51-60
    Ideal: 1-2 extremos por jogo
    """
    
    @staticmethod
    def calcular_score(numeros: List[int], historico: pd.DataFrame = None) -> float:
        """
        Score baseado em extremos
        """
        baixos = len([n for n in numeros if n <= 10])
        altos = len([n for n in numeros if n >= 51])
        total_extremos = baixos + altos
        
        # Ideal: 1-2 extremos
        if total_extremos == 1 or total_extremos == 2:
            return 50
        elif total_extremos == 0 or total_extremos == 3:
            return 30
        else:
            return 10


class PadraoDezenaIndicador:
    """
    Analisa padrão de terminações (unidades 0-9)
    Ideal: Dezenas variadas (não repetir muito)
    """
    
    @staticmethod
    def calcular_score(numeros: List[int], historico: pd.DataFrame = None) -> float:
        """
        Score baseado na variedade de dezenas
        """
        dezenas = [n % 10 for n in numeros]
        dezenas_unicas = len(set(dezenas))
        
        # Quanto mais variado, melhor
        if dezenas_unicas >= 5:  # 5-6 dezenas diferentes
            return 60
        elif dezenas_unicas >= 4:
            return 40
        else:
            return 20


class CicloAparicaoIndicador:
    """
    Analisa ciclo de aparição dos números
    Números com ciclo médio são bons candidatos
    """
    
    @staticmethod
    def calcular_score(numeros: List[int], historico: pd.DataFrame) -> float:
        """
        Score baseado no ciclo de aparição
        """
        if historico is None or len(historico) < 10:
            return 30  # Score neutro se não há histórico
        
        # Calcular frequência nos últimos 100 sorteios
        ultimos_100 = historico.tail(100)
        
        freq = Counter()
        for idx in range(len(ultimos_100)):
            try:
                for j in range(1, 7):
                    num = ultimos_100.iloc[idx].get(f'Bola{j}')
                    if pd.notna(num):
                        freq[int(num)] += 1
            except:
                pass
        
        # Frequência média
        media_freq = np.mean(list(freq.values())) if freq else 0
        
        # Score para números com frequência próxima à média
        score = 0
        for num in numeros:
            f = freq.get(num, 0)
            if 0.8 * media_freq <= f <= 1.2 * media_freq:
                score += 10
            elif 0.6 * media_freq <= f <= 1.4 * media_freq:
                score += 5
        
        return min(score, 60)  # Máximo 60


# ============================================================================
# FUNÇÃO PARA CALCULAR TODOS OS 5 INDICADORES
# ============================================================================

def calcular_indicadores_extras(numeros: List[int], historico: pd.DataFrame = None) -> Dict[str, float]:
    """
    Calcula todos os 5 indicadores extras
    
    Returns:
        Dicionário com scores de cada indicador
    """
    return {
        'Sequencias': SequenciasIndicador.calcular_score(numeros, historico),
        'DistanciaMedia': DistanciaMediaIndicador.calcular_score(numeros, historico),
        'NumerosExtremos': NumerosExtremosIndicador.calcular_score(numeros, historico),
        'PadraoDezena': PadraoDezenaIndicador.calcular_score(numeros, historico),
        'CicloAparicao': CicloAparicaoIndicador.calcular_score(numeros, historico)
    }


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Teste com jogo de exemplo
    numeros_teste = [5, 13, 22, 34, 41, 55]
    
    scores = calcular_indicadores_extras(numeros_teste)
    
    print("📊 Scores dos Indicadores Extras:")
    for ind, score in scores.items():
        print(f"   {ind}: {score}")
    
    print(f"\n   Total: {sum(scores.values())}")
