"""
Analisador de Grupos de Indicadores - Meg

aCLI v6.1

Implementa análise combinatória para identificar quais grupos de indicadores
funcionam melhor juntos para prever sorteios da Mega-Sena.

Autor: MegaCLI Team
Data: 01/02/2026
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from itertools import combinations
from collections import defaultdict

from src.core.previsao_30n import selecionar_top_30_numeros, refinar_selecao


def analisar_grupos_indicadores(
    df_historico: pd.DataFrame,
    todos_indicadores: List[Dict],
    tamanho_grupo: int = 5,
    n_jogos_teste: int = 50
) -> List[Dict]:
    """
    Testa combinações de indicadores para encontrar melhores grupos.
    
    Args:
        df_historico: DataFrame com histórico completo
        todos_indicadores: Lista com todos os indicadores disponíveis
        tamanho_grupo: Quantos indicadores por grupo (default: 5)
        n_jogos_teste: Quantos jogos usar para teste (default: 50)
        
    Returns:
        Lista com top 10 melhores grupos ordenados por taxa de sucesso
    """
    print(f"\n🔬 Analisando grupos de {tamanho_grupo} indicadores...")
    print(f"   📊 Testando em {n_jogos_teste} jogos históricos...")
    
    # Limitar número de combinações para evitar explosão combinatória
    max_combinacoes = 100
    
    # Pegar apenas os top N indicadores para combinar
    top_n = min(15, len(todos_indicadores))
    top_indicadores = sorted(todos_indicadores, key=lambda x: x.get('relevancia', 0), reverse=True)[:top_n]
    
    nomes_indicadores = [ind['indicador'] for ind in top_indicadores]
    
    resultados = []
    combinacoes_testadas = 0
    
    print(f"   🧮 Gerando combinações de {tamanho_grupo} a partir de {len(nomes_indicadores)} indicadores...")
    
    for combo in combinations(top_indicadores, tamanho_grupo):
        if combinacoes_testadas >= max_combinacoes:
            print(f"   ⚠️  Limite de {max_combinacoes} combinações atingido")
            break
        
        # Criar ranking apenas com esses indicadores
        ranking_combo = list(combo)
        
        # Testar em últimos N jogos
        taxa_sucesso = _validar_ranking_historico(ranking_combo, df_historico, n_jogos_teste)
        
        resultados.append({
            'grupo': [ind['indicador'] for ind in combo],
            'taxa_acerto_top30': taxa_sucesso['top30'],
            'taxa_acerto_top20': taxa_sucesso['top20'],
            'taxa_acerto_top10': taxa_sucesso['top10'],
            'media_acertos': taxa_sucesso['media_acertos'],
            'jogos_testados': taxa_sucesso['n_jogos']
        })
        
        combinacoes_testadas += 1
        
        # Progresso
        if combinacoes_testadas % 20 == 0:
            print(f"   ... {combinacoes_testadas} combinações testadas")
    
    # Ordenar por taxa de sucesso TOP 30
    resultados.sort(key=lambda x: (x['taxa_acerto_top30'], x['media_acertos']), reverse=True)
    
    print(f"   ✅ Análise concluída! {combinacoes_testadas} combinações testadas")
    
    return resultados[:10]  # Top 10 melhores grupos


def _validar_ranking_historico(
    ranking: List[Dict],
    df_historico: pd.DataFrame,
    n_jogos: int
) -> Dict[str, float]:
    """
    Valida um ranking em N jogos históricos.
    
    Args:
        ranking: Ranking de indicadores
        df_historico: Histórico completo
        n_jogos: Quantos jogos testar
        
    Returns:
        Dict com taxas de sucesso
    """
    inicio = max(0, len(df_historico) - n_jogos - 50)  # Margem para indicadores
    acertos_top30 = []
    acertos_top20 = []
    acertos_top10 = []
    
    for i in range(inicio, len(df_historico)):
        df_corte = df_historico.iloc[:i]
        jogo_real = df_historico.iloc[i]
        
        # Extrair números reais
        try:
            numeros_reais = set([jogo_real[f'Bola{k}'] for k in range(1, 7)])
        except:
            continue
        
        # Gerar previsão
        try:
            top_30, scores_30, _, _ = selecionar_top_30_numeros(
                df_corte,
                ranking,
                verbose=False
            )
            
            lista_refinada, _ = refinar_selecao(top_30, scores_30, df_corte, verbose=False)
            
            # Contar acertos em cada nível
            acertos_top30.append(len(numeros_reais & set(lista_refinada[:30])))
            acertos_top20.append(len(numeros_reais & set(lista_refinada[:20])))
            acertos_top10.append(len(numeros_reais & set(lista_refinada[:10])))
        except:
            continue
    
    if not acertos_top30:
        return {
            'top30': 0,
            'top20': 0,
            'top10': 0,
            'media_acertos': 0,
            'n_jogos': 0
        }
    
    return {
        'top30': np.mean([a >= 4 for a in acertos_top30]),  # Taxa de 4+ acertos
        'top20': np.mean([a >= 3 for a in acertos_top20]),
        'top10': np.mean([a >= 2 for a in acertos_top10]),
        'media_acertos': np.mean(acertos_top30),
        'n_jogos': len(acertos_top30)
    }


def identificar_grupo_otimo(
    resultados_grupos: List[Dict],
    criterio: str = 'top30'
) -> Dict:
    """
    Identifica o grupo ótimo baseado no critério escolhido.
    
    Args:
        resultados_grupos: Lista de resultados da análise de grupos
        criterio: 'top30', 'top20', 'top10' ou 'media_acertos'
        
    Returns:
        Dict com o melhor grupo
    """
    if not resultados_grupos:
        return None
    
    campo_criterio = f'taxa_acerto_{criterio}' if criterio != 'media_acertos' else 'media_acertos'
    melhor = max(resultados_grupos, key=lambda x: x.get(campo_criterio, 0))
    
    return melhor


# Exports
__all__ = [
    'analisar_grupos_indicadores',
    'identificar_grupo_otimo'
]
