"""
Análise de Frequência Mínima para Mega-Sena

Este módulo implementa métodos para detectar padrões de frequência mínima
e janelas de oportunidade, mesmo em sorteios genuinamente aleatórios.

Inclui:
1. IntervaloMinimoAnalyzer - Calcula intervalos mínimos entre aparições
2. TaxaDecaimentoAnalyzer - Modela decaimento de probabilidade
3. JanelaOportunidadeDetector - Identifica períodos favoráveis
4. MarkovAnalyzer - Análise de cadeias de Markov

Baseado em análise estatística rigorosa documentada em:
analise_frequencia_minima.md
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class IntervaloStats:
    """Estatísticas de intervalo para um número"""
    numero: int
    intervalo_medio: float
    intervalo_minimo: int
    intervalo_maximo: int
    desvio_padrao: float
    ultimo_intervalo: int
    em_atraso: bool
    score_oportunidade: float


@dataclass
class JanelaOportunidade:
    """Representa uma janela de oportunidade para um número"""
    numero: int
    probabilidade_base: float
    probabilidade_ajustada: float
    melhoria_percentual: float
    razoes: List[str]
    confianca: float


# ============================================================================
# ANALYZER 1: INTERVALO MÍNIMO
# ============================================================================

class IntervaloMinimoAnalyzer:
    """
    Analisa intervalos entre aparições de cada número.
    
    Detecta números "atrasados" que estão além do intervalo esperado.
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str]):
        """
        Args:
            historico: DataFrame com histórico de sorteios
            ball_cols: Lista de colunas com as bolas
        """
        self.historico = historico.copy()
        self.ball_cols = ball_cols
        self.stats_cache = {}
        
    def _obter_indices_aparicoes(self, numero: int) -> List[int]:
        """Retorna índices de todas as aparições de um número"""
        indices = []
        for idx, row in self.historico.iterrows():
            for col in self.ball_cols:
                if pd.notna(row[col]) and int(row[col]) == numero:
                    indices.append(idx)
                    break  # Conta apenas uma vez por sorteio
        return indices
    
    def calcular_stats_numero(self, numero: int) -> IntervaloStats:
        """Calcula estatísticas de intervalo para um número"""
        
        if numero in self.stats_cache:
            return self.stats_cache[numero]
        
        aparicoes = self._obter_indices_aparicoes(numero)
        
        if len(aparicoes) < 2:
            # Número apareceu 0 ou 1 vez - caso especial
            ultimo_idx = len(self.historico) - 1
            ultimo_intervalo = ultimo_idx - aparicoes[0] if aparicoes else ultimo_idx
            
            stats = IntervaloStats(
                numero=numero,
                intervalo_medio=float('inf'),
                intervalo_minimo=0,
                intervalo_maximo=0,
                desvio_padrao=0,
                ultimo_intervalo=ultimo_intervalo,
                em_atraso=True,
                score_oportunidade=1.0
            )
        else:
            # Calcular intervalos entre aparições consecutivas
            intervalos = [aparicoes[i+1] - aparicoes[i] for i in range(len(aparicoes) - 1)]
            
            intervalo_medio = np.mean(intervalos)
            intervalo_minimo = np.min(intervalos)
            intervalo_maximo = np.max(intervalos)
            desvio_padrao = np.std(intervalos)
            
            # Último intervalo (desde última aparição até agora)
            ultimo_idx = len(self.historico) - 1
            ultimo_intervalo = ultimo_idx - aparicoes[-1]
            
            # Em atraso se último intervalo > média + 2*DP
            limiar_atraso = intervalo_medio + 2 * desvio_padrao
            em_atraso = ultimo_intervalo > limiar_atraso
            
            # Score de oportunidade (0-1)
            # Quanto maior o atraso relativo, maior o score
            if desvio_padrao > 0:
                atraso_relativo = (ultimo_intervalo - intervalo_medio) / desvio_padrao
                score = min(1.0, max(0.0, atraso_relativo / 3.0))  # Normalizar para 0-1
            else:
                score = 0.5
            
            stats = IntervaloStats(
                numero=numero,
                intervalo_medio=intervalo_medio,
                intervalo_minimo=intervalo_minimo,
                intervalo_maximo=intervalo_maximo,
                desvio_padrao=desvio_padrao,
                ultimo_intervalo=ultimo_intervalo,
                em_atraso=em_atraso,
                score_oportunidade=score
            )
        
        self.stats_cache[numero] = stats
        return stats
    
    def obter_numeros_atrasados(self, top_n: int = 10) -> List[Tuple[int, IntervaloStats]]:
        """Retorna os top N números mais atrasados"""
        todos_stats = [(n, self.calcular_stats_numero(n)) for n in range(1, 61)]
        
        # Ordenar por score de oportunidade (descendente)
        ordenados = sorted(todos_stats, key=lambda x: x[1].score_oportunidade, reverse=True)
        
        return ordenados[:top_n]
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório completo de intervalos"""
        atrasados = self.obter_numeros_atrasados(10)
        
        return {
            'analyzer': 'IntervaloMinimo',
            'top_10_atrasados': [
                {
                    'numero': num,
                    'ultimo_intervalo': stats.ultimo_intervalo,
                    'intervalo_medio': round(stats.intervalo_medio, 1),
                    'score': round(stats.score_oportunidade, 2)
                }
                for num, stats in atrasados
            ],
            'insight': f"Números mais atrasados: {', '.join(str(n) for n, _ in atrasados[:5])}"
        }


# ============================================================================
# ANALYZER 2: TAXA DE DECAIMENTO
# ============================================================================

class TaxaDecaimentoAnalyzer:
    """
    Modela probabilidade de aparição baseada em taxa de decaimento exponencial.
    
    P(aparição em t) = baseline * (1 - e^(-λ*t))
    onde t = tempo desde última aparição
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str]):
        self.historico = historico.copy()
        self.ball_cols = ball_cols
        self.baseline_prob = 6 / 60  # Probabilidade base (~10%)
        self.lambda_cache = {}
        
    def _calcular_lambda(self, numero: int) -> float:
        """
        Calcula taxa de decaimento (λ) para um número.
        
        λ é estimado ajustando curva exponencial aos dados históricos.
        """
        if numero in self.lambda_cache:
            return self.lambda_cache[numero]
        
        # Obter todas as aparições
        aparicoes = []
        for idx, row in self.historico.iterrows():
            for col in self.ball_cols:
                if pd.notna(row[col]) and int(row[col]) == numero:
                    aparicoes.append(idx)
                    break
        
        if len(aparicoes) < 5:
            # Poucos dados, usar λ médio
            lambda_val = 0.1
        else:
            # Calcular intervalos
            intervalos = [aparicoes[i+1] - aparicoes[i] for i in range(len(aparicoes) - 1)]
            
            # λ ≈ 1 / intervalo_medio (aproximação simples)
            lambda_val = 1.0 / np.mean(intervalos) if np.mean(intervalos) > 0 else 0.1
        
        self.lambda_cache[numero] = lambda_val
        return lambda_val
    
    def calcular_probabilidade(self, numero: int, tempo_desde_ultima: int) -> float:
        """
        Calcula probabilidade ajustada por decaimento
        
        Args:
            numero: Número a analisar
            tempo_desde_ultima: Sorteios desde última aparição
            
        Returns:
            Probabilidade ajustada (0-1)
        """
        lambda_val = self._calcular_lambda(numero)
        
        # P(t) = baseline * (1 - e^(-λ*t))
        prob = self.baseline_prob * (1 - np.exp(-lambda_val * tempo_desde_ultima))
        
        return min(1.0, prob)
    
    def obter_probabilidades_ajustadas(self) -> Dict[int, float]:
        """Retorna probabilidades ajustadas para todos os números"""
        ultimo_idx = len(self.historico) - 1
        probabilidades = {}
        
        for num in range(1, 61):
            # Encontrar última aparição
            ultima_aparicao = -1
            for idx in range(ultimo_idx, -1, -1):
                for col in self.ball_cols:
                    if pd.notna(self.historico.iloc[idx][col]) and int(self.historico.iloc[idx][col]) == num:
                        ultima_aparicao = idx
                        break
                if ultima_aparicao != -1:
                    break
            
            tempo = ultimo_idx - ultima_aparicao if ultima_aparicao != -1 else ultimo_idx
            probabilidades[num] = self.calcular_probabilidade(num, tempo)
        
        return probabilidades
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório de probabilidades"""
        probs = self.obter_probabilidades_ajustadas()
        
        # Top 10 probabilidades
        top_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'analyzer': 'TaxaDecaimento',
            'top_10_probabilidades': [
                {'numero': num, 'probabilidade': round(prob, 3)}
                for num, prob in top_probs
            ],
            'probabilidade_media': round(np.mean(list(probs.values())), 3),
            'insight': f"Maiores probabilidades: {', '.join(str(n) for n, _ in top_probs[:5])}"
        }


# ============================================================================
# ANALYZER 3: JANELA DE OPORTUNIDADE
# ============================================================================

class JanelaOportunidadeDetector:
    """
    Detecta janelas de oportunidade combinando múltiplos sinais.
    
    Janela = período onde número tem probabilidade acima do baseline.
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str]):
        self.historico = historico.copy()
        self.ball_cols = ball_cols
        self.intervalo_analyzer = IntervaloMinimoAnalyzer(historico, ball_cols)
        self.decaimento_analyzer = TaxaDecaimentoAnalyzer(historico, ball_cols)
        
    def detectar_janela(self, numero: int) -> Optional[JanelaOportunidade]:
        """
        Detecta se número está em janela de oportunidade
        
        Returns:
            JanelaOportunidade se detectada, None caso contrário
        """
        # Obter stats de intervalo
        stats_intervalo = self.intervalo_analyzer.calcular_stats_numero(numero)
        
        # Obter probabilidade por decaimento
        prob_decaimento = self.decaimento_analyzer.obter_probabilidades_ajustadas()[numero]
        
        # Probabilidade base
        prob_base = 6 / 60  # ~0.10
        
        # Combinar sinais
        razoes = []
        bonus_total = 0
        
        # Sinal 1: Atraso
        if stats_intervalo.em_atraso:
            bonus_atraso = stats_intervalo.score_oportunidade * 0.05  # Até +5%
            bonus_total += bonus_atraso
            razoes.append(f"Atraso de {stats_intervalo.ultimo_intervalo} sorteios ({stats_intervalo.score_oportunidade:.0%} do limiar)")
        
        # Sinal 2: Decaimento favorável
        if prob_decaimento > prob_base * 1.2:  # 20% acima do baseline
            bonus_decaimento = (prob_decaimento - prob_base)
            bonus_total += bonus_decaimento
            razoes.append(f"Taxa de decaimento favorável (+{(prob_decaimento/prob_base - 1)*100:.0f}%)")
        
        # Calcular probabilidade ajustada
        prob_ajustada = prob_base + bonus_total
        
        # Janela detectada se melhoria >= 10%
        if prob_ajustada >= prob_base * 1.1 and razoes:
            melhoria = (prob_ajustada / prob_base - 1) * 100
            
            # Confiança baseada em quantos sinais confirmam
            confianca = min(1.0, len(razoes) / 2.0)
            
            return JanelaOportunidade(
                numero=numero,
                probabilidade_base=prob_base,
                probabilidade_ajustada=min(0.2, prob_ajustada),  # Cap em 20%
                melhoria_percentual=melhoria,
                razoes=razoes,
                confianca=confianca
            )
        
        return None
    
    def detectar_todas_janelas(self) -> List[JanelaOportunidade]:
        """Detecta janelas para todos os números"""
        janelas = []
        
        for num in range(1, 61):
            janela = self.detectar_janela(num)
            if janela:
                janelas.append(janela)
        
        # Ordenar por probabilidade ajustada (descendente)
        janelas.sort(key=lambda j: j.probabilidade_ajustada, reverse=True)
        
        return janelas
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório de janelas detectadas"""
        janelas = self.detectar_todas_janelas()
        
        return {
            'analyzer': 'JanelaOportunidade',
            'total_janelas_detectadas': len(janelas),
            'top_10_janelas': [
                {
                    'numero': j.numero,
                    'prob_ajustada': round(j.probabilidade_ajustada, 3),
                    'melhoria': f"+{j.melhoria_percentual:.0f}%",
                    'confianca': round(j.confianca, 2),
                    'razoes': j.razoes
                }
                for j in janelas[:10]
            ],
            'insight': f"{len(janelas)} números em janela de oportunidade"
        }


# ============================================================================
# ANALYZER 4: MARKOV
# ============================================================================

class MarkovAnalyzer:
    """
    Análise de cadeias de Markov - probabilidades condicionais.
    
    P(número X no próximo sorteio | X apareceu há N sorteios atrás)
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str]):
        self.historico = historico.copy()
        self.ball_cols = ball_cols
        self.matriz_transicao = self._calcular_matriz_transicao()
        
    def _calcular_matriz_transicao(self) -> Dict[int, Dict[int, int]]:
        """
        Calcula matriz de transição
        
        matriz[numero][delay] = quantas vezes o número apareceu após 'delay' sorteios
        """
        matriz = defaultdict(lambda: defaultdict(int))
        
        for numero in range(1, 61):
            aparicoes = []
            for idx, row in self.historico.iterrows():
                for col in self.ball_cols:
                    if pd.notna(row[col]) and int(row[col]) == numero:
                        aparicoes.append(idx)
                        break
            
            # Calcular delays entre aparições
            for i in range(len(aparicoes) - 1):
                delay = aparicoes[i+1] - aparicoes[i]
                matriz[numero][delay] += 1
        
        return dict(matriz)
    
    def calcular_probabilidade_condicional(self, numero: int, delay_atual: int) -> float:
        """
        Calcula P(aparecer no próximo | delay atual = delay_atual)
        
        Args:
            numero: Número a analisar
            delay_atual: Sorteios desde última aparição
            
        Returns:
            Probabilidade condicional
        """
        if numero not in self.matriz_transicao:
            return 0.1  # Baseline
        
        delays = self.matriz_transicao[numero]
        
        if not delays:
            return 0.1
        
        # Probabilidade empírica para esse delay específico
        total_aparicoes = sum(delays.values())
        aparicoes_nesse_delay = delays.get(delay_atual, 0)
        
        if total_aparicoes > 0:
            prob = aparicoes_nesse_delay / total_aparicoes
        else:
            prob = 0.1
        
        # Suavizar com baseline
        prob_suavizada = 0.7 * prob + 0.3 * 0.1
        
        return prob_suavizada
    
    def obter_recomendacoes_markov(self) -> List[Tuple[int, float]]:
        """Retorna números com maior probabilidade por Markov"""
        ultimo_idx = len(self.historico) - 1
        probabilidades = []
        
        for num in range(1, 61):
            # Encontrar delay atual
            delay = None
            for idx in range(ultimo_idx, -1, -1):
                for col in self.ball_cols:
                    if pd.notna(self.historico.iloc[idx][col]) and int(self.historico.iloc[idx][col]) == num:
                        delay = ultimo_idx - idx
                        break
                if delay is not None:
                    break
            
            if delay is None:
                delay = ultimo_idx  # Nunca apareceu
            
            prob = self.calcular_probabilidade_condicional(num, delay)
            probabilidades.append((num, prob))
        
        # Ordenar por probabilidade
        probabilidades.sort(key=lambda x: x[1], reverse=True)
        
        return probabilidades[:15]
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório de análise Markov"""
        recomendacoes = self.obter_recomendacoes_markov()
        
        return {
            'analyzer': 'Markov',
            'top_15_markov': [
                {'numero': num, 'probabilidade': round(prob, 3)}
                for num, prob in recomendacoes
            ],
            'insight': f"Markov sugere: {', '.join(str(n) for n, _ in recomendacoes[:5])}"
        }


# ============================================================================
# CLASSE PRINCIPAL: FREQUENCIA MINIMA ANALYZER
# ============================================================================

class FrequenciaMinimaAnalyzer:
    """
    Combina todos os 4 analyzers para análise completa de frequência mínima.
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str]):
        self.historico = historico.copy()
        self.ball_cols = ball_cols
        
        # Criar analyzers
        self.intervalo = IntervaloMinimoAnalyzer(historico, ball_cols)
        self.decaimento = TaxaDecaimentoAnalyzer(historico, ball_cols)
        self.janela = JanelaOportunidadeDetector(historico, ball_cols)
        self.markov = MarkovAnalyzer(historico, ball_cols)
    
    def analisar_numero(self, numero: int) -> Dict[str, Any]:
        """Análise completa de um número específico"""
        stats_intervalo = self.intervalo.calcular_stats_numero(numero)
        janela = self.janela.detectar_janela(numero)
        
        # Delay atual
        ultimo_idx = len(self.historico) - 1
        delay = None
        for idx in range(ultimo_idx, -1, -1):
            for col in self.ball_cols:
                if pd.notna(self.historico.iloc[idx][col]) and int(self.historico.iloc[idx][col]) == numero:
                    delay = ultimo_idx - idx
                    break
            if delay is not None:
                break
        
        if delay is None:
            delay = ultimo_idx
        
        prob_markov = self.markov.calcular_probabilidade_condicional(numero, delay)
        
        # Score final combinado
        score_final = (
            0.3 * stats_intervalo.score_oportunidade +
            0.25 * (janela.confianca if janela else 0) +
            0.25 * min(1.0, prob_markov / 0.1) +  # Normalizar
            0.2 * (1.0 if stats_intervalo.em_atraso else 0.3)
        )
        
        return {
            'numero': numero,
            'score_final': score_final,
            'em_janela_oportunidade': janela is not None,
            'stats_intervalo': stats_intervalo,
            'janela': janela,
            'prob_markov': prob_markov,
            'recomendacao': 'PRIORIZAR' if score_final > 0.7 else ('CONSIDERAR' if score_final > 0.5 else 'NEUTRO')
        }
    
    def gerar_previsao(self, top_n: int = 15) -> List[Dict[str, Any]]:
        """
        Gera lista de números recomendados baseado em frequência mínima
        
        Returns:
            Lista dos top N números com análise completa
        """
        analises = [self.analisar_numero(n) for n in range(1, 61)]
        
        # Ordenar por score final
        analises.sort(key=lambda a: a['score_final'], reverse=True)
        
        return analises[:top_n]
    
    def gerar_relatorio_completo(self) -> Dict[str, Any]:
        """Gera relatório completo de todos os analyzers"""
        return {
            'FrequenciaMinima': {
                'intervalo_minimo': self.intervalo.gerar_relatorio(),
                'taxa_decaimento': self.decaimento.gerar_relatorio(),
                'janelas_oportunidade': self.janela.gerar_relatorio(),
                'markov': self.markov.gerar_relatorio()
            }
        }


if __name__ == "__main__":
    print("Módulo de Análise de Frequência Mínima carregado com sucesso!")
    print("Analyzers disponíveis: IntervaloMinimo, TaxaDecaimento, JanelaOportunidade, Markov")
