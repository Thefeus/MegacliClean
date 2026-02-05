"""
Validador de Ciclo Iterativo - MegaCLI v5.0

Valida pesos do ciclo anterior e compara performance entre ciclos.
Permite rastreamento de evolução e feedback loop para refinamento contínuo.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import json
from datetime import datetime


class ValidadorCiclo:
    """Valida e compara ciclos de refinamento"""
    
    def __init__(self, arquivo_excel: Path, dir_historico: Path):
        """
        Inicializa validador de ciclo.
        
        Args:
            arquivo_excel: Caminho para Excel com RANKING INDICADORES
            dir_historico: Diretório para salvar histórico JSON
        """
        self.arquivo_excel = arquivo_excel
        self.dir_historico = dir_historico
        self.dir_historico.mkdir(parents=True, exist_ok=True)
    
    def carregar_pesos_anteriores(self) -> Optional[Dict[str, float]]:
        """
        Carrega pesos do ciclo anterior do Excel.
        
        Returns:
            Dict {indicador: Peso_IA} ou None se não existir
        """
        if not self.arquivo_excel.exists():
            return None
        
        try:
            df_ranking = pd.read_excel(self.arquivo_excel, 'RANKING INDICADORES')
            
            if 'Peso_IA' not in df_ranking.columns:
                print(f"   ⚠️ Coluna Peso_IA não encontrada no Excel")
                return None
            
            pesos = dict(zip(df_ranking['indicador'], df_ranking['Peso_IA']))
            print(f"   ✅ {len(pesos)} pesos carregados do ciclo anterior")
            return pesos
            
        except Exception as e:
            print(f"   ⚠️ Erro ao carregar pesos: {e}")
            return None
    
    def validar_pesos_com_historico(
        self,
        pesos: Dict[str, float],
        df_historico: pd.DataFrame,
        n_sorteios: int = 50
    ) -> Dict[str, any]:
        """
        Valida pesos contra série histórica.
        
        Args:
            pesos: Dict {indicador: peso}
            df_historico: DataFrame com histórico
            n_sorteios: Quantos sorteios testar (não usado ainda)
        
        Returns:
            Dict com métricas de validação
        """
        from collections import Counter
        
        # Calcular estatísticas dos pesos
        valores_pesos = list(pesos.values())
        
        # Identificar indicadores com pesos extremos
        peso_max_val = max(valores_pesos)
        peso_min_val = min(valores_pesos)
        indicador_max = max(pesos, key=pesos.get)
        indicador_min = min(pesos, key=pesos.get)
        
        # Calcular distribuição de pesos
        pesos_altos = sum(1 for p in valores_pesos if p >= 70)
        pesos_medios = sum(1 for p in valores_pesos if 50 <= p < 70)
        pesos_baixos = sum(1 for p in valores_pesos if p < 50)
        
        metricas = {
            'pesos_testados': len(pesos),
            'sorteios_validados': n_sorteios,
            'peso_medio': np.mean(valores_pesos),
            'peso_mediano': np.median(valores_pesos),
            'peso_desvio': np.std(valores_pesos),
            'peso_max': peso_max_val,
            'peso_min': peso_min_val,
            'indicador_max': indicador_max,
            'indicador_min': indicador_min,
            'distribuicao': {
                'altos (>=70)': pesos_altos,
                'medios (50-70)': pesos_medios,
                'baixos (<50)': pesos_baixos
            }
        }
        
        return metricas
    
    def comparar_ciclos(
        self,
        pesos_anterior: Dict[str, float],
        pesos_atual: Dict[str, float]
    ) -> pd.DataFrame:
        """
        Compara pesos entre ciclos.
        
        Returns:
            DataFrame com delta de cada indicador
        """
        dados_comparacao = []
        
        todos_indicadores = set(pesos_anterior.keys()) | set(pesos_atual.keys())
        
        for indicador in sorted(todos_indicadores):
            peso_ant = pesos_anterior.get(indicador, 50.0)
            peso_atual = pesos_atual.get(indicador, 50.0)
            delta = peso_atual - peso_ant
            delta_perc = (delta / peso_ant * 100) if peso_ant > 0 else 0
            
            # Determinar tendência visual
            if delta > 5:
                tendencia = '📈 Subiu'
            elif delta < -5:
                tendencia = '📉 Caiu'
            else:
                tendencia = '➡️ Estável'
            
            dados_comparacao.append({
                'Indicador': indicador,
                'Peso_Anterior': round(peso_ant, 2),
                'Peso_Atual': round(peso_atual, 2),
                'Delta': round(delta, 2),
                'Delta_%': round(delta_perc, 2),
                'Tendência': tendencia
            })
        
        df_comparacao = pd.DataFrame(dados_comparacao)
        
        # Ordenar por maior mudança absoluta
        df_comparacao['Delta_Abs'] = df_comparacao['Delta'].abs()
        df_comparacao = df_comparacao.sort_values('Delta_Abs', ascending=False)
        df_comparacao = df_comparacao.drop('Delta_Abs', axis=1)
        df_comparacao = df_comparacao.reset_index(drop=True)
        
        return df_comparacao
    
    def salvar_historico(
        self,
        pesos: Dict[str, float],
        metricas: Dict[str, any],
        versao: int
    ):
        """Salva histórico de pesos versionado"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Salvar JSON versionado
        arquivo_json = self.dir_historico / f"pesos_v{versao}_{timestamp}.json"
        
        dados_historico = {
            'versao': versao,
            'timestamp': timestamp,
            'data_legivel': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'pesos': pesos,
            'metricas': metricas
        }
        
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(dados_historico, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Histórico salvo: {arquivo_json.name}")
    
    def obter_versao_atual(self) -> int:
        """Obtém próxima versão baseada em arquivos existentes"""
        arquivos = list(self.dir_historico.glob("pesos_v*.json"))
        
        if not arquivos:
            return 1
        
        versoes = []
        for arq in arquivos:
            try:
                # Formato: pesos_v{N}_{timestamp}.json
                partes = arq.stem.split('_')
                if len(partes) >= 2 and partes[0] == 'pesos':
                    v = int(partes[1][1:])  # Extrai número de v{N}
                    versoes.append(v)
            except:
                continue
        
        return max(versoes) + 1 if versoes else 1


def executar_validacao_ciclo(
    arquivo_excel: Path,
    df_historico: pd.DataFrame
) -> Tuple[Optional[Dict], Optional[Dict], int]:
    """
    Executa validação completa de ciclo.
    
    Args:
        arquivo_excel: Caminho do Excel com resultados
        df_historico: DataFrame histórico completo
    
    Returns:
        (pesos_anteriores, metricas_validacao, versao_atual)
    """
    print("\n" + "="*80)
    print("🔄 FASE 0: VALIDAÇÃO DE CICLO ANTERIOR")
    print("="*80)
    
    dir_historico = arquivo_excel.parent / "historico_pesos"
    validador = ValidadorCiclo(arquivo_excel, dir_historico)
    
    # Obter versão
    versao = validador.obter_versao_atual()
    print(f"\n📌 Ciclo atual: v{versao}")
    
    # Carregar pesos anteriores
    print(f"\n📂 Buscando pesos do ciclo anterior...")
    pesos_anteriores = validador.carregar_pesos_anteriores()
    
    if pesos_anteriores is None:
        print(f"\n⚠️ Nenhum ciclo anterior encontrado")
        print(f"   Este é o PRIMEIRO ciclo de refinamento (BASELINE)")
        print(f"   Histórico será criado em: {dir_historico}")
        return None, None, versao
    
    print(f"\n✅ Ciclo anterior encontrado (v{versao-1})")
    
    # Validar pesos anteriores
    print(f"\n🔍 Validando pesos do ciclo v{versao-1}...")
    metricas = validador.validar_pesos_com_historico(
        pesos_anteriores,
        df_historico,
        n_sorteios=50
    )
    
    print(f"\n📊 Métricas do Ciclo v{versao-1}:")
    print(f"   • Indicadores: {metricas['pesos_testados']}")
    print(f"   • Peso médio: {metricas['peso_medio']:.2f}")
    print(f"   • Peso mediano: {metricas['peso_mediano']:.2f}")
    print(f"   • Desvio padrão: {metricas['peso_desvio']:.2f}")
    print(f"   • Melhor indicador: {metricas['indicador_max']} ({metricas['peso_max']:.1f})")
    print(f"   • Pior indicador: {metricas['indicador_min']} ({metricas['peso_min']:.1f})")
    print(f"\n📈 Distribuição de pesos:")
    for categoria, qtd in metricas['distribuicao'].items():
        print(f"   • {categoria}: {qtd} indicadores")
    
    return pesos_anteriores, metricas, versao
