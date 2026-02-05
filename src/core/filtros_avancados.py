"""
Filtros Avançados (Smart Filters) - MegaCLI v6.1

Módulo central de validação que rejeita jogos que não atendem
aos padrões estatísticos históricos da Mega-Sena.

Filtros:
1. Soma Total (120-250)
2. Par/Ímpar (Equilíbrio)
3. Quadrantes
4. Primos
5. Deltas

Autor: MegaCLI Team
Data: 23/01/2026
"""

from typing import List, Tuple, Dict
from src.utils.indicador_padrao_delta import analisar_padrao_delta

class FiltrosAvancados:
    
    @staticmethod
    def validar_jogo(jogo: List[int]) -> Tuple[bool, List[str]]:
        """
        Valida um jogo contra todos os filtros.
        
        Args:
            jogo: Lista de 6 inteiros
            
        Returns:
            (Aprovado, Lista de Motivos de Rejeição)
        """
        motivos = []
        
        # 1. Filtro de Soma (120 - 250)
        # Histórico: 80% dos jogos caem nesta faixa
        soma = sum(jogo)
        if not (120 <= soma <= 250):
            motivos.append(f"Soma {soma} fora do padrão (120-250)")
            
        # 2. Filtro Par/Ímpar (Balanceado)
        # Aceitável: 3P/3I, 4P/2I, 2P/4I
        # Rejeitar: 6P/0I, 0P/6I, 5P/1I, 1P/5I
        pares = sum(1 for n in jogo if n % 2 == 0)
        if pares not in [2, 3, 4]:
            motivos.append(f"Deseliquilíbrio Par/Ímpar ({pares} pares)")
            
        # 3. Filtro de Consecutivos (Deltas)
        delta_ok, delta_msg = analisar_padrao_delta(jogo)
        if not delta_ok:
            motivos.append(f"Padrão Delta: {delta_msg}")
            
        # 4. Filtro de Quadrantes
        # Q1: 01-15, Q2: 16-30, Q3: 31-45, Q4: 46-60
        # Evitar mais de 3 números no mesmo quadrante
        q_counts = [0, 0, 0, 0]
        for n in jogo:
            if 1 <= n <= 15: q_counts[0] += 1
            elif 16 <= n <= 30: q_counts[1] += 1
            elif 31 <= n <= 45: q_counts[2] += 1
            elif 46 <= n <= 60: q_counts[3] += 1
            
        if any(c > 3 for c in q_counts):
            motivos.append(f"Excesso em Quadrante {q_counts}")
            
        # Resultado
        aprovado = len(motivos) == 0
        return aprovado, motivos

    @staticmethod
    def filtrar_lista_jogos(jogos: List[List[int]], verbose: bool = True) -> List[List[int]]:
        """
        Filtra uma lista de jogos e reporta estatísticas.
        """
        aprovados = []
        rejeitados = 0
        
        for jogo in jogos:
            ok, _ = FiltrosAvancados.validar_jogo(jogo)
            if ok:
                aprovados.append(jogo)
            else:
                rejeitados += 1
                
        if verbose:
            print(f"\n🛡️  SMART FILTERS:")
            print(f"   • Total analisado: {len(jogos)}")
            print(f"   • Aprovados: {len(aprovados)}")
            print(f"   • Rejeitados: {rejeitados} ({rejeitados/len(jogos)*100:.1f}%)")
            
        return aprovados
