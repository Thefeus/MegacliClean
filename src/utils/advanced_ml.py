"""
Módulo de Machine Learning Avançado com Ensemble para Mega-Sena.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from typing import List, Tuple, Dict
import logging
import pickle
from pathlib import Path

from .app_config import config
from .feature_engineer import AdvancedFeatureEngineer
from .pair_predictor import PairPredictor


class EnsemblePredictor:
    """
    Preditor ensemble que combina Random Forest e XGBoost.
    """
    
    def __init__(self):
        self.rf_models = {}
        self.xgb_models = {}
        self.feature_names = []
        self.is_trained = False
        self.training_history = {'total_trainings': 0, 'last_accuracy': {}}
        logging.info("Ensemble Predictor inicializado")
    
    def train(
        self, 
        X: np.ndarray,
        y: np.ndarray,
        feature_names: List[str],
        rf_estimators: int = 100,
        xgb_estimators: int = 50
    ) -> Tuple[Dict, Dict]:
        """
        Treina o ensemble e retorna métricas e importância das features.
        """
        logging.info(f"Iniciando treinamento do ensemble...")
        self.feature_names = feature_names
        
        if len(X) < 10:
            raise ValueError(f"Dados insuficientes para treinar: {len(X)}")
        
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        
        accuracies = []
        all_rf_importances = []
        all_xgb_importances = []

        for num_idx in range(config.mega_sena.max_number):
            num = num_idx + 1
            y_train_num, y_val_num = y_train[:, num_idx], y_val[:, num_idx]
            
            if len(np.unique(y_train_num)) < 2:
                continue
            
            rf_model = RandomForestClassifier(n_estimators=rf_estimators, max_depth=10, min_samples_split=5, random_state=42, n_jobs=-1)
            rf_model.fit(X_train, y_train_num)
            self.rf_models[num] = rf_model
            all_rf_importances.append(rf_model.feature_importances_)
            
            xgb_model = XGBClassifier(n_estimators=xgb_estimators, max_depth=6, learning_rate=0.1, random_state=42, eval_metric='logloss', use_label_encoder=False, verbosity=0)
            xgb_model.fit(X_train, y_train_num)
            self.xgb_models[num] = xgb_model
            all_xgb_importances.append(xgb_model.feature_importances_)
            
            accuracies.append(0.6 * rf_model.score(X_val, y_val_num) + 0.4 * xgb_model.score(X_val, y_val_num))
        
        self.is_trained = True
        self.training_history['total_trainings'] += 1
        
        accuracy_metrics = {}
        if accuracies:
            accuracy_metrics = {'mean': np.mean(accuracies), 'std': np.std(accuracies), 'min': np.min(accuracies), 'max': np.max(accuracies)}
            logging.info(f"Treinamento concluído! Accuracy média: {accuracy_metrics['mean']:.3f}")

        # Calcula a importância média das features
        feature_importance_dict = {}
        if all_rf_importances and all_xgb_importances:
            avg_rf_imp = np.mean(all_rf_importances, axis=0)
            avg_xgb_imp = np.mean(all_xgb_importances, axis=0)
            combined_imp = 0.6 * avg_rf_imp + 0.4 * avg_xgb_imp
            feature_importance_dict = {name: imp for name, imp in zip(self.feature_names, combined_imp)}
            
        return accuracy_metrics, feature_importance_dict

    def predict(self, X: np.ndarray, n_numbers: int = 6, temperature: float = 1.0) -> Tuple[List[int], Dict[int, float]]:
        if not self.is_trained:
            raise RuntimeError("Modelo não treinado.")
        
        if X.ndim == 1:
            X = X.reshape(1, -1)

        probabilities = {}
        for num in range(1, config.mega_sena.max_number + 1):
            if num not in self.rf_models:
                probabilities[num] = 0.0
                continue
            
            rf_proba = self.rf_models[num].predict_proba(X)[0][1]
            xgb_proba = self.xgb_models[num].predict_proba(X)[0][1]
            combined_proba = 0.6 * rf_proba + 0.4 * xgb_proba
            
            probabilities[num] = combined_proba ** (1.0 / temperature)
        
        total_prob = sum(probabilities.values())
        if total_prob > 0:
            probabilities = {k: v / total_prob for k, v in probabilities.items()}
        
        sorted_numbers = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        predicted_numbers = [num for num, _ in sorted_numbers[:n_numbers]]
        predicted_scores = {num: probabilities[num] for num in predicted_numbers}
        
        return sorted(predicted_numbers), predicted_scores
    
    # Métodos predict_with_pairs, save_model e load_model permanecem, mas podem precisar de ajustes
    # para a nova lógica de features se forem usados externamente. Para este plano, eles não são o foco.
    
    def save_model(self, filepath: str) -> None:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        model_data = {
            'rf_models': self.rf_models,
            'xgb_models': self.xgb_models,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained,
            'training_history': self.training_history
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        logging.info(f"Modelo salvo em: {filepath}")

    def load_model(self, filepath: str) -> None:
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        self.rf_models = model_data['rf_models']
        self.xgb_models = model_data['xgb_models']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
        self.training_history = model_data['training_history']
        logging.info(f"Modelo carregado de: {filepath}")
