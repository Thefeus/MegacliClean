"""
Classe Base para Indicadores - MegaCLI v5.0

Fornece interface padronizada para todos os indicadores.
Permite análise individual e cálculo de eficácia.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Callable
from abc import ABC, abstractmethod


class IndicadorBase(ABC):
    """
    Classe base abstrata para todos os indicadores.
    
    Todos os indicadores devem herdar desta classe e implementar:
    - nome (property)
    - avaliar() - retorna score 0-100 para números
    - analisar_serie_historica() - analisa eficácia em sorteios passados
    """
    
    @property
    @abstractmethod
    def nome(self) -> str:
        """Nome do indicador"""
        pass
    
    @property
    def descricao(self) -> str:
        """Descrição opcional do indicador"""
        return f"Indicador {self.nome}"
    
    @abstractmethod
    def avaliar(self, historico: pd.DataFrame, numeros: List[int]) -> float:
        """
        Avalia um conjunto de números usando este indicador.
        
        Args:
            historico: DataFrame com histórico de sorteios
            numeros: Lista de 6 números a avaliar
            
        Returns:
            Score de 0 a 100
        """
        pass
    
    def analisar_serie_historica(
        self,
        historico: pd.DataFrame,
        n_sorteios: int = 100,
        ball_cols: List[str] = None
    ) -> Dict[str, Any]:
        """
        Analisa eficácia deste indicador em sorteios históricos.
        
        Args:
            historico: DataFrame completo
            n_sorteios: Quantos sorteios analisar (últimos N)
            ball_cols: Colunas das bolas
            
        Returns:
            Dict com estatísticas de eficácia
        """
        if ball_cols is None:
            ball_cols = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
        
        # Limitar ao número de sorteios disponíveis
        n_sorteios = min(n_sorteios, len(historico))
        historico_teste = historico.tail(n_sorteios)
        
        scores = []
        acertos_4plus = 0
        acertos_5plus = 0
        acertos_6 = 0
        
        # Analisar cada sorteio
        for idx, row in historico_teste.iterrows():
            # Extrair números do sorteio
            numeros_sorteio = []
            for col in ball_cols:
                if pd.notna(row.get(col)):
                    numeros_sorteio.append(int(row[col]))
            
            if len(numeros_sorteio) != 6:
                continue
            
            try:
                # Avaliar este sorteio usando histórico anterior
                idx_atual = historico.index.get_loc(idx)
                historico_anterior = historico.iloc[:idx_atual]
                
                if len(historico_anterior) > 0:
                    score = self.avaliar(historico_anterior, numeros_sorteio)
                    scores.append(score)
                    
                    # Classificar acertos (score alto = bom prognóstico)
                    if score >= 70:  # Threshold para "acerto"
                        acertos_4plus += 1
                        if score >= 80:
                            acertos_5plus += 1
                        if score >= 90:
                            acertos_6 += 1
            except Exception as e:
                # Ignorar erros individuais
                pass
        
        # Calcular estatísticas
        if scores:
            eficacia_pct = (acertos_4plus / len(scores)) * 100 if scores else 0
            taxa_4plus = (acertos_4plus / len(scores)) * 100 if scores else 0
            taxa_5plus = (acertos_5plus / len(scores)) * 100 if scores else 0
            taxa_6 = (acertos_6 / len(scores)) * 100 if scores else 0
        else:
            eficacia_pct = 0
            taxa_4plus = 0
            taxa_5plus = 0
            taxa_6 = 0
        
        return {
            'nome': self.nome,
            'eficacia_%': round(eficacia_pct, 2),
            'taxa_4+_%': round(taxa_4plus, 2),
            'taxa_5+_%': round(taxa_5plus, 2),
            'taxa_6_%': round(taxa_6, 2),
            'score_medio': round(np.mean(scores), 2) if scores else 0,
            'score_max': round(max(scores), 2) if scores else 0,
            'score_min': round(min(scores), 2) if scores else 0,
            'desvio_padrao': round(np.std(scores), 2) if scores else 0,
            'n_sorteios_analisados': len(scores)
        }


class IndicadorWrapper(IndicadorBase):
    """
    Wrapper para adaptar funções legadas (signature antiga) à nova interface.
    
    Funções antigas têm signature: f(historico, numeros) -> float
    Este wrapper as transforma em classes IndicadorBase.
    """
    
    def __init__(self, nome: str, funcao_legada: Callable, descricao: str = ""):
        self._nome = nome
        self._funcao = funcao_legada
        self._descricao = descricao or f"Indicador {nome} (wrapper)"
    
    @property
    def nome(self) -> str:
        return self._nome
    
    @property
    def descricao(self) -> str:
        return self._descricao
    
    def avaliar(self, historico: pd.DataFrame, numeros: List[int]) -> float:
        """Delega para função legada"""
        try:
            return self._funcao(historico, numeros)
        except Exception as e:
            # Fallback em caso de erro
            return 50.0  # Score neutro


def criar_wrapper_para_funcao(nome: str, funcao: Callable) -> IndicadorBase:
    """
    Helper para criar wrapper de função legada.
    
    Args:
        nome: Nome do indicador
        funcao: Função com signature (historico, numeros) -> float
        
    Returns:
        IndicadorBase compatível
    """
    return IndicadorWrapper(nome, funcao)


def criar_wrappers_batch(indicadores_dict: Dict[str, Callable]) -> Dict[str, IndicadorBase]:
    """
    Cria wrappers para todos indicadores de um dict.
    
    Args:
        indicadores_dict: Dict {nome: funcao}
        
    Returns:
        Dict {nome: IndicadorBase}
    """
    return {
        nome: criar_wrapper_para_funcao(nome, funcao)
        for nome, funcao in indicadores_dict.items()
    }
