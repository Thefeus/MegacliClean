"""
Indicadores com IA Generativa para Mega-Sena

Este módulo implementa indicadores que usam Google Gemini para detectar
padrões complexos que métodos estatísticos tradicionais não identificam.

Inclui:
1. PadroesSubconjuntosIndicador - Detecta pares/triplas que aparecem juntos
2. MicroTendenciasIndicador - Identifica mudanças sutis de padrão
3. AnaliseContextualIndicador - Usa contexto temporal (datas, sazonalidade)
4. EmbeddingIndicador - Similaridade entre sorteios via embeddings

Características:
- Cache agressivo para economizar tokens
- Fallback para métodos estatísticos se IA falhar
- Retry automático com backoff
- Validação robusta de respostas JSON
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import os
import json
import time
import re
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Imports de IA (movidos para lazy load)
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.messages import HumanMessage



# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

# Cache directory
CACHE_DIR = Path("cache/indicadores_ia")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# LLM instance (compartilhada)
# LLM instance (lazy initialization)
_llm_instance = None

def get_llm():
    """Retorna instância do LLM (lazy init)"""
    global _llm_instance
    if _llm_instance is None:
        try:
            # Componente Unificado
            from src.core.conexao_ia import conectar_ia
            
            _llm_instance = conectar_ia(
                modelo="gemini-2.5-pro",
                temperatura=0.1,
                verbose=False
            )
        except Exception as e:
            print(f"⚠️  Erro ao inicializar LLM: {e}")
            return None
    return _llm_instance


# ============================================================================
# UTILITÁRIOS DE CACHE
# ============================================================================

def _gerar_cache_key(prompt: str) -> str:
    """Gera chave de cache baseada no prompt"""
    import hashlib
    return hashlib.md5(prompt.encode()).hexdigest()


def _ler_cache(cache_key: str) -> Optional[Dict]:
    """Lê resultado do cache"""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None


def _salvar_cache(cache_key: str, data: Dict):
    """Salva resultado no cache"""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass


def _chamar_ia_com_cache(prompt: str, max_retries: int = 2) -> Optional[Dict]:
    """
    Chama IA com cache e retry
    
    Returns:
        Dict parseado do JSON, ou None se falhar
    """
    # Verificar cache
    cache_key = _gerar_cache_key(prompt)
    cached = _ler_cache(cache_key)
    
    if cached:
        return cached
    
    # Chamar IA com retry
    for attempt in range(max_retries):
        try:
            llm_inst = get_llm()
            if not llm_inst:
                return None
                
            from langchain_core.messages import HumanMessage
            response = llm_inst.invoke([HumanMessage(content=prompt)])
            
            # Tentar parsear JSON
            result = _parsear_json_ia(response.content)
            
            if result:
                # Salvar no cache
                _salvar_cache(cache_key, result)
                return result
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Backoff exponencial
            continue
    
    return None


def _parsear_json_ia(content: str) -> Optional[Dict]:
    """Parse robusto de JSON da resposta da IA"""
    patterns = [
        r'```json\n({.*?})\n```',  # Bloco markdown
        r'{.*?}',  # JSON direto
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            try:
                json_str = match.group(1) if '```' in pattern else match.group(0)
                return json.loads(json_str)
            except:
                continue
    
    return None


# ============================================================================
# INDICADOR 1: PADRÕES DE SUBCONJUNTOS
# ============================================================================

class PadroesSubconjuntosIndicador:
    """
    Detecta pares e triplas que aparecem juntos com frequência acima do esperado.
    
    Usa IA para identificar padrões não-óbvios que análise estatística simples perde.
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str]):
        self.historico = historico.copy()
        self.ball_cols = ball_cols
        self.padroes_cache = None
        
    def _calcular_pares_estatisticos(self) -> Dict[Tuple[int, int], int]:
        """Fallback: cálculo estatístico de pares"""
        pares = Counter()
        
        for _, row in self.historico.iterrows():
            numeros = sorted([int(row[col]) for col in self.ball_cols if pd.notna(row[col])])
            
            # Contar todos os pares
            for i in range(len(numeros)):
                for j in range(i + 1, len(numeros)):
                    par = (numeros[i], numeros[j])
                    pares[par] += 1
        
        return dict(pares)
    
    def detectar_padroes_ia(self, ultimos_n: int = 200) -> Dict[str, Any]:
        """
        Usa IA para detectar padrões de subconjuntos
        
        Args:
            ultimos_n: Quantos sorteios considerar
        """
        if self.padroes_cache:
            return self.padroes_cache
        
        # Preparar dados
        ultimos = self.historico.tail(ultimos_n)
        sample_sorteios = []
        
        for _, row in ultimos.head(30).iterrows():  # Apenas 30 para o prompt
            nums = sorted([int(row[col]) for col in self.ball_cols if pd.notna(row[col])])
            sample_sorteios.append(nums)
        
        # Prompt para IA
        prompt = f"""Analise os sorteios da Mega-Sena e identifique padrões de subconjuntos.

ÚLTIMOS 30 SORTEIOS (de {len(ultimos)} total):
{chr(10).join(f"Sorteio: {nums}" for nums in sample_sorteios)}

TAREFA:
1. Identifique PARES de números que aparecem juntos ≥15% das vezes
2. Identifique TRIPLAS que aparecem juntas ≥5% das vezes
3. Identifique padrões de SEQUÊNCIA (ex: se X sai, Y tende a sair em 1-3 sorteios)

Responda em JSON:
{{
  "pares_frequentes": [[n1, n2], ...],
  "triplas_frequentes": [[n1, n2, n3], ...],
  "padroes_sequenciais": [{{"se": n1, "entao": [n2, n3], "delay": "1-3"}}],
  "confianca": 0.75
}}
"""
        
        # Chamar IA com cache
        resultado = _chamar_ia_com_cache(prompt)
        
        if resultado:
            self.padroes_cache = resultado
            return resultado
        
        # Fallback: usar análise estatística
        pares_stats = self._calcular_pares_estatisticos()
        total_sorteios = len(ultimos)
        
        # Filtrar pares frequentes (≥15%)
        limiar = total_sorteios * 0.15
        pares_freq = [list(par) for par, count in pares_stats.items() if count >= limiar]
        
        fallback_result = {
            "pares_frequentes": pares_freq[:10],
            "triplas_frequentes": [],
            "padroes_sequenciais": [],
            "confianca": 0.5,
            "fonte": "fallback_estatistico"
        }
        
        self.padroes_cache = fallback_result
        return fallback_result
    
    def calcular_score(self, numeros: List[int]) -> float:
        """
        Pontua baseado em quantos subconjuntos frequentes estão presentes
        
        Args:
            numeros: Lista de 6 números
            
        Returns:
            Score 0-100
        """
        padroes = self.detectar_padroes_ia()
        score = 50.0  # Base
        
        # Verificar pares frequentes
        pares_encontrados = 0
        for par in padroes.get('pares_frequentes', []):
            if par[0] in numeros and par[1] in numeros:
                pares_encontrados += 1
        
        score += pares_encontrados * 10  # +10 por par
        
        # Verificar triplas
        triplas_encontradas = 0
        for tripla in padroes.get('triplas_frequentes', []):
            if all(n in numeros for n in tripla):
                triplas_encontradas += 1
        
        score += triplas_encontradas * 20  # +20 por tripla
        
        # Cap em 100
        return min(100, score)
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Gera relatório dos padrões detectados"""
        padroes = self.detectar_padroes_ia()
        
        return {
            'indicador': 'PadroesSubconjuntos',
            'pares_frequentes': padroes.get('pares_frequentes', [])[:5],
            'triplas_frequentes': padroes.get('triplas_frequentes', [])[:3],
            'confianca_ia': padroes.get('confianca', 0.5),
            'fonte': padroes.get('fonte', 'ia'),
            'insight': f"{len(padroes.get('pares_frequentes', []))} pares frequentes detectados"
        }


# ============================================================================
# INDICADOR 2: MICRO-TENDÊNCIAS
# ============================================================================

class MicroTendenciasIndicador:
    """
    Detecta pequenas mudanças de padrão que indicam tendências emergentes.
    
    Usa IA para identificar variações sutis invisíveis a análises tradicionais.
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str]):
        self.historico = historico.copy()
        self.ball_cols = ball_cols
        self.tendencias_cache = None
        
    def _calcular_tendencias_estatisticas(self) -> Dict[str, Any]:
        """Fallback: análise estatística simples"""
        # Frequência nos últimos 50 vs últimos 100
        last_50 = self.historico.tail(50)
        last_100 = self.historico.tail(100)
        
        freq_50 = Counter()
        freq_100 = Counter()
        
        for col in self.ball_cols:
            freq_50.update(last_50[col].dropna().astype(int))
            freq_100.update(last_100[col].dropna().astype(int))
        
        # Números em alta (frequência crescente)
        em_alta = []
        for num in range(1, 61):
            f50 = freq_50.get(num, 0) / 50
            f100 = freq_100.get(num, 0) / 100
            
            if f50 > f100 * 1.3:  # 30% maior
                em_alta.append(num)
        
        return {
            "numeros_em_alta": em_alta[:10],
            "numeros_em_baixa": [],
            "confianca": 0.6
        }
    
    def detectar_tendencias_ia(self) -> Dict[str, Any]:
        """Usa IA para detectar micro-tendências"""
        if self.tendencias_cache:
            return self.tendencias_cache
        
        # Preparar estatísticas
        last_30 = self.historico.tail(30)
        
        # Calcular médias móveis
        freq_recente = Counter()
        for col in self.ball_cols:
            freq_recente.update(last_30[col].dropna().astype(int))
        
        top_recentes = dict(freq_recente.most_common(15))
        
        prompt = f"""Analise as tendências recentes em sorteios da Mega-Sena.

NÚMEROS MAIS FREQUENTES (últimos 30 sorteios):
{json.dumps(top_recentes, indent=2)}

TAREFA:
Identifique micro-tendências:
1. Números que estão AUMENTANDO em frequência (tendência de alta)
2. Números que estão DIMINUINDO (tendência de baixa)
3. Padrões emergentes (ex: números pares aumentando, ímpares diminuindo)

Responda em JSON:
{{
  "numeros_em_alta": [n1, n2, ...],
  "numeros_em_baixa": [n1, n2, ...],
  "padroes_emergentes": ["descrição1", "descrição2"],
  "confianca": 0.70
}}
"""
        
        resultado = _chamar_ia_com_cache(prompt)
        
        if resultado:
            self.tendencias_cache = resultado
            return resultado
        
        # Fallback
        fallback = self._calcular_tendencias_estatisticas()
        fallback['fonte'] = 'fallback_estatistico'
        self.tendencias_cache = fallback
        return fallback
    
    def calcular_score(self, numeros: List[int]) -> float:
        """Pontua baseado em alinhamento com tendências"""
        tendencias = self.detectar_tendencias_ia()
        
        em_alta = tendencias.get('numeros_em_alta', [])
        em_baixa = tendencias.get('numeros_em_baixa', [])
        
        score = 50.0
        
        # Bonus por números em alta
        nums_em_alta = sum(1 for n in numeros if n in em_alta)
        score += nums_em_alta * 8  # +8 por número
        
        # Penalidade por números em baixa
        nums_em_baixa = sum(1 for n in numeros if n in em_baixa)
        score -= nums_em_baixa * 5
        
        return max(0, min(100, score))
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Relatório de tendências"""
        tendencias = self.detectar_tendencias_ia()
        
        return {
            'indicador': 'MicroTendencias',
            'numeros_em_alta': tendencias.get('numeros_em_alta', [])[:5],
            'numeros_em_baixa': tendencias.get('numeros_em_baixa', [])[:5],
            'confianca_ia': tendencias.get('confianca', 0.6),
            'fonte': tendencias.get('fonte', 'ia'),
            'insight': f"{len(tendencias.get('numeros_em_alta', []))} números em tendência de alta"
        }


# ============================================================================
# INDICADOR 3: ANÁLISE CONTEXTUAL
# ============================================================================

class AnaliseContextualIndicador:
    """
    Usa contexto temporal (datas, sazonalidade, eventos) para ajustar probabilidades.
    
    IA identifica se há padrões relacionados a época do ano, mês, etc.
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str], data_col: str = 'Data'):
        self.historico = historico.copy()
        self.ball_cols = ball_cols
        self.data_col = data_col
        self.contexto_cache = None
        
    def analisar_contexto_ia(self, data_proxima: Optional[datetime] = None) -> Dict[str, Any]:
        """Análise contextual com IA"""
        if self.contexto_cache:
            return self.contexto_cache
        
        if data_proxima is None:
            data_proxima = datetime.now()
        
        mes_atual = data_proxima.month
        
        prompt = f"""Analise padrões sazonais na Mega-Sena.

CONTEXTO:
- Próximo sorteio: {data_proxima.strftime('%d/%m/%Y')}
- Mês: {mes_atual}
- Época: {'Fim de ano' if mes_atual == 12 else 'Meio de ano' if mes_atual == 6 else 'Normal'}

PERGUNTA:
Existe algum padrão sazonal? Certos números aparecem mais em determinados meses?

Responda em JSON:
{{
  "existe_sazonalidade": true/false,
  "numeros_favorecidos_mes_atual": [n1, n2, ...],
  "ajuste_probabilidade": {{"n1": 1.15, "n2": 1.10}},
  "confianca": 0.65
}}
"""
        
        resultado = _chamar_ia_com_cache(prompt)
        
        if resultado:
            self.contexto_cache = resultado
            return resultado
        
        # Fallback: sem ajuste contextual
        fallback = {
            "existe_sazonalidade": False,
            "numeros_favorecidos_mes_atual": [],
            "ajuste_probabilidade": {},
            "confianca": 0.5,
            "fonte": "fallback"
        }
        
        self.contexto_cache = fallback
        return fallback
    
    def calcular_score(self, numeros: List[int]) -> float:
        """Score baseado em contexto"""
        contexto = self.analisar_contexto_ia()
        
        if not contexto.get('existe_sazonalidade', False):
            return 50.0  # Neutro
        
        score = 50.0
        favorecidos = contexto.get('numeros_favorecidos_mes_atual', [])
        
        # Bonus por números favorecidos
        nums_favorecidos = sum(1 for n in numeros if n in favorecidos)
        score += nums_favorecidos * 10
        
        return min(100, score)
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Relatório contextual"""
        contexto = self.analisar_contexto_ia()
        
        return {
            'indicador': 'AnaliseContextual',
            'existe_sazonalidade': contexto.get('existe_sazonalidade', False),
            'numeros_favorecidos': contexto.get('numeros_favorecidos_mes_atual', [])[:5],
            'confianca_ia': contexto.get('confianca', 0.5),
            'fonte': contexto.get('fonte', 'ia'),
            'insight': 'Sazonalidade detectada' if contexto.get('existe_sazonalidade') else 'Sem padrão sazonal claro'
        }


# ============================================================================
# INDICADOR 4: EMBEDDING (SIMILARIDADE)
# ============================================================================

class EmbeddingIndicador:
    """
    Usa embeddings para encontrar sorteios similares e prever baseado neles.
    
    NOTA: Implementação simplificada - embeddings reais requerem API específica.
    """
    
    def __init__(self, historico: pd.DataFrame, ball_cols: List[str]):
        self.historico = historico.copy()
        self.ball_cols = ball_cols
        
    def _calcular_similaridade_simples(self, sorteio1: List[int], sorteio2: List[int]) -> float:
        """Fallback: similaridade baseada em sobreposição"""
        intersecao = len(set(sorteio1).intersection(set(sorteio2)))
        return intersecao / 6.0  # Normalizar
    
    def encontrar_sorteios_similares(self, referencia: List[int], top_n: int = 5) -> List[Tuple[int, List[int], float]]:
        """
        Encontra sorteios mais similares ao de referência
        
        Returns:
            Lista de (índice, sorteio, similaridade)
        """
        similaridades = []
        
        for idx, row in self.historico.iterrows():
            sorteio = sorted([int(row[col]) for col in self.ball_cols if pd.notna(row[col])])
            sim = self._calcular_similaridade_simples(referencia, sorteio)
            similaridades.append((idx, sorteio, sim))
        
        # Ordenar por similaridade
        similaridades.sort(key=lambda x: x[2], reverse=True)
        
        return similaridades[:top_n]
    
    def calcular_score(self, numeros: List[int]) -> float:
        """Score baseado em similaridade com sorteios anteriores bem-sucedidos"""
        # Usar último sorteio como referência
        if len(self.historico) > 0:
            ultimo = sorted([int(self.historico.iloc[-1][col]) for col in self.ball_cols if pd.notna(self.historico.iloc[-1][col])])
            similaridade = self._calcular_similaridade_simples(numeros, ultimo)
            
            # Score: 50 base + bonus por similaridade moderada (não muito alta, não muito baixa)
            # Similaridade ideal ~0.3-0.5 (2-3 números em comum)
            if 0.3 <= similaridade <= 0.5:
                score = 70
            elif 0.15 <= similaridade < 0.3 or 0.5 < similaridade <= 0.65:
                score = 60
            else:
                score = 50
            
            return score
        
        return 50.0
    
    def gerar_relatorio(self) -> Dict[str, Any]:
        """Relatório de embeddings"""
        return {
            'indicador': 'Embedding',
            'metodo': 'similaridade_simples',
            'insight': 'Analisa similaridade com sorteios anteriores',
            'nota': 'Implementação simplificada - embeddings completos requerem API específica'
        }


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def criar_indicadores_ia(historico: pd.DataFrame, ball_cols: List[str]) -> Dict[str, Any]:
    """
    Cria todos os indicadores de IA
    
    Returns:
        Dict com instâncias de cada indicador
    """
    return {
        'PadroesSubconjuntos': PadroesSubconjuntosIndicador(historico, ball_cols),
        'MicroTendencias': MicroTendenciasIndicador(historico, ball_cols),
        'AnaliseContextual': AnaliseContextualIndicador(historico, ball_cols),
        'Embedding': EmbeddingIndicador(historico, ball_cols)
    }


if __name__ == "__main__":
    print("Módulo de Indicadores com IA carregado com sucesso!")
    print("Indicadores disponíveis: PadroesSubconjuntos, MicroTendencias, AnaliseContextual, Embedding")
