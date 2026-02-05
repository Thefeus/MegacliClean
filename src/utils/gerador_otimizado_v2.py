"""
Gerador Otimizado v2 - Data-Driven

Gera jogos usando indicadores ranqueados por relevância histórica.
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from collections import Counter


def gerar_jogos_data_driven(
    df_historico: pd.DataFrame,
    ranking: List[Dict],
    n_jogos: int = 84,
    top_indicadores: int = 15
) -> List[Dict]:
    """
    Gera jogos usando estratégia data-driven baseada em ranking.
    
    Estratégia:
    - Top 15 indicadores = 80% do peso
    - Indicadores 16-30 = 15% do peso
    - Indicadores 31-42 = 5% do peso
    
    Args:
        df_historico: Histórico completo
        ranking: Lista de indicadores ranqueados
        n_jogos: Quantidade de jogos a gerar
        top_indicadores: Quantos indicadores usar como "top"
        
    Returns:
        Lista de jogos com scores e probabilidades
    """
    from utils.funcoes_principais import criar_all_indicators_dict
    
    print("\n" + "="*80)
    print(f"🎯 GERAÇÃO DATA-DRIVEN: {n_jogos} Jogos Otimizados (Ranking-Based)")
    print("="*80)
    
    # Carregar funções de indicadores
    todos_indicadores = criar_all_indicators_dict()
    
    # Criar pesos baseados no ranking
    pesos = {}
    for item in ranking:
        nome = item['indicador']
        rank = item['rank']
        
        if rank <= top_indicadores:  # Top 15
            peso_base = item['relevancia']
            multiplicador = 1.0
        elif rank <= 30:  # Mid-tier
            peso_base = item['relevancia']
            multiplicador = 0.5
        else:  # Bottom-tier
            peso_base = item['relevancia']
            multiplicador = 0.2
        
        pesos[nome] = peso_base * multiplicador
    
    print(f"   Top {top_indicadores} indicadores: peso médio {np.mean([pesos[r['indicador']] for r in ranking[:top_indicadores]]):.1f}")
    
    # Calcular frequências
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    freq_total = Counter()
    for col in ball_cols:
        freq_total.update(df_historico[col].dropna().astype(int).tolist())
    
    jogos = []
    tentativas = 0
    max_tentativas = n_jogos * 100
    
    from tqdm import tqdm
    
    with tqdm(total=n_jogos, desc="🎯 Gerando jogos otimizados", 
              unit="jogo", ncols=100) as pbar:
        
        while len(jogos) < n_jogos and tentativas < max_tentativas:
            tentativas += 1
            
            # Gerar números com bias de frequência
            pool = list(range(1, 61))
            probs = np.array([freq_total.get(n, 1) for n in pool])
            probs = probs / probs.sum()
            
            nums = sorted(np.random.choice(pool, size=6, replace=False, p=probs).tolist())
            
            # Evitar duplicatas
            if any(j['numeros'] == nums for j in jogos):
                continue
            
            # Calcular score com indicadores disponíveis
            score_total = 0
            matches_top = 0
            
            for item in ranking[:top_indicadores]:
                nome_ind = item['indicador']
                if nome_ind in todos_indicadores:
                    try:
                        func = todos_indicadores[nome_ind]
                        score_ind = func(df_historico, nums)
                        peso_ind = pesos.get(nome_ind, 50)
                        
                        score_total += score_ind * peso_ind / 100
                        
                        if score_ind >= 70:
                            matches_top += 1
                    except:
                        pass
            
            # Probabilidade estimada (baseada em matches)
            prob_estimada = (matches_top / top_indicadores) * 100
            
            jogos.append({
                'numeros': nums,
                'score': round(score_total, 2),
                'probabilidade': round(prob_estimada, 2),
                'top_matches': matches_top
            })
            
            # Atualizar progress bar
            pbar.update(1)
            pbar.set_postfix({
                'Tentativas': tentativas,
                'Score_Médio': f"{np.mean([j['score'] for j in jogos]):.1f}" if jogos else "0"
            })
    
    # Ordenar por score
    jogos.sort(key=lambda x: x['score'], reverse=True)
    
    # Adicionar ranking
    for i, jogo in enumerate(jogos, 1):
        jogo['rank'] = i
        
        # Classificar confiança
        if jogo['probabilidade'] >= 80:
            jogo['confianca'] = 'Alta'
        elif jogo['probabilidade'] >= 60:
            jogo['confianca'] = 'Média-Alta'
        elif jogo['probabilidade'] >= 40:
            jogo['confianca'] = 'Média'
        else:
            jogo['confianca'] = 'Baixa'
    
    print(f"   ✅ {len(jogos)} jogos gerados e ordenados")
    print(f"   🎯 Top 10: probabilidade média {np.mean([j['probabilidade'] for j in jogos[:10]]):.1f}%")
    print(f"   📊 全体: score médio {np.mean([j['score'] for j in jogos]):.1f}\n")
    
    return jogos
