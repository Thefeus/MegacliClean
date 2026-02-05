"""
Avaliador de Eficácia de Indicadores - MegaCLI v5.0

Calcula eficácia individual de cada indicador contra série histórica.
Usado pela FASE 1 Etapa 0 para atualizar PESOS FINAIS.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Callable, Union
from datetime import datetime
from pathlib import Path
import json
from tqdm import tqdm

from utils.indicador_base import IndicadorBase, IndicadorWrapper


def calcular_eficacia_indicador(
    indicador: Union[IndicadorBase, Callable],
    historico: pd.DataFrame,
    n_sorteios: int = 100,
    nome_indicador: str = None
) -> Dict[str, Any]:
    """
    Calcula eficácia de um indicador em série histórica.
    
    Args:
        indicador: IndicadorBase ou função legada
        historico: DataFrame histórico completo
        n_sorteios: Quantos sorteios analisar
        nome_indicador: Nome (obrigatório se for função)
        
    Returns:
        Dict com:
            - nome: str
            - eficacia_%: float
            - taxa_4+_%: float
            - taxa_5+_%: float
            - taxa_6_%: float
            - score_medio: float
            - timestamp: str
    """
    # Se for função, criar wrapper
    if not isinstance(indicador, IndicadorBase):
        if nome_indicador is None:
            raise ValueError("nome_indicador obrigatório para funções legadas")
        indicador = IndicadorWrapper(nome_indicador, indicador)
    
    # Analisar série histórica
    resultado = indicador.analisar_serie_historica(historico, n_sorteios)
    
    # Adicionar timestamp
    resultado['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return resultado


def avaliar_todos_indicadores(
    indicadores_dict: Dict[str, Union[IndicadorBase, Callable]],
    historico: pd.DataFrame,
    n_sorteios: int = 100,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Avalia todos os indicadores e retorna DataFrame com resultados.
    
    Args:
        indicadores_dict: Dict {nome: indicador/funcao}
        historico: DataFrame histórico
        n_sorteios: Quantos sorteios por indicador
        verbose: Mostrar progresso
        
    Returns:
        DataFrame com colunas:
            - Indicador
            - Eficácia_%
            - Taxa_4+_%
            - Taxa_5+_%
            - Taxa_6_%
            - Score_Médio
            - Última_Análise
    """
    resultados = []
    total = len(indicadores_dict)
    
    if verbose:
        print(f"\n📊 Avaliando {total} indicadores...")
        print(f"   Série histórica: {n_sorteios} sorteios\n")
    
    # Criar barra de progresso com tqdm
    indicadores_items = list(indicadores_dict.items())
    
    if verbose:
        pbar = tqdm(
            indicadores_items, 
            desc="📊 Avaliando Indicadores",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]',
            ncols=100
        )
    else:
        pbar = indicadores_items
    
    for nome, indicador in pbar:
        # Atualizar descrição da barra com o indicador atual
        if verbose:
            pbar.set_description(f"📊 {nome[:25]:25s}")
        
        try:
            resultado = calcular_eficacia_indicador(
                indicador,
                historico,
                n_sorteios,
                nome_indicador=nome
            )
            
            resultados.append({
                'Indicador': nome,
                'Eficácia_%': resultado['eficacia_%'],
                'Taxa_4+_%': resultado['taxa_4+_%'],
                'Taxa_5+_%': resultado['taxa_5+_%'],
                'Taxa_6_%': resultado['taxa_6_%'],
                'Score_Médio': resultado['score_medio'],
                'Desvio_Padrão': resultado.get('desvio_padrao', 0),
                'Última_Análise': resultado['timestamp']
            })
            
            # Atualizar postfix com a eficácia calculada
            if verbose:
                pbar.set_postfix({'Eficácia': f"{resultado['eficacia_%']:5.2f}%"})
        
        except Exception as e:
            if verbose:
                pbar.set_postfix({'Status': f"❌ Erro"})
            
            resultados.append({
                'Indicador': nome,
                'Eficácia_%': 0.0,
                'Taxa_4+_%': 0.0,
                'Taxa_5+_%': 0.0,
                'Taxa_6_%': 0.0,
                'Score_Médio': 0.0,
                'Desvio_Padrão': 0.0,
                'Última_Análise': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
    
    df_resultado = pd.DataFrame(resultados)
    
    # Ordenar por eficácia (maior primeiro)
    df_resultado = df_resultado.sort_values('Eficácia_%', ascending=False).reset_index(drop=True)
    
    if verbose:
        print(f"\n✅ Avaliação concluída!")
        print(f"   Média geral de eficácia: {df_resultado['Eficácia_%'].mean():.2f}%")
        print(f"   Melhor indicador: {df_resultado.iloc[0]['Indicador']} ({df_resultado.iloc[0]['Eficácia_%']:.2f}%)")
    
    return df_resultado


def salvar_eficacias_cache(df_eficacias: pd.DataFrame, arquivo: str = "cache/eficacias_indicadores.json"):
    """Salva eficácias em cache JSON"""
    Path(arquivo).parent.mkdir(parents=True, exist_ok=True)
    
    dados = df_eficacias.to_dict('records')
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def carregar_eficacias_cache(arquivo: str = "cache/eficacias_indicadores.json") -> pd.DataFrame:
    """Carrega eficácias do cache se existir"""
    if Path(arquivo).exists():
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        return pd.DataFrame(dados)
    return pd.DataFrame()


def mesclar_eficacias_com_pesos(
    df_pesos: pd.DataFrame,
    df_eficacias: pd.DataFrame
) -> pd.DataFrame:
    """
    Mescla eficácias calculadas com pesos existentes.
    
    Args:
        df_pesos: DataFrame atual com Indicador, Peso
        df_eficacias: DataFrame com eficácias calculadas
        
    Returns:
        DataFrame mesclado com todas as colunas
    """
    # Merge por Indicador
    df_merged = pd.merge(
        df_pesos,
        df_eficacias[[
            'Indicador', 'Eficácia_%', 'Taxa_4+_%', 
            'Taxa_5+_%', 'Taxa_6_%', 'Última_Análise'
        ]],
        on='Indicador',
        how='left'
    )
    
    # Preencher NaN com 0 ou "N/A"
    df_merged['Eficácia_%'] = df_merged['Eficácia_%'].fillna(0)
    df_merged['Taxa_4+_%'] = df_merged['Taxa_4+_%'].fillna(0)
    df_merged['Taxa_5+_%'] = df_merged['Taxa_5+_%'].fillna(0)
    df_merged['Taxa_6_%'] = df_merged['Taxa_6_%'].fillna(0)
    df_merged['Última_Análise'] = df_merged['Última_Análise'].fillna('N/A')
    
    return df_merged
