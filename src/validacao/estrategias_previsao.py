"""
Múltiplas Estratégias de Previsão - MegaCLI

5 estratégias diferentes para gerar previsões diversificadas:
1. Estratégia Conservadora - Baseada em frequências históricas
2. Estratégia Agressiva - Números "atrasados"
3. Estratégia Balanceada - Mix de indicadores
4. Estratégia IA - Consultando Gemini periodicamente
5. Estratégia Aleatória Inteligente - Aleatoriedade ponderada
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter
import time
import os
from dotenv import load_dotenv


class EstrategiaConservadora:
    """
    Estratégia 1: Conservadora
    
    Foca em números mais frequentes no histórico
    Justificativa: "Tende a repetir o que já funcionou"
    """
    
    @staticmethod
    def gerar(historico: pd.DataFrame) -> Tuple[List[int], str]:
        # Contar frequência de todos os números
        freq = Counter()
        for idx in range(len(historico)):
            try:
                for j in range(1, 7):
                    num = historico.iloc[idx].get(f'Bola{j}')
                    if pd.notna(num):
                        freq[int(num)] += 1
            except:
                pass
        
        # Top 10 mais frequentes
        top_frequentes = [n for n, _ in freq.most_common(10)]
        
        # Selecionar 6 aleatoriamente dos top 10
        if len(top_frequentes) >= 6:
            previsao = sorted(np.random.choice(top_frequentes, 6, replace=False).tolist())
        else:
            previsao = sorted(np.random.choice(range(1, 61), 6, replace=False).tolist())
        
        justificativa = f"Números frequentes: {freq.most_common(3)}"
        
        return previsao, justificativa


class EstrategiaAgressiva:
    """
    Estratégia 2: Agressiva
    
    Foca em números "atrasados" (não saíram recentemente)
    Justificativa: "Números atrasados tendem a sair"
    """
    
    @staticmethod
    def gerar(historico: pd.DataFrame) -> Tuple[List[int], str]:
        # Últimos 50 sorteios
        recentes = historico.tail(50)
        
        # Números que NÃO apareceram
        numeros_recentes = set()
        for idx in range(len(recentes)):
            try:
                for j in range(1, 7):
                    num = recentes.iloc[idx].get(f'Bola{j}')
                    if pd.notna(num):
                        numeros_recentes.add(int(num))
            except:
                pass
        
        # Números "atrasados"
        todos_numeros = set(range(1, 61))
        atrasados = list(todos_numeros - numeros_recentes)
        
        # Se poucos atrasados, usar menos frequentes
        if len(atrasados) < 6:
            freq = Counter()
            for idx in range(len(recentes)):
                try:
                    for j in range(1, 7):
                        num = recentes.iloc[idx].get(f'Bola{j}')
                        if pd.notna(num):
                            freq[int(num)] += 1
                except:
                    pass
            
            # Menos frequentes
            atrasados = [n for n in range(1, 61) if freq.get(n, 0) <= 2]
        
        # Selecionar 6
        if len(atrasados) >= 6:
            previsao = sorted(np.random.choice(atrasados, 6, replace=False).tolist())
        else:
            previsao = sorted(np.random.choice(range(1, 61), 6, replace=False).tolist())
        
        justificativa = f"Atrasados (>50 sorteios): {len(atrasados)} números"
        
        return previsao, justificativa


class EstrategiaBalanceada:
    """
    Estratégia 3: Balanceada
    
    Mix de indicadores (Fibonacci, Primos, Pares/Ímpares)
    Justificativa: "Equilíbrio entre padrões matemáticos"
    """
    
    @staticmethod
    def gerar(historico: pd.DataFrame) -> Tuple[List[int], str]:
        fibonacci = {1, 2, 3, 5, 8, 13, 21, 34, 55}
        primos = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59}
        
        previsao = []
        
        # 2 Fibonacci
        fibs_disponiveis = list(fibonacci)
        if len(fibs_disponiveis) >= 2:
            previsao.extend(np.random.choice(fibs_disponiveis, 2, replace=False))
        
        # 2 Primos
        primos_nao_usados = [p for p in primos if p not in previsao]
        if len(primos_nao_usados) >= 2:
            previsao.extend(np.random.choice(primos_nao_usados, 2, replace=False))
        
        # 2 Aleatórios (garantindo par/ímpar)
        restantes = [n for n in range(1, 61) if n not in previsao]
        if len(restantes) >= 2:
            # 1 par, 1 ímpar
            pares = [n for n in restantes if n % 2 == 0]
            impares = [n for n in restantes if n % 2 == 1]
            
            if pares:
                previsao.append(np.random.choice(pares))
            if impares:
                previsao.append(np.random.choice(impares))
        
        # Completar se necessário
        while len(previsao) < 6:
            restantes = [n for n in range(1, 61) if n not in previsao]
            if restantes:
                previsao.append(np.random.choice(restantes))
            else:
                break
        
        previsao = sorted(previsao[:6])
        
        pares = len([n for n in previsao if n % 2 == 0])
        justificativa = f"Fib:{len([n for n in previsao if n in fibonacci])}, Primos:{len([n for n in previsao if n in primos])}, Pares:{pares}"
        
        return previsao, justificativa


class EstrategiaIA:
    """
    Estratégia 4: IA Periódica
    
    Consulta Gemini a cada N sorteios para ajustar critérios
    Rate limiting: 1 consulta a cada 100 sorteios
    """
    
    def __init__(self):
        self.ultima_consulta = None
        self.criterios_atuais = None
        self.intervalo_consulta = 100  # Consultar a cada 100 sorteios
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_API_KEY')
    
    def gerar(self, historico: pd.DataFrame, indice_atual: int) -> Tuple[List[int], str]:
        # Verificar se precisa consultar IA
        if (self.ultima_consulta is None or 
            (indice_atual - self.ultima_consulta >= self.intervalo_consulta)):
            
            if self.api_key:
                self._consultar_ia(historico)
                self.ultima_consulta = indice_atual
        
        # Gerar previsão baseada nos critérios
        if self.criterios_atuais:
            previsao = self._aplicar_criterios(historico)
            justificativa = f"IA (última consulta: sorteio {self.ultima_consulta or 'nunca'})"
        else:
            # Fallback: estratégia balanceada
            previsao, _ = EstrategiaBalanceada.gerar(historico)
            justificativa = "IA indisponível, usando Balanceada"
        
        return previsao, justificativa
    
    def _consultar_ia(self, historico: pd.DataFrame):
        """Consulta IA para obter novos critérios"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            import json
            import re
            
            # Analisar últimos 50 sorteios
            ultimos = historico.tail(50)
            
            # Estatísticas rápidas
            freq = Counter()
            for idx in range(len(ultimos)):
                try:
                    for j in range(1, 7):
                        num = ultimos.iloc[idx].get(f'Bola{j}')
                        if pd.notna(num):
                            freq[int(num)] += 1
                except:
                    pass
            
            top5 = freq.most_common(5)
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",  # Modelo funcional!
                temperature=0.7,
                google_api_key=self.api_key
            )
            
            prompt = f"""
            Baseado nos últimos 50 sorteios da Mega-Sena:
            - Números mais frequentes: {top5}
            
            Sugira 6 números para o próximo sorteio em JSON:
           {{
                "numeros": [n1, n2, n3, n4, n5, n6],
                "justificativa": "breve explicação"
            }}
            """
            
            response = llm.invoke(prompt)
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            
            if json_match:
                self.criterios_atuais = json.loads(json_match.group())
        except:
            self.criterios_atuais = None
    
    def _aplicar_criterios(self, historico: pd.DataFrame) -> List[int]:
        """Aplica critérios da IA"""
        if self.criterios_atuais and 'numeros' in self.criterios_atuais:
            numeros = self.criterios_atuais['numeros']
            if len(numeros) == 6:
                return sorted(numeros)
        
        # Fallback
        return sorted(np.random.choice(range(1, 61), 6, replace=False).tolist())


class EstrategiaAleatoriaInteligente:
    """
    Estratégia 5: Aleatória Inteligente
    
    Aleatoriedade ponderada por frequência + variação
    Justificativa: "Aleatoriedade com viés estatístico"
    """
    
    @staticmethod
    def gerar(historico: pd.DataFrame) -> Tuple[List[int], str]:
        # Frequências
        freq = Counter()
        for idx in range(len(historico)):
            try:
                for j in range(1, 7):
                    num = historico.iloc[idx].get(f'Bola{j}')
                    if pd.notna(num):
                        freq[int(num)] += 1
            except:
                pass
        
        # Criar pesos (frequência + noise)
        pesos = []
        for n in range(1, 61):
            peso_base = freq.get(n, 1)
            noise = np.random.uniform(0.8, 1.2)  # Variação ±20%
            pesos.append(peso_base * noise)
        
        # Normalizar
        pesos = np.array(pesos)
        pesos = pesos / pesos.sum()
        
        # Selecionar
        previsao = sorted(np.random.choice(range(1, 61), 6, replace=False, p=pesos).tolist())
        
        justificativa = f"Aleatório ponderado (var ±20%)"
        
        return previsao, justificativa


# ============================================================================
# ORQUESTRADOR DE ESTRATÉGIAS
# ============================================================================

class GeradorMultiplasEstrategias:
    """Gerencia todas as 5 estratégias"""
    
    def __init__(self):
        self.estrategia_ia = EstrategiaIA()
    
    def gerar_todas(self, historico: pd.DataFrame, indice_atual: int = 0) -> Dict[str, Tuple[List[int], str]]:
        """
        Gera previsão com todas as 5 estratégias
        
        Returns:
            Dict com nome_estrategia: (previsao, justificativa)
        """
        resultados = {}
        
        # 1. Conservadora
        prev, just = EstrategiaConservadora.gerar(historico)
        resultados['Conservadora'] = (prev, just)
        
        # 2. Agressiva
        prev, just = EstrategiaAgressiva.gerar(historico)
        resultados['Agressiva'] = (prev, just)
        
        # 3. Balanceada
        prev, just = EstrategiaBalanceada.gerar(historico)
        resultados['Balanceada'] = (prev, just)
        
        # 4. IA
        prev, just = self.estrategia_ia.gerar(historico, indice_atual)
        resultados['IA'] = (prev, just)
        
        # 5. Aleatória Inteligente
        prev, just = EstrategiaAleatoriaInteligente.gerar(historico)
        resultados['Aleatória'] = (prev, just)
        
        return resultados


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    from pathlib import Path
    
    planilha = Path(__file__).parent.parent.parent / 'Resultado' / 'ANALISE_HISTORICO_COMPLETO.xlsx'
    df = pd.read_excel(planilha, 'MEGA SENA')
    
    gerador = GeradorMultiplasEstrategias()
    
    # Gerar com todas as estratégias
    historico_teste = df.head(100)
    resultados = gerador.gerar_todas(historico_teste, indice_atual=100)
    
    print("\n📊 Previsões - Múltiplas Estratégias")
    print("="*60)
    
    for nome, (numeros, justificativa) in resultados.items():
        print(f"\n{nome}:")
        print(f"  Números: {numeros}")
        print(f"  Justificativa: {justificativa}")
