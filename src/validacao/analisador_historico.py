"""
Analisador Histórico - MegaCLI v5.0

Avalia todos os 42 indicadores contra cada jogo da série histórica
para identificar quais indicadores têm melhor taxa de acerto.

Autor: MegaCLI v5.0
Data: 27/12/2024
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
import json


@dataclass
class EstatisticasIndicador:
    """Estatísticas de desempenho de um indicador"""
    nome: str
    total_jogos: int = 0
    acertos_3_ou_mais: int = 0
    acertos_4_ou_mais: int = 0
    acertos_5_ou_mais: int = 0
    acertos_sena: int = 0
    score_total: float = 0.0
    scores: List[float] = None
    
    def __post_init__(self):
        if self.scores is None:
            self.scores = []
    
    @property
    def taxa_acerto_3_mais(self) -> float:
        return (self.acertos_3_ou_mais / self.total_jogos * 100) if self.total_jogos > 0 else 0.0
    
    @property
    def taxa_acerto_4_mais(self) -> float:
        return (self.acertos_4_ou_mais / self.total_jogos * 100) if self.total_jogos > 0 else 0.0
    
    @property
    def taxa_acerto_5_mais(self) -> float:
        return (self.acertos_5_ou_mais / self.total_jogos * 100) if self.total_jogos > 0 else 0.0
    
    @property
    def score_medio(self) -> float:
        return (self.score_total / self.total_jogos) if self.total_jogos > 0 else 0.0
    
    @property
    def desvio_padrao(self) -> float:
        return np.std(self.scores) if len(self.scores) > 0 else 0.0
    
    def to_dict(self) -> Dict:
        """Converte para dict sem lista de scores (muito grande)"""
        d = asdict(self)
        d['taxa_acerto_3+'] = round(self.taxa_acerto_3_mais, 2)
        d['taxa_acerto_4+'] = round(self.taxa_acerto_4_mais, 2)
        d['taxa_acerto_5+'] = round(self.taxa_acerto_5_mais, 2)
        d['score_medio'] = round(self.score_medio, 2)
        d['desvio_padrao'] = round(self.desvio_padrao, 2)
        del d['scores']  # Não salvar lista completa
        del d['score_total']
        return d


def calcular_acertos_jogo(numeros_previstos: List[int], 
                           resultado_real: List[int]) -> int:
    """
    Calcula quantos números acertou.
    
    Args:
        numeros_previstos: Lista com 6 números previstos
        resultado_real: Lista com 6 números do sorteio real
        
    Returns:
        Quantidade de acertos (0-6)
    """
    set_prev = set(numeros_previstos)
    set_real = set(resultado_real)
    return len(set_prev & set_real)


def avaliar_jogo_contra_indicadores(
    historico_anterior: pd.DataFrame,
    resultado_real: List[int],
    todos_indicadores: Dict[str, callable]
) -> Dict[str, Tuple[float, int]]:
    """
    Avalia um jogo real contra todos os indicadores.
    
    Args:
        historico_anterior: DataFrame com histórico até antes deste jogo
        resultado_real: Números que saíram neste jogo
        todos_indicadores: Dict {nome: funcao_calculo}
        
    Returns:
        Dict {nome_indicador: (score, acertos)}
    """
    resultados = {}
    
    for nome_indicador, funcao_calculo in todos_indicadores.items():
        try:
            # Calcular score do indicador para os números que realmente saíram
            score = funcao_calculo(historico_anterior, resultado_real)
            
            # Score alto = indicador "aprovou" este jogo
            # Registrar score para análise posterior
            resultados[nome_indicador] = (score, None)  # None porque não prevemos números aqui
            
        except Exception as e:
            # Em caso de erro, score = 0
            resultados[nome_indicador] = (0.0, 0)
    
    return resultados


def avaliar_serie_historica_completa(
    df_historico: pd.DataFrame,
    janela_inicial: int = 500,
    passo: int = 1,
    max_jogos: int = None
) -> Dict[str, EstatisticasIndicador]:
    """
    Avalia toda a série histórica.
    
    Para cada jogo N:
    - Usa jogos 1 até N-1 como base
    - Calcula score de cada indicador para o jogo N
    - Registra estatísticas
    
    Args:
        df_historico: DataFrame completo
        janela_inicial: Mínimo de jogos para começar análise
        passo: Passo de avaliação (1 = todos os jogos)
        max_jogos: Máximo de jogos a avaliar (None = todos)
        
    Returns:
        Dict {nome_indicador: EstatisticasIndicador}
    """
    # Import da função helper
    from utils.funcoes_principais import criar_all_indicators_dict
    
    print("\n" + "="*80)
    print("🔍 ETAPA 1: ANÁLISE HISTÓRICA COMPLETA - Avaliando Indicadores")
    print("="*80)
    
    # Carregar todos os indicadores disponíveis
    todos_indicadores = criar_all_indicators_dict()
    
    print(f"\n📊 Indicadores carregados: {len(todos_indicadores)}")
    print(f"   Janela inicial: {janela_inicial} jogos")
    print(f"   Total para avaliar: {len(df_historico) - janela_inicial} jogos\n")
    
    # Inicializar estatísticas
    estatisticas = {
        nome: EstatisticasIndicador(nome=nome)
        for nome in todos_indicadores.keys()
    }
    
    ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    
    # Determinar range de jogos a avaliar
    inicio = janela_inicial
    fim = len(df_historico) if max_jogos is None else min(janela_inicial + max_jogos, len(df_historico))
    
    jogos_avaliados = 0
    
    # Para cada jogo após a janela inicial (COM PROGRESS BAR)
    from tqdm import tqdm
    
    with tqdm(total=fim-inicio, desc="📊 Avaliando jogos históricos", 
              unit="jogo", ncols=100) as pbar:
        
        for idx in range(inicio, fim, passo):
            # Histórico anterior (tudo antes deste jogo)
            hist_anterior = df_historico.iloc[:idx]
            
            # Jogo atual (resultado real)
            jogo_atual = df_historico.iloc[idx]
            resultado_real = [int(jogo_atual[col]) for col in ball_cols if pd.notna(jogo_atual[col])]
            
            # Avaliar este jogo
            resultados = avaliar_jogo_contra_indicadores(
                hist_anterior,
                resultado_real,
                todos_indicadores
            )
            
            # Atualizar estatísticas
            for nome_ind, (score, _) in resultados.items():
                estat = estatisticas[nome_ind]
                estat.total_jogos += 1
                estat.score_total += score
                estat.scores.append(score)
                
                # Score alto (>70) = indicador "previu bem"
                if score >= 70:
                    estat.acertos_3_ou_mais += 1
                if score >= 80:
                    estat.acertos_4_ou_mais += 1
                if score >= 90:
                    estat.acertos_5_ou_mais += 1
                if score >= 95:
                    estat.acertos_sena += 1
            
            jogos_avaliados += 1
            pbar.update(1)
            
            # Atualizar descrição com indicador sendo avaliado
            if jogos_avaliados % 10 == 0:
                pbar.set_postfix({
                    'Indicadores': len(todos_indicadores),
                    'Avg_Score': f"{np.mean([s for e in estatisticas.values() for s in e.scores[-10:]]):.1f}"
                })
    
    print(f"\n✅ Análise completa: {jogos_avaliados} jogos avaliados")
    print(f"   Estatísticas geradas para {len(estatisticas)} indicadores\n")
    
    return estatisticas


def salvar_estatisticas(estatisticas: Dict[str, EstatisticasIndicador],
                        arquivo: str = 'Resultado/estatisticas_indicadores.json'):
    """
    Salva estatísticas em JSON.
    
    Args:
        estatisticas: Dict com estatísticas
        arquivo: Caminho do arquivo
    """
    # Converter para dict serializável
    dados = {
        nome: estat.to_dict()
        for nome, estat in estatisticas.items()
    }
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Estatísticas salvas em: {arquivo}")


def carregar_estatisticas(arquivo: str = 'Resultado/estatisticas_indicadores.json') -> Dict[str, Dict]:
    """
    Carrega estatísticas de JSON.
    
    Returns:
        Dict com estatísticas
    """
    with open(arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)
