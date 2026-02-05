"""
Análise de Refinamento com IA - Google Gemini

Módulo para consultar a IA e obter pesos refinados para os indicadores.
Retorna dados estruturados (dicionário) para uso no sistema.
"""

import pandas as pd
import json
import os
import sys
from typing import Dict, Any, Tuple
import re

# Importar componente unificado
sys.path.insert(0, 'd:\\MegaCLI')
from src.core.conexao_ia import conectar_ia

def limpar_json_markdown(texto: str) -> str:
    """Remove formatação Markdown de blocos de código JSON."""
    padrao = r"```json\s*(.*?)\s*```"
    match = re.search(padrao, texto, re.DOTALL)
    if match:
        return match.group(1)
    return texto.strip()

def obter_sugestao_pesos(
    df_performance: pd.DataFrame,
    df_validacao: pd.DataFrame,
    feedback_texto: str = None
) -> Tuple[Dict[str, float], Dict[str, Any]]:
    """
    Consulta a IA para sugerir novos pesos para os indicadores.
    
    Args:
        df_performance: DataFrame com performance histórica dos indicadores
        df_validacao: DataFrame com validação recente
        feedback_texto: (Opcional) Texto com análise de desvio da previsão anterior
        
    Returns:
        Tuple(dict_pesos, dict_analise_completa)
    """
    
    # 1. Preparar Contexto
    media_acertos = df_validacao['Acertos'].mean() if not df_validacao.empty else 0
    taxa_3_plus = (df_validacao['Acertos'] >= 3).sum() / len(df_validacao) * 100 if not df_validacao.empty else 0
    
    # Identificar coluna de relevância disponível
    col_relevancia = None
    if not df_performance.empty:
        for col in ['Confianca', 'Relevancia', 'relevancia', 'Peso_Atual', 'Peso']:
            if col in df_performance.columns:
                col_relevancia = col
                break
    
    if col_relevancia:
        indicadores_top = df_performance.nlargest(5, col_relevancia)
    else:
        # Se não achar coluna de relevância, pega os 5 primeiros
        indicadores_top = df_performance.head(5) if not df_performance.empty else pd.DataFrame()

    # Identificar coluna de nome do indicador (Geralmente 'Indicador' ou 'indicador')
    col_indicador = None
    if not df_performance.empty:
        for col in ['Indicador', 'indicador', 'Nome', 'nome']:
            if col in df_performance.columns:
                col_indicador = col
                break
    
    if col_indicador:
        lista_indicadores = df_performance[col_indicador].tolist()
    else:
        # Fallback: Lista COMPLETA de 42 indicadores (v5.0)
        lista_indicadores = [
            # Básicos (12)
            'Quadrantes', 'Div9', 'Fibonacci', 'Div6', 'Mult5', 'Div3', 
            'Gap', 'Primos', 'Simetria', 'ParImpar', 'Amplitude', 'Soma',
            # Avançados (5)
            'RaizDigital', 'VariacaoSoma', 'Conjugacao', 'RepeticaoAnterior', 'FrequenciaMensal',
            # Extras (5)
            'Sequencias', 'DistanciaMedia', 'NumerosExtremos', 'PadraoDezena', 'CicloAparicao',
            # Temporais (4)
            'TendenciaQuadrantes', 'CiclosSemanais', 'AcumulacaoConsecutiva', 'JanelaDeslizante',
            # Geométricos (3)
            'MatrizPosicional', 'ClusterEspacial', 'SimetriaCentral',
            # Frequência (4)
            'FrequenciaRelativa', 'DesvioFrequencia', 'EntrópiaDistribuicao', 'CorrelacaoTemporal',
            # Numerológicos (2)
            'SomaDigitos', 'PadraoModular',
            # ML (3)
            'ScoreAnomalia', 'ProbabilidadeCondicional', 'ImportanciaFeature',
            # IA (4)
            'PadroesSubconjuntos', 'MicroTendencias', 'AnaliseContextual', 'Embedding'
        ]

    prompt = f"""
    Atue como um Especialista Estatístico em Loterias (Mega-Sena).
    
    CONTEXTO ATUAL:
    - Média de Acertos (Validação): {media_acertos:.3f} (em 6 números)
    - Taxa de Sucesso (3+ acertos): {taxa_3_plus:.1f}%
    
    FEEDBACK DA PREVISÃO ANTERIOR (Onde erramos?):
    {feedback_texto if feedback_texto else "Nenhum feedback disponível para este ciclo."}
    
    TOP INDICADORES ATUAIS (Referência):
    {indicadores_top[[col_indicador, col_relevancia] if (col_indicador and col_relevancia) else ([col_indicador] if col_indicador else [])].to_string(index=False) if not indicadores_top.empty else 'N/A'}
    
    OBJETIVO:
    Refinar os pesos (0 a 100) de TODOS os indicadores listados abaixo para MELHORAR a previsibilidade.
    Você DEVE retornar um peso para CADA UM dos indicadores da lista.
    
    LISTA COMPLETA DE INDICADORES A REFINAR:
    {', '.join(lista_indicadores)}
    
    ALERTA CRÍTICO:
    - Você DEVE retornar um peso para CADA UM dos {len(lista_indicadores)} indicadores listados acima.
    - NÃO OMITA NENHUM INDICADOR. A lista de saída deve ter EXATAMENTE o mesmo tamanho da lista de entrada.
    - Indicadores de 'Padrões' (Deltas, Ciclos) devem ter peso alto se mostrarem consistência.
    - Indicadores sem relevância estatística recente devem ter peso reduzido (< 50).
    - Mantenha a soma total coerente (não precisa somar 100, são pesos relativos 0-100).
    
    SAÍDA OBRIGATÓRIA:
    Retorne APENAS um JSON válido com a seguinte estrutura:
    {{
        "analise_ciclo": "Texto explicativo sobre o que mudou neste ciclo e por que. Quais indicadores se destacaram?",
        "justificativas_top": [
            {{ "indicador": "Nome", "motivo": "Por que aumentou/diminuiu" }}
        ],
        "pesos": {{
            "NomeDoIndicador1": 85.5,
            "NomeDoIndicador2": 60.0,
            ... para TODOS da lista ...
        }}
    }}
    """
    
    print("\n🤖 Consultando IA para refinamento de pesos...")
    
    try:
        # Usar componente unificado
        llm = conectar_ia(modelo="gemini-2.5-pro", temperatura=0.2)
        
        if not llm:
            print("❌ Falha na conexão com IA (Componente Unificado).")
            return {}, {}
        
        resposta = llm.invoke(prompt)
        conteudo = resposta.content
        
        # Limpar e parsear JSON
        json_str = limpar_json_markdown(conteudo)
        try:
            dados_ia = json.loads(json_str)
            
            # Extrair pesos
            pesos_raw = dados_ia.get('pesos', {})
            # Compatibilidade backward se a IA retornar formato antigo
            if not pesos_raw and any(isinstance(v, (int, float)) for v in dados_ia.values()):
                pesos_raw = dados_ia
            
            # Validar e normalizar pesos
            pesos_normalizados = {}
            for k, v in pesos_raw.items():
                try:
                    pesos_normalizados[k] = float(v)
                except:
                    pass
            
            print(f"✅ IA retornou pesos para {len(pesos_normalizados)} indicadores.")
            return pesos_normalizados, dados_ia
            
        except json.JSONDecodeError:
            print(f"❌ Erro ao decodificar JSON da IA: {json_str[:100]}...")
            return {}, {}
            
    except Exception as e:
        print(f"❌ Erro na execução da IA: {e}")
        return {}, {}

# Manter compatibilidade com scripts antigos se necessário (pode ser removido depois)
if __name__ == "__main__":
    # Teste rápido
    print("Teste de módulo (mock de dados)...")
    mock_perf = pd.DataFrame({
        'Indicador': ['Quadrantes', 'ParImpar', 'Soma'],
        'Confianca': [90, 80, 70]
    })
    mock_val = pd.DataFrame({'Acertos': [3, 4, 2, 3, 5]})
    
    pesos, analise = obter_sugestao_pesos(mock_perf, mock_val)
    print("Pesos recebidos:", pesos)
