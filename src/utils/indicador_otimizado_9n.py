"""
Indicador Otimizado para 9 Números - MegaCLI v6.0

Indicador específico otimizado para seleção de universo de 9 números.
Foco em alta precisão e co-ocorrência.

Autor: MegaCLI Team
Data: 22/01/2026
Versão: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from src.utils.parametros_otimizacao import ParametrosOtimizacao
from src.utils.indicador_probabilidade_universo import IndicadorProbabilidadeUniverso


class IndicadorOtimizado9N(IndicadorProbabilidadeUniverso):
    """
    Indicador otimizado para seleção de 9 números.
    
    Características:
    - Foco em alta precisão
    - Peso maior para co-ocorrência (números que aparecem juntos)
    - Janela menor (50 jogos) para capturar tendências recentes
    - Bônus alto para recência
    """
    
    def __init__(self, parametros: ParametrosOtimizacao = None):
        """
        Inicializa indicador com parâmetros otimizados para 9 números.
        
        Args:
            parametros: Parâmetros customizados (opcional)
        """
        # Parâmetros padrão otimizados para 9 números
        if parametros is None:
            parametros = ParametrosOtimizacao(
                peso_frequencia=0.30,
                peso_co_ocorrencia=0.45,  # Maior peso
                peso_tendencia=0.25,
                janela_principal=50,  # Janela menor
                janela_recente=10,
                bonus_recencia=1.20,  # Bônus maior
                bonus_consistencia=1.08,
                penalidade_ausencia=0.88
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
            print(f"\n🎯 Calculando Scores com Indicador Otimizado 9N")
            print(f"   Parâmetros:")
            print(f"   • Peso Frequência: {self.parametros.peso_frequencia:.2f}")
            print(f"   • Peso Co-ocorrência: {self.parametros.peso_co_ocorrencia:.2f} (ALTO)")
            print(f"   • Peso Tendência: {self.parametros.peso_tendencia:.2f}")
            print(f"   • Janela: {self.parametros.janela_principal} jogos (CURTA)")
        
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
    
    def selecionar_top_9(
        self,
        df_historico: pd.DataFrame,
        verbose: bool = True
    ) -> Tuple[List[int], Dict[int, float]]:
        """
        Seleciona os 9 números com maior score.
        
        Args:
            df_historico: DataFrame com histórico
            verbose: Se True, exibe informações
            
        Returns:
            Tupla (lista de 9 números, dicionário {número: score})
        """
        # Calcular scores
        scores = self.calcular_scores_otimizado(df_historico, verbose=False)
        
        # Ordenar e pegar top 9
        numeros_ordenados = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_9 = [num for num, _ in numeros_ordenados[:9]]
        scores_top_9 = {num: score for num, score in numeros_ordenados[:9]}
        
        if verbose:
            print(f"\n📊 Top 9 Números Selecionados (Indicador Otimizado):")
            print(f"\n{'#':<4} {'Número':<8} {'Score':<10} {'Barra':<30}")
            print("-"*70)
            
            max_score = max(scores_top_9.values())
            for i, (num, score) in enumerate(numeros_ordenados[:9], 1):
                barra_len = int((score / max_score) * 25)
                barra = '█' * barra_len
                print(f"{i:<4} {num:02d}       {score:>6.2f}     {barra}")
            
            print(f"\n📋 Universo: {'-'.join(f'{n:02d}' for n in sorted(top_9))}")
        
        return sorted(top_9), scores_top_9
    
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
__all__ = ['IndicadorOtimizado9N']


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando Indicador Otimizado 9N...\n")
    
    import sys
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(PROJECT_ROOT))
    
    from src.core.config import ARQUIVO_HISTORICO
    
    # Carregar histórico
    df_historico = pd.read_excel(str(ARQUIVO_HISTORICO), sheet_name='MEGA SENA')
    print(f"✅ {len(df_historico)} sorteios carregados")
    
    # Criar indicador
    indicador = IndicadorOtimizado9N()
    
    print("\nParâmetros do indicador:")
    print(indicador.get_parametros())
    
    # Selecionar top 9
    numeros, scores = indicador.selecionar_top_9(df_historico, verbose=True)
    
    # Validar cobertura
    validacao = indicador.validar_cobertura(
        numeros,
        df_historico,
        janela_validacao=100,
        verbose=True
    )
    
    print(f"\n✅ Indicador 9N funcionando corretamente!")
    print(f"   Cobertura 6: {validacao['cobertura_6']:.1f}%")
    print(f"   Recomendação: {validacao['recomendacao']}\n")
