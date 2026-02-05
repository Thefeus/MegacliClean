"""
Detector de Overfitting - MegaCLI v6.2

Detecta automaticamente sinais de overfitting no sistema de previsão.
Analisa múltiplos critérios e emite alertas coloridos.

Autor: MegaCLI Team
Data: 02/02/2026
Versão: 1.0.0
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ThresholdsOverfit:
    """Thresholds para detecção de overfitting."""
    degradacao_maxima: float = 0.25  # 25% de queda é preocupante
    treino_minimo_suspeito: float = 0.85  # >85% em treino é suspeito
    teste_minimo_aceitavel: float = 0.60  # <60% em teste é ruim
    indicadores_max: int = 20  # >20 indicadores = risco
    universo_minimo: int = 15  # <15 números = muito arriscado


class DetectorOverfitting:
    """
    Detecta sinais de overfitting através de múltiplos critérios.
    """
    
    def __init__(self, thresholds: ThresholdsOverfit = None):
        self.thresholds = thresholds or ThresholdsOverfit()
    
    def analisar(
        self,
        performance_treino: float,
        performance_teste: float,
        n_indicadores: int,
        tamanho_universo: int
    ) -> Dict[str, Any]:
        """
        Analisa múltiplos critérios de overfitting.
        
        Args:
            performance_treino: Taxa de sucesso no treino
            performance_teste: Taxa de sucesso no teste
            n_indicadores: Número de indicadores usados
            tamanho_universo: Tamanho do universo reduzido
            
        Returns:
            Dict com análise completa
        """
        alertas = []
        pontos_risco = 0
        
        # 1. Análise de degradação
        degradacao = performance_treino - performance_teste
        degradacao_pct = abs(degradacao) * 100
        
        if degradacao > self.thresholds.degradacao_maxima:
            alertas.append(
                f"⚠️ Degradação alta: {degradacao_pct:.1f}% (limite: {self.thresholds.degradacao_maxima*100:.0f}%)"
            )
            pontos_risco += 3
        elif degradacao > self.thresholds.degradacao_maxima * 0.6:
            alertas.append(
                f"⚠️ Degradação moderada: {degradacao_pct:.1f}%"
            )
            pontos_risco += 1
        
        # 2. Performance de treino suspeita
        if performance_treino > self.thresholds.treino_minimo_suspeito:
            alertas.append(
                f"⚠️ Performance de treino muito alta: {performance_treino*100:.1f}% (suspeito > {self.thresholds.treino_minimo_suspeito*100:.0f}%)"
            )
            pontos_risco += 2
        
        # 3. Performance de teste baixa
        if performance_teste < self.thresholds.teste_minimo_aceitavel:
            alertas.append(
                f"⚠️ Performance de teste baixa: {performance_teste*100:.1f}% (aceitável > {self.thresholds.teste_minimo_aceitavel*100:.0f}%)"
            )
            pontos_risco += 2
        
        # 4. Muitos indicadores
        if n_indicadores > self.thresholds.indicadores_max:
            alertas.append(
                f"⚠️ Muitos indicadores: {n_indicadores} (recomendado ≤ {self.thresholds.indicadores_max})"
            )
            pontos_risco += 1
        
        # 5. Universo muito restrito
        if tamanho_universo < self.thresholds.universo_minimo:
            alertas.append(
                f"⚠️ Universo muito restrito: {tamanho_universo} números (mínimo recomendado: {self.thresholds.universo_minimo})"
            )
            pontos_risco += 1
        
        # Classificar nível de risco
        if pontos_risco >= 5:
            nivel_risco = "ALTO"
            overfitting_detectado = True
        elif pontos_risco >= 3:
            nivel_risco = "MÉDIO"
            overfitting_detectado = False
        else:
            nivel_risco = "BAIXO"
            overfitting_detectado = False
        
        # Gerar recomendações
        recomendacoes = self._gerar_recomendacoes(
            nivel_risco,
            degradacao_pct,
            n_indicadores,
            tamanho_universo
        )
        
        return {
            'overfitting_detectado': overfitting_detectado,
            'nivel_risco': nivel_risco,
            'pontos_risco': pontos_risco,
            'degradacao_pct': degradacao_pct,
            'alertas': alertas,
            'recomendacoes': recomendacoes,
            'metricas': {
                'performance_treino': performance_treino,
                'performance_teste': performance_teste,
                'n_indicadores': n_indicadores,
                'tamanho_universo': tamanho_universo
            }
        }
    
    def _gerar_recomendacoes(
        self,
        nivel_risco: str,
        degradacao: float,
        n_indicadores: int,
        tamanho_universo: int
    ) -> List[str]:
        """Gera recomendações específicas."""
        recs = []
        
        if nivel_risco == "ALTO":
            recs.append("🔴 AÇÃO NECESSÁRIA: Sistema está overfitting!")
            recs.append("   1. Use o Modo Conservador (Opção 12)")
            recs.append("   2. Reduza indicadores para 5-7 principais")
            recs.append("   3. Aumente universo para 25+ números")
        
        elif nivel_risco == "MÉDIO":
            recs.append("🟡 ATENÇÃO: Sinais de overfitting moderado")
            if n_indicadores > 15:
                recs.append(f"   • Reduza indicadores (atual: {n_indicadores}, alvo: 10-15)")
            if tamanho_universo < 20:
                recs.append(f"   • Aumente universo (atual: {tamanho_universo}, alvo: 20-25)")
            if degradacao > 15:
                recs.append(f"   • Monit ore dradação (atual: {degradacao:.1f}%)")
        
        else:
            recs.append("✅ Sistema generaliza bem")
            recs.append("   • Performance consistente entre treino e teste")
            recs.append("   • Continue monitorando novos sorteios")
        
        return recs
    
    def gerar_relatorio_visual(self, analise: Dict[str, Any]) -> str:
        """Gera relatório visual colorido."""
        nivel = analise['nivel_risco']
        
        # Cores e emojis
        if nivel == "ALTO":
            emoji = "🔴"
            cor = "VERMELHO"
        elif nivel == "MÉDIO":
            emoji = "🟡"
            cor = "AMARELO"
        else:
            emoji = "🟢"
            cor = "VERDE"
        
        relatorio = f"""
{'='*70}
{emoji} ANÁLISE DE OVERFITTING - NÍVEL: {nivel}
{'='*70}

📊 Métricas:
   • Treino: {analise['metricas']['performance_treino']*100:.1f}%
   • Teste: {analise['metricas']['performance_teste']*100:.1f}%
   • Degradação: {analise['degradacao_pct']:.1f}%
   • Indicadores: {analise['metricas']['n_indicadores']}
   • Universo: {analise['metricas']['tamanho_universo']} números

⚠️ Alertas:
"""
        
        if analise['alertas']:
            for alerta in analise['alertas']:
                relatorio += f"   {alerta}\n"
        else:
            relatorio += "   ✅ Nenhum alerta\n"
        
        relatorio += "\n💡 Recomendações:\n"
        for rec in analise['recomendacoes']:
            relatorio += f"{rec}\n"
        
        relatorio += "\n" + "="*70
        
        return relatorio


# Exports
__all__ = [
    'DetectorOverfitting',
    'ThresholdsOverfitting'
]


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando Detector de Overfitting...\n")
    
    detector = DetectorOverfitting()
    
    # Caso 1: Overfitting alto
    print("Teste 1: Overfitting ALTO")
    analise1 = detector.analisar(
        performance_treino=0.90,
        performance_teste=0.55,
        n_indicadores=30,
        tamanho_universo=9
    )
    print(detector.gerar_relatorio_visual(analise1))
    
    # Caso 2: Sistema bom
    print("\nTeste 2: Sistema BOM")
    analise2 = detector.analisar(
        performance_treino=0.72,
        performance_teste=0.68,
        n_indicadores=10,
        tamanho_universo=25
    )
    print(detector.gerar_relatorio_visual(analise2))
    
    print("\n✅ Testes concluídos!\n")
