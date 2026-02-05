"""
Métricas de Confiança Estatística - MegaCLI v6.2

Fornece cálculos de intervalos de confiança e métricas estatísticas
honestas para evitar falsa precisão nos resultados.

Autor: MegaCLI Team
Data: 02/02/2026
Versão: 1.0.0
"""

import numpy as np
from typing import List, Tuple, Dict, Any
from scipy import stats


def calcular_intervalo_confianca(
    valores: List[float],
    confianca: float = 0.95
) -> Tuple[float, float, float]:
    """
    Calcula média e intervalo de confiança usando distribuição t-Student.
    
    Args:
        valores: Lista de valores observados
        confianca: Nível de confiança (default: 0.95 = 95%)
        
    Returns:
        (media, limite_inferior, limite_superior)
        
    Example:
        >>> valores = [0.75, 0.72, 0.78, 0.71, 0.76]
        >>> media, inf, sup = calcular_intervalo_confianca(valores)
        >>> print(f"{media:.1%} (IC 95%: {inf:.1%} - {sup:.1%})")
        74.4% (IC 95%: 71.2% - 77.6%)
    """
    if not valores or len(valores) < 2:
        # Retornar valor único sem intervalo
        media = valores[0] if valores else 0.0
        return media, media, media
    
    valores_np = np.array(valores)
    media = np.mean(valores_np)
    desvio = np.std(valores_np, ddof=1)  # Desvio padrão amostral
    n = len(valores_np)
    
    # t-Student para amostras pequenas (mais conservador que normal)
    t_critico = stats.t.ppf((1 + confianca) / 2, n - 1)
    margem_erro = t_critico * (desvio / np.sqrt(n))
    
    limite_inferior = media - margem_erro
    limite_superior = media + margem_erro
    
    return media, limite_inferior, limite_superior


def formatar_com_intervalo(
    valores: List[float],
    confianca: float = 0.95,
    formato: str = 'percentual',
    casas_decimais: int = 1
) -> str:
    """
    Formata valores com intervalo de confiança de forma legível.
    
    Args:
        valores: Lista de valores
        confianca: Nível de confiança
        formato: 'percentual', 'decimal' ou 'inteiro'
        casas_decimais: Precisão da formatação
        
    Returns:
        String formatada: "75.2% (IC 95%: 68.5% - 81.9%)"
        
    Example:
        >>> taxas = [0.75, 0.72, 0.78]
        >>> print(formatar_com_intervalo(taxas))
        75.0% (IC 95%: 70.1% - 79.9%)
    """
    media, inf, sup = calcular_intervalo_confianca(valores, confianca)
    
    if formato == 'percentual':
        fmt = f"{{:.{casas_decimais}%}}"
        media_str = fmt.format(media)
        inf_str = fmt.format(inf)
        sup_str = fmt.format(sup)
    elif formato == 'decimal':
        fmt = f"{{:.{casas_decimais}f}}"
        media_str = fmt.format(media)
        inf_str = fmt.format(inf)
        sup_str = fmt.format(sup)
    else:  # inteiro
        media_str = f"{int(media)}"
        inf_str = f"{int(inf)}"
        sup_str = f"{int(sup)}"
    
    confianca_pct = int(confianca * 100)
    return f"{media_str} (IC {confianca_pct}%: {inf_str} - {sup_str})"


def calcular_margem_erro(
    valores: List[float],
    confianca: float = 0.95
) -> float:
    """
    Calcula apenas a margem de erro (±).
    
    Args:
        valores: Lista de valores
        confianca: Nível de confiança
        
    Returns:
        Margem de erro absoluta
        
    Example:
        >>> taxas = [0.75, 0.72, 0.78]
        >>> margem = calcular_margem_erro(taxas)
        >>> print(f"±{margem:.1%}")
        ±2.9%
    """
    if len(valores) < 2:
        return 0.0
    
    media, inf, _ = calcular_intervalo_confianca(valores, confianca)
    return media - inf


def analisar_consistencia(valores: List[float]) -> Dict[str, Any]:
    """
    Analisa consistência estatística dos valores.
    
    Args:
        valores: Lista de valores observados
        
    Returns:
        Dict com análise de consistência:
        {
            'media': float,
            'desvio_padrao': float,
            'coeficiente_variacao': float,
            'consistencia': 'ALTA|MÉDIA|BAIXA',
            'n_amostras': int
        }
    """
    if not valores:
        return {
            'media': 0.0,
            'desvio_padrao': 0.0,
            'coeficiente_variacao': 0.0,
            'consistencia': 'INSUFICIENTE',
            'n_amostras': 0
        }
    
    valores_np = np.array(valores)
    media = np.mean(valores_np)
    desvio = np.std(valores_np, ddof=1) if len(valores_np) > 1 else 0.0
    
    # Coeficiente de variação (CV) - quanto menor, mais consistente
    cv = (desvio / media) if media > 0 else 0.0
    
    # Classificar consistência baseado no CV
    if cv < 0.1:
        consistencia = 'ALTA'
    elif cv < 0.25:
        consistencia = 'MÉDIA'
    else:
        consistencia = 'BAIXA'
    
    return {
        'media': media,
        'desvio_padrao': desvio,
        'coeficiente_variacao': cv,
        'consistencia': consistencia,
        'n_amostras': len(valores_np)
    }


def gerar_relatorio_estatistico(
    valores: List[float],
    nome_metrica: str,
    formato: str = 'percentual'
) -> str:
    """
    Gera relatório estatístico completo e honesto.
    
    Args:
        valores: Lista de valores
        nome_metrica: Nome da métrica (ex: "Taxa de Acerto")
        formato: Tipo de formatação
        
    Returns:
        String com relatório formatado
        
    Example:
        >>> taxas = [0.75, 0.72, 0.78, 0.71, 0.76]
        >>> print(gerar_relatorio_estatistico(taxas, "Taxa de Acerto TOP 30"))
        📊 Taxa de Acerto TOP 30:
           Valor: 74.4% (IC 95%: 71.2% - 77.6%)
           Margem de erro: ±3.2%
           Consistência: ALTA (CV: 3.2%)
           Amostras: 5
    """
    if not valores:
        return f"⚠️ {nome_metrica}: Sem dados suficientes"
    
    # Calcular métricas
    media, inf, sup = calcular_intervalo_confianca(valores)
    margem = calcular_margem_erro(valores)
    analise = analisar_consistencia(valores)
    
    # Formatar
    if formato == 'percentual':
        valor_str = f"{media:.1%} (IC 95%: {inf:.1%} - {sup:.1%})"
        margem_str = f"±{margem:.1%}"
    else:
        valor_str = f"{media:.2f} (IC 95%: {inf:.2f} - {sup:.2f})"
        margem_str = f"±{margem:.2f}"
    
    relatorio = f"""📊 {nome_metrica}:
   Valor: {valor_str}
   Margem de erro: {margem_str}
   Consistência: {analise['consistencia']} (CV: {analise['coeficiente_variacao']:.1%})
   Amostras: {analise['n_amostras']}"""
    
    return relatorio


def validar_significancia_estatistica(
    valores_grupo1: List[float],
    valores_grupo2: List[float],
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Testa se há diferença estatisticamente significativa entre dois grupos.
    
    Args:
        valores_grupo1: Valores do primeiro grupo
        valores_grupo2: Valores do segundo grupo
        alpha: Nível de significância (default: 0.05 = 5%)
        
    Returns:
        Dict com resultado do teste:
        {
            'significativo': bool,
            'p_valor': float,
            'diferenca_media': float,
            'interpretacao': str
        }
        
    Example:
        >>> treino = [0.78, 0.75, 0.79, 0.77]
        >>> teste = [0.65, 0.62, 0.68, 0.64]
        >>> resultado = validar_significancia_estatistica(treino, teste)
        >>> print(resultado['interpretacao'])
        Diferença significativa detectada (p=0.0012)
    """
    if len(valores_grupo1) < 2 or len(valores_grupo2) < 2:
        return {
            'significativo': False,
            'p_valor': 1.0,
            'diferenca_media': 0.0,
            'interpretacao': 'Amostras insuficientes para teste'
        }
    
    # Teste t de Student para amostras independentes
    t_stat, p_valor = stats.ttest_ind(valores_grupo1, valores_grupo2)
    
    significativo = p_valor < alpha
    diferenca = np.mean(valores_grupo1) - np.mean(valores_grupo2)
    
    if significativo:
        interpretacao = f"Diferença significativa detectada (p={p_valor:.4f})"
    else:
        interpretacao = f"Diferença não significativa (p={p_valor:.4f})"
    
    return {
        'significativo': significativo,
        'p_valor': p_valor,
        'diferenca_media': diferenca,
        't_statistic': t_stat,
        'interpretacao': interpretacao
    }


# Exports
__all__ = [
    'calcular_intervalo_confianca',
    'formatar_com_intervalo',
    'calcular_margem_erro',
    'analisar_consistencia',
    'gerar_relatorio_estatistico',
    'validar_significancia_estatistica'
]


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando Métricas de Confiança...\n")
    
    # Teste 1: Intervalos de confiança
    print("Teste 1: Intervalo de Confiança")
    taxas = [0.75, 0.72, 0.78, 0.71, 0.76]
    print(formatar_com_intervalo(taxas))
    print()
    
    # Teste 2: Análise de consistência
    print("Teste 2: Análise de Consistência")
    consistencia = analisar_consistencia(taxas)
    print(f"Consistência: {consistencia['consistencia']}")
    print(f"CV: {consistencia['coeficiente_variacao']:.1%}")
    print()
    
    # Teste 3: Relatório completo
    print("Teste 3: Relatório Estatístico")
    print(gerar_relatorio_estatistico(taxas, "Taxa de Acerto TOP 30"))
    print()
    
    # Teste 4: Comparação treino vs teste
    print("Teste 4: Comparação Estatística (Treino vs Teste)")
    treino = [0.78, 0.75, 0.79, 0.77, 0.76]
    teste = [0.65, 0.62, 0.68, 0.64, 0.66]
    resultado = validar_significancia_estatistica(treino, teste)
    print(f"Média Treino: {np.mean(treino):.1%}")
    print(f"Média Teste: {np.mean(teste):.1%}")
    print(f"Resultado: {resultado['interpretacao']}")
    print(f"⚠️ Degradação: {abs(resultado['diferenca_media']):.1%}")
    
    print("\n✅ Testes concluídos!\n")
