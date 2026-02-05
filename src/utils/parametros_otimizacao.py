"""
Classe Base para Parâmetros de Otimização - MegaCLI v6.0

Define estrutura de parâmetros ajustáveis para indicadores otimizados.

Autor: MegaCLI Team
Data: 22/01/2026
Versão: 1.0.0
"""

from dataclasses import dataclass, asdict
from typing import Dict
import json


@dataclass
class ParametrosOtimizacao:
    """
    Parâmetros ajustáveis para otimização de indicadores.
    
    Attributes:
        peso_frequencia: Peso da métrica de frequência (0-1)
        peso_co_ocorrencia: Peso da métrica de co-ocorrência (0-1)
        peso_tendencia: Peso da métrica de tendência (0-1)
        janela_principal: Número de sorteios para análise principal
        janela_recente: Número de sorteios recentes para bônus
        bonus_recencia: Multiplicador para números recentes
        bonus_consistencia: Multiplicador para números consistentes
        penalidade_ausencia: Multiplicador para números ausentes
    """
    
    # Pesos das métricas (devem somar 1.0)
    peso_frequencia: float = 0.40
    peso_co_ocorrencia: float = 0.30
    peso_tendencia: float = 0.30
    
    # Janelas de análise
    janela_principal: int = 100
    janela_recente: int = 10
    
    # Bônus e penalidades
    bonus_recencia: float = 1.1
    bonus_consistencia: float = 1.05
    penalidade_ausencia: float = 0.9
    
    def __post_init__(self):
        """Valida parâmetros após inicialização."""
        # Validar que pesos somam ~1.0
        soma_pesos = self.peso_frequencia + self.peso_co_ocorrencia + self.peso_tendencia
        if abs(soma_pesos - 1.0) > 0.01:
            raise ValueError(f"Pesos devem somar 1.0, soma atual: {soma_pesos}")
        
        # Validar ranges
        if not (0 <= self.peso_frequencia <= 1):
            raise ValueError("peso_frequencia deve estar entre 0 e 1")
        if not (0 <= self.peso_co_ocorrencia <= 1):
            raise ValueError("peso_co_ocorrencia deve estar entre 0 e 1")
        if not (0 <= self.peso_tendencia <= 1):
            raise ValueError("peso_tendencia deve estar entre 0 e 1")
        
        if self.janela_principal < 10:
            raise ValueError("janela_principal deve ser >= 10")
        if self.janela_recente < 1:
            raise ValueError("janela_recente deve ser >= 1")
    
    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ParametrosOtimizacao':
        """Cria instância a partir de dicionário."""
        return cls(**data)
    
    def to_json(self) -> str:
        """Converte para JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ParametrosOtimizacao':
        """Cria instância a partir de JSON."""
        return cls.from_dict(json.loads(json_str))
    
    def __str__(self) -> str:
        """Representação em string."""
        return (
            f"ParametrosOtimizacao(\n"
            f"  Pesos: F={self.peso_frequencia:.2f}, "
            f"CO={self.peso_co_ocorrencia:.2f}, "
            f"T={self.peso_tendencia:.2f}\n"
            f"  Janelas: Principal={self.janela_principal}, "
            f"Recente={self.janela_recente}\n"
            f"  Bônus: Recência={self.bonus_recencia:.2f}, "
            f"Consistência={self.bonus_consistencia:.2f}\n"
            f")"
        )


# Exports
__all__ = ['ParametrosOtimizacao']


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando ParametrosOtimizacao...\n")
    
    # Criar com valores padrão
    params = ParametrosOtimizacao()
    print("Parâmetros padrão:")
    print(params)
    
    # Testar conversão para dict/json
    print("\nJSON:")
    print(params.to_json())
    
    # Testar criação a partir de dict
    params2 = ParametrosOtimizacao.from_dict(params.to_dict())
    print("\nRecriado a partir de dict:")
    print(params2)
    
    # Testar validação
    try:
        params_invalido = ParametrosOtimizacao(
            peso_frequencia=0.5,
            peso_co_ocorrencia=0.3,
            peso_tendencia=0.3  # Soma > 1.0
        )
    except ValueError as e:
        print(f"\n✅ Validação funcionando: {e}")
    
    print("\n✅ Módulo funcionando corretamente!\n")
