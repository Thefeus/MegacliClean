"""
from src.utils.detector_colunas import extrair_numeros_sorteio
Sistema de Refinamento Automático - MegaCLI v6.0

Sistema que aprende e melhora parâmetros automaticamente a cada execução.

Autor: MegaCLI Team
Data: 22/01/2026
Versão: 1.0.0
"""

import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from src.utils.parametros_otimizacao import ParametrosOtimizacao


class SistemaRefinamento:
    """Sistema de refinamento automático de parâmetros."""
    
    def __init__(self, dir_historico: Path):
        """
        Args:
            dir_historico: Diretório para salvar histórico
        """
        self.dir_historico = dir_historico
        self.dir_historico.mkdir(parents=True, exist_ok=True)
    
    def salvar_execucao(
        self,
        universo: str,
        numeros: List[int],
        parametros: ParametrosOtimizacao,
        metricas: Dict[str, float]
    ) -> None:
        """Salva execução no histórico."""
        arquivo = self.dir_historico / f"{universo}_execucoes.json"
        
        # Carregar histórico existente
        historico = []
        if arquivo.exists():
            with open(arquivo, 'r') as f:
                historico = json.load(f)
        
        # Adicionar nova execução
        execucao = {
            'timestamp': datetime.now().isoformat(),
            'numeros': numeros,
            'parametros': parametros.to_dict(),
            'metricas': metricas
        }
        
        historico.append(execucao)
        
        # Salvar
        with open(arquivo, 'w') as f:
            json.dump(historico, f, indent=2)
    
    def calcular_metricas_performance(
        self,
        numeros: List[int],
        df_historico: pd.DataFrame,
        janela: int = 100
    ) -> Dict[str, float]:
        """Calcula métricas de performance."""
        df_teste = df_historico.tail(janela)
        
        acertos_6 = 0
        acertos_5 = 0
        acertos_4 = 0
        lista_acertos = []
        
        for _, row in df_teste.iterrows():
            numeros_sorteio = set([row[f'Bola{i}'] for i in range(1, 7)])
            acertos = len(numeros_sorteio & set(numeros))
            lista_acertos.append(acertos)
            
            if acertos == 6:
                acertos_6 += 1
            if acertos >= 5:
                acertos_5 += 1
            if acertos >= 4:
                acertos_4 += 1
        
        taxa_6 = (acertos_6 / janela) * 100
        taxa_5 = (acertos_5 / janela) * 100
        taxa_4 = (acertos_4 / janela) * 100
        
        # Calcular eficiência ponderada
        eficiencia = (taxa_6 * 3 + taxa_5 * 2 + taxa_4) / 6
        
        import numpy as np
        consistencia = np.std(lista_acertos)
        
        return {
            'taxa_cobertura_6': taxa_6,
            'taxa_cobertura_5': taxa_5,
            'taxa_cobertura_4': taxa_4,
            'score_medio': np.mean(lista_acertos),
            'consistencia': consistencia,
            'eficiencia': eficiencia
        }
    
    def otimizar_parametros(
        self,
        universo: str
    ) -> Tuple[ParametrosOtimizacao, str]:
        """
        Otimiza parâmetros baseado no histórico.
        
        Returns:
            (parametros_otimizados, recomendacao)
        """
        arquivo = self.dir_historico / f"{universo}_execucoes.json"
        
        if not arquivo.exists():
            # Primeira execução - usar padrão
            return self._get_parametros_padrao(universo), "Primeira execução - usando padrão"
        
        # Carregar histórico
        with open(arquivo, 'r') as f:
            historico = json.load(f)
        
        if len(historico) < 2:
            return self._get_parametros_padrao(universo), "Histórico insuficiente - usando padrão"
        
        # Pegar última execução
        ultima = historico[-1]
        params_atual = ParametrosOtimizacao.from_dict(ultima['parametros'])
        metricas_atual = ultima['metricas']
        
        # Pegar penúltima para comparação
        penultima = historico[-2]
        metricas_anterior = penultima['metricas']
        
        # Calcular delta de eficiência
        delta_eficiencia = metricas_atual['eficiencia'] - metricas_anterior['eficiencia']
        
        # Ajustar parâmetros baseado em performance
        if delta_eficiencia < -5:  # Piorou muito
            # Reverter para anterior
            params_otimizado = ParametrosOtimizacao.from_dict(penultima['parametros'])
            recomendacao = f"Revertendo (piora de {delta_eficiencia:.1f}%)"
        
        elif delta_eficiencia < 0:  # Piorou levemente
            # Ajuste conservador
            params_otimizado = self._interpolar_parametros(params_atual, penultima['parametros'], 0.5)
            recomendacao = f"Ajuste conservador (piora de {delta_eficiencia:.1f}%)"
        
        elif delta_eficiencia < 2:  # Melhorou pouco
            # Pequeno ajuste na mesma direção
            params_otimizado = self._extrapolar_parametros(params_atual, penultima['parametros'], 0.1)
            recomendacao = f"Continuando direção (melhora de {delta_eficiencia:.1f}%)"
        
        else:  # Melhorou muito
            # Ajuste maior na mesma direção
            params_otimizado = self._extrapolar_parametros(params_atual, penultima['parametros'], 0.2)
            recomendacao = f"Acelerando melhoria (+{delta_eficiencia:.1f}%)"
        
        return params_otimizado, recomendacao
    
    def _get_parametros_padrao(self, universo: str) -> ParametrosOtimizacao:
        """Retorna parâmetros padrão por universo."""
        if universo == '9N':
            return ParametrosOtimizacao(
                peso_frequencia=0.30,
                peso_co_ocorrencia=0.45,
                peso_tendencia=0.25,
                janela_principal=50,
                bonus_recencia=1.2
            )
        elif universo == '10N':
            return ParametrosOtimizacao(
                peso_frequencia=0.35,
                peso_co_ocorrencia=0.35,
                peso_tendencia=0.30,
                janela_principal=75,
                bonus_recencia=1.15
            )
        else:  # 20N
            return ParametrosOtimizacao(
                peso_frequencia=0.45,
                peso_co_ocorrencia=0.30,
                peso_tendencia=0.25,
                janela_principal=100,
                bonus_recencia=1.1
            )
    
    def _interpolar_parametros(self, params1: ParametrosOtimizacao, params2_dict: Dict, fator: float) -> ParametrosOtimizacao:
        """Interpola entre dois conjuntos de parâmetros."""
        params2 = ParametrosOtimizacao.from_dict(params2_dict)
        
        return ParametrosOtimizacao(
            peso_frequencia=params1.peso_frequencia * (1 - fator) + params2.peso_frequencia * fator,
            peso_co_ocorrencia=params1.peso_co_ocorrencia * (1 - fator) + params2.peso_co_ocorrencia * fator,
            peso_tendencia=params1.peso_tendencia * (1 - fator) + params2.peso_tendencia * fator,
            janela_principal=int(params1.janela_principal * (1 - fator) + params2.janela_principal * fator),
            bonus_recencia=params1.bonus_recencia * (1 - fator) + params2.bonus_recencia * fator
        )
    
    def _extrapolar_parametros(self, params1: ParametrosOtimizacao, params2_dict: Dict, fator: float) -> ParametrosOtimizacao:
        """Extrapola na direção de melhoria."""
        params2 = ParametrosOtimizacao.from_dict(params2_dict)
        
        # Calcular direção de mudança
        delta_freq = params1.peso_frequencia - params2.peso_frequencia
        delta_co_oc = params1.peso_co_ocorrencia - params2.peso_co_ocorrencia
        delta_tend = params1.peso_tendencia - params2.peso_tendencia
        
        # Extrapolar
        novo_freq = params1.peso_frequencia + delta_freq * fator
        novo_co_oc = params1.peso_co_ocorrencia + delta_co_oc * fator
        novo_tend = params1.peso_tendencia + delta_tend * fator
        
        # Normalizar para somar 1.0
        soma = novo_freq + novo_co_oc + novo_tend
        novo_freq /= soma
        novo_co_oc /= soma
        novo_tend /= soma
        
        return ParametrosOtimizacao(
            peso_frequencia=novo_freq,
            peso_co_ocorrencia=novo_co_oc,
            peso_tendencia=novo_tend,
            janela_principal=params1.janela_principal,
            bonus_recencia=params1.bonus_recencia
        )


# Exports
__all__ = ['SistemaRefinamento']

