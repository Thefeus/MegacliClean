"""
Ranking de Indicadores - MegaCLI v5.0

Ordena indicadores por relevância baseado em estatísticas históricas.
"""

import pandas as pd
from typing import Dict, List
from validacao.analisador_historico import EstatisticasIndicador


def calcular_relevancia(estat: Dict) -> float:
    """
    Calcula score de relevância de um indicador.
    
    Critérios:
    - Taxa acerto 4+ (40%)
    - Taxa acerto 3+ (30%)
    - Consistência/baixo desvio (20%)
    - Score médio (10%)
    
    Returns:
        Score 0-100
    """
    # Pesos dos critérios
    score = 0.0
    
    # Taxa de acerto 4+ (peso 40%)
    score += estat['taxa_acerto_4+'] * 0.4
    
    # Taxa de acerto 3+ (peso 30%)
    score += estat['taxa_acerto_3+'] * 0.3
    
    # Consistência: menor desvio = melhor (peso 20%)
    # Normalizar desvio (0-30 → 100-0)
    consistencia = max(0, 100 - (estat['desvio_padrao'] / 30 * 100))
    score += consistencia * 0.2
    
    # Score médio (peso 10%)
    score += estat['score_medio'] * 0.1
    
    return min(score, 100.0)


def criar_ranking(estatisticas: Dict[str, Dict]) -> List[Dict]:
    """
    Cria ranking ordenado de indicadores.
    
    Args:
        estatisticas: Dict {nome: estat_dict}
        
    Returns:
        Lista ordenada de dicts com ranking
    """
    ranking = []
    
    for nome, estat in estatisticas.items():
        relevancia = calcular_relevancia(estat)
        
        ranking.append({
            'indicador': nome,
            'relevancia': round(relevancia, 2),
            'taxa_4+': estat['taxa_acerto_4+'],
            'taxa_3+': estat['taxa_acerto_3+'],
            'score_medio': estat['score_medio'],
            'desvio_padrao': estat['desvio_padrao'],
            'total_jogos': estat['total_jogos']
        })
    
    # Ordenar por relevância (maior primeiro)
    ranking.sort(key=lambda x: x['relevancia'], reverse=True)
    
    # Adicionar posição
    for i, item in enumerate(ranking, 1):
        item['rank'] = i
        # Estrelas baseadas em relevância
        if item['relevancia'] >= 80:
            item['estrelas'] = '⭐⭐⭐⭐⭐'
        elif item['relevancia'] >= 70:
            item['estrelas'] = '⭐⭐⭐⭐'
        elif item['relevancia'] >= 60:
            item['estrelas'] = '⭐⭐⭐'
        elif item['relevancia'] >= 50:
            item['estrelas'] = '⭐⭐'
        else:
            item['estrelas'] = '⭐'
    
    return ranking


def imprimir_ranking(ranking: List[Dict], top_n: int = 15):
    """Imprime ranking formatado"""
    print("\n" + "="*80)
    print(f"🏆 RANKING DE INDICADORES (Top {top_n})")
    print("="*80)
    print(f"{'Rank':<6} {'Indicador':<30} {'Relev.':<8} {' Taxa4+':<8} {'Estrelas'}")
    print("-"*80)
    
    for item in ranking[:top_n]:
        print(f"{item['rank']:<6} {item['indicador']:<30} {item['relevancia']:<8.1f} {item['taxa_4+']:<8.1f}% {item['estrelas']}")
    
    print("="*80 + "\n")


def gerar_dataframe_ranking(ranking: List[Dict]) -> pd.DataFrame:
    """Converte ranking para DataFrame"""
    return pd.DataFrame(ranking)
