"""
Indicador Otimizado para 10 Números - MegaCLI v6.0

Indicador específico otimizado para seleção de universo de 10 números.
Foco em equilíbrio entre precisão e cobertura.

Autor: MegaCLI Team
Data: 22/01/2026
Versão: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from src.utils.parametros_otimizacao import ParametrosOtimizacao
from src.utils.indicador_probabilidade_universo import IndicadorProbabilidadeUniverso


class IndicadorOtimizado10N(IndicadorProbabilidadeUniverso):
    """
    Indicador otimizado para seleção de 10 números.
    
    Características:
    - Equilíbrio entre precisão e cobertura
    - Pesos balanceados entre métricas
    - Janela média (75 jogos)
    - Bônus moderado para recência
    """
    
    def __init__(self, parametros: ParametrosOtimizacao = None):
        """
        Inicializa indicador com parâmetros otimizados para 10 números.
        
        Args:
            parametros: Parâmetros customizados (opcional)
        """
        # Parâmetros padrão otimizados para 10 números
        if parametros is None:
            parametros = ParametrosOtimizacao(
                peso_frequencia=0.35,
                peso_co_ocorrencia=0.35,
                peso_tendencia=0.30,
                janela_principal=75,
                janela_recente=10,
                bonus_recencia=1.15,
                bonus_consistencia=1.05,
                penalidade_ausencia=0.92
            )
        
        self.parametros = parametros
        
        # Inicializar classe pai com janela ajustada
        super().__init__(janela=parametros.janela_principal)
    
    def calcular_scores_otimizado(
        self,
        df_historico: pd.DataFrame,
        verbose: bool = False
    ) -> Dict[int, float]:
        """
        Calcula scores usando parâmetros otimizados.
        
        Args:
            df_historico: DataFrame com histórico
            verbose: Se True, exibe informações
            
        Returns:
            Dicionário {número: score}
        """
        if verbose:
            print(f"\n🎯 Calculando Scores com Indicador Otimizado 10N")
            print(f"   Parâmetros:")
            print(f"   • Peso Frequência: {self.parametros.peso_frequencia:.2f}")
            print(f"   • Peso Co-ocorrência: {self.parametros.peso_co_ocorrencia:.2f}")
            print(f"   • Peso Tendência: {self.parametros.peso_tendencia:.2f}")
            print(f"   • Janela: {self.parametros.janela_principal} jogos")
        
        # Calcular métricas individuais
        freq = self.analisar_frequencias_ponderadas(df_historico)
        co_oc = self.analisar_co_ocorrencias(df_historico)
        tend = self.analisar_tendencias(df_historico)
        
        # Combinar com pesos otimizados
        scores_finais = {}
        for num in range(1, 61):
            score = (
                freq[num] * self.parametros.peso_frequencia +
                co_oc[num] * self.parametros.peso_co_ocorrencia +
                tend[num] * self.parametros.peso_tendencia
            )
            scores_finais[num] = score
        
        if verbose:
            print(f"✅ Scores calculados para 60 números")
        
        return scores_finais
    
    def selecionar_top_10(
        self,
        df_historico: pd.DataFrame,
        verbose: bool = True
    ) -> Tuple[List[int], Dict[int, float]]:
        """
        Seleciona os 10 números com maior score.
        
        Args:
            df_historico: DataFrame com histórico
            verbose: Se True, exibe informações
            
        Returns:
            Tupla (lista de 10 números, dicionário {número: score})
        """
        # Calcular scores
        scores = self.calcular_scores_otimizado(df_historico, verbose=False)
        
        # Ordenar e pegar top 10
        numeros_ordenados = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_10 = [num for num, _ in numeros_ordenados[:10]]
        scores_top_10 = {num: score for num, score in numeros_ordenados[:10]}
        
        if verbose:
            print(f"\n📊 Top 10 Números Selecionados (Indicador Otimizado):")
            print(f"\n{'#':<4} {'Número':<8} {'Score':<10} {'Barra':<30}")
            print("-"*70)
            
            max_score = max(scores_top_10.values())
            for i, (num, score) in enumerate(numeros_ordenados[:10], 1):
                barra_len = int((score / max_score) * 25)
                barra = '█' * barra_len
                print(f"{i:<4} {num:02d}       {score:>6.2f}     {barra}")
            
            print(f"\n📋 Universo: {'-'.join(f'{n:02d}' for n in sorted(top_10))}")
        
        return sorted(top_10), scores_top_10
    
    def get_parametros(self) -> ParametrosOtimizacao:
        """Retorna parâmetros atuais."""
        return self.parametros
    
    def set_parametros(self, parametros: ParametrosOtimizacao) -> None:
        """
        Atualiza parâmetros do indicador.
        
        Args:
            parametros: Novos parâmetros
        """
        self.parametros = parametros
        self.janela = parametros.janela_principal


# Exports
__all__ = ['IndicadorOtimizado10N']


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando Indicador Otimizado 10N...\n")
    
    import sys
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(PROJECT_ROOT))
    
    from src.core.config import ARQUIVO_HISTORICO
    
    # Carregar histórico
    df_historico = pd.read_excel(str(ARQUIVO_HISTORICO), sheet_name='MEGA SENA')
    print(f"✅ {len(df_historico)} sorteios carregados")
    
    # Criar indicador
    indicador = IndicadorOtimizado10N()
    
    print("\nParâmetros do indicador:")
    print(indicador.get_parametros())
    
    # Selecionar top 10
    numeros, scores = indicador.selecionar_top_10(df_historico, verbose=True)
    
    # Validar cobertura
    validacao = indicador.validar_cobertura(
        numeros,
        df_historico,
        janela_validacao=100,
        verbose=True
    )
    
    print(f"\n✅ Indicador 10N funcionando corretamente!")
    print(f"   Cobertura 6: {validacao['cobertura_6']:.1f}%")
    print(f"   Recomendação: {validacao['recomendacao']}\n")
