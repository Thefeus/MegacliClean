"""
BATIMENTO v2.0 - Múltiplas Estratégias Simultâneas

Testa 5 estratégias diferentes lado a lado:
1. Conservadora - Baseada em frequências
2. Agressiva - Números atrasados
3. Balanceada - Mix de indicadores
4. IA Periódica - Consulta Gemini (rate limited)
5. Pesos+Frequências - Usa indicadores e análise de frequência

Cada linha do BATIMENTO mostra:
- Resultado real
- Previsão de cada estratégia
- Acertos de cada uma
- Justificativa
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from pathlib import Path
import json

# Importar estratégias
from validacao.estrategias_previsao import GeradorMultiplasEstrategias


class BatimentoMultiplasEstrategias:
    """BATIMENTO com 5 estratégias simultâneas"""
    
    def __init__(self, df_historico: pd.DataFrame, pesos_iniciais: Dict[str, float]):
        self.df_historico = df_historico
        self.pesos = pesos_iniciais
        self.gerador = GeradorMultiplasEstrategias()
        self.resultados = []
    
    def executar_backtest_completo(self, inicio: int = 50) -> pd.DataFrame:
        """
        Executa backtest com todas as 5 estratégias
        
        Returns:
            DataFrame com colunas para cada estratégia
        """
        total_sorteios = len(self.df_historico)
        total_testes = total_sorteios - inicio
        
        print(f"\n🔄 BATIMENTO v2.0 - 2 Estratégias Otimizadas")
        print(f"   Sorteios a testar: {total_testes}")
        print(f"   Estratégias: IA Periódica + Pesos+Frequências\n")
        
        for i in range(inicio, total_sorteios):
            # Progresso
            if (i - inicio) % 100 == 0:
                progresso = ((i - inicio) / total_testes) * 100
                print(f"   Progresso: {progresso:.1f}% ({i - inicio}/{total_testes})")
            
            # Histórico até este ponto
            historico_ate_aqui = self.df_historico.iloc[:i]
            
            # Resultado real
            resultado_real = self._extrair_resultado(i)
            if not resultado_real:
                continue
            
            # Gerar com APENAS 2 estratégias otimizadas
            previsoes = {}
            
            # 1. IA Periódica
            prev_ia, just_ia = self.gerador.estrategia_ia.gerar(historico_ate_aqui, i)
            previsoes['IA'] = (prev_ia, just_ia)
            
            # 2. Pesos+Frequências (baseada em indicadores)
            prev_pesos, just_pesos = self._estrategia_pesos_frequencias(historico_ate_aqui)
            previsoes['Pesos+Freq'] = (prev_pesos, just_pesos)
            
            # Calcular acertos de cada
            linha_resultado = {
                'Concurso': int(self.df_historico.iloc[i]['Concurso']),
                'Resultado': ', '.join(map(str, resultado_real))
            }
            
            for nome_estrategia, (prev, just) in previsoes.items():
                acertos = len(set(prev).intersection(set(resultado_real)))
                linha_resultado[f'{nome_estrategia}_Prev'] = ', '.join(map(str, prev))
                linha_resultado[f'{nome_estrategia}_Acertos'] = acertos
                linha_resultado[f'{nome_estrategia}_Just'] = just
            
            self.resultados.append(linha_resultado)
        
        df_resultado = pd.DataFrame(self.resultados)
        
        # Estatísticas finais
        print(f"\n📊 Estatísticas por Estratégia:")
        print("="*60)
        
        estrategias = ['IA', 'Pesos+Freq']
        
        for est in estrategias:
            col_acertos = f'{est}_Acertos'
            if col_acertos in df_resultado.columns:
                taxa_3plus = len(df_resultado[df_resultado[col_acertos] >= 3]) / len(df_resultado) * 100
                media = df_resultado[col_acertos].mean()
                print(f"   {est:15s}: Taxa 3+ = {taxa_3plus:5.1f}%  |  Média = {media:.2f}")
        
        return df_resultado
    
    def _estrategia_pesos_frequencias(self, historico: pd.DataFrame) -> tuple:
        """
        Estratégia baseada em pesos dos indicadores + frequências
        
        Usa os 26 indicadores com seus pesos atuais
        Pondera por frequência histórica
        """
        from collections import Counter
        
        scores = {n: 0 for n in range(1, 61)}
        
        # 1. Calcular frequências
        freq = Counter()
        for idx in range(len(historico)):
            try:
                for j in range(1, 7):
                    num = historico.iloc[idx].get(f'Bola{j}')
                    if pd.notna(num):
                        freq[int(num)] += 1
            except:
                pass
        
        media_freq = np.mean(list(freq.values())) if freq else 0
        
        # 2. Aplicar indicadores com pesos
        fibonacci = {1, 2, 3, 5, 8, 13, 21, 34, 55}
        for num in fibonacci:
            if num <= 60:
                scores[num] += self.pesos.get('Fibonacci', 76) * 0.5
        
        primos = {2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59}
        for num in primos:
            if num <= 60:
                scores[num] += self.pesos.get('Primos', 58.5) * 0.4
        
        for num in range(1, 61):
            if num % 3 == 0:
                scores[num] += self.pesos.get('Div3', 64) * 0.3
            if num % 6 == 0:
                scores[num] += self.pesos.get('Div6', 73.5) * 0.3
        
        # 3. Ponderar por frequência
        for num in range(1, 61):
            f = freq.get(num, 0)
            # Números com frequência próxima à média ganham boost
            if media_freq > 0:
                if 0.9 * media_freq <= f <= 1.1 * media_freq:
                    scores[num] += 20
                elif 0.7 * media_freq <= f <= 1.3 * media_freq:
                    scores[num] += 10
        
        # Selecionar top 6
        top6 = sorted(scores.items(), key=lambda x: -x[1])[:6]
        previsao = sorted([n for n, _ in top6])
        
        # Estatísticas para justificativa
        fibs = len([n for n in previsao if n in fibonacci])
        freq_nums = [freq.get(n, 0) for n in previsao]
        
        justificativa = f"Ind:{fibs}fib, Freq:média={np.mean(freq_nums):.1f}"
        
        return previsao, justificativa
    
    def _extrair_resultado(self, indice: int) -> List[int]:
        """Extrai resultado real"""
        try:
            linha = self.df_historico.iloc[indice]
            resultado = sorted([
                int(linha[f'Bola{j}'])
                for j in range(1, 7)
                if pd.notna(linha.get(f'Bola{j}'))
            ])
            return resultado if len(resultado) == 6 else None
        except:
            return None
    
    def salvar_resultados(self, arquivo: str = "logs/batimento_v2_multiplas_estrategias.json"):
        """Salva resultados"""
        Path(arquivo).parent.mkdir(exist_ok=True)
        
        # Análise comparativa
        df = pd.DataFrame(self.resultados)
        
        estrategias = ['IA', 'Pesos+Freq']
        
        resumo = {}
        for est in estrategias:
            col = f'{est}_Acertos'
            if col in df.columns:
                resumo[est] = {
                    'taxa_3plus': float(len(df[df[col] >= 3]) / len(df) * 100),
                    'taxa_4plus': float(len(df[df[col] >= 4]) / len(df) * 100),
                    'media_acertos': float(df[col].mean()),
                    'total_previsoes': len(df)
                }
        
        dados = {
            'resumo_estrategias': resumo,
            'melhor_estrategia': max(resumo.items(), key=lambda x: x[1]['taxa_3plus'])[0] if resumo else None,
            'total_analises': len(df)
        }
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        
        print(f"\n   💾 Resultados salvos: {arquivo}")


# ============================================================================
# ALIAS PARA COMPATIBILIDADE COM v5.0
# ============================================================================

class BatchTester(BatimentoMultiplasEstrategias):
    """
    Alias para compatibilidade com gerar_analise_v5.py
    
    v5.0 espera BatchTester com método executar_batimento_completo()
    Esta classe herda de BatimentoMultiplasEstrategias e adiciona o método esperado.
    """
    
    def executar_batimento_completo(self, df_historico: pd.DataFrame, ranking: List[Dict] = None, todos_indicadores: Dict = None) -> pd.DataFrame:
        """
        Método compatível com v5.0 + Análise de Ganhadores com TOP 10
        
        Args:
            df_historico: DataFrame com histórico completo
            ranking: Lista de indicadores ranqueados (opcional)
            todos_indicadores: Dict com todos indicadores (opcional)
            
        Returns:
            DataFrame com resultados para aba GANHADORES
        """
        # Atualizar histórico se necessário
        if df_historico is not None and len(df_historico) > 0:
            self.df_historico = df_historico
        
        # Se tiver ranking, fazer análise TOP 10
        if ranking and todos_indicadores:
            print("\n" + "🏆"*40)
            print("FASE 5: ANÁLISE GANHADORES - TOP 10 INDICADORES")
            print("🏆"*40)
            
            from validacao.analise_ganhadores_top10 import (
                gerar_com_top_indicadores,
                comparar_com_historico,
                calcular_correlacao_indicadores,
                atualizar_aba_ganhadores
            )
            
            # 1. Gerar jogos com TOP 10 indicadores
            print("\n📊 Gerando jogos com TOP 10 indicadores...")
            
            # Importar configuração
            from src.core.config import AnaliseConfig
            
            jogos_top10 = gerar_com_top_indicadores(
                self.df_historico,
                ranking,
                todos_indicadores,
                n_jogos=AnaliseConfig.FASE5_N_JOGOS_ANALISE
            )
            print(f"   ✅ {len(jogos_top10)} jogos gerados")
            
            # 2. Comparar com histórico (últimos 100 sorteios)
            print("\n🔍 Comparando com série histórica...")
            historico_recente = self.df_historico.tail(100)
            df_comparacao = comparar_com_historico(jogos_top10, historico_recente)
            print(f"   ✅ {len(df_comparacao)} sorteios analisados")
            
            # 3. Calcular correlação
            print("\n📈 Calculando correlação dos indicadores...")
            df_correlacao = calcular_correlacao_indicadores(
                self.df_historico,
                ranking,
                todos_indicadores
            )
            print(f"   ✅ Correlação de {len(df_correlacao)} indicadores")
            
            # 4. Montar aba GANHADORES
            print("\n📋 Montando aba GANHADORES...")
            df_ganhadores = atualizar_aba_ganhadores(
                df_comparacao,
                df_correlacao,
                ranking
            )
            
            # Estatísticas finais
            taxa_4plus = df_comparacao['Total_Acertos_4plus'].sum() / len(df_comparacao) if len(df_comparacao) > 0 else 0
            print(f"\n📊 RESUMO:")
            print(f"   • Sorteios analisados: {len(df_comparacao)}")
            print(f"   • Taxa 4+ acertos: {taxa_4plus:.2%}")
            print(f"   • Melhor resultado: {df_comparacao['Melhor_Jogo'].max()} acertos")
            
            return df_ganhadores
        
        # Fallback: batimento padrão (se não tiver ranking/indicadores)
        else:
            print("\n⏭️ Análise TOP 10 não disponível - executando batimento padrão")
            inicio = max(50, len(self.df_historico) - 50)
            df_resultado = self.executar_backtest_completo(inicio=inicio)
            self.salvar_resultados()
            return df_resultado


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    planilha = Path(__file__).parent.parent.parent / 'Resultado' / 'ANALISE_HISTORICO_COMPLETO.xlsx'
    df = pd.read_excel(planilha, 'MEGA SENA')
    
    # Pesos (26 indicadores)
    pesos = {
        'Quadrantes': 100, 'Div9': 79.7, 'Fibonacci': 76.0,
        'Div6': 73.5, 'Mult5': 70.5, 'Div3': 64.1,
        'Gap': 61.8, 'Primos': 58.5, 'Simetria': 57.7,
        'ParImpar': 57.4, 'Amplitude': 42.1, 'Soma': 25.0,
        'RaizDigital': 60.0, 'VariacaoSoma': 65.0, 'Conjugacao': 55.0,
        'RepeticaoAnterior': 50.0, 'FrequenciaMensal': 45.0,
        'PadroesSubconjuntos': 70.0, 'MicroTendencias': 65.0,
        'AnaliseContextual': 60.0, 'Embedding': 55.0,
        'Sequencias': 50.0, 'DistanciaMedia': 55.0,
        'NumerosExtremos': 45.0, 'PadraoDezena': 50.0,
        'CicloAparicao': 52.0
    }
    
    # Executar
    batimento = BatimentoMultiplasEstrategias(df, pesos)
    df_resultado = batimento.executar_backtest_completo(inicio=50)
    
    # Salvar
    batimento.salvar_resultados()
    
    print(f"\n✅ Concluído! {len(df_resultado)} previsões geradas")
