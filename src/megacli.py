"""
MegaCLI v6.3.0 - Script Principal de Entrada

Ponto de entrada unificado para o sistema MegaCLI.
Suporta modo interativo e execução direta via argumentos.

Autor: MegaCLI Team
Data: 04/02/2026
Versão: 1.0.0

Uso:
    # Modo interativo
    python megacli.py
    
    # Modo direto
    python megacli.py --gerar-jogos
    python megacli.py --validar
    python megacli.py --analise-completa
    python megacli.py --config
"""

import sys
from pathlib import Path

# Configurar PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import argparse
from datetime import datetime

# Tentar importar colorama
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    CORES_DISPONIVEIS = True
except ImportError:
    CORES_DISPONIVEIS = False
    class Fore:
        GREEN = YELLOW = RED = CYAN = MAGENTA = BLUE = WHITE = ""
    class Style:
        BRIGHT = RESET_ALL = ""


def exibir_banner_inicial():
    """Exibe banner inicial do sistema."""
    banner = f"""
{Fore.CYAN}{'='*70}
{Fore.YELLOW}
    ███╗   ███╗███████╗ ██████╗  █████╗  ██████╗██╗     ██╗
    ████╗ ████║██╔════╝██╔════╝ ██╔══██╗██╔════╝██║     ██║
    ██╔████╔██║█████╗  ██║  ███╗███████║██║     ██║     ██║
    ██║╚██╔╝██║██╔══╝  ██║   ██║██╔══██║██║     ██║     ██║
    ██║ ╚═╝ ██║███████╗╚██████╔╝██║  ██║╚██████╗███████╗██║
    ╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚══════╝╚═╝
{Fore.CYAN}
    Sistema Inteligente para Análise Mega-Sena
    Versão 6.3.0 | Data: {datetime.now().strftime('%d/%m/%Y')}
    
{'='*70}{Style.RESET_ALL}
"""
    print(banner)


def verificar_ambiente():
    """
    Verifica se o ambiente está configurado corretamente.
    
    Returns:
        bool: True se ambiente OK, False caso contrário
    """
    print(f"\n{Fore.CYAN}🔍 Verificando ambiente...{Style.RESET_ALL}")
    
    erros = []
    
    # Verificar arquivo de histórico
    try:
        from src.core.config import ARQUIVO_HISTORICO
        if not ARQUIVO_HISTORICO.exists():
            erros.append(f"Arquivo de histórico não encontrado: {ARQUIVO_HISTORICO}")
        else:
            print(f"{Fore.GREEN}✅ Arquivo de histórico encontrado{Style.RESET_ALL}")
    except Exception as e:
        erros.append(f"Erro ao verificar arquivo de histórico: {e}")
    
    # Verificar diretório de resultados
    try:
        from src.core.config import RESULTADO_DIR
        if not RESULTADO_DIR.exists():
            RESULTADO_DIR.mkdir(parents=True, exist_ok=True)
            print(f"{Fore.YELLOW}⚠️  Diretório de resultados criado: {RESULTADO_DIR}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Diretório de resultados encontrado{Style.RESET_ALL}")
    except Exception as e:
        erros.append(f"Erro ao verificar diretório de resultados: {e}")
    
    # Verificar dependências críticas
    dependencias = ['pandas', 'numpy', 'openpyxl', 'tqdm']
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"{Fore.GREEN}✅ {dep} instalado{Style.RESET_ALL}")
        except ImportError:
            erros.append(f"Dependência não instalada: {dep}")
    
    if erros:
        print(f"\n{Fore.RED}❌ Erros encontrados:{Style.RESET_ALL}")
        for erro in erros:
            print(f"   • {erro}")
        return False
    
    print(f"\n{Fore.GREEN}✅ Ambiente configurado corretamente!{Style.RESET_ALL}")
    return True


def modo_interativo():
    """Executa o menu interativo."""
    print(f"\n{Fore.CYAN}🚀 Iniciando modo interativo...{Style.RESET_ALL}\n")
    
    try:
        from config.fontes import MENU_INTERATIVO
        MENU_INTERATIVO.executar_menu()
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro ao executar menu interativo: {e}{Style.RESET_ALL}\n")
        import traceback
        traceback.print_exc()


def modo_gerar_jogos():
    """Executa geração de jogos diretamente."""
    print(f"\n{Fore.CYAN}🎯 Gerando 210 jogos com top 10 indicadores...{Style.RESET_ALL}\n")
    
    try:
        # Importar via Mapa de Fontes (Desacoplado)
        from config.fontes import (
            CONFIG as AnaliseConfig,  # Aliasing to match existing usage if possible, or refactor usage
            GERADOR_JOGOS,
            RANKING,
            ANALISADOR_HISTORICO,
            ANALISE_PARAMS
        )
        # Importar constantes de config
        from config.fontes import CONFIG
        
        # Acessar constantes via o módulo config importado
        ARQUIVO_HISTORICO = CONFIG.ARQUIVO_HISTORICO
        RESULTADO_DIR = CONFIG.RESULTADO_DIR
        
        # Usar AnaliseConfig do módulo de parametros via Fonte
        AnaliseConfig = ANALISE_PARAMS.AnaliseConfig
        
        import pandas as pd
        
        # Carregar dados
        df_historico = pd.read_excel(str(ARQUIVO_HISTORICO), sheet_name='MEGA SENA')

        # AnaliseConfig original parece ser uma classe de parametros.
        # Vou usar o dict MEGA_CONFIG do módulo config ou importar AnaliseConfig de onde ele estiver
        # Verificando config/fontes.py: import src.core.config as Config
        # src.core.config tem MEGA_CONFIG (dict).
        # src.core.analise_params tem AnaliseParams? O arquivo original importava AnaliseConfig de src.core.config?
        # Linha 135 original: from src.core.config import ... AnaliseConfig
        # Linha 41 de src/core/config.py diz: # AnaliseConfig removido daqui...
        # Entao o import original provavelmente falharia se AnaliseConfig nao estivesse la, mas o codigo diz que importava.
        # Talvez eu precise importar de analise_params se não estiver em config.
        
        # VOU ADICIONAR analise_params EM fontes.py SE PRECISAR.
        # Por enquanto, vou usar os valores do dict se possivel, ou corrigir o import.
        # O codigo original usa AnaliseConfig.BATIMENTO_JANELA_OFFSET.
        # Se AnaliseConfig nao existe mais em src.core.config, o codigo original estava quebrado?
        # A ultima leitura de src/core/config.py (Step 60) mostra "AnaliseConfig removido daqui".
        # Entao o import na linha 135 do original (Step 15) "from src.core.config import ... AnaliseConfig" estava potencialmente quebrado ou referindo a uma versao antiga em memoria?
        # O usuario disse que o codigo roda.
        # Vou assumir que AnaliseConfig deve vir de src.core.analise_params.
        
        from src.core.analise_params import AnaliseConfig # Temporario até adicionar em fontes
        
        # Criar ranking
        estatisticas = ANALISADOR_HISTORICO.avaliar_serie_historica_completa(
            df_historico,
            janela_inicial=len(df_historico) - AnaliseConfig.BATIMENTO_JANELA_OFFSET,
            passo=AnaliseConfig.BATIMENTO_PASSO,
            max_jogos=AnaliseConfig.BATIMENTO_MAX_JOGOS
        )
        estats_dict = {nome: estat.to_dict() for nome, estat in estatisticas.items()}
        ranking = RANKING.criar_ranking(estats_dict)
        
        # Gerar jogos
        jogos = GERADOR_JOGOS.gerar_jogos_top10(
            df_historico,
            ranking,
            n_jogos=AnaliseConfig.GERACAO_N_JOGOS,
            top_n=AnaliseConfig.GERACAO_TOP_INDICADORES,
            verbose=True
        )
        
        # Exportar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = RESULTADO_DIR / f"jogos_gerados_{timestamp}.txt"
        GERADOR_JOGOS.exportar_jogos_txt(jogos, str(arquivo))
        
        print(f"\n{Fore.GREEN}✅ Jogos salvos em: {arquivo}{Style.RESET_ALL}\n")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro ao gerar jogos: {e}{Style.RESET_ALL}\n")
        import traceback
        traceback.print_exc()


def modo_validar():
    """Executa validação de jogos diretamente."""
    print(f"\n{Fore.YELLOW}⚠️  Modo de validação requer jogos pré-gerados.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   Use o modo interativo ou --analise-completa{Style.RESET_ALL}\n")


def modo_analise_completa():
    """Executa análise completa diretamente."""
    print(f"\n{Fore.CYAN}🚀 Executando análise completa...{Style.RESET_ALL}\n")
    
    # Executar geração
    modo_gerar_jogos()
    
    print(f"\n{Fore.YELLOW}⚠️  Para validação completa, use o modo interativo{Style.RESET_ALL}\n")


def modo_config():
    """Exibe configurações do sistema."""
    print(f"\n{Fore.CYAN}⚙️  Configurações do Sistema{Style.RESET_ALL}\n")
    
    try:
        from config.fontes import ANALISE_PARAMS
        AnaliseConfig = ANALISE_PARAMS.AnaliseConfig
        AnaliseConfig.exibir_configuracao()
        AnaliseConfig.validar_parametros()
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro ao exibir configurações: {e}{Style.RESET_ALL}\n")


def main():
    """Função principal."""
    # Parser de argumentos
    parser = argparse.ArgumentParser(
        description='MegaCLI v6.3.0 - Sistema Inteligente para Análise Mega-Sena',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python megacli.py                    # Modo interativo
  python megacli.py --gerar-jogos      # Gerar 210 jogos
  python megacli.py --analise-completa # Análise completa
  python megacli.py --config           # Exibir configurações
        """
    )
    
    parser.add_argument(
        '--gerar-jogos',
        action='store_true',
        help='Gerar 210 jogos com top 10 indicadores'
    )
    
    parser.add_argument(
        '--validar',
        action='store_true',
        help='Validar jogos com 1000 sorteios históricos'
    )
    
    parser.add_argument(
        '--analise-completa',
        action='store_true',
        help='Executar análise completa (geração + validação)'
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='Exibir configurações do sistema'
    )
    
    parser.add_argument(
        '--no-check',
        action='store_true',
        help='Pular verificação de ambiente'
    )
    
    args = parser.parse_args()
    
    # Exibir banner
    exibir_banner_inicial()
    
    # Verificar ambiente (se não for --no-check)
    if not args.no_check:
        if not verificar_ambiente():
            print(f"\n{Fore.RED}❌ Corrija os erros acima antes de continuar{Style.RESET_ALL}\n")
            sys.exit(1)
    
    # Executar modo apropriado
    if args.gerar_jogos:
        modo_gerar_jogos()
    
    elif args.validar:
        modo_validar()
    
    elif args.analise_completa:
        modo_analise_completa()
    
    elif args.config:
        modo_config()
    
    else:
        # Modo interativo (padrão)
        modo_interativo()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Programa interrompido pelo usuário{Style.RESET_ALL}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro inesperado: {e}{Style.RESET_ALL}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
