"""
Utilitário para detectar automaticamente nomes de colunas de números
em diferentes abas do Excel.

Autor: MegaCLI Team
Data: 23/01/2026
"""

import pandas as pd
from typing import List


def detectar_colunas_numeros(df: pd.DataFrame) -> str:
    """
    Detecta automaticamente se o DataFrame usa 'Num' ou 'Bola' para colunas.
    
    Args:
        df: DataFrame a verificar
        
    Returns:
        'Num' ou 'Bola' dependendo das colunas presentes
    """
    colunas = df.columns.tolist()
    
    # Verificar se tem Bola1
    if 'Bola1' in colunas:
        return 'Bola'
    # Verificar se tem Num1
    elif 'Num1' in colunas:
        return 'Num'
    else:
        # Padrão: assumir Bola (aba MEGA SENA)
        return 'Bola'


def extrair_numeros_sorteio(row: pd.Series, prefixo: str = None) -> List[int]:
    """
    Extrai os 6 números de um sorteio, detectando automaticamente o prefixo.
    
    Args:
        row: Linha do DataFrame
        prefixo: 'Num' ou 'Bola'. Se None, detecta automaticamente
        
    Returns:
        Lista com 6 números do sorteio
    """
    if prefixo is None:
        # Detectar automaticamente
        if 'Bola1' in row.index:
            prefixo = 'Bola'
        elif 'Num1' in row.index:
            prefixo = 'Num'
        else:
            prefixo = 'Bola'  # Padrão
    
    return [int(row[f'{prefixo}{i}']) for i in range(1, 7)]


# Exports
__all__ = ['detectar_colunas_numeros', 'extrair_numeros_sorteio']
