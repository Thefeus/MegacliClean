"""
Indicadores Avançados para Análise da Mega-Sena

Este módulo implementa os 5 novos indicadores sugeridos pela IA:
1. Raiz Digital
2. Variação da Soma
3. Conjugação
4. Repetição do Concurso Anterior
5. Frequência Mensal

Cada indicador herda de IndicadorBase e implementa:
- calcular_score(): Retorna pontuação 0-100
- gerar_relatorio(): Retorna dict com análise detalhada
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from datetime import datetime


# ============================================================================
# CLASSE BASE
# ============================================================================

class IndicadorBase(ABC):
    """Classe base para todos os indicadores"""
    
    def __init__(self, historico: pd.DataFrame):
        """
        Args:
            historico: DataFrame com histórico de sorteios
        """
        self.historico = historico.copy()
        self.nome = self.__class__.__name__.replace('Indicador', '')
        
    @abstractmethod
    def calcular_score(self, numeros: List[int]) -> float:
        """
        Calcula score para conjunto de números
        
        Args:
            numeros: Lista de 6 números a pontuar
            
        Returns:
            Score entre 0-100
        """
        pass
    
    @abstractmethod
    def gerar_relatorio(self) -> Dict[str, Any]:
        """
        Gera relatório detalhado do indicador
        
        Returns:
            Dict com análise e insights
        """
        pass
    
    def _normalizar_score(self, valor: float, min_val: float, max_val: float) -> float:
        """Normaliza valor para escala 0-100"""
        if max_val == min_val:
            return 50.0
        return ((valor - min_val) / (max_val - min_val)) * 100


# ============================================================================
# INDICADOR 1: RAIZ DIGITAL
# ============================================================================

class RaizDigitalIndicador(IndicadorBase):
    """
    Calcula e analisa raízes digitais dos números.
    
    Raiz digital = soma iterada dos dígitos até obter um único dígito.
    Ex: 38 -> 3+8=11 -> 1+1=2
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str] = None):
        super().__init__(historico)
        self.ball_cols = ball_cols or ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
        self.distribuicao_historica = self._calcular_distribuicao_historica()
        
    def _calcular_raiz_digital(self, numero: int) -> int:
        """Calcula raiz digital de um número"""
        while numero >= 10:
            numero = sum(int(d) for d in str(numero))
        return numero
    
    def _calcular_distribuicao_historica(self) -> Dict[int, int]:
        """Calcula distribuição histórica de raízes digitais"""
        raizes = defaultdict(int)
        
        for _, row in self.historico.iterrows():
            for col in self.ball_cols:
                if pd.notna(row[col]):
                    num = int(row[col])
                    raiz = self._calcular_raiz_digital(num)
                    raizes[raiz] += 1
        
        return dict(raizes)
    
    def calcular_score(self, numeros: List[int]) -> float:
        """
        Pontua baseado na distribuição de raízes digitais
        
        Estratégia: Favorece distribuição que imita histórico
        """
        # Raízes dos números propostos
        raizes_propostas = Counter(self._calcular_raiz_digital(n) for n in numeros)
        
        # Distribuição esperada (normalizada)
        total_historico = sum(self.distribuicao_historica.values())
        freq_esperada = {
            r: count / total_historico 
            for r, count in self.distribuicao_historica.items()
        }
        
        # Calcular diferença (KL divergence simplificada)
        diferencas = []
        for raiz in range(1, 10):
            esperada = freq_esperada.get(raiz, 0) * 6  # Esperado para 6 números
            obtida = raizes_propostas.get(raiz, 0)
            diff = abs(esperada - obtida)
            diferencas.append(diff)
        
        # Score: quanto menor a diferença, melhor
        diferenca_media = np.mean(diferencas)
        # Normalizar: diferença 0 = 100, diferença > 2 = 0
        score = max(0, 100 - (diferenca_media * 50))
        
        return score
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório sobre distribuição de raízes digitais"""
        total = sum(self.distribuicao_historica.values())
        
        return {
            'indicador': self.nome,
            'distribuicao_historica': self.distribuicao_historica,
            'frequencia_percentual': {
                r: (count / total * 100) 
                for r, count in self.distribuicao_historica.items()
            },
            'raiz_mais_comum': max(self.distribuicao_historica.items(), key=lambda x: x[1])[0],
            'insight': 'Raízes digitais mais frequentes: ' + 
                      ', '.join(str(r) for r, _ in sorted(
                          self.distribuicao_historica.items(), 
                          key=lambda x: -x[1]
                      )[:3])
        }


# ============================================================================
# INDICADOR 2: VARIAÇÃO DA SOMA
# ============================================================================

class VariacaoSomaIndicador(IndicadorBase):
    """
    Analisa desvio da soma total em relação à média histórica.
    
    Sorteios tendem a ter soma em faixa específica (140-220).
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str] = None):
        super().__init__(historico)
        self.ball_cols = ball_cols or ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
        self.somas_historicas = self._calcular_somas_historicas()
        self.media_soma = np.mean(self.somas_historicas)
        self.desvio_soma = np.std(self.somas_historicas)
        
    def _calcular_somas_historicas(self) -> List[int]:
        """Calcula soma de cada sorteio histórico"""
        somas = []
        for _, row in self.historico.iterrows():
            soma = sum(int(row[col]) for col in self.ball_cols if pd.notna(row[col]))
            somas.append(soma)
        return somas
    
    def calcular_score(self, numeros: List[int]) -> float:
        """
        Pontua baseado na proximidade com soma média
        
        Score alto: soma próxima da média ± 1 desvio padrão
        """
        soma = sum(numeros)
        
        # Distância em desvios padrão
        distancia_dp = abs(soma - self.media_soma) / self.desvio_soma
        
        # Score decresce com distância
        # 0 DP = 100, 1 DP = 70, 2 DP = 30, 3+ DP = 0
        if distancia_dp <= 1:
            score = 100 - (distancia_dp * 30)
        elif distancia_dp <= 2:
            score = 70 - ((distancia_dp - 1) * 40)
        elif distancia_dp <= 3:
            score = 30 - ((distancia_dp - 2) * 30)
        else:
            score = 0
        
        return max(0, min(100, score))
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório sobre distribuição de somas"""
        return {
            'indicador': self.nome,
            'media_soma': round(self.media_soma, 2),
            'desvio_padrao': round(self.desvio_soma, 2),
            'faixa_ideal': (
                round(self.media_soma - self.desvio_soma, 0),
                round(self.media_soma + self.desvio_soma, 0)
            ),
            'faixa_aceitavel': (
                round(self.media_soma - 2 * self.desvio_soma, 0),
                round(self.media_soma + 2 * self.desvio_soma, 0)
            ),
            'soma_minima': min(self.somas_historicas),
            'soma_maxima': max(self.somas_historicas),
            'insight': f'Somas ideais: {round(self.media_soma - self.desvio_soma, 0)} a {round(self.media_soma + self.desvio_soma, 0)}'
        }


# ============================================================================
# INDICADOR 3: CONJUGAÇÃO
# ============================================================================

class ConjugacaoIndicador(IndicadorBase):
    """
    Detecta números conjugados (vizinhos ou em padrão).
    
    Exemplos: (1,2), (21,22), (5,10,15)
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str] = None):
        super().__init__(historico)
        self.ball_cols = ball_cols or ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
        self.pares_conjugados = self._detectar_pares_conjugados()
        
    def _detectar_pares_conjugados(self) -> Dict[tuple, int]:
        """Detecta frequência de pares conjugados no histórico"""
        pares = defaultdict(int)
        
        for _, row in self.historico.iterrows():
            numeros = sorted([int(row[col]) for col in self.ball_cols if pd.notna(row[col])])
            
            # Verifica todos os pares
            for i in range(len(numeros) - 1):
                for j in range(i + 1, len(numeros)):
                    n1, n2 = numeros[i], numeros[j]
                    
                    # Par conjugado se diferença = 1, 5, 10
                    if n2 - n1 in [1, 5, 10]:
                        pares[(n1, n2)] += 1
        
        return dict(pares)
    
    def calcular_score(self, numeros: List[int]) -> float:
        """
        Pontua baseado na presença de números conjugados
        
        Score aumenta se há pares que aparecem historicamente
        """
        numeros_sorted = sorted(numeros)
        score = 50.0  # Score base
        
        # Verifica pares consecutivos
        consecutivos = 0
        for i in range(len(numeros_sorted) - 1):
            if numeros_sorted[i + 1] - numeros_sorted[i] == 1:
                consecutivos += 1
        
        # Bonus por pares consecutivos (mas não demais)
        if consecutivos == 1:
            score += 20
        elif consecutivos == 2:
            score += 10
        elif consecutivos >= 3:
            score -= 10  # Penalidade por muitos consecutivos
        
        # Verifica conjugações históricas
        bonus_historico = 0
        for i in range(len(numeros_sorted) - 1):
            for j in range(i + 1, len(numeros_sorted)):
                par = (numeros_sorted[i], numeros_sorted[j])
                if par in self.pares_conjugados:
                    freq = self.pares_conjugados[par]
                    bonus_historico += min(freq / 10, 5)  # Máx 5 pontos por par
        
        score += bonus_historico
        
        return max(0, min(100, score))
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório sobre conjugações"""
        top_pares = sorted(
            self.pares_conjugados.items(),
            key=lambda x: -x[1]
        )[:10]
        
        return {
            'indicador': self.nome,
            'total_pares_conjugados': len(self.pares_conjugados),
            'top_10_pares': {
                f'{p[0]}-{p[1]}': freq 
                for p, freq in top_pares
            },
            'insight': 'Pares mais frequentes: ' + 
                      ', '.join(f'{p[0]}-{p[1]}' for p, _ in top_pares[:3])
        }


# ============================================================================
# INDICADOR 4: REPETIÇÃO DO CONCURSO ANTERIOR
# ============================================================================

class RepeticaoAnteriorIndicador(IndicadorBase):
    """
    Analisa quantos números se repetem do concurso anterior.
    
    Historicamente, 1-3 números tendem a se repetir.
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str] = None):
        super().__init__(historico)
        self.ball_cols = ball_cols or ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
        self.distribuicao_repeticoes = self._calcular_distribuicao_repeticoes()
        
    def _calcular_distribuicao_repeticoes(self) -> Dict[int, int]:
        """Calcula quantos números se repetem entre sorteios consecutivos"""
        repeticoes = defaultdict(int)
        
        for i in range(1, len(self.historico)):
            atual = set(int(self.historico.iloc[i][col]) for col in self.ball_cols if pd.notna(self.historico.iloc[i][col]))
            anterior = set(int(self.historico.iloc[i-1][col]) for col in self.ball_cols if pd.notna(self.historico.iloc[i-1][col]))
            
            num_repeticoes = len(atual.intersection(anterior))
            repeticoes[num_repeticoes] += 1
        
        return dict(repeticoes)
    
    def calcular_score(self, numeros: List[int], sorteio_anterior: Optional[List[int]] = None) -> float:
        """
        Pontua baseado na quantidade de repetições esperadas
        
        Args:
            numeros: Números a pontuar
            sorteio_anterior: Números do último sorteio (se disponível)
        """
        if sorteio_anterior is None:
            # Se não temos sorteio anterior, usar score médio
            return 50.0
        
        # Conta repetições
        repeticoes = len(set(numeros).intersection(set(sorteio_anterior)))
        
        # Frequência esperada
        total = sum(self.distribuicao_repeticoes.values())
        freq_esperada = {
            r: count / total 
            for r, count in self.distribuicao_repeticoes.items()
        }
        
        # Score baseado na frequência histórica dessa quantidade de repetições
        score_base = freq_esperada.get(repeticoes, 0) * 100
        
        # Ajustar para favorecer 1-3 repetições (padrão mais comum)
        if 1 <= repeticoes <= 3:
            score = score_base * 1.2
        else:
            score = score_base * 0.8
        
        return max(0, min(100, score))
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório sobre repetições"""
        total = sum(self.distribuicao_repeticoes.values())
        
        return {
            'indicador': self.nome,
            'distribuicao': self.distribuicao_repeticoes,
            'frequencia_percentual': {
                r: round(count / total * 100, 1)
                for r, count in self.distribuicao_repeticoes.items()
            },
            'repeticoes_mais_comum': max(self.distribuicao_repeticoes.items(), key=lambda x: x[1])[0],
            'insight': f'Mais comum: {max(self.distribuicao_repeticoes.items(), key=lambda x: x[1])[0]} repetições ({max(self.distribuicao_repeticoes.values()) / total * 100:.1f}%)'
        }


# ============================================================================
# INDICADOR 5: FREQUÊNCIA MENSAL
# ============================================================================

class FrequenciaMensalIndicador(IndicadorBase):
    """
    Analisa frequência de números por mês do ano.
    
    Detecta se certos números aparecem mais em determinados meses.
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str] = None, data_col: str = 'Data'):
        super().__init__(historico)
        self.ball_cols = ball_cols or ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
        self.data_col = data_col
        self.freq_mensal = self._calcular_frequencia_mensal()
        
    def _calcular_frequencia_mensal(self) -> Dict[int, Dict[int, int]]:
        """Calcula frequência de cada número por mês"""
        freq = defaultdict(lambda: defaultdict(int))
        
        for _, row in self.historico.iterrows():
            if pd.notna(row.get(self.data_col)):
                try:
                    # Tenta parsear a data
                    if isinstance(row[self.data_col], str):
                        data = pd.to_datetime(row[self.data_col], dayfirst=True)
                    else:
                        data = row[self.data_col]
                    
                    mes = data.month
                    
                    for col in self.ball_cols:
                        if pd.notna(row[col]):
                            num = int(row[col])
                            freq[num][mes] += 1
                except:
                    continue
        
        return {num: dict(meses) for num, meses in freq.items()}
    
    def calcular_score(self, numeros: List[int], mes_proximo_sorteio: Optional[int] = None) -> float:
        """
        Pontua baseado na frequência dos números no mês do próximo sorteio
        
        Args:
            numeros: Números a pontuar
            mes_proximo_sorteio: Mês (1-12) do próximo sorteio
        """
        if mes_proximo_sorteio is None:
            mes_proximo_sorteio = datetime.now().month
        
        scores_individuais = []
        
        for num in numeros:
            if num in self.freq_mensal:
                freq_mes = self.freq_mensal[num].get(mes_proximo_sorteio, 0)
                freq_total = sum(self.freq_mensal[num].values())
                
                if freq_total > 0:
                    # Score = quão acima/abaixo da média está este mês
                    freq_esperada = freq_total / 12  # Média se uniforme
                    ratio = freq_mes / freq_esperada if freq_esperada > 0 else 1.0
                    
                    # Converter ratio para score 0-100
                    # ratio=1.0 (média) = 50, ratio=1.5 (50% acima) = 75, ratio=2.0 = 100
                    score_num = min(100, 50 + (ratio - 1.0) * 50)
                    scores_individuais.append(score_num)
                else:
                    scores_individuais.append(50)
            else:
                scores_individuais.append(50)
        
        return np.mean(scores_individuais) if scores_individuais else 50.0
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório sobre frequências mensais"""
        # Encontrar números com maior variação mensal
        variacoes = {}
        for num, meses in self.freq_mensal.items():
            if len(meses) > 0:
                valores = list(meses.values())
                variacoes[num] = np.std(valores)
        
        top_variacoes = sorted(variacoes.items(), key=lambda x: -x[1])[:5]
        
        return {
            'indicador': self.nome,
            'numeros_com_sazonalidade': [num for num, _ in top_variacoes],
            'insight': 'Números com maior variação mensal: ' + 
                      ', '.join(str(num) for num, _ in top_variacoes),
            'mes_atual': datetime.now().month,
            'total_numeros_analisados': len(self.freq_mensal)
        }


# ============================================================================
# UTILITÁRIOS
# ============================================================================

def criar_todos_indicadores(historico: pd.DataFrame, ball_cols: List[str] = None) -> Dict[str, IndicadorBase]:
    """
    Cria instância de todos os indicadores
    
    Args:
        historico: DataFrame com histórico
        ball_cols: Lista de colunas com as bolas
        
    Returns:
        Dict com todos os indicadores instanciados
    """
    ball_cols = ball_cols or ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    return {
        'RaizDigital': RaizDigitalIndicador(historico, ball_cols),
        'VariacaoSoma': VariacaoSomaIndicador(historico, ball_cols),
        'Conjugacao': ConjugacaoIndicador(historico, ball_cols),
        'RepeticaoAnterior': RepeticaoAnteriorIndicador(historico, ball_cols),
        'FrequenciaMensal': FrequenciaMensalIndicador(historico, ball_cols)
    }


def gerar_relatorio_completo(indicadores: Dict[str, IndicadorBase]) -> Dict[str, Any]:
    """
    Gera relatório completo de todos os indicadores
    
    Args:
        indicadores: Dict de indicadores
        
    Returns:
        Dict com todos os relatórios
    """
    return {
        nome: indicador.gerar_relatorio()
        for nome, indicador in indicadores.items()
    }


if __name__ == "__main__":
    # Teste básico
    print("Módulo de Indicadores Avançados carregado com sucesso!")
    print(f"Indicadores disponíveis: {len(criar_todos_indicadores.__code__.co_consts)}")
