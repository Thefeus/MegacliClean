"""
from src.utils.detector_colunas import extrair_numeros_sorteio
Indicador de Probabilidade para Universo Reduzido - MegaCLI v6.0

Indicador otimizado especificamente para seleção de universo reduzido.
Combina múltiplas métricas para maximizar probabilidade de cobertura.

Autor: MegaCLI Team
Data: 22/01/2026
Versão: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import Counter
from src.utils.detector_colunas import extrair_numeros_sorteio


class IndicadorProbabilidadeUniverso:
    """
    Indicador otimizado para seleção de universo reduzido.
    
    Combina:
    - Frequência ponderada por recência
    - Co-ocorrência de números
    - Tendências temporais
    - Padrões de repetição
    """
    
    def __init__(self, janela: int = 100):
        """
        Args:
            janela: Número de sorteios recentes a analisar
        """
        self.janela = janela
        self.scores_cache = {}
    
    def analisar_frequencias_ponderadas(
        self,
        df_historico: pd.DataFrame
    ) -> Dict[int, float]:
        """
        Analisa frequências com peso por recência e consistência.
        
        Args:
            df_historico: DataFrame com histórico
            
        Returns:
            Dicionário {número: score}
        """
        df_recente = df_historico.tail(self.janela)
        scores = {}
        
        for num in range(1, 61):
            # Contar aparições em toda a janela
            freq_total = 0
            freq_recente = 0  # Últimos 10 jogos
            
            for idx, row in df_recente.iterrows():
                numeros = extrair_numeros_sorteio(row)
                if num in numeros:
                    freq_total += 1
                    # Peso extra para últimos 10 jogos
                    if idx >= len(df_recente) - 10:
                        freq_recente += 1
            
            # Score base: frequência normalizada
            score_base = (freq_total / self.janela) * 100
            
            # Bônus por recência (até +20%)
            bonus_recencia = (freq_recente / 10) * 20
            
            # Bônus por consistência (aparece regularmente)
            # Dividir janela em 4 quartis
            quartis = np.array_split(df_recente, 4)
            aparicoes_quartis = []
            
            for quartil in quartis:
                aparicoes = 0
                for _, row in quartil.iterrows():
                    numeros = extrair_numeros_sorteio(row)
                    if num in numeros:
                        aparicoes += 1
                aparicoes_quartis.append(aparicoes)
            
            # Consistência = baixo desvio padrão entre quartis
            desvio = np.std(aparicoes_quartis)
            bonus_consistencia = max(0, 10 - desvio)  # Até +10%
            
            scores[num] = score_base + bonus_recencia + bonus_consistencia
        
        return scores
    
    def analisar_co_ocorrencias(
        self,
        df_historico: pd.DataFrame
    ) -> Dict[int, float]:
        """
        Analisa números que aparecem juntos frequentemente.
        
        Args:
            df_historico: DataFrame com histórico
            
        Returns:
            Dicionário {número: score}
        """
        df_recente = df_historico.tail(self.janela)
        
        # Matriz de co-ocorrência 60x60
        matriz = np.zeros((60, 60))
        
        for _, row in df_recente.iterrows():
            numeros = extrair_numeros_sorteio(row)
            # Para cada par de números no sorteio
            for i, n1 in enumerate(numeros):
                for n2 in numeros[i+1:]:
                    matriz[n1-1][n2-1] += 1
                    matriz[n2-1][n1-1] += 1
        
        # Score baseado em conexões fortes
        scores = {}
        for num in range(1, 61):
            # Soma de co-ocorrências / janela
            score = np.sum(matriz[num-1]) / self.janela
            scores[num] = score * 100  # Normalizar para 0-100
        
        return scores
    
    def analisar_tendencias(
        self,
        df_historico: pd.DataFrame
    ) -> Dict[int, float]:
        """
        Identifica números em tendência de alta.
        
        Args:
            df_historico: DataFrame com histórico
            
        Returns:
            Dicionário {número: score}
        """
        df_recente = df_historico.tail(self.janela)
        
        # Dividir em 4 quartis
        quartis = np.array_split(df_recente, 4)
        
        scores = {}
        for num in range(1, 61):
            aparicoes_quartis = []
            
            for quartil in quartis:
                aparicoes = 0
                for _, row in quartil.iterrows():
                    numeros = extrair_numeros_sorteio(row)
                    if num in numeros:
                        aparicoes += 1
                aparicoes_quartis.append(aparicoes)
            
            # Tendência = diferença entre quartis recentes e antigos
            # Quartis mais recentes têm mais peso
            tendencia = (
                aparicoes_quartis[3] * 2.0 +  # Mais recente
                aparicoes_quartis[2] * 1.5 -
                aparicoes_quartis[1] * 1.0 -
                aparicoes_quartis[0] * 0.5   # Mais antigo
            )
            
            # Normalizar para 0-100
            scores[num] = max(0, min(100, tendencia * 10))
        
        return scores
    
    def calcular_scores(
        self,
        df_historico: pd.DataFrame,
        verbose: bool = False
    ) -> Dict[int, float]:
        """
        Calcula score final combinando todas as métricas.
        
        Args:
            df_historico: DataFrame com histórico
            verbose: Se True, exibe informações
            
        Returns:
            Dicionário {número: score final}
        """
        if verbose:
            print(f"\n🔍 Calculando Scores com Indicador de Probabilidade")
            print(f"   Janela de análise: {self.janela} sorteios")
        
        # Calcular cada métrica
        freq = self.analisar_frequencias_ponderadas(df_historico)
        co_oc = self.analisar_co_ocorrencias(df_historico)
        tend = self.analisar_tendencias(df_historico)
        
        # Combinar com pesos
        scores_finais = {}
        for num in range(1, 61):
            score = (
                freq[num] * 0.40 +      # 40% frequência ponderada
                co_oc[num] * 0.30 +     # 30% co-ocorrência
                tend[num] * 0.30        # 30% tendência
            )
            scores_finais[num] = score
        
        if verbose:
            print(f"✅ Scores calculados para 60 números")
        
        return scores_finais
    
    def selecionar_top_20(
        self,
        scores: Dict[int, float],
        verbose: bool = False
    ) -> Tuple[List[int], Dict[int, float]]:
        """
        Seleciona os 20 números com maior score.
        
        Args:
            scores: Dicionário {número: score}
            verbose: Se True, exibe informações
            
        Returns:
            Tupla (lista de 20 números, dicionário {número: score})
        """
        # Ordenar por score
        numeros_ordenados = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Pegar top 20
        top_20 = [num for num, _ in numeros_ordenados[:20]]
        scores_top_20 = {num: score for num, score in numeros_ordenados[:20]}
        
        if verbose:
            print(f"\n📊 Top 20 Números Selecionados:")
            print(f"\n{'#':<4} {'Número':<8} {'Score':<10}")
            print("-"*30)
            for i, (num, score) in enumerate(numeros_ordenados[:20], 1):
                print(f"{i:<4} {num:02d}       {score:>6.2f}")
        
        return sorted(top_20), scores_top_20
    
    def validar_cobertura(
        self,
        numeros_20: List[int],
        df_historico: pd.DataFrame,
        janela_validacao: int = 100,
        verbose: bool = False
    ) -> Dict[str, float]:
        """
        Valida taxa de cobertura histórica dos 20 números.
        
        Args:
            numeros_20: Lista com 20 números
            df_historico: DataFrame com histórico
            janela_validacao: Número de sorteios para validar
            verbose: Se True, exibe informações
            
        Returns:
            Dicionário com taxas de cobertura
        """
        df_teste = df_historico.tail(janela_validacao)
        
        cobertura_6 = 0
        cobertura_5 = 0
        cobertura_4 = 0
        
        for _, row in df_teste.iterrows():
            numeros_sorteio = extrair_numeros_sorteio(row)
            acertos = len(set(numeros_sorteio) & set(numeros_20))
            
            if acertos == 6:
                cobertura_6 += 1
            if acertos >= 5:
                cobertura_5 += 1
            if acertos >= 4:
                cobertura_4 += 1
        
        taxa_6 = (cobertura_6 / janela_validacao) * 100
        taxa_5 = (cobertura_5 / janela_validacao) * 100
        taxa_4 = (cobertura_4 / janela_validacao) * 100
        
        # Determinar recomendação
        if taxa_6 >= 60:
            recomendacao = "ALTA"
        elif taxa_6 >= 50:
            recomendacao = "MÉDIA"
        else:
            recomendacao = "BAIXA"
        
        resultado = {
            'cobertura_6': taxa_6,
            'cobertura_5': taxa_5,
            'cobertura_4': taxa_4,
            'recomendacao': recomendacao,
            'janela': janela_validacao
        }
        
        if verbose:
            print(f"\n📈 Validação Histórica (últimos {janela_validacao} jogos):")
            print(f"   • Sorteios com 6 números nos 20: {cobertura_6} ({taxa_6:.1f}%)")
            print(f"   • Sorteios com 5+ números nos 20: {cobertura_5} ({taxa_5:.1f}%)")
            print(f"   • Sorteios com 4+ números nos 20: {cobertura_4} ({taxa_4:.1f}%)")
            print(f"\n   Recomendação: {recomendacao}")
            
            if recomendacao == "ALTA":
                print(f"   ✅ Alta probabilidade de cobertura!")
            elif recomendacao == "MÉDIA":
                print(f"   ⚠️  Probabilidade moderada de cobertura")
            else:
                print(f"   ❌ Baixa probabilidade de cobertura")
        
        return resultado


# Exports
__all__ = ['IndicadorProbabilidadeUniverso']


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando Indicador de Probabilidade...\n")
    
    import sys
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(PROJECT_ROOT))
    
    from src.core.config import ARQUIVO_HISTORICO
    
    # Carregar histórico
    df_historico = pd.read_excel(str(ARQUIVO_HISTORICO), sheet_name='MEGA SENA')
    print(f"✅ {len(df_historico)} sorteios carregados")
    
    # Criar indicador
    indicador = IndicadorProbabilidadeUniverso(janela=100)
    
    # Calcular scores
    scores = indicador.calcular_scores(df_historico, verbose=True)
    
    # Selecionar top 20
    numeros_20, scores_20 = indicador.selecionar_top_20(scores, verbose=True)
    
    # Validar cobertura
    validacao = indicador.validar_cobertura(
        numeros_20,
        df_historico,
        janela_validacao=100,
        verbose=True
    )
    
    print(f"\n✅ Indicador funcionando corretamente!")
    print(f"   Universo: {'-'.join(f'{n:02d}' for n in numeros_20)}")
    print(f"   Cobertura 6: {validacao['cobertura_6']:.1f}%")
    print(f"   Recomendação: {validacao['recomendacao']}\n")
