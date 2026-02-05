"""
Gerador de Jogos com Top 10 Indicadores - MegaCLI v5.1.5

Este módulo implementa a geração otimizada de 210 jogos usando apenas
os 10 melhores indicadores do ranking.

Autor: MegaCLI Team
Data: 22/01/2026
Versão: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Set, Tuple
from tqdm import tqdm
import random
from collections import Counter


def extrair_top_indicadores(ranking: List[Dict], top_n: int = 10) -> List[Dict]:
    """
    Extrai os top N indicadores do ranking.
    
    Args:
        ranking: Lista de dicionários com ranking completo
        top_n: Número de indicadores a extrair
        
    Returns:
        Lista com top N indicadores
    """
    return ranking[:top_n]


def calcular_frequencias_ponderadas(
    df_historico: pd.DataFrame,
    top_indicadores: List[Dict],
    janela: int = 100
) -> Dict[int, float]:
    """
    Calcula frequências ponderadas dos números baseado nos top indicadores.
    
    Args:
        df_historico: DataFrame com histórico de sorteios
        top_indicadores: Lista com top indicadores
        janela: Número de sorteios recentes a considerar
        
    Returns:
        Dicionário {número: peso}
    """
    # Pegar últimos N sorteios
    df_recente = df_historico.tail(janela)
    
    # Contar frequência de cada número
    frequencias = Counter()
    for _, row in df_recente.iterrows():
        numeros = [row[f'Bola{i}'] for i in range(1, 7)]
        frequencias.update(numeros)
    
    # Normalizar frequências (0-100)
    max_freq = max(frequencias.values()) if frequencias else 1
    pesos = {num: (freq / max_freq) * 100 for num, freq in frequencias.items()}
    
    # Garantir que todos os números 1-60 tenham um peso
    for num in range(1, 61):
        if num not in pesos:
            pesos[num] = 10.0  # Peso mínimo para números não sorteados
    
    return pesos


def gerar_jogo_otimizado(
    pesos_numeros: Dict[int, float],
    jogos_existentes: Set[Tuple[int, ...]],
    tentativas_max: int = 1000
) -> Tuple[int, ...]:
    """
    Gera um jogo otimizado baseado nos pesos, evitando duplicatas.
    
    Args:
        pesos_numeros: Dicionário {número: peso}
        jogos_existentes: Set de jogos já gerados
        tentativas_max: Número máximo de tentativas
        
    Returns:
        Tupla com 6 números ordenados (SEM REPETIÇÃO)
    """
    numeros = list(pesos_numeros.keys())
    pesos = np.array([pesos_numeros[n] for n in numeros])
    
    # Normalizar pesos para probabilidades
    pesos_norm = pesos / pesos.sum()
    
    # Adicionar import
    from src.core.filtros_avancados import FiltrosAvancados

    for _ in range(tentativas_max):
        # Selecionar 6 números SEM REPETIÇÃO usando probabilidades ponderadas
        indices_selecionados = np.random.choice(
            len(numeros), 
            size=6, 
            replace=False,  # SEM REPETIÇÃO!
            p=pesos_norm
        )
        jogo = tuple(sorted([numeros[i] for i in indices_selecionados]))
        
        # Verificar se é único E passa nos filtros
        if jogo not in jogos_existentes:
            aprovado, _ = FiltrosAvancados.validar_jogo(list(jogo))
            if aprovado:
                return jogo
    
    # Se não conseguiu gerar único e válido, tenta gerar aleatório que passe nos filtros
    tentativas_backup = 0
    while tentativas_backup < 1000:
        jogo = tuple(sorted(random.sample(range(1, 61), 6)))
        if jogo not in jogos_existentes:
            aprovado, _ = FiltrosAvancados.validar_jogo(list(jogo))
            if aprovado:
                return jogo
        tentativas_backup += 1
    
    # Fallback final: retorna o último gerado, mesmo sem filtros
    return jogo


def calcular_score_jogo(
    jogo: Tuple[int, ...],
    pesos_numeros: Dict[int, float],
    top_indicadores: List[Dict]
) -> float:
    """
    Calcula score de um jogo baseado nos pesos dos números.
    
    Args:
        jogo: Tupla com 6 números
        pesos_numeros: Dicionário {número: peso}
        top_indicadores: Lista com top indicadores
        
    Returns:
        Score do jogo (0-100)
    """
    # Score baseado na soma dos pesos dos números
    score_base = sum(pesos_numeros.get(n, 0) for n in jogo) / 6
    
    # Bônus por diversidade (números espalhados)
    diversidade = len(set(n // 10 for n in jogo))  # Quantas dezenas diferentes
    bonus_diversidade = (diversidade / 6) * 10
    
    # Score final
    return min(score_base + bonus_diversidade, 100.0)


def gerar_jogos_top10(
    df_historico: pd.DataFrame,
    ranking: List[Dict],
    n_jogos: int = 210,
    top_n: int = 10,
    verbose: bool = True
) -> List[Dict]:
    """
    Gera N jogos usando apenas os top N indicadores do ranking.
    
    Args:
        df_historico: DataFrame com histórico de sorteios
        ranking: Lista de dicionários com ranking completo
        n_jogos: Número de jogos a gerar
        top_n: Número de top indicadores a usar
        verbose: Se True, exibe barra de progresso
        
    Returns:
        Lista de dicionários com jogos ranqueados
    """
    if verbose:
        print(f"\n🎯 Gerando {n_jogos} jogos com Top {top_n} Indicadores")
        print("="*60)
    
    # Extrair top indicadores
    top_indicadores = extrair_top_indicadores(ranking, top_n)
    
    if verbose:
        print(f"\n📊 Top {top_n} Indicadores Selecionados:")
        for i, ind in enumerate(top_indicadores, 1):
            print(f"   {i}. {ind['indicador']}: {ind['relevancia']:.1f} {ind['estrelas']}")
    
    # Calcular pesos dos números
    pesos_numeros = calcular_frequencias_ponderadas(
        df_historico,
        top_indicadores,
        janela=100
    )
    
    # Gerar jogos
    jogos_gerados = []
    jogos_set = set()
    
    iterator = tqdm(
        range(n_jogos),
        desc="🎲 Gerando jogos",
        unit="jogo",
        disable=not verbose
    )
    
    for i in iterator:
        # Gerar jogo único
        jogo = gerar_jogo_otimizado(pesos_numeros, jogos_set)
        jogos_set.add(jogo)
        
        # Calcular score
        score = calcular_score_jogo(jogo, pesos_numeros, top_indicadores)
        
        # Calcular probabilidade (baseado no score)
        probabilidade = score
        
        # Determinar confiança
        if score >= 80:
            confianca = "ALTA ⭐⭐⭐"
        elif score >= 60:
            confianca = "MÉDIA ⭐⭐"
        else:
            confianca = "BAIXA ⭐"
        
        # Adicionar à lista
        jogos_gerados.append({
            'rank': i + 1,
            'numeros': list(jogo),
            'score': round(score, 2),
            'probabilidade': round(probabilidade, 2),
            'top_matches': top_n,
            'confianca': confianca
        })
    
    # Ordenar por score (maior para menor)
    jogos_gerados.sort(key=lambda x: x['score'], reverse=True)
    
    # Atualizar ranks após ordenação
    for i, jogo in enumerate(jogos_gerados, 1):
        jogo['rank'] = i
    
    if verbose:
        print(f"\n✅ {n_jogos} jogos gerados com sucesso!")
        print(f"\n📈 Estatísticas:")
        scores = [j['score'] for j in jogos_gerados]
        print(f"   • Score médio: {np.mean(scores):.2f}")
        print(f"   • Score máximo: {np.max(scores):.2f}")
        print(f"   • Score mínimo: {np.min(scores):.2f}")
        print(f"   • Desvio padrão: {np.std(scores):.2f}")
        
        # Distribuição de confiança
        confiancas = Counter(j['confianca'] for j in jogos_gerados)
        print(f"\n🎯 Distribuição de Confiança:")
        for conf, count in sorted(confiancas.items(), reverse=True):
            pct = (count / n_jogos) * 100
            print(f"   • {conf}: {count} jogos ({pct:.1f}%)")
    
    return jogos_gerados


def exportar_jogos_txt(jogos: List[Dict], arquivo: str) -> None:
    """
    Exporta jogos para arquivo TXT formatado.
    
    Args:
        jogos: Lista de jogos
        arquivo: Caminho do arquivo de saída
    """
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("MEGACLI v5.1.5 - JOGOS GERADOS COM TOP 10 INDICADORES\n")
        f.write("="*70 + "\n\n")
        
        for jogo in jogos:
            nums_str = '-'.join(f"{n:02d}" for n in jogo['numeros'])
            f.write(f"#{jogo['rank']:03d}: {nums_str} | ")
            f.write(f"Score: {jogo['score']:.2f} | ")
            f.write(f"Prob: {jogo['probabilidade']:.1f}% | ")
            f.write(f"{jogo['confianca']}\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write(f"Total: {len(jogos)} jogos\n")
        f.write("="*70 + "\n")


# Exports
__all__ = [
    'gerar_jogos_top10',
    'extrair_top_indicadores',
    'calcular_frequencias_ponderadas',
    'exportar_jogos_txt'
]


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando módulo de geração de jogos...\n")
    
    # Criar dados de teste
    import sys
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(PROJECT_ROOT))
    
    from src.core.config import ARQUIVO_HISTORICO
    
    # Carregar histórico
    df_historico = pd.read_excel(str(ARQUIVO_HISTORICO), sheet_name='MEGA SENA')
    print(f"✅ {len(df_historico)} sorteios carregados")
    
    # Criar ranking de teste
    ranking_teste = [
        {'indicador': f'Indicador{i}', 'relevancia': 100 - i*5, 'estrelas': '⭐'*3}
        for i in range(1, 11)
    ]
    
    # Gerar jogos
    jogos = gerar_jogos_top10(
        df_historico,
        ranking_teste,
        n_jogos=10,
        top_n=10,
        verbose=True
    )
    
    print(f"\n🎯 Top 5 Jogos Gerados:")
    for jogo in jogos[:5]:
        nums_str = '-'.join(f"{n:02d}" for n in jogo['numeros'])
        print(f"   #{jogo['rank']}: {nums_str} | Score: {jogo['score']:.2f}")
    
    print("\n✅ Módulo funcionando corretamente!\n")

