"""
Mapa de Fontes - MegaCLI

Arquivo central de referência para todos os módulos do projeto.
Facilita a reestruturação e desacopla os imports dos caminhos físicos.
"""

import sys
from pathlib import Path

# Garantir que a raiz e src estejam no path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

# ==============================================================================
# IMPORTS - CORE
# ==============================================================================
import src.core.config as Config
import src.core.paths as Paths
import src.core.gerador_jogos_top10 as GeradorJogos
import src.core.modo_conservador as ModoConservador
import src.core.visualizacao_graficos as VisGraficos
import src.core.previsao_30n as Previsao30N
import src.core.metricas_confianca as MetricasConfianca
import src.core.conexao_ia as ConexaoIA
import src.core.analise_params as AnaliseParams
import src.core.ciclo_refinamento_ia as CicloRefinamentoIA
import src.core.analisador_9_numeros as Analisador9Numeros
import src.core.analisador_universo_reduzido as AnalisadorUniversoReduzido
import src.core.filtros_avancados as FiltrosAvancados
import src.core.seletor_universo_inteligente as SeletorUniversoInteligente
import src.core.sistema_refinamento as SistemaRefinamento
import src.core.sistema_voto as SistemaVoto
import src.core.sistema_voto as SistemaVoto

# ==============================================================================
# IMPORTS - VALIDAÇÃO
# ==============================================================================
import src.validacao.ranking_indicadores as RankingIndicadores
import src.validacao.analisador_historico as AnalisadorHistorico
import src.validacao.analise_correlacao as AnaliseCorrelacao
import src.validacao.detector_overfitting as DetectorOverfitting
import src.validacao.validador_train_test as ValidadorTrainTest
import src.validacao.validador_1000_jogos as Validador1000Jogos
import src.validacao.validador_ciclo as ValidadorCiclo
import src.validacao.validacao_continua as ValidacaoContinua
import src.validacao.backtest_comparativo as BacktestComparativo
import src.validacao.estrategias_previsao as EstrategiasPrevisao
try:
    import src.validacao.validador_retroativo_v2_completo as ValidadorRetroativoV2
except ImportError:
    ValidadorRetroativoV2 = None # Pode ter deps opcionais

# ==============================================================================
# IMPORTS - UTILS
# ==============================================================================
import src.utils.export_jogos_top9 as ExportJogos
import src.utils.indicador_otimizado_10n as IndicadorOtimizado10N
import src.utils.sistema_exportacao as SistemaExportacao
import src.utils.utils as UtilsGenerico
import src.utils.limpar_documentos as LimparDocumentos
import src.utils.exportador_excel as ExportadorExcel

# Indicadores (Agrupados)
try:
    import src.utils.indicadores_avancados as IndAvancados
    import src.utils.indicadores_basicos as IndBasicos
    import src.utils.indicadores_frequencia as IndFrequencia
    import src.utils.indicadores_geometricos as IndGeometricos
except ImportError:
    pass # Falha silenciosa para utils opcionais

# ==============================================================================
# IMPORTS - INTERFACE
# ==============================================================================



# ==============================================================================
# EXPORTAÇÃO DAS VARIÁVEIS (MAPPING)
# ==============================================================================

# Core
CONFIG = Config
PATHS = Paths
GERADOR_JOGOS = GeradorJogos
MODO_CONSERVADOR = ModoConservador
VISUALIZACAO = VisGraficos
PREVISAO_30N = Previsao30N
METRICAS_CONFIANCA = MetricasConfianca
CONEXAO_IA = ConexaoIA
ANALISE_PARAMS = AnaliseParams
CICLO_REFINAMENTO = CicloRefinamentoIA
ANALISADOR_9_NUMEROS = Analisador9Numeros
ANALISADOR_UNIVERSO_REDUZIDO = AnalisadorUniversoReduzido
FILTROS_AVANCADOS = FiltrosAvancados
SELETOR_UNIVERSO = SeletorUniversoInteligente
SISTEMA_REFINAMENTO = SistemaRefinamento
SISTEMA_VOTO = SistemaVoto


# Validação
RANKING = RankingIndicadores
ANALISADOR_HISTORICO = AnalisadorHistorico
ANALISE_CORRELACAO = AnaliseCorrelacao
DETECTOR_OVERFITTING = DetectorOverfitting
VALIDADOR_TRAIN_TEST = ValidadorTrainTest
VALIDADOR_1000_JOGOS = Validador1000Jogos
VALIDADOR_CICLO = ValidadorCiclo
VALIDACAO_CONTINUA = ValidacaoContinua
BACKTEST = BacktestComparativo
ESTRATEGIAS = EstrategiasPrevisao
VALIDADOR_RETROATIVO = ValidadorRetroativoV2

# Utils
EXPORT_JOGOS = ExportJogos
INDICADOR_OTIMIZADO_10N = IndicadorOtimizado10N
SISTEMA_EXPORTACAO = SistemaExportacao
UTILS = UtilsGenerico
LIMPAR_DOCS = LimparDocumentos
EXPORTADOR_EXCEL = ExportadorExcel

# Interface


import src.gerar_analise_v6 as AnaliseV6
ANALISE_V6 = AnaliseV6

# Interface (Movido para o final para evitar ciclo com CONFIG)
import src.menu_interativo as MenuInterativo
MENU_INTERATIVO = MenuInterativo




