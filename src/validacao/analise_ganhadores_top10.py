"""
BATIMENTO v5.0 - Top 10 Indicadores com Análise de Acertos

Gera predições usando os TOP 10 indicadores do ranking
Compara com série histórica
Calcula correlação e total de acertos
Atualiza aba GANHADORES com análise completa
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import Counter
from tqdm import tqdm


def gerar_com_top_indicadores(
    historico: pd.DataFrame,
    top_indicadores: List[Dict],
    todos_indicadores: Dict,
    n_jogos: int = 50
) -> List[Dict]:
    """
    Gera jogos usando apenas TOP indicadores
    
    Args:
        historico: DataFrame histórico
        top_indicadores: Lista de top N indicadores do ranking
        todos_indicadores: Dict com funções de todos indicadores
        n_jogos: Quantos jogos gerar
        
    Returns:
        Lista de jogos com scores
    """
    import random
    
    # Importar configuração
    from src.core.config import AnaliseConfig
    
    # Filtrar apenas indicadores do top
    nomes_top = [ind['indicador'] for ind in top_indicadores[:10]]
    
    # Gerar candidatos de forma inteligente (não todas as combinações!)
    candidatos = []
    tentativas_max = n_jogos * AnaliseConfig.FASE5_MULTIPLICADOR_CANDIDATOS  # Configurável
    
    print(f"   Gerando {tentativas_max:,} jogos candidatos (selecionará os {n_jogos} melhores)...")
    
    jogos_unicos = set()
    
    with tqdm(total=tentativas_max, desc="   Gerando jogos", unit="jogos", ncols=100) as pbar:
        while len(candidatos) < tentativas_max:
            # Gerar jogo aleatório
            nums = sorted(random.sample(range(1, 61), 6))
            nums_tuple = tuple(nums)
            
            # Evitar duplicatas
            if nums_tuple in jogos_unicos:
                continue
            
            jogos_unicos.add(nums_tuple)
            score = 0
            
            # Avaliar com cada indicador do top 10
            for item in top_indicadores[:10]:
                nome = item['indicador']
                if nome in todos_indicadores:
                    try:
                        funcao = todos_indicadores[nome]
                        score_ind = funcao(historico, nums)
                        # Ponderar pela relevância do indicador
                        score += score_ind * (item['relevancia'] / 100)
                    except:
                        pass
            
            candidatos.append({
                'numeros': nums,
                'score': score
            })
            
            # Atualizar barra de progresso
            pbar.update(1)
    
    # Ordenar e pegar top N
    candidatos.sort(key=lambda x: x['score'], reverse=True)
    return candidatos[:n_jogos]



def comparar_com_historico(
    jogos_gerados: List[Dict],
    historico: pd.DataFrame,
    ball_cols: List[str] = None
) -> pd.DataFrame:
    """
    Compara jogos gerados com cada sorteio histórico
    
    Args:
        jogos_gerados: Lista de jogos com números
        historico: DataFrame histórico
        ball_cols: Colunas das bolas
        
    Returns:
        DataFrame com análise de acertos
    """
    if ball_cols is None:
        ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    resultados = []
    
    print(f"   Comparando {len(jogos_gerados)} jogos com {len(historico)} sorteios...")
    
    # Para cada sorteio histórico
    for idx, row in tqdm(historico.iterrows(), total=len(historico), desc="   Comparando histórico", unit="sorteios", ncols=100):
        # Extrair números do sorteio
        sorteio = []
        for col in ball_cols:
            if pd.notna(row[1].get(col)):
                sorteio.append(int(row[1][col]))
        
        if len(sorteio) != 6:
            continue
        
        sorteio_set = set(sorteio)
        
        # Comparar com cada jogo gerado
        acertos_por_jogo = []
        for jogo in jogos_gerados:
            jogo_set = set(jogo['numeros'])
            acertos = len(sorteio_set.intersection(jogo_set))
            acertos_por_jogo.append(acertos)
        
        # Estatísticas deste sorteio
        resultados.append({
            'Concurso': int(row[1].get('Concurso', idx)),
            'Resultado': '-'.join(f"{n:02d}" for n in sorted(sorteio)),
            'Melhor_Jogo': max(acertos_por_jogo),
            'Pior_Jogo': min(acertos_por_jogo),
            'Média_Acertos': np.mean(acertos_por_jogo),
            'Total_Acertos_4plus': sum(1 for a in acertos_por_jogo if a >= 4),
            'Total_Acertos_5plus': sum(1 for a in acertos_por_jogo if a >= 5),
            'Total_Acertos_6': sum(1 for a in acertos_por_jogo if a == 6),
            'Taxa_3plus_%': sum(1 for a in acertos_por_jogo if a >= 3) / len(acertos_por_jogo) * 100
        })
    
    return pd.DataFrame(resultados)


def calcular_correlacao_indicadores(
    historico: pd.DataFrame,
    top_indicadores: List[Dict],
    todos_indicadores: Dict
) -> pd.DataFrame:
    """
    Calcula correlação entre indicadores top e acertos reais
    
    Args:
        historico: DataFrame histórico
        top_indicadores: Top indicadores
        todos_indicadores: Dict de indicadores
        
    Returns:
        DataFrame com correlação de cada indicador
    """
    correlacoes = []
    
    print(f"   Calculando correlação de {len(top_indicadores[:10])} indicadores...")
    
    for item in tqdm(top_indicadores[:10], desc="   Calculando correlações", unit="indicador", ncols=100):
        nome = item['indicador']
        
        if nome not in todos_indicadores:
            continue
        
        scores = []
        funcao = todos_indicadores[nome]
        
        # Calcular score do indicador para cada sorteio
        for idx, row in historico.tail(100).iterrows():  # Últimos 100 para velocidade
            try:
                nums = [int(row[f'Bola{j}']) for j in range(1, 7) if pd.notna(row.get(f'Bola{j}'))]
                if len(nums) == 6:
                    score = funcao(historico.iloc[:idx], nums)
                    scores.append(score)
                else:
                    scores.append(0)
            except:
                scores.append(0)
        
        correlacoes.append({
            'Indicador': nome,
            'Relevância': item['relevancia'],
            'Score_Médio': np.mean(scores) if scores else 0,
            'Desvio_Padrão': np.std(scores) if scores else 0,
            'Score_Máximo': max(scores) if scores else 0
        })
    
    return pd.DataFrame(correlacoes)


def atualizar_aba_ganhadores(
    df_comparacao: pd.DataFrame,
    df_correlacao: pd.DataFrame,
    top_indicadores: List[Dict]
) -> pd.DataFrame:
    """
    Cria DataFrame completo para aba GANHADORES
    
    Returns:
        DataFrame formatado para Excel
    """
    # Resumo geral
    resumo = pd.DataFrame([
        {
            'Métrica': 'Total de Sorteios Analisados',
            'Valor': len(df_comparacao)
        },
        {
            'Métrica': 'Taxa com 4+ Acertos (%)',
            'Valor': f"{df_comparacao['Total_Acertos_4plus'].sum() / len(df_comparacao):.2f}%"
        },
        {
            'Métrica': 'Taxa com 5+ Acertos (%)',
            'Valor': f"{df_comparacao['Total_Acertos_5plus'].sum() / len(df_comparacao):.2f}%"
        },
        {
            'Métrica': 'Taxa com 6 Acertos (%)',
            'Valor': f"{df_comparacao['Total_Acertos_6'].sum() / len(df_comparacao):.2f}%"
        },
        {
            'Métrica': 'Média de Acertos por Sorteio',
            'Valor': f"{df_comparacao['Média_Acertos'].mean():.2f}"
        },
        {
            'Métrica': 'Melhor Resultado',
            'Valor': f"{df_comparacao['Melhor_Jogo'].max()} acertos"
        }
    ])
    
    # Adicionar seção com TOP 10 indicadores
    top_10_info = pd.DataFrame([
        {
            'Rank': i + 1,
            'Indicador': item['indicador'],
            'Relevância': item['relevancia'],
            'Taxa_4+_%': item.get('taxa_4_plus', 0)
        }
        for i, item in enumerate(top_indicadores[:10])
    ])
    
    # Combinar tudo
    df_final = pd.concat([
        pd.DataFrame([{'': '=== RESUMO GERAL ==='}]),
        resumo,
        pd.DataFrame([{'': ''}]),
        pd.DataFrame([{'': '=== TOP 10 INDICADORES ==='}]),
        top_10_info,
        pd.DataFrame([{'': ''}]),
        pd.DataFrame([{'': '=== CORRELAÇÃO INDICADORES ==='}]),
        df_correlacao,
        pd.DataFrame([{'': ''}]),
        pd.DataFrame([{'': '=== ANÁLISE POR SORTEIO ==='}]),
        df_comparacao
    ], ignore_index=True)
    
    return df_final
