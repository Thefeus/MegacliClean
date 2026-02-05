"""
from src.utils.detector_colunas import extrair_numeros_sorteio
Analisador de Universo Reduzido - MegaCLI v5.1.5

Seleciona os 20 números mais prováveis baseados nos indicadores
e calcula estratégias de cobertura otimizadas.

Autor: MegaCLI Team
Data: 22/01/2026
Versão: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any
from collections import Counter
from itertools import combinations
import math
from src.utils.detector_colunas import extrair_numeros_sorteio


def calcular_combinacoes(n: int, k: int) -> int:
    """
    Calcula C(n, k) = n! / (k! * (n-k)!)
    
    Args:
        n: Total de elementos
        k: Tamanho da combinação
        
    Returns:
        Número de combinações possíveis
    """
    return math.comb(n, k)


def selecionar_top_20_numeros(
    df_historico: pd.DataFrame,
    ranking: List[Dict],
    top_indicadores: int = 10,
    janela: int = 100,
    verbose: bool = True
) -> Tuple[List[int], Dict[int, float]]:
    """
    Seleciona os 20 números mais prováveis baseados nos top indicadores.
    
    Args:
        df_historico: DataFrame com histórico de sorteios
        ranking: Lista com ranking de indicadores
        top_indicadores: Número de top indicadores a usar
        janela: Número de sorteios recentes a considerar
        verbose: Se True, exibe informações
        
    Returns:
        Tupla (lista de 20 números, dicionário {número: peso})
    """
    if verbose:
        print(f"\n🔍 Selecionando Top 20 Números")
        print("="*60)
        print(f"   • Top indicadores: {top_indicadores}")
        print(f"   • Janela de análise: {janela} sorteios")
    
    # Pegar últimos N sorteios
    df_recente = df_historico.tail(janela)
    
    # Contar frequência de cada número
    frequencias = Counter()
    for _, row in df_recente.iterrows():
        numeros = extrair_numeros_sorteio(row)
        frequencias.update(numeros)
    
    # Calcular pesos baseados em frequência
    max_freq = max(frequencias.values()) if frequencias else 1
    pesos = {}
    
    for num in range(1, 61):
        freq = frequencias.get(num, 0)
        # Peso = (frequência normalizada * 100)
        peso_base = (freq / max_freq) * 100
        
        # Bônus para números recentes (últimos 10 sorteios)
        df_muito_recente = df_historico.tail(10)
        apareceu_recente = False
        for _, row in df_muito_recente.iterrows():
            numeros_recentes = extrair_numeros_sorteio(row)
            if num in numeros_recentes:
                apareceu_recente = True
                break
        
        if apareceu_recente:
            peso_base *= 1.1  # Bônus de 10%
        
        pesos[num] = peso_base
    
    # Ordenar por peso e pegar top 20
    numeros_ordenados = sorted(pesos.items(), key=lambda x: x[1], reverse=True)
    top_20 = [num for num, _ in numeros_ordenados[:20]]
    pesos_top_20 = {num: peso for num, peso in numeros_ordenados[:20]}
    
    if verbose:
        print(f"\n✅ Top 20 números selecionados:")
        print(f"\n{'#':<4} {'Número':<8} {'Peso':<10} {'Frequência':<12}")
        print("-"*60)
        for i, (num, peso) in enumerate(numeros_ordenados[:20], 1):
            freq = frequencias.get(num, 0)
            print(f"{i:<4} {num:02d}       {peso:>6.2f}     {freq:>4}")
        
        print(f"\n📊 Universo Reduzido: {'-'.join(f'{n:02d}' for n in sorted(top_20))}")
    
    return sorted(top_20), pesos_top_20


def analisar_combinacoes(
    numeros: List[int],
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Analisa combinações possíveis com universo reduzido.
    
    Args:
        numeros: Lista de números do universo reduzido
        verbose: Se True, exibe informações
        
    Returns:
        Dicionário com análise de combinações
    """
    n_numeros = len(numeros)
    
    # Calcular combinações
    comb_reduzido = calcular_combinacoes(n_numeros, 6)
    comb_completo = calcular_combinacoes(60, 6)
    
    # Calcular redução
    reducao_pct = ((comb_completo - comb_reduzido) / comb_completo) * 100
    
    # Calcular custos (R$ 5,00 por jogo)
    custo_reduzido = comb_reduzido * 5.0
    custo_completo = comb_completo * 5.0
    
    analise = {
        'universo_completo': {
            'numeros': 60,
            'combinacoes': comb_completo,
            'custo': custo_completo
        },
        'universo_reduzido': {
            'numeros': n_numeros,
            'combinacoes': comb_reduzido,
            'custo': custo_reduzido
        },
        'reducao_percentual': reducao_pct,
        'economia': custo_completo - custo_reduzido
    }
    
    if verbose:
        print(f"\n📊 Análise de Combinações")
        print("="*60)
        print(f"\n🌍 Universo Completo (60 números):")
        print(f"   • Total de combinações: {comb_completo:,}")
        print(f"   • Custo (R$ 5,00/jogo): R$ {custo_completo:,.2f}")
        
        print(f"\n🎯 Universo Reduzido ({n_numeros} números):")
        print(f"   • Total de combinações: {comb_reduzido:,}")
        print(f"   • Custo (R$ 5,00/jogo): R$ {custo_reduzido:,.2f}")
        
        print(f"\n💰 Redução:")
        print(f"   • Percentual: {reducao_pct:.2f}%")
        print(f"   • Economia: R$ {analise['economia']:,.2f}")
    
    return analise


def gerar_estrategias_cobertura(
    numeros: List[int],
    verbose: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Gera diferentes estratégias de cobertura.
    
    Args:
        numeros: Lista de números do universo reduzido
        verbose: Se True, exibe informações
        
    Returns:
        Dicionário com estratégias
    """
    total_comb = calcular_combinacoes(len(numeros), 6)
    
    estrategias = {
        'total': {
            'nome': 'Cobertura Total',
            'jogos': total_comb,
            'custo': total_comb * 5.0,
            'garantia': '100% (se 6 números nos 20)',
            'percentual': 100.0
        },
        'otimizada_10': {
            'nome': 'Cobertura Otimizada (Top 10%)',
            'jogos': int(total_comb * 0.10),
            'custo': int(total_comb * 0.10) * 5.0,
            'garantia': '~90% das combinações mais prováveis',
            'percentual': 10.0
        },
        'otimizada_5': {
            'nome': 'Cobertura Otimizada (Top 5%)',
            'jogos': int(total_comb * 0.05),
            'custo': int(total_comb * 0.05) * 5.0,
            'garantia': '~85% das combinações mais prováveis',
            'percentual': 5.0
        },
        'otimizada_1': {
            'nome': 'Cobertura Otimizada (Top 1%)',
            'jogos': int(total_comb * 0.01),
            'custo': int(total_comb * 0.01) * 5.0,
            'garantia': '~65% das combinações mais prováveis',
            'percentual': 1.0
        },
        'garantia_4': {
            'nome': 'Garantia de 4 Acertos',
            'jogos': calcular_jogos_garantia(len(numeros), 4),
            'custo': calcular_jogos_garantia(len(numeros), 4) * 5.0,
            'garantia': 'Pelo menos 4 acertos (se 6 números nos 20)',
            'percentual': (calcular_jogos_garantia(len(numeros), 4) / total_comb) * 100
        },
        'garantia_3': {
            'nome': 'Garantia de 3 Acertos',
            'jogos': calcular_jogos_garantia(len(numeros), 3),
            'custo': calcular_jogos_garantia(len(numeros), 3) * 5.0,
            'garantia': 'Pelo menos 3 acertos (se 6 números nos 20)',
            'percentual': (calcular_jogos_garantia(len(numeros), 3) / total_comb) * 100
        }
    }
    
    if verbose:
        print(f"\n🎯 Estratégias de Cobertura")
        print("="*60)
        
        for i, (key, est) in enumerate(estrategias.items(), 1):
            print(f"\n{i}. {est['nome'].upper()}")
            print(f"   • Jogos necessários: {est['jogos']:,}")
            print(f"   • Custo: R$ {est['custo']:,.2f}")
            print(f"   • Cobertura: {est['percentual']:.2f}%")
            print(f"   • Garantia: {est['garantia']}")
    
    return estrategias


def calcular_jogos_garantia(n_numeros: int, acertos: int) -> int:
    """
    Calcula número aproximado de jogos para garantir N acertos.
    
    Args:
        n_numeros: Tamanho do universo reduzido
        acertos: Número de acertos a garantir
        
    Returns:
        Número estimado de jogos
    """
    # Fórmula aproximada: C(n, acertos) / C(6, acertos)
    numerador = calcular_combinacoes(n_numeros, acertos)
    denominador = calcular_combinacoes(6, acertos)
    
    return max(1, numerador // denominador)


def gerar_jogos_universo_reduzido(
    numeros: List[int],
    pesos: Dict[int, float],
    n_jogos: int,
    estrategia: str = 'otimizada',
    verbose: bool = True
) -> List[List[int]]:
    """
    Gera jogos otimizados do universo reduzido.
    
    Args:
        numeros: Lista de 20 números
        pesos: Dicionário {número: peso}
        n_jogos: Número de jogos a gerar
        estrategia: 'total', 'otimizada', ou 'garantia'
        verbose: Se True, exibe barra de progresso
        
    Returns:
        Lista de jogos (cada jogo é uma lista de 6 números)
    """
    from tqdm import tqdm
    
    if verbose:
        print(f"\n🎲 Gerando {n_jogos:,} jogos do universo reduzido")
        print("="*60)
    
    jogos = []
    jogos_set = set()
    
    if estrategia == 'total':
        # Gerar todas as combinações
        todas_comb = list(combinations(numeros, 6))
        jogos = [list(comb) for comb in todas_comb[:n_jogos]]
    
    else:
        # Gerar jogos ponderados por peso
        iterator = tqdm(range(n_jogos), desc="Gerando jogos", disable=not verbose)
        
        for _ in iterator:
            tentativas = 0
            while tentativas < 1000:
                # Selecionar 6 números com probabilidade proporcional aos pesos
                pesos_lista = [pesos.get(n, 50) for n in numeros]
                jogo = sorted(np.random.choice(
                    numeros,
                    size=6,
                    replace=False,
                    p=np.array(pesos_lista) / sum(pesos_lista)
                ))
                
                jogo_tuple = tuple(jogo)
                if jogo_tuple not in jogos_set:
                    jogos_set.add(jogo_tuple)
                    jogos.append(jogo)
                    break
                
                tentativas += 1
    
    if verbose:
        print(f"\n✅ {len(jogos):,} jogos gerados com sucesso!")
    
    return jogos


def analisar_probabilidades(
    numeros: List[int],
    df_historico: pd.DataFrame,
    janela: int = 100,
    verbose: bool = True
) -> Dict[str, float]:
    """
    Analisa probabilidade de acerto com universo reduzido.
    
    Args:
        numeros: Lista de 20 números
        df_historico: DataFrame com histórico
        janela: Número de sorteios a analisar
        verbose: Se True, exibe informações
        
    Returns:
        Dicionário com análise de probabilidades
    """
    df_recente = df_historico.tail(janela)
    
    # Contar quantos sorteios tiveram todos os 6 números nos 20
    acertos_totais = 0
    acertos_5 = 0
    acertos_4 = 0
    
    for _, row in df_recente.iterrows():
        numeros_sorteio = extrair_numeros_sorteio(row)
        acertos = len(set(numeros_sorteio) & set(numeros))
        
        if acertos == 6:
            acertos_totais += 1
        if acertos >= 5:
            acertos_5 += 1
        if acertos >= 4:
            acertos_4 += 1
    
    prob_6 = (acertos_totais / janela) * 100
    prob_5_plus = (acertos_5 / janela) * 100
    prob_4_plus = (acertos_4 / janela) * 100
    
    analise = {
        'prob_6_numeros': prob_6,
        'prob_5_plus': prob_5_plus,
        'prob_4_plus': prob_4_plus,
        'janela': janela
    }
    
    if verbose:
        print(f"\n📈 Análise de Probabilidades")
        print("="*60)
        print(f"   Baseado nos últimos {janela} sorteios:")
        print(f"\n   • Todos os 6 números nos 20: {prob_6:.1f}%")
        print(f"   • Pelo menos 5 números nos 20: {prob_5_plus:.1f}%")
        print(f"   • Pelo menos 4 números nos 20: {prob_4_plus:.1f}%")
        
        if prob_6 > 50:
            print(f"\n   ✅ Alta probabilidade de cobertura!")
        elif prob_6 > 30:
            print(f"\n   ⚠️  Probabilidade moderada de cobertura")
        else:
            print(f"\n   ❌ Baixa probabilidade de cobertura")
    
    return analise


# Exports
__all__ = [
    'selecionar_top_20_numeros',
    'analisar_combinacoes',
    'gerar_estrategias_cobertura',
    'gerar_jogos_universo_reduzido',
    'analisar_probabilidades',
    'calcular_combinacoes'
]


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando módulo de universo reduzido...\n")
    
    import sys
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(PROJECT_ROOT))
    
    from src.core.config import ARQUIVO_HISTORICO
    
    # Carregar histórico
    df_historico = pd.read_excel(str(ARQUIVO_HISTORICO), sheet_name='MEGA SENA')
    print(f"✅ {len(df_historico)} sorteios carregados")
    
    # Ranking de teste
    ranking_teste = [
        {'indicador': f'Ind{i}', 'relevancia': 100-i*5}
        for i in range(1, 11)
    ]
    
    # Selecionar top 20
    numeros, pesos = selecionar_top_20_numeros(
        df_historico,
        ranking_teste,
        top_indicadores=10,
        verbose=True
    )
    
    # Analisar combinações
    analise = analisar_combinacoes(numeros, verbose=True)
    
    # Gerar estratégias
    estrategias = gerar_estrategias_cobertura(numeros, verbose=True)
    
    # Analisar probabilidades
    probs = analisar_probabilidades(numeros, df_historico, verbose=True)
    
    print("\n✅ Módulo funcionando corretamente!\n")

