"""
Modo Conservador - MegaCLI v6.2

Modo de operação estatisticamente robusto e conservador.
Usa apenas indicadores robustos, universo maior e validação rigorosa.

Autor: MegaCLI Team
Data: 02/02/2026
Versão: 1.0.0
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from src.core.metricas_confianca import gerar_relatorio_estatistico
from src.validacao.validador_train_test import validacao_train_test_split
from src.validacao.detector_overfitting import DetectorOverfitting


class ModoConservador:
    """
    Modo de operação conservador e estatisticamente robusto.
    """
    
    # Indicadores mais robustos (menor risco de overfitting)
    INDICADORES_ROBUSTOS = [
        'Quadrantes',
        'ParImpar',
        'Soma',
        'Primos',
        'Gap',
        'Fibonacci',
        'Dezenas'
    ]
    
    # Configuração conservadora
    CONFIG = {
        'max_indicadores': 7,
        'min_universo': 25,
        'validacao_cruzada': True,
        'intervalo_confianca': 0.95,
        'split_train_test': True,
        'split_ratio': 0.8,
        'n_jogos': 100,  # Reduzido para menor custo
    }
    
    def __init__(self):
        self.detector = DetectorOverfitting()
    
    def filtrar_indicadores_robustos(
        self,
        ranking_completo: List[Dict]
    ) -> List[Dict]:
        """
        Filtra apenas indicadores robustos e confiáveis.
        
        Args:
            ranking_completo: Ranking completo de indicadores
            
        Returns:
            Lista com apenas indicadores robustos
        """
        ranking_filtrado = []
        
        for ind in ranking_completo:
            nome = ind['indicador']
            
            # Verificar se é um indicador robusto
            if any(robusto.lower() in nome.lower() for robusto in self.INDICADORES_ROBUSTOS):
                ranking_filtrado.append(ind)
        
        # Limitar ao máximo configurado
        ranking_filtrado = ranking_filtrado[:self.CONFIG['max_indicadores']]
        
        print(f"\n🔒 Modo Conservador: {len(ranking_filtrado)} indicadores robustos selecionados")
        for i, ind in enumerate(ranking_filtrado, 1):
            print(f"   {i}. {ind['indicador']} (relevância: {ind.get('relevancia', 50):.1f})")
        
        return ranking_filtrado
    
    def selecionar_universo_conservador(
        self,
        df_historico: pd.DataFrame,
        ranking_robustos: List[Dict]
    ) -> Dict[str, Any]:
        """
        Seleciona universo reduzido de forma conservadora (mínimo 25 números).
        
        Args:
            df_historico: DataFrame histórico
            ranking_robustos: Ranking de indicadores robustos
            
        Returns:
            Dict com universo e métricas
        """
        from src.core.previsao_30n import selecionar_top_30_numeros, refinar_selecao
        
        print(f"\n🎯 Selecionando universo conservador (mínimo {self.CONFIG['min_universo']} números)...")
        
        # Usar últimos 200 sorteios para análise
        df_recente = df_historico.tail(200)
        
        # Gerar TOP 30
        top_30, scores_30, _, _ = selecionar_top_30_numeros(
            df_recente,
            ranking_robustos,
            verbose=False
        )
        
        lista_refinada, _ = refinar_selecao(top_30, scores_30, df_recente, verbose=False)
        
        # Pegar top 25-30 para ser conservador
        universo = lista_refinada[:self.CONFIG['min_universo']]
        
        print(f"   ✅ Universo: {len(universo)} números")
        print(f"   📋 {'-'.join(f'{n:02d}' for n in universo)}")
        
        return {
            'numeros': universo,
            'tamanho': len(universo),
            'scores': {n: scores_30.get(n, 50) for n in universo}
        }
    
    def executar_analise_conservadora(
        self,
        df_historico: pd.DataFrame,
        ranking_completo: List[Dict]
    ) -> Dict[str, Any]:
        """
        Executa análise completa no modo conservador.
        
        Args:
            df_historico: DataFrame histórico
            ranking_completo: Ranking completo de indicadores
            
        Returns:
            Dict com análise completa
        """
        print("\n" + "="*70)
        print("🔒 MODO CONSERVADOR - ANÁLISE ESTATISTICAMENTE ROBUSTA")
        print("="*70)
        
        # 1. Filtrar indicadores robustos
        ranking_robustos = self.filtrar_indicadores_robustos(ranking_completo)
        
        # 2. Validação Train/Test
        print("\n📊 Executando validação Train/Test rigorosa...")
        resultado_validacao = validacao_train_test_split(
            df_historico,
            ranking_robustos,
            split_ratio=self.CONFIG['split_ratio']
        )
        
        # 3. Análise de overfitting
        print("\n🔬 Analisando sinais de overfitting...")
        analise_overfit = self.detector.analisar(
            performance_treino=resultado_validacao['treino']['taxa_4_mais_top30'],
            performance_teste=resultado_validacao['teste']['taxa_4_mais_top30'],
            n_indicadores=len(ranking_robustos),
            tamanho_universo=self.CONFIG['min_universo']
        )
        
        print(self.detector.gerar_relatorio_visual(analise_overfit))
        
        # 4. Selecionar universo conservador
        universo = self.selecionar_universo_conservador(df_historico, ranking_robustos)
        
        # 5. Gerar jogos conservadores
        print(f"\n🎲 Gerando {self.CONFIG['n_jogos']} jogos conservadores...")
        jogos = self._gerar_jogos_conservadores(
            df_historico,
            ranking_robustos,
            universo['numeros']
        )
        
        # 6. Gerar previsões expandidas (TOP 20, 15, 10, 9)
        print(f"\n🎯 Gerando previsões expandidas (TOP 20/15/10/9)...")
        top_20_numeros = universo['numeros'][:20]
        top_15_numeros = universo['numeros'][:15]
        top_10_numeros = universo['numeros'][:10]
        top_9_numeros = universo['numeros'][:9]
        
        # Calcular scores médios
        score_medio_top20 = np.mean([universo['scores'][n] for n in top_20_numeros])
        score_medio_top15 = np.mean([universo['scores'][n] for n in top_15_numeros])
        score_medio_top10 = np.mean([universo['scores'][n] for n in top_10_numeros])
        score_medio_top9 = np.mean([universo['scores'][n] for n in top_9_numeros])
        
        # Gerar jogos automáticos do TOP 9
        print(f"\n🎲 Gerando jogos automáticos com TOP 9...")
        jogos_top9 = self._gerar_todos_jogos_top9(top_9_numeros)
        
        # Análise de correlação TOP 9 (opcional, pode demorar)
        print(f"\n📊 Executando análise de correlação TOP 9...")
        from src.validacao.analise_correlacao import analisar_correlacao_top9, gerar_relatorio_correlacao
        
        try:
            analise_correlacao = analisar_correlacao_top9(
                df_historico,
                ranking_robustos,
                n_sorteios_analise=min(50, len(df_historico) - 200)
            )
            
            if analise_correlacao.get('sucesso'):
                print(gerar_relatorio_correlacao(analise_correlacao))
            else:
                print(f"   ⚠️ Análise não pôde ser realizada: {analise_correlacao.get('erro')}")
                analise_correlacao = None
        except Exception as e:
            print(f"   ⚠️ Erro na análise de correlação: {e}")
            analise_correlacao = None
        
        # 7. Relatório final
        print("\n" + "="*70)
        print("📊 RELATÓRIO FINAL - MODO CONSERVADOR")
        print("="*70)
        
        print(f"\n✅ Configuração:")
        print(f"   • Indicadores: {len(ranking_robustos)}")
        print(f"   • Universo: {universo['tamanho']} números")
        print(f"   • Jogos gerados: {len(jogos)}")
        
        print(f"\n📈 Performance (com intervalos de confiança 95%):")
        print(gerar_relatorio_estatistico(
            resultado_validacao['treino']['acertos_top30'],
            "Taxa Acerto Treino",
            'decimal'
        ))
        print(gerar_relatorio_estatistico(
            resultado_validacao['teste']['acertos_top30'],
            "Taxa Acerto Teste",
            'decimal'
        ))
        
        print(f"\n🎯 Nível de Risco: {analise_overfit['nivel_risco']}")
        if analise_overfit['nivel_risco'] == "BAIXO":
            print("   ✅ Sistema está robusto e generaliza bem!")
        
        # Mostrar todas as previsões
        print(f"\n" + "="*70)
        print(f"🎯 PREVISÕES PARA PRÓXIMO SORTEIO")
        print("="*70)
        
        print(f"\n2️⃣0️⃣ TOP 20 NÚMEROS (Score médio: {score_medio_top20:.1f}):")
        print(f"   {' - '.join([f'{n:02d}' for n in top_20_numeros])}")
        
        print(f"\n1️⃣5️⃣ TOP 15 NÚMEROS (Score médio: {score_medio_top15:.1f}):")
        print(f"   {' - '.join([f'{n:02d}' for n in top_15_numeros])}")
        
        print(f"\n🔟 TOP 10 NÚMEROS (Score médio: {score_medio_top10:.1f}):")
        print(f"   {' - '.join([f'{n:02d}' for n in top_10_numeros])}")
        
        print(f"\n9️⃣  TOP 9 NÚMEROS (Score médio: {score_medio_top9:.1f}):")
        print(f"   {' - '.join([f'{n:02d}' for n in top_9_numeros])}")
        
        print(f"\n🎲 JOGOS AUTOMÁTICOS TOP 9:")
        print(f"   Total de jogos possíveis: {len(jogos_top9)}")
        print(f"   Primeiros 3 jogos:")
        for i, jogo in enumerate(jogos_top9[:3], 1):
            print(f"     {i}. {'-'.join([f'{n:02d}' for n in jogo['numeros']])}")
        print(f"   ... (todos salvos em arquivo)")
        
        print(f"\n💡 Dica: Use TOP 9 para jogos mais focados ou TOP 15/20 para maior cobertura!")
        print("="*70)
        
        # Gerar visualizações gráficas
        print(f"\n📊 Gerando visualizações gráficas...")
        from src.core.visualizacao_graficos import gerar_todas_visualizacoes
        from src.core.config import RESULTADO_DIR
        
        try:
            graficos_dir = RESULTADO_DIR / 'graficos'
            arquivos_graficos = gerar_todas_visualizacoes(
                {
                    'universo': universo,
                    'previsoes': {
                        'top_20': {'numeros': top_20_numeros},
                        'top_15': {'numeros': top_15_numeros},
                        'top_10': {'numeros': top_10_numeros},
                        'top_9': {'numeros': top_9_numeros}
                    },
                    'analise_correlacao': analise_correlacao
                },
                graficos_dir
            )
            
            if arquivos_graficos:
                print(f"\n📁 Gráficos salvos em: graficos/")
                for arq in arquivos_graficos:
                    print(f"   • {arq.name}")
        except Exception as e:
            print(f"\n⚠️ Não foi possível gerar gráficos: {e}")
            arquivos_graficos = []
        
        return {
            'timestamp': datetime.now().isoformat(),
            'modo': 'CONSERVADOR',
            'ranking_robustos': ranking_robustos,
            'universo': universo,
            'validacao': resultado_validacao,
            'analise_overfitting': analise_overfit,
            'jogos': jogos,
            'previsoes': {
                'top_20': {
                    'numeros': top_20_numeros,
                    'score_medio': float(score_medio_top20),
                    'formatado': '-'.join([f'{n:02d}' for n in top_20_numeros])
                },
                'top_15': {
                    'numeros': top_15_numeros,
                    'score_medio': float(score_medio_top15),
                    'formatado': '-'.join([f'{n:02d}' for n in top_15_numeros])
                },
                'top_10': {
                    'numeros': top_10_numeros,
                    'score_medio': float(score_medio_top10),
                    'formatado': '-'.join([f'{n:02d}' for n in top_10_numeros])
                },
                'top_9': {
                    'numeros': top_9_numeros,
                    'score_medio': float(score_medio_top9),
                    'formatado': '-'.join([f'{n:02d}' for n in top_9_numeros])
                }
            },
            'jogos_top9': {
                'total': len(jogos_top9),
                'jogos': jogos_top9
            },
            'analise_correlacao': analise_correlacao if analise_correlacao and analise_correlacao.get('sucesso') else None,
            'config': self.CONFIG
        }
    
    def _gerar_todos_jogos_top9(self, top_9_numeros: List[int]) -> List[Dict]:
        """
        Gera todas as combinações possíveis de 6 números do TOP 9.
        
        Total: C(9,6) = 84 jogos
        """
        from itertools import combinations
        
        todas_combinacoes = list(combinations(top_9_numeros, 6))
        
        jogos = []
        for i, comb in enumerate(todas_combinacoes, 1):
            jogos.append({
                'id': i,
                'numeros': sorted(list(comb))
            })
        
        print(f"   ✅ {len(jogos)} jogos gerados (C(9,6) = 84)")
        
        return jogos
    
    def _gerar_jogos_conservadores(
        self,
        df_historico: pd.DataFrame,
        ranking: List[Dict],
        universo: List[int]
    ) -> List[Dict]:
        """Gera jogos usando apenas o universo conservador."""
        from src.core.gerador_jogos_top10 import gerar_jogos_top10
        
        # Gerar jogos com universo filtrado
        jogos_brutos = gerar_jogos_top10(
            df_historico,
            ranking,
            n_jogos=self.CONFIG['n_jogos'] * 2,  # Gerar mais para filtrar
            top_n=len(ranking),
            verbose=False
        )
        
        # Filtrar apenas jogos dentro do universo conservador
        universo_set = set(universo)
        jogos_filtrados = []
        
        for jogo in jogos_brutos:
            if set(jogo['numeros']).issubset(universo_set):
                jogos_filtrados.append(jogo)
        
        # Retornar apenas o número solicitado
        return jogos_filtrados[:self.CONFIG['n_jogos']]


# Exports
__all__ = ['ModoConservador']


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando Modo Conservador...\n")
    print("(Necessita dados reais para teste completo)")
    print("Execute via menu interativo (Opção 12)")
