"""
Módulo de Feature Engineering Avançado para Análise de Mega-Sena.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import Counter
import logging
from .app_config import config

def _get_digital_root(n: int) -> int:
    """Calcula a raiz digital de um número. Função helper."""
    while n >= 10:
        n = sum(int(digit) for digit in str(n))
    return n

class AdvancedFeatureEngineer:
    """
    Extrai features avançadas de dados históricos da Mega-Sena.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        if self.df.empty:
            raise ValueError("DataFrame de entrada para AdvancedFeatureEngineer não pode estar vazio.")
        self.balls = config.get_ball_columns()
        self.n_numbers = config.mega_sena.max_number
        logging.info(f"Feature Engineer inicializado com {len(df)} sorteios")
    
    def extract_tesla_features(self) -> pd.DataFrame:
        """Extrai features baseadas nos 'Princípios de Tesla' (3,6,9)."""
        logging.info("Extraindo features de Tesla...")
        features = {}
        
        # Cria colunas temporárias para os cálculos
        temp_df = self.df.copy()
        temp_df['Tesla_Div_3_Count'] = temp_df[self.balls].apply(lambda row: sum(1 for x in row if x % 3 == 0), axis=1)
        temp_df['Tesla_DR_369_Count'] = temp_df[self.balls].apply(lambda row: sum(1 for x in row if _get_digital_root(x) in [3, 6, 9]), axis=1)
        temp_df['Soma'] = temp_df[self.balls].sum(axis=1)
        temp_df['Tesla_Sum_DR'] = temp_df['Soma'].apply(_get_digital_root)

        # Agrega como features
        features['tesla_div_3_mean'] = temp_df['Tesla_Div_3_Count'].mean()
        features['tesla_dr_369_mean'] = temp_df['Tesla_DR_369_Count'].mean()
        features['tesla_sum_dr_last'] = temp_df['Tesla_Sum_DR'].iloc[-1]
        
        return pd.DataFrame([features])

    def extract_frequency_features(self, window_sizes: List[int] = [10, 50, 100, 250, 500]) -> pd.DataFrame:
        logging.info("Extraindo features de frequência...")
        features = {}
        for window in window_sizes:
            effective_window = min(window, len(self.df))
            if effective_window == 0: continue
            recent_draws = self.df.tail(effective_window)
            all_numbers = recent_draws[self.balls].values.flatten()
            freq_counts = Counter(all_numbers)
            for num in range(1, self.n_numbers + 1):
                features[f'freq_w{window}_n{num}'] = freq_counts.get(num, 0) / effective_window
        return pd.DataFrame([features])
    
    def extract_delay_features(self) -> pd.DataFrame:
        logging.info("Extraindo features de atraso...")
        features = {}
        last_appearance = {num: -1 for num in range(1, self.n_numbers + 1)}
        for idx, row in self.df.iterrows():
            for num in row[self.balls].values:
                last_appearance[num] = idx
        
        last_idx = self.df.index[-1]
        for num, idx in last_appearance.items():
            features[f'delay_n{num}'] = last_idx - idx if idx != -1 else len(self.df)
        return pd.DataFrame([features])
    
    def extract_statistical_features(self) -> pd.DataFrame:
        logging.info("Extraindo features estatísticas...")
        sums = self.df[self.balls].sum(axis=1)
        even_counts = self.df[self.balls].apply(lambda row: sum(1 for x in row if x % 2 == 0), axis=1)
        
        all_numbers_flat = self.df[self.balls].values.flatten()
        if all_numbers_flat.size == 0:
            entropy = 0
        else:
            probs = pd.Series(all_numbers_flat).value_counts(normalize=True)
            entropy = -np.sum(probs * np.log2(probs))
            
        features = {
            'sum_mean': sums.mean(),
            'sum_std': sums.std(),
            'even_ratio_mean': (even_counts / 6).mean(),
            'distribution_entropy': entropy
        }
        return pd.DataFrame([features])

    def build_feature_matrix(self) -> Tuple[pd.DataFrame, List[str]]:
        """Constrói matriz completa de features combinando todos os métodos."""
        logging.info("Construindo matriz completa de features...")
        
        # Extrai todas as features
        freq_features = self.extract_frequency_features()
        delay_features = self.extract_delay_features()
        stat_features = self.extract_statistical_features()
        tesla_features = self.extract_tesla_features()
        
        # Combina todos os DataFrames
        all_features = pd.concat([
            freq_features,
            delay_features,
            stat_features,
            tesla_features
        ], axis=1)
        
        feature_names = all_features.columns.tolist()
        logging.info(f"Matriz de features construída: {len(feature_names)} features")
        return all_features, feature_names