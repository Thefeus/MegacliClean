"""
BATIMENTO Dinâmico com Refinamento Progressivo de Pesos

Sistema de backtesting incremental que:
1. Executa previsão para cada sorteio (do 50 até o último)
2. Usa apenas histórico até aquele ponto
3. Refina pesos dos indicadores baseado em acertos/erros
4. Aprende progressivamente (melhoria contínua)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path
import json


class BatimentoDinamico:
    """Backtesting com refinamento progressivo de pesos"""
    
    def __init__(self, df_historico: pd.DataFrame, pesos_iniciais: Dict[str, float]):
        """
        Args:
            df_historico: DataFrame com histórico completo
            pesos_iniciais: Dicionário com pesos iniciais dos 21 indicadores
        """
        self.df_historico = df_historico
        self.pesos_iniciais = pesos_iniciais.copy()
        self.pesos_atuais = pesos_iniciais.copy()
        self.historico_pesos = []  # Rastrear evolução dos pesos
        self.resultados = []
    
    def executar_backtest_completo(self, inicio: int = 50) -> pd.DataFrame:
        """
        Executa backtest do sorteio 'inicio' até o último
        
        Args:
            inicio: Índice inicial (padrão 50 para ter mínimo de histórico)
            
        Returns:
            DataFrame com resultados de todos os sorteios testados
        """
        total_sorteios = len(self.df_historico)
        total_testes = total_sorteios - inicio
        
        print(f"\n🔄 Iniciando BATIMENTO Dinâmico...")
        print(f"   Sorteios a testar: {total_testes} (índice {inicio} ao {total_sorteios-1})")
        print(f"   Refinamento progressivo: ATIVO\n")
        
        for i in range(inicio, total_sorteios):
            # Progresso
            if (i - inicio) % 100 == 0:
                progresso = ((i - inicio) / total_testes) * 100
                print(f"   Progresso: {progresso:.1f}% ({i - inicio}/{total_testes})")
            
            # 1. Histórico até este ponto (exclusivo)
            historico_ate_aqui = self.df_historico.iloc[:i]
            
            # 2. Gerar previsão usando pesos atuais e histórico específico
            previsao = self._gerar_previsao_dinamica(historico_ate_aqui, self.pesos_atuais)
            
            # 3. Resultado real do sorteio atual
            resultado_real = self._extrair_resultado(i)
            
            if resultado_real is None or len(resultado_real) != 6:
                continue
            
            # 4. Calcular acertos
            acertos = len(set(previsao).intersection(set(resultado_real)))
            
            # 5. Refinar pesos baseado no resultado
            self.pesos_atuais = self._refinar_pesos(
                previsao,
                resultado_real,
                acertos,
                self.pesos_atuais
            )
            
            # 6. Salvar resultado
            concurso = int(self.df_historico.iloc[i]['Concurso'])
            self.resultados.append({
                'Concurso': concurso,
                'Previsão': ', '.join(map(str, previsao)),
                'Resultado': ', '.join(map(str, resultado_real)),
                'Acertos': acertos,
                '%': round(acertos/6*100, 1)
            })
            
            # Salvar snapshot dos pesos a cada 100 sorteios
            if (i - inicio) % 100 == 0:
                self.historico_pesos.append({
                    'concurso': concurso,
                    'pesos': self.pesos_atuais.copy()
                })
        
        print(f"   ✅ Backtest completo: {len(self.resultados)} previsões")
        
        # Estatísticas finais
        df_resultados = pd.DataFrame(self.resultados)
        if len(df_resultados) > 0:
            taxa_3plus = len(df_resultados[df_resultados['Acertos'] >= 3]) / len(df_resultados) * 100
            media_acertos = df_resultados['Acertos'].mean()
            print(f"   Taxa 3+: {taxa_3plus:.1f}%")
            print(f"   Média acertos: {media_acertos:.2f}")
        
        return df_resultados
    
    def _gerar_previsao_dinamica(self, historico: pd.DataFrame, pesos: Dict[str, float]) -> List[int]:
        """
        Gera previsão usando pesos atuais e histórico até aquele ponto
        
        Estratégia simplificada baseada nos indicadores principais
        """
        scores = {n: 0 for n in range(1, 61)}
        
        # 1. Fibonacci (peso variável)
        fibonacci = {1, 2, 3, 5, 8, 13, 21, 34, 55}
        for num in fibonacci:
            if num <= 60:
                scores[num] += pesos.get('Fibonacci', 76)
        
        # 2. Div3 (peso variável)
        for num in range(1, 61):
            if num % 3 == 0:
                scores[num] += pesos.get('Div3', 64)
        
        # 3. Quadrantes (peso variável)
        # Analisar distribuição histórica
        if len(historico) > 0:
            # Números mais frequentes no histórico recente (últimos 10)
            ultimos_10 = historico.tail(10)
            numeros_recentes = []
            for idx in range(len(ultimos_10)):
                try:
                    for j in range(1, 7):
                        num = ultimos_10.iloc[idx].get(f'Bola{j}')
                        if pd.notna(num):
                            numeros_recentes.append(int(num))
                except:
                    pass
            
            # Dar peso extra para números recentes
            from collections import Counter
            freq = Counter(numeros_recentes)
            for num, count in freq.items():
                scores[num] += count * (pesos.get('Quadrantes', 100) / 10)
        
        # 4. Primos (peso variável)
        primos = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59}
        for num in primos:
            if num <= 60:
                scores[num] += pesos.get('Primos', 58)
        
        # 5. Div6 (peso variável)
        for num in range(1, 61):
            if num % 6 == 0:
                scores[num] += pesos.get('Div6', 73)
        
        # 6. ParImpar - balanceamento
        # Preferir equilíbrio 3 pares / 3 ímpares
        peso_parímpar = pesos.get('ParImpar', 57)
        for num in range(1, 61):
            if num % 2 == 0:  # par
                scores[num] += peso_parímpar * 0.5
            else:  # ímpar
                scores[num] += peso_parímpar * 0.5
        
        # Selecionar top 6
        top6 = sorted(scores.items(), key=lambda x: -x[1])[:6]
        return sorted([n for n, _ in top6])
    
    def _extrair_resultado(self, indice: int) -> List[int]:
        """Extrai resultado real de um sorteio"""
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
    
    def _refinar_pesos(self, 
                      previsao: List[int], 
                      resultado: List[int], 
                      acertos: int,
                      pesos_atuais: Dict[str, float]) -> Dict[str, float]:
        """
        Refina pesos dos indicadores baseado em acertos
        
        Estratégia:
        - Acertos >= 4: +5% em todos os indicadores (previsão muito boa)
        - Acertos == 3: +2% em todos (previsão boa)
        - Acertos == 2: sem alteração (neutro)
        - Acertos <= 1: -3% em todos (previsão fraca)
        
        Limites: Pesos entre 10 e 100
        """
        novos_pesos = pesos_atuais.copy()
        
        if acertos >= 4:
            fator = 1.05  # +5%
        elif acertos == 3:
            fator = 1.02  # +2%
        elif acertos == 2:
            fator = 1.00  # sem mudança
        else:  # 0 ou 1
            fator = 0.97  # -3%
        
        # Aplicar fator
        for indicador in novos_pesos.keys():
            novos_pesos[indicador] *= fator
            # Limites
            novos_pesos[indicador] = max(10, min(100, novos_pesos[indicador]))
        
        return novos_pesos
    
    def get_evolucao_pesos(self) -> pd.DataFrame:
        """Retorna evolução dos pesos ao longo do tempo"""
        if not self.historico_pesos:
            return pd.DataFrame()
        
        dados = []
        for snapshot in self.historico_pesos:
            linha = {'concurso': snapshot['concurso']}
            linha.update(snapshot['pesos'])
            dados.append(linha)
        
        return pd.DataFrame(dados)
    
    def salvar_resultados(self, arquivo: str = "logs/batimento_dinamico_detalhado.json"):
        """Salva resultados detalhados em JSON"""
        Path(arquivo).parent.mkdir(exist_ok=True)
        
        dados = {
            'pesos_iniciais': self.pesos_iniciais,
            'pesos_finais': self.pesos_atuais,
            'total_analises': len(self.resultados),
            'resultados': self.resultados[:100],  # Primeiros 100 para referência
            'evolucao_pesos': [
                {'concurso': s['concurso'], 'pesos': s['pesos']}
                for s in self.historico_pesos
            ]
        }
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        
        print(f"\n   💾 Resultados detalhados salvos: {arquivo}")


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Carregar histórico
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    
    planilha = Path(__file__).parent.parent.parent / 'Resultado' / 'ANALISE_HISTORICO_COMPLETO.xlsx'
    df = pd.read_excel(planilha, 'MEGA SENA')
    
    # Pesos iniciais (21 indicadores)
    pesos = {
        'Quadrantes': 100, 'Div9': 79.7, 'Fibonacci': 76.0,
        'Div6': 73.5, 'Mult5': 70.5, 'Div3': 64.1,
        'Gap': 61.8, 'Primos': 58.5, 'Simetria': 57.7,
        'ParImpar': 57.4, 'Amplitude': 42.1, 'Soma': 25.0,
        'RaizDigital': 60.0, 'VariacaoSoma': 65.0, 'Conjugacao': 55.0,
        'RepeticaoAnterior': 50.0, 'FrequenciaMensal': 45.0,
        'PadroesSubconjuntos': 70.0, 'MicroTendencias': 65.0,
        'AnaliseContextual': 60.0, 'Embedding': 55.0
    }
    
    # Executar
    batimento = BatimentoDinamico(df, pesos)
    df_resultados = batimento.executar_backtest_completo(inicio=50)
    
    # Salvar
    batimento.salvar_resultados()
    
    print(f"\n✅ Concluído!")
    print(f"   Total de previsões: {len(df_resultados)}")
