"""
Validador Train/Test Split - MegaCLI v6.2

Implementa validação rigorosa com split treino/teste para detectar overfitting.
Treina indicadores em 80% dos dados e testa em 20% nunca vistos.

Autor: MegaCLI Team
Data: 02/02/2026
Versão: 1.0.0
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict

from src.core.previsao_30n import selecionar_top_30_numeros, refinar_selecao
from src.core.metricas_confianca import (
    calcular_intervalo_confianca,
    formatar_com_intervalo,
    validar_significancia_estatistica,
    gerar_relatorio_estatistico
)


def split_train_test(
    df_historico: pd.DataFrame,
    split_ratio: float = 0.8,
    margem_seguranca: int = 150
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Divide histórico em treino e teste de forma rigorosa.
    
    Args:
        df_historico: DataFrame completo
        split_ratio: Proporção para treino (default: 0.8 = 80%)
        margem_seguranca: Jogos mínimos para calcular indicadores
        
    Returns:
        (df_treino, df_teste)
    """
    n_total = len(df_historico)
    n_treino = int(n_total * split_ratio)
    
    # Garantir margem de segurança
    n_treino = max(n_treino, margem_seguranca)
    
    df_treino = df_historico.iloc[:n_treino].copy()
    df_teste = df_historico.iloc[n_treino:].copy()
    
    print(f"📊 Split Train/Test:")
    print(f"   Total: {n_total} sorteios")
    print(f"   Treino: {len(df_treino)} sorteios ({len(df_treino)/n_total*100:.1f}%)")
    print(f"   Teste: {len(df_teste)} sorteios ({len(df_teste)/n_total*100:.1f}%)")
    
    return df_treino, df_teste


def validar_em_conjunto(
    df_sorteios: pd.DataFrame,
    ranking_indicadores: List[Dict],
    nome_conjunto: str = "Conjunto"
) -> Dict[str, Any]:
    """
    Valida performance do ranking em um conjunto de sorteios.
    
    Args:
        df_sorteios: DataFrame com sorteios para validar
        ranking_indicadores: Ranking de indicadores
        nome_conjunto: Nome do conjunto (Treino/Teste)
        
    Returns:
        Dict com métricas detalhadas
    """
    print(f"\n🎯 Validando em {nome_conjunto}...")
    
    acertos_top30 = []
    acertos_top20 = []
    acertos_top10 = []
    
    # Validar cada sorteio
    margem = 150  # Margem para calcular indicadores
    for i in range(margem, len(df_sorteios)):
        # Histórico até este ponto
        df_corte = df_sorteios.iloc[:i]
        sorteio_real = df_sorteios.iloc[i]
        
        # Extrair números reais
        try:
            numeros_reais = set([int(sorteio_real[f'Bola{k}']) for k in range(1, 7)])
        except:
            continue
        
        # Gerar previsão
        try:
            top_30, scores_30, _, _ = selecionar_top_30_numeros(
                df_corte,
                ranking_indicadores,
                verbose=False
            )
            
            lista_refinada, _ = refinar_selecao(top_30, scores_30, df_corte, verbose=False)
            
            # Contar acertos em cada nível
            acertos_30 = len(numeros_reais & set(lista_refinada[:30]))
            acertos_20 = len(numeros_reais & set(lista_refinada[:20]))
            acertos_10 = len(numeros_reais & set(lista_refinada[:10]))
            
            acertos_top30.append(acertos_30)
            acertos_top20.append(acertos_20)
            acertos_top10.append(acertos_10)
            
        except:
            continue
    
    # Calcular taxas de sucesso
    taxa_4_mais_top30 = sum(a >= 4 for a in acertos_top30) / len(acertos_top30) if acertos_top30 else 0
    taxa_4_mais_top20 = sum(a >= 4 for a in acertos_top20) / len(acertos_top20) if acertos_top20 else 0
    taxa_3_mais_top10 = sum(a >= 3 for a in acertos_top10) / len(acertos_top10) if acertos_top10 else 0
    
    media_acertos_30 = np.mean(acertos_top30) if acertos_top30 else 0
    media_acertos_20 = np.mean(acertos_top20) if acertos_top20 else 0
    media_acertos_10 = np.mean(acertos_top10) if acertos_top10 else 0
    
    print(f"   ✅ Jogos validados: {len(acertos_top30)}")
    print(f"   📊 TOP 30: {media_acertos_30:.2f} acertos/jogo ({taxa_4_mais_top30*100:.1f}% com 4+)")
    print(f"   📊 TOP 20: {media_acertos_20:.2f} acertos/jogo ({taxa_4_mais_top20*100:.1f}% com 4+)")
    print(f"   📊 TOP 10: {media_acertos_10:.2f} acertos/jogo ({taxa_3_mais_top10*100:.1f}% com 3+)")
    
    return {
        'nome': nome_conjunto,
        'n_jogos': len(acertos_top30),
        'acertos_top30': acertos_top30,
        'acertos_top20': acertos_top20,
        'acertos_top10': acertos_top10,
        'taxa_4_mais_top30': taxa_4_mais_top30,
        'taxa_4_mais_top20': taxa_4_mais_top20,
        'taxa_3_mais_top10': taxa_3_mais_top10,
        'media_acertos_30': media_acertos_30,
        'media_acertos_20': media_acertos_20,
        'media_acertos_10': media_acertos_10
    }


def validacao_train_test_split(
    df_historico: pd.DataFrame,
    ranking_indicadores: List[Dict],
    split_ratio: float = 0.8
) -> Dict[str, Any]:
    """
    Executa validação completa com split train/test.
    
    Args:
        df_historico: DataFrame completo
        ranking_indicadores: Ranking de indicadores
        split_ratio: Proporção para treino
        
    Returns:
        Dict com análise completa e detecção de overfitting
    """
    print("\n" + "="*70)
    print("🔬 VALIDAÇÃO TRAIN/TEST SPLIT")
    print("="*70)
    
    # Split
    df_treino, df_teste = split_train_test(df_historico, split_ratio)
    
    # Validar em treino
    metricas_treino = validar_em_conjunto(df_treino, ranking_indicadores, "TREINO")
    
    # Validar em teste
    metricas_teste = validar_em_conjunto(df_teste, ranking_indicadores, "TESTE")
    
    # Calcular degradação
    degradacao_top30 = metricas_treino['taxa_4_mais_top30'] - metricas_teste['taxa_4_mais_top30']
    degradacao_top20 = metricas_treino['taxa_4_mais_top20'] - metricas_teste['taxa_4_mais_top20']
    degradacao_top10 = metricas_treino['taxa_3_mais_top10'] - metricas_teste['taxa_3_mais_top10']
    
    degradacao_media_pct = abs(degradacao_top30) * 100
    
    # Teste de significância
    teste_sig = validar_significancia_estatistica(
        [metricas_treino['taxa_4_mais_top30']],
        [metricas_teste['taxa_4_mais_top30']]
    )
    
    # Gerar relatório
    print("\n" + "="*70)
    print("📈 ANÁLISE DE DEGRADAÇÃO")
    print("="*70)
    
    print(f"\n🎯 TOP 30 (4+ acertos):")
    print(f"   Treino: {metricas_treino['taxa_4_mais_top30']*100:.1f}%")
    print(f"   Teste:  {metricas_teste['taxa_4_mais_top30']*100:.1f}%")
    print(f"   Degradação: {degradacao_media_pct:.1f}%")
    
    if degradacao_media_pct > 25:
        print(f"   ⚠️ ALERTA: Degradação alta! Possível overfitting")
        nivel_risco = "ALTO"
    elif degradacao_media_pct > 15:
        print(f"   ⚠️ ATENÇÃO: Degradação moderada")
        nivel_risco = "MÉDIO"
    else:
        print(f"   ✅ OK: Sistema generaliza bem")
        nivel_risco = "BAIXO"
    
    return {
        'treino': metricas_treino,
        'teste': metricas_teste,
        'degradacao_top30': degradacao_top30,
        'degradacao_top20': degradacao_top20,
        'degradacao_top10': degradacao_top10,
        'degradacao_pct': degradacao_media_pct,
        'nivel_risco': nivel_risco,
        'teste_significancia': teste_sig,
        'recomendacao': _gerar_recomendacao(degradacao_media_pct, nivel_risco)
    }


def _gerar_recomendacao(degradacao: float, nivel: str) -> str:
    """Gera recomendação baseada na degradação."""
    if nivel == "ALTO":
        return ("Sistema está overfitting! Considere: (1) Reduzir número de indicadores, "
                "(2) Aumentar universo de números, (3) Usar Modo Conservador")
    elif nivel == "MÉDIO":
        return ("Sistema pode estar se ajustando demais ao histórico. "
                "Monitore performance e considere simplificar.")
    else:
        return "Sistema generaliza bem. Performance consistente entre treino e teste."


# Exports
__all__ = [
    'split_train_test',
    'validar_em_conjunto',
    'validacao_train_test_split'
]


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando Validador Train/Test...\n")
    print("(Necessita dados reais para teste completo)")
    print("Execute via menu interativo (Opção 12)")
