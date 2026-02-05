"""
from src.utils.detector_colunas import extrair_numeros_sorteio
Analisador de Universo Super Reduzido (9 Números) - MegaCLI v6.0

Extensão do analisador de universo reduzido para trabalhar com apenas
9 números mais prováveis, aplicando a mesma metodologia dos 20 números.

Autor: MegaCLI Team
Data: 22/01/2026
Versão: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any
from src.utils.indicador_probabilidade_universo import IndicadorProbabilidadeUniverso
import math


def selecionar_top_9_numeros(
    df_historico: pd.DataFrame,
    ranking: List[Dict],
    top_indicadores: int = 10,
    janela_analise: int = 100,
    verbose: bool = True
) -> Tuple[List[int], Dict[int, float]]:
    """
    Seleciona os 9 números mais prováveis usando indicador otimizado.
    
    Args:
        df_historico: DataFrame com histórico
        ranking: Lista com ranking de indicadores
        top_indicadores: Número de top indicadores
        janela_analise: Janela de análise
        verbose: Se True, exibe informações
        
    Returns:
        Tupla (lista de 9 números, dicionário {número: score})
    """
    if verbose:
        print(f"\n🎯 Selecionando Top 9 Números (Universo Super Reduzido)")
        print("="*70)
    
    # Usar indicador de probabilidade
    indicador = IndicadorProbabilidadeUniverso(janela=janela_analise)
    
    # Calcular scores
    scores = indicador.calcular_scores(df_historico, verbose=False)
    
    # Ordenar e pegar top 9
    numeros_ordenados = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_9 = [num for num, _ in numeros_ordenados[:9]]
    scores_top_9 = {num: score for num, score in numeros_ordenados[:9]}
    
    if verbose:
        print(f"\n📊 Top 9 Números Selecionados:")
        print(f"\n{'#':<4} {'Número':<8} {'Score':<10} {'Barra':<30}")
        print("-"*70)
        
        max_score = max(scores_top_9.values())
        for i, (num, score) in enumerate(numeros_ordenados[:9], 1):
            barra_len = int((score / max_score) * 25)
            barra = '█' * barra_len
            print(f"{i:<4} {num:02d}       {score:>6.2f}     {barra}")
        
        print(f"\n📋 Universo Super Reduzido: {'-'.join(f'{n:02d}' for n in sorted(top_9))}")
    
    return sorted(top_9), scores_top_9


def analisar_combinacoes_9(
    numeros: List[int],
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Analisa combinações possíveis com 9 números.
    
    Args:
        numeros: Lista de 9 números
        verbose: Se True, exibe informações
        
    Returns:
        Dicionário com análise
    """
    # C(9, 6) = 84 combinações
    comb_9 = math.comb(9, 6)
    comb_20 = math.comb(20, 6)
    comb_60 = math.comb(60, 6)
    
    analise = {
        'universo_9': {
            'numeros': 9,
            'combinacoes': comb_9,
            'custo': comb_9 * 5.0
        },
        'universo_20': {
            'numeros': 20,
            'combinacoes': comb_20,
            'custo': comb_20 * 5.0
        },
        'universo_60': {
            'numeros': 60,
            'combinacoes': comb_60,
            'custo': comb_60 * 5.0
        },
        'reducao_vs_20': ((comb_20 - comb_9) / comb_20) * 100,
        'reducao_vs_60': ((comb_60 - comb_9) / comb_60) * 100
    }
    
    if verbose:
        print(f"\n📊 Análise de Combinações (9 Números)")
        print("="*70)
        
        print(f"\n🎯 Universo Super Reduzido (9 números):")
        print(f"   • Total de combinações: {comb_9:,}")
        print(f"   • Custo (R$ 5,00/jogo): R$ {comb_9 * 5.0:,.2f}")
        
        print(f"\n📊 Comparação:")
        print(f"   • vs 20 números: {analise['reducao_vs_20']:.2f}% menos combinações")
        print(f"   • vs 60 números: {analise['reducao_vs_60']:.2f}% menos combinações")
        
        print(f"\n💰 Economia:")
        print(f"   • vs 20 números: R$ {(comb_20 - comb_9) * 5.0:,.2f}")
        print(f"   • vs 60 números: R$ {(comb_60 - comb_9) * 5.0:,.2f}")
    
    return analise


def validar_cobertura_9(
    numeros_9: List[int],
    df_historico: pd.DataFrame,
    janela_validacao: int = 100,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Valida cobertura histórica dos 9 números.
    
    Args:
        numeros_9: Lista com 9 números
        df_historico: DataFrame com histórico
        janela_validacao: Janela de validação
        verbose: Se True, exibe informações
        
    Returns:
        Dicionário com validação
    """
    df_teste = df_historico.tail(janela_validacao)
    
    # Contar acertos
    acertos_6 = 0
    acertos_5 = 0
    acertos_4 = 0
    acertos_3 = 0
    
    for _, row in df_teste.iterrows():
        numeros_sorteio = set([row[f'Bola{i}'] for i in range(1, 7)])
        acertos = len(numeros_sorteio & set(numeros_9))
        
        if acertos == 6:
            acertos_6 += 1
        if acertos >= 5:
            acertos_5 += 1
        if acertos >= 4:
            acertos_4 += 1
        if acertos >= 3:
            acertos_3 += 1
    
    taxa_6 = (acertos_6 / janela_validacao) * 100
    taxa_5 = (acertos_5 / janela_validacao) * 100
    taxa_4 = (acertos_4 / janela_validacao) * 100
    taxa_3 = (acertos_3 / janela_validacao) * 100
    
    # Recomendação
    if taxa_6 >= 40:
        recomendacao = "EXCELENTE"
    elif taxa_6 >= 30:
        recomendacao = "ALTA"
    elif taxa_6 >= 20:
        recomendacao = "MÉDIA"
    else:
        recomendacao = "BAIXA"
    
    resultado = {
        'cobertura_6': taxa_6,
        'cobertura_5': taxa_5,
        'cobertura_4': taxa_4,
        'cobertura_3': taxa_3,
        'recomendacao': recomendacao,
        'janela': janela_validacao
    }
    
    if verbose:
        print(f"\n📈 Validação Histórica (últimos {janela_validacao} jogos)")
        print("="*70)
        print(f"   • Sorteios com 6 números nos 9: {acertos_6} ({taxa_6:.1f}%)")
        print(f"   • Sorteios com 5+ números nos 9: {acertos_5} ({taxa_5:.1f}%)")
        print(f"   • Sorteios com 4+ números nos 9: {acertos_4} ({taxa_4:.1f}%)")
        print(f"   • Sorteios com 3+ números nos 9: {acertos_3} ({taxa_3:.1f}%)")
        
        print(f"\n   Recomendação: {recomendacao}")
        
        if recomendacao in ["EXCELENTE", "ALTA"]:
            print(f"   ✅ Excelente probabilidade de cobertura!")
        elif recomendacao == "MÉDIA":
            print(f"   ⚠️  Probabilidade moderada de cobertura")
        else:
            print(f"   ❌ Baixa probabilidade - considere universo maior")
    
    return resultado


def gerar_todos_jogos_9(
    numeros_9: List[int],
    verbose: bool = True
) -> List[List[int]]:
    """
    Gera todas as 84 combinações possíveis com 9 números.
    
    Args:
        numeros_9: Lista com 9 números
        verbose: Se True, exibe informações
        
    Returns:
        Lista com todas as 84 combinações
    """
    from itertools import combinations
    
    if verbose:
        print(f"\n🎲 Gerando Todas as Combinações (9 números)")
        print("="*70)
    
    # C(9, 6) = 84 combinações
    todas_comb = list(combinations(numeros_9, 6))
    jogos = [list(comb) for comb in todas_comb]
    
    if verbose:
        print(f"✅ {len(jogos)} jogos gerados (cobertura total)")
        print(f"   Custo total: R$ {len(jogos) * 5.0:,.2f}")
    
    return jogos


def comparar_universos(
    numeros_9: List[int],
    numeros_20: List[int],
    df_historico: pd.DataFrame,
    janela: int = 100,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Compara performance entre universo de 9 e 20 números.
    
    Args:
        numeros_9: Lista com 9 números
        numeros_20: Lista com 20 números
        df_historico: DataFrame com histórico
        janela: Janela de análise
        verbose: Se True, exibe informações
        
    Returns:
        DataFrame com comparação
    """
    df_teste = df_historico.tail(janela)
    
    comparacao = []
    
    for idx, row in df_teste.iterrows():
        concurso = row['Concurso']
        numeros_sorteio = set([row[f'Bola{i}'] for i in range(1, 7)])
        
        acertos_9 = len(numeros_sorteio & set(numeros_9))
        acertos_20 = len(numeros_sorteio & set(numeros_20))
        
        comparacao.append({
            'Concurso': concurso,
            'Acertos_9': acertos_9,
            'Acertos_20': acertos_20,
            'Diferenca': acertos_20 - acertos_9,
            'Cobertura_9': '✅' if acertos_9 == 6 else ('⚠️' if acertos_9 >= 4 else '❌'),
            'Cobertura_20': '✅' if acertos_20 == 6 else ('⚠️' if acertos_20 >= 4 else '❌')
        })
    
    df_comp = pd.DataFrame(comparacao)
    
    if verbose:
        print(f"\n📊 Comparação: 9 vs 20 Números")
        print("="*70)
        
        # Estatísticas
        media_9 = df_comp['Acertos_9'].mean()
        media_20 = df_comp['Acertos_20'].mean()
        
        cobertura_total_9 = (df_comp['Acertos_9'] == 6).sum()
        cobertura_total_20 = (df_comp['Acertos_20'] == 6).sum()
        
        print(f"\n📈 Estatísticas ({janela} jogos):")
        print(f"   • Média de acertos (9 números): {media_9:.2f}")
        print(f"   • Média de acertos (20 números): {media_20:.2f}")
        print(f"   • Cobertura total 6 (9 números): {cobertura_total_9} ({(cobertura_total_9/janela)*100:.1f}%)")
        print(f"   • Cobertura total 6 (20 números): {cobertura_total_20} ({(cobertura_total_20/janela)*100:.1f}%)")
        
        print(f"\n🎯 Top 10 Sorteios com Melhor Cobertura (9 números):")
        top_10 = df_comp.nlargest(10, 'Acertos_9')[['Concurso', 'Acertos_9', 'Acertos_20', 'Cobertura_9']]
        print(top_10.to_string(index=False))
    
    return df_comp


# Exports
__all__ = [
    'selecionar_top_9_numeros',
    'analisar_combinacoes_9',
    'validar_cobertura_9',
    'gerar_todos_jogos_9',
    'comparar_universos'
]


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando Analisador de 9 Números...\n")
    
    import sys
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(PROJECT_ROOT))
    
    from src.core.config import ARQUIVO_HISTORICO
    from src.core.analisador_universo_reduzido import selecionar_top_20_numeros
    
    # Carregar histórico
    df_historico = pd.read_excel(str(ARQUIVO_HISTORICO), sheet_name='MEGA SENA')
    print(f"✅ {len(df_historico)} sorteios carregados")
    
    # Ranking de teste
    ranking_teste = [
        {'indicador': f'Ind{i}', 'relevancia': 100-i*5}
        for i in range(1, 11)
    ]
    
    # Selecionar top 9
    numeros_9, scores_9 = selecionar_top_9_numeros(
        df_historico,
        ranking_teste,
        top_indicadores=10,
        verbose=True
    )
    
    # Analisar combinações
    analise = analisar_combinacoes_9(numeros_9, verbose=True)
    
    # Validar cobertura
    validacao = validar_cobertura_9(numeros_9, df_historico, verbose=True)
    
    # Gerar todos os jogos
    jogos = gerar_todos_jogos_9(numeros_9, verbose=True)
    
    # Comparar com 20 números
    numeros_20, _ = selecionar_top_20_numeros(
        df_historico,
        ranking_teste,
        top_indicadores=10,
        verbose=False
    )
    
    df_comp = comparar_universos(numeros_9, numeros_20, df_historico, verbose=True)
    
    print("\n✅ Módulo funcionando corretamente!\n")

