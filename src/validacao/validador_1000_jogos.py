"""
Validador de Jogos com 1000 Sorteios Históricos - MegaCLI v5.1.5

Este módulo implementa a validação de jogos gerados contra os últimos
1000 sorteios históricos, divididos em 2 séries de 500 para análise comparativa.

Autor: MegaCLI Team
Data: 22/01/2026
Versão: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any
from tqdm import tqdm
from collections import Counter
import json
from datetime import datetime


def carregar_ultimos_sorteios(
    df_historico: pd.DataFrame,
    n_sorteios: int = 1000
) -> pd.DataFrame:
    """
    Carrega os últimos N sorteios do histórico.
    
    Args:
        df_historico: DataFrame com histórico completo
        n_sorteios: Número de sorteios a carregar
        
    Returns:
        DataFrame com últimos N sorteios
    """
    return df_historico.tail(n_sorteios).copy()


def dividir_series(
    df_sorteios: pd.DataFrame,
    splits: List[int] = [500, 500]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Divide DataFrame em duas séries para análise comparativa.
    
    Args:
        df_sorteios: DataFrame com sorteios
        splits: Lista com tamanhos das séries [serie1, serie2]
        
    Returns:
        Tupla (serie1, serie2)
    """
    total = sum(splits)
    df_ultimos = df_sorteios.tail(total)
    
    serie1 = df_ultimos.head(splits[0])
    serie2 = df_ultimos.tail(splits[1])
    
    return serie1, serie2


def contar_acertos(
    jogo: List[int],
    sorteio: pd.Series
) -> int:
    """
    Conta quantos números do jogo acertaram no sorteio.
    
    Args:
        jogo: Lista com 6 números do jogo
        sorteio: Series com dados do sorteio
        
    Returns:
        Número de acertos (0-6)
    """
    numeros_sorteio = [sorteio[f'Bola{i}'] for i in range(1, 7)]
    return len(set(jogo) & set(numeros_sorteio))


def validar_jogo_contra_serie(
    jogo: List[int],
    df_serie: pd.DataFrame
) -> Dict[str, int]:
    """
    Valida um jogo contra uma série de sorteios.
    
    Args:
        jogo: Lista com 6 números
        df_serie: DataFrame com série de sorteios
        
    Returns:
        Dicionário com contagem de acertos por categoria
    """
    acertos = {
        '3': 0,
        '4': 0,
        '5': 0,
        '6': 0
    }
    
    for _, sorteio in df_serie.iterrows():
        n_acertos = contar_acertos(jogo, sorteio)
        
        if n_acertos >= 3:
            acertos[str(n_acertos)] += 1
    
    return acertos


def validar_jogos_historico(
    jogos: List[Dict],
    df_historico: pd.DataFrame,
    n_sorteios: int = 1000,
    splits: List[int] = [500, 500],
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Valida jogos contra os últimos N sorteios históricos.
    
    Args:
        jogos: Lista de dicionários com jogos
        df_historico: DataFrame com histórico completo
        n_sorteios: Número de sorteios a validar
        splits: Divisão das séries
        verbose: Se True, exibe barra de progresso
        
    Returns:
        Dicionário com resultados da validação
    """
    if verbose:
        print(f"\n📊 Validando {len(jogos)} jogos contra {n_sorteios} sorteios históricos")
        print("="*60)
    
    # Carregar últimos sorteios
    df_ultimos = carregar_ultimos_sorteios(df_historico, n_sorteios)
    
    if verbose:
        print(f"\n✅ Carregados {len(df_ultimos)} sorteios")
        print(f"   • Período: Sorteio {df_ultimos.iloc[0]['Concurso']} a {df_ultimos.iloc[-1]['Concurso']}")
    
    # Dividir em séries
    serie1, serie2 = dividir_series(df_ultimos, splits)
    
    if verbose:
        print(f"\n📋 Séries divididas:")
        print(f"   • Série 1: {len(serie1)} sorteios (Concurso {serie1.iloc[0]['Concurso']} a {serie1.iloc[-1]['Concurso']})")
        print(f"   • Série 2: {len(serie2)} sorteios (Concurso {serie2.iloc[0]['Concurso']} a {serie2.iloc[-1]['Concurso']})")
    
    # Validar cada jogo
    resultados = []
    
    iterator = tqdm(
        jogos,
        desc="🔍 Validando jogos",
        unit="jogo",
        disable=not verbose
    )
    
    for jogo in iterator:
        numeros = jogo['numeros']
        
        # Validar contra série completa
        acertos_total = validar_jogo_contra_serie(numeros, df_ultimos)
        
        # Validar contra série 1
        acertos_s1 = validar_jogo_contra_serie(numeros, serie1)
        
        # Validar contra série 2
        acertos_s2 = validar_jogo_contra_serie(numeros, serie2)
        
        # Calcular taxas
        total_sorteios = len(df_ultimos)
        taxa_3_plus = ((acertos_total['3'] + acertos_total['4'] + 
                       acertos_total['5'] + acertos_total['6']) / total_sorteios) * 100
        taxa_4_plus = ((acertos_total['4'] + acertos_total['5'] + 
                       acertos_total['6']) / total_sorteios) * 100
        taxa_5_plus = ((acertos_total['5'] + acertos_total['6']) / total_sorteios) * 100
        taxa_6 = (acertos_total['6'] / total_sorteios) * 100
        
        # Adicionar resultado
        resultados.append({
            'rank': jogo['rank'],
            'numeros': numeros,
            'score': jogo['score'],
            'acertos_3': acertos_total['3'],
            'acertos_4': acertos_total['4'],
            'acertos_5': acertos_total['5'],
            'acertos_6': acertos_total['6'],
            'taxa_3+_%': round(taxa_3_plus, 2),
            'taxa_4+_%': round(taxa_4_plus, 2),
            'taxa_5+_%': round(taxa_5_plus, 2),
            'taxa_6_%': round(taxa_6, 2),
            'serie1_3': acertos_s1['3'],
            'serie1_4': acertos_s1['4'],
            'serie1_5': acertos_s1['5'],
            'serie1_6': acertos_s1['6'],
            'serie2_3': acertos_s2['3'],
            'serie2_4': acertos_s2['4'],
            'serie2_5': acertos_s2['5'],
            'serie2_6': acertos_s2['6']
        })
    
    # Calcular estatísticas gerais
    df_resultados = pd.DataFrame(resultados)
    
    estatisticas = {
        'total_jogos': len(jogos),
        'total_sorteios': n_sorteios,
        'serie1_sorteios': len(serie1),
        'serie2_sorteios': len(serie2),
        'media_acertos_3': df_resultados['acertos_3'].mean(),
        'media_acertos_4': df_resultados['acertos_4'].mean(),
        'media_acertos_5': df_resultados['acertos_5'].mean(),
        'media_acertos_6': df_resultados['acertos_6'].mean(),
        'media_taxa_3+': df_resultados['taxa_3+_%'].mean(),
        'media_taxa_4+': df_resultados['taxa_4+_%'].mean(),
        'media_taxa_5+': df_resultados['taxa_5+_%'].mean(),
        'media_taxa_6': df_resultados['taxa_6_%'].mean(),
        'melhor_jogo_3+': df_resultados.loc[df_resultados['acertos_3'].idxmax()].to_dict(),
        'melhor_jogo_4+': df_resultados.loc[df_resultados['acertos_4'].idxmax()].to_dict(),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if verbose:
        print(f"\n✅ Validação concluída!")
        print(f"\n📈 Estatísticas Gerais:")
        print(f"   • Média de acertos 3+: {estatisticas['media_acertos_3']:.2f}")
        print(f"   • Média de acertos 4+: {estatisticas['media_acertos_4']:.2f}")
        print(f"   • Média de acertos 5+: {estatisticas['media_acertos_5']:.2f}")
        print(f"   • Média de acertos 6: {estatisticas['media_acertos_6']:.2f}")
        print(f"\n📊 Taxas Médias:")
        print(f"   • Taxa 3+: {estatisticas['media_taxa_3+']:.2f}%")
        print(f"   • Taxa 4+: {estatisticas['media_taxa_4+']:.2f}%")
        print(f"   • Taxa 5+: {estatisticas['media_taxa_5+']:.2f}%")
        print(f"   • Taxa 6: {estatisticas['media_taxa_6']:.2f}%")
    
    return {
        'resultados': df_resultados,
        'estatisticas': estatisticas,
        'serie1': serie1,
        'serie2': serie2
    }


def comparar_series(
    resultados: pd.DataFrame
) -> pd.DataFrame:
    """
    Compara performance entre as duas séries.
    
    Args:
        resultados: DataFrame com resultados da validação
        
    Returns:
        DataFrame com comparação entre séries
    """
    comparacao = []
    
    for _, row in resultados.iterrows():
        total_s1 = row['serie1_3'] + row['serie1_4'] + row['serie1_5'] + row['serie1_6']
        total_s2 = row['serie2_3'] + row['serie2_4'] + row['serie2_5'] + row['serie2_6']
        
        comparacao.append({
            'rank': row['rank'],
            'numeros': '-'.join(f"{n:02d}" for n in row['numeros']),
            'serie1_total': total_s1,
            'serie2_total': total_s2,
            'diferenca': total_s2 - total_s1,
            'melhor_serie': 'Série 2' if total_s2 > total_s1 else ('Série 1' if total_s1 > total_s2 else 'Empate')
        })
    
    return pd.DataFrame(comparacao)


def gerar_relatorio_validacao(
    validacao: Dict[str, Any],
    arquivo: str
) -> None:
    """
    Gera relatório de validação em formato JSON.
    
    Args:
        validacao: Dicionário com resultados da validação
        arquivo: Caminho do arquivo de saída
    """
    # Preparar dados para JSON
    relatorio = {
        'estatisticas': validacao['estatisticas'],
        'top_10_jogos': validacao['resultados'].head(10).to_dict('records')
    }
    
    # Salvar JSON
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)


# Exports
__all__ = [
    'validar_jogos_historico',
    'comparar_series',
    'gerar_relatorio_validacao',
    'carregar_ultimos_sorteios',
    'dividir_series'
]


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando módulo de validação...\n")
    
    # Criar dados de teste
    import sys
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(PROJECT_ROOT))
    
    from src.core.config import ARQUIVO_HISTORICO
    
    # Carregar histórico
    df_historico = pd.read_excel(str(ARQUIVO_HISTORICO), sheet_name='MEGA SENA')
    print(f"✅ {len(df_historico)} sorteios carregados")
    
    # Criar jogos de teste
    jogos_teste = [
        {
            'rank': i,
            'numeros': [1, 10, 20, 30, 40, 50],
            'score': 80.0
        }
        for i in range(1, 6)
    ]
    
    # Validar
    validacao = validar_jogos_historico(
        jogos_teste,
        df_historico,
        n_sorteios=100,  # Usar 100 para teste rápido
        splits=[50, 50],
        verbose=True
    )
    
    print(f"\n✅ Validação concluída!")
    print(f"   • Jogos validados: {validacao['estatisticas']['total_jogos']}")
    print(f"   • Sorteios analisados: {validacao['estatisticas']['total_sorteios']}")
    
    print("\n✅ Módulo funcionando corretamente!\n")
