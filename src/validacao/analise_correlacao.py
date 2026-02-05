"""
Análise de Correlação TOP 9 - MegaCLI v6.3

Analisa retroativamente quantos números do TOP 9 previsto
realmente saíram nos sorteios históricos.

Autor: MegaCLI Team
Data: 02/02/2026
Versão: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from pathlib import Path


def extrair_numeros_sorteio(sorteio_row: pd.Series) -> List[int]:
    """Extrai os 6 números de um sorteio."""
    try:
        numeros = []
        for i in range(1, 7):
            col_name = f'Bola{i}'
            if col_name in sorteio_row:
                numeros.append(int(sorteio_row[col_name]))
        return sorted(numeros)
    except:
        return []


def gerar_top9_historico(
    df_treino: pd.DataFrame,
    ranking: List[Dict]
) -> List[int]:
    """
    Gera TOP 9 usando dados históricos até determinado ponto.
    
    Simplificado: usa os 9 primeiros do universo previsto.
    """
    try:
        from src.core.previsao_30n import selecionar_top_30_numeros, refinar_selecao
        
        # Limitar histórico para não sobrecarregar
        df_recente = df_treino.tail(200) if len(df_treino) > 200 else df_treino
        
        top_30, scores_30, _, _ = selecionar_top_30_numeros(
            df_recente,
            ranking,
            verbose=False
        )
        
        lista_refinada, _ = refinar_selecao(top_30, scores_30, df_recente, verbose=False)
        
        return lista_refinada[:9]
    except Exception as e:
        # Fallback: retornar números mais frequentes
        print(f"   ⚠️ Fallback para números frequentes: {e}")
        return [1, 5, 10, 23, 27, 33, 41, 50, 54]


def analisar_correlacao_top9(
    df_historico: pd.DataFrame,
    ranking: List[Dict],
    n_sorteios_analise: int = 50
) -> Dict[str, Any]:
    """
    Analisa correlação entre TOP 9 previsto e sorteios reais.
    
    Para cada sorteio histórico:
    1. Gera TOP 9 usando dados até aquele momento
    2. Compara com números sorteados
    3. Conta acertos
    
    Args:
        df_historico: DataFrame completo
        ranking: Ranking de indicadores
        n_sorteios_analise: Quantos sorteios analisar (default: 50)
        
    Returns:
        Dict com análise completa
    """
    print(f"\n📊 Analisando correlação TOP 9 (últimos {n_sorteios_analise} sorteios)...")
    
    # Determinar range de análise
    n_total = len(df_historico)
    inicio = max(200, n_total - n_sorteios_analise)  # Mínimo 200 para ter histórico
    
    resultados = []
    
    for i in range(inicio, n_total):
        # Dados até este ponto (treino)
        df_treino = df_historico.iloc[:i]
        sorteio_real = df_historico.iloc[i]
        
        # Gerar TOP 9 previsto
        top_9_previsto = gerar_top9_historico(df_treino, ranking)
        
        # Números reais
        numeros_reais = extrair_numeros_sorteio(sorteio_real)
        
        if not numeros_reais:
            continue
        
        # Contar acertos
        acertos = len(set(top_9_previsto) & set(numeros_reais))
        
        resultado_item = {
            'concurso': int(sorteio_real.get('Concurso', i)),
            'top_9_previsto': top_9_previsto,
            'numeros_reais': numeros_reais,
            'acertos': acertos
        }
        
        resultados.append(resultado_item)
        
        # Progresso a cada 10 sorteios
        if (len(resultados) % 10 == 0):
            print(f"   Analisados: {len(resultados)}/{n_sorteios_analise}")
    
    # Estatísticas
    if not resultados:
        return {
            'sucesso': False,
            'erro': 'Nenhum sorteio analisado'
        }
    
    acertos_lista = [r['acertos'] for r in resultados]
    
    # Distribuição de acertos
    distribuicao = {}
    for i in range(7):  # 0 a 6 acertos
        distribuicao[f'{i}_acertos'] = sum(a == i for a in acertos_lista)
    
    # Taxa de sucesso (3+ acertos)
    sucesso_3_mais = sum(a >= 3 for a in acertos_lista)
    taxa_sucesso = sucesso_3_mais / len(acertos_lista) if resultados else 0
    
    # Melhor e pior
    idx_melhor = acertos_lista.index(max(acertos_lista))
    idx_pior = acertos_lista.index(min(acertos_lista))
    
    return {
        'sucesso': True,
        'n_sorteios_analisados': len(resultados),
        'acertos_medio': float(np.mean(acertos_lista)),
        'acertos_max': int(max(acertos_lista)),
        'acertos_min': int(min(acertos_lista)),
        'desvio_padrao': float(np.std(acertos_lista)),
        'taxa_sucesso_3_mais': float(taxa_sucesso),
        'distribuicao_acertos': distribuicao,
        'melhor_resultado': {
            'concurso': resultados[idx_melhor]['concurso'],
            'acertos': resultados[idx_melhor]['acertos'],
            'top_9': resultados[idx_melhor]['top_9_previsto'],
            'sorteados': resultados[idx_melhor]['numeros_reais']
        },
        'pior_resultado': {
            'concurso': resultados[idx_pior]['concurso'],
            'acertos': resultados[idx_pior]['acertos'],
            'top_9': resultados[idx_pior]['top_9_previsto'],
            'sorteados': resultados[idx_pior]['numeros_reais']
        },
        'detalhes': resultados[-10:]  # Últimos 10 para não sobrecarregar JSON
    }


def gerar_relatorio_correlacao(analise: Dict[str, Any]) -> str:
    """
    Gera relatório formatado da análise de correlação.
    
    Args:
        analise: Resultado de analisar_correlacao_top9()
        
    Returns:
        String com relatório formatado
    """
    if not analise.get('sucesso'):
        return f"❌ Erro na análise: {analise.get('erro', 'Desconhecido')}"
    
    dist = analise['distribuicao_acertos']
    n = analise['n_sorteios_analisados']
    
    relatorio = f"""
{'='*70}
📊 ANÁLISE DE CORRELAÇÃO TOP 9 vs SORTEIOS REAIS
{'='*70}

📈 Estatísticas Gerais:
   Sorteios analisados: {n}
   Acertos médio: {analise['acertos_medio']:.2f} números
   Desvio padrão: {analise['desvio_padrao']:.2f}
   Taxa de sucesso (3+): {analise['taxa_sucesso_3_mais']*100:.1f}%

📊 Distribuição de Acertos:
   0 acertos: {dist['0_acertos']:3d} ({dist['0_acertos']/n*100:5.1f}%)
   1 acerto:  {dist['1_acertos']:3d} ({dist['1_acertos']/n*100:5.1f}%)
   2 acertos: {dist['2_acertos']:3d} ({dist['2_acertos']/n*100:5.1f}%) 
   3 acertos: {dist['3_acertos']:3d} ({dist['3_acertos']/n*100:5.1f}%) ⭐
   4 acertos: {dist['4_acertos']:3d} ({dist['4_acertos']/n*100:5.1f}%) ⭐⭐
   5 acertos: {dist['5_acertos']:3d} ({dist['5_acertos']/n*100:5.1f}%) ⭐⭐⭐
   6 acertos: {dist['6_acertos']:3d} ({dist['6_acertos']/n*100:5.1f}%) 🏆

🏆 Melhor Resultado:
   Concurso: {analise['melhor_resultado']['concurso']}
   Acertos: {analise['melhor_resultado']['acertos']}
   TOP 9: {'-'.join([f'{n:02d}' for n in analise['melhor_resultado']['top_9']])}
   Sorteados: {'-'.join([f'{n:02d}' for n in analise['melhor_resultado']['sorteados']])}

💡 Interpretação:
"""
    
    # Interpretação
    acerto_medio = analise['acertos_medio']
    if acerto_medio >= 3.0:
        relatorio += "   ✅ EXCELENTE: Sistema acerta em média 3+ números!\n"
    elif acerto_medio >= 2.5:
        relatorio += "   ✅ BOM: Sistema tem boa correlação com sorteios reais.\n"
    elif acerto_medio >= 2.0:
        relatorio += "   ⚠️ RAZOÁVEL: Sistema funciona, mas pode melhorar.\n"
    else:
        relatorio += "   ❌ BAIXO: Sistema precisa de ajustes nos indicadores.\n"
    
    taxa = analise['taxa_sucesso_3_mais'] * 100
    if taxa >= 50:
        relatorio += f"   ✅ Em {taxa:.0f}% dos casos acerta 3 ou mais números!\n"
    elif taxa >= 30:
        relatorio += f"   ⚠️ Em {taxa:.0f}% dos casos acerta 3 ou mais números.\n"
    else:
        relatorio += f"   ❌ Apenas {taxa:.0f}% de sucesso com 3+ acertos.\n"
    
    relatorio += f"\n{'='*70}"
    
    return relatorio


# Exports
__all__ = [
    'analisar_correlacao_top9',
    'gerar_relatorio_correlacao',
    'extrair_numeros_sorteio',
    'gerar_top9_historico'
]


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando Análise de Correlação...\n")
    print("(Necessita dados reais para teste completo)")
    print("Execute via modo conservador")
