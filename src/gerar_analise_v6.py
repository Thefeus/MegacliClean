"""
Gerador de Análise V6 Completa
Versão 6.3.0

Orquestrador para análise completa envolvendo:
- Análise Histórica (Batimento)
- Ranking de Indicadores
- Validação IA
- Universos Reduzidos (20N, 10N, 9N)
- Geração de Jogos (210 combinações)
- Exportação Excel/TXT
"""

import pandas as pd
import sys
from datetime import datetime
from colorama import Fore, Style, init

# Inicializar Colorama
init(autoreset=True)

# Importar do Mapa de Fontes
from config.fontes import (
    CONFIG,
    PATHS,
    ANALISE_PARAMS,
    ANALISADOR_HISTORICO,
    RANKING,
    ANALISADOR_UNIVERSO_REDUZIDO,
    ANALISADOR_9_NUMEROS,
    INDICADOR_OTIMIZADO_10N,
    GERADOR_JOGOS,
    VALIDADOR_1000_JOGOS,
    SISTEMA_EXPORTACAO
)

# Aliases
AnaliseConfig = ANALISE_PARAMS.AnaliseConfig
SistemaExportacao = SISTEMA_EXPORTACAO.SistemaExportacao
criar_config_jogos = SISTEMA_EXPORTACAO.criar_config_jogos

def main():
    print(f"\n{Fore.YELLOW}{'='*70}")
    print(f"🚀 INICIANDO ANÁLISE V6 COMPLETA")
    print(f"{'='*70}{Style.RESET_ALL}\n")

    # 1. Carregar Dados
    print(f"{Fore.CYAN}📂 Carregando base de dados...{Style.RESET_ALL}")
    if not CONFIG.ARQUIVO_HISTORICO.exists():
        print(f"{Fore.RED}❌ Arquivo de histórico não encontrado!{Style.RESET_ALL}")
        return

    try:
        df_historico = pd.read_excel(str(CONFIG.ARQUIVO_HISTORICO), sheet_name='MEGA SENA')
        print(f"{Fore.GREEN}✅ Histórico carregado: {len(df_historico)} sorteios{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Erro ao ler Excel: {e}{Style.RESET_ALL}")
        return

    # 2. Análise Histórica & Ranking
    print(f"\n{Fore.CYAN}📊 [1/6] Executando Análise Histórica e Ranking...{Style.RESET_ALL}")
    try:
        estatisticas = ANALISADOR_HISTORICO.avaliar_serie_historica_completa(
            df_historico,
            janela_inicial=len(df_historico) - AnaliseConfig.BATIMENTO_JANELA_OFFSET,
            passo=AnaliseConfig.BATIMENTO_PASSO,
            max_jogos=AnaliseConfig.BATIMENTO_MAX_JOGOS
        )
        estats_dict = {nome: estat.to_dict() for nome, estat in estatisticas.items()}
        ranking = RANKING.criar_ranking(estats_dict)
        print(f"{Fore.GREEN}✅ Ranking gerado com sucesso ({len(ranking)} indicadores){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Falha no Ranking: {e}{Style.RESET_ALL}")
        return

    # 3. Universos Reduzidos (20N)
    print(f"\n{Fore.CYAN}🎲 [2/6] Gerando Universo Reduzido TOP 20N...{Style.RESET_ALL}")
    try:
        numeros_20, pesos_20 = ANALISADOR_UNIVERSO_REDUZIDO.selecionar_top_20_numeros(
            df_historico,
            ranking,
            top_indicadores=10,
            janela=100,
            verbose=True
        )
    except Exception as e:
        print(f"{Fore.RED}❌ Erro no 20N: {e}{Style.RESET_ALL}")
        return
        
    # 4. Universos Reduzidos (10N - Indicador Otimizado)
    print(f"\n{Fore.CYAN}🎲 [3/6] Gerando Universo Reduzido TOP 10N...{Style.RESET_ALL}")
    try:
        indicador_10n = INDICADOR_OTIMIZADO_10N.IndicadorOtimizado10N()
        numeros_10, _ = indicador_10n.selecionar_top_10(df_historico, verbose=True)
    except Exception as e:
        print(f"{Fore.RED}❌ Erro no 10N: {e}{Style.RESET_ALL}")
        numeros_10 = []

    # 5. Universos Reduzidos (9N)
    print(f"\n{Fore.CYAN}🎲 [4/6] Gerando Universo Reduzido TOP 9N...{Style.RESET_ALL}")
    try:
        numeros_9, _ = ANALISADOR_9_NUMEROS.selecionar_top_9_numeros(df_historico, ranking, verbose=True)
    except Exception as e:
        print(f"{Fore.RED}❌ Erro no 9N: {e}{Style.RESET_ALL}")
        numeros_9 = []
        
    # 6. Geração de Jogos (Baseada no Ranking Principal - Padrão V6)
    # A V6 original gerava 210 jogos baseados no ranking geral (Top Indicators), 
    # mas o usuário mencionou "Geração de 210 jogos". Vamos usar a geração padrão Top 10 Indicadores.
    
    print(f"\n{Fore.CYAN}🎯 [5/6] Gerando 210 Jogos Finais (Top 10 Indicadores)...{Style.RESET_ALL}")
    try:
        jogos = GERADOR_JOGOS.gerar_jogos_top10(
            df_historico,
            ranking,
            n_jogos=210, # Fixo na V6
            top_n=10,
            verbose=True
        )
    except Exception as e:
        print(f"{Fore.RED}❌ Erro na Geração de Jogos: {e}{Style.RESET_ALL}")
        return

    # 7. Validação
    print(f"\n{Fore.CYAN}🔍 [6/6] Validando Jogos (1000 Sorteios Históricos)...{Style.RESET_ALL}")
    try:
        validacao = VALIDADOR_1000_JOGOS.validar_jogos_historico(
            jogos,
            df_historico,
            n_sorteios=1000,
            verbose=True
        )
    except Exception as e:
        print(f"{Fore.YELLOW}⚠️  Aviso: Erro na validação ({e}), seguindo para exportação...{Style.RESET_ALL}")
        validacao = None

    # 8. Exportação Unificada
    print(f"\n{Fore.CYAN}💾 Exportando Resultados...{Style.RESET_ALL}")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    sistema = SistemaExportacao()
    
    # Exportar TXT
    arquivo_txt = CONFIG.RESULTADO_DIR / f"V6_JOGOS_{timestamp}.txt"
    config_txt = {
        "tipo": "txt",
        "arquivo": str(arquivo_txt),
        "dados": jogos,
        "formatacao": {"titulo": "MEGACLI V6.3.0 - ANÁLISE COMPLETA"},
        "formato_linha": "#{rank:03d}: {numeros_str} | Score: {score:.2f}"
    }
    
    # Preparar dados TXT
    dados_txt = []
    for j in jogos:
        dados_txt.append({
            'rank': j.get('rank', 0),
            'numeros_str': '-'.join(f"{n:02d}" for n in j['numeros']),
            'score': j.get('score', 0)
        })
    config_txt['dados'] = dados_txt
    sistema.exportar(config_txt)
    print(f"{Fore.GREEN}✅ TXT salvo: {arquivo_txt.name}{Style.RESET_ALL}")
    
    # Exportar Excel Completo
    # Precisamos criar um Excel com abas para 9N, 10N, 20N e Jogos
    arquivo_excel = CONFIG.RESULTADO_DIR / f"V6_ANALISE_COMPLETA_{timestamp}.xlsx"
    
    try:
        with pd.ExcelWriter(arquivo_excel, engine='openpyxl') as writer:
            # Aba Jogos
            df_jogos = pd.DataFrame([{
                'Rank': j.get('rank'),
                'Numeros': '-'.join(f"{n:02d}" for n in j['numeros']),
                'Score': j.get('score'),
                'Probabilidade': j.get('probabilidade', 0),
                'Confianca': j.get('confianca', 'N/A')
            } for j in jogos])
            df_jogos.to_excel(writer, sheet_name='JOGOS_GERADOS', index=False)
            
            # Aba 20N
            if numeros_20:
                df_20n = pd.DataFrame({'Numeros_20N': numeros_20})
                df_20n.to_excel(writer, sheet_name='TOP_20N', index=False)
                
            # Aba 10N
            if numeros_10:
                df_10n = pd.DataFrame({'Numeros_10N': numeros_10})
                df_10n.to_excel(writer, sheet_name='TOP_10N', index=False)
                
            # Aba 9N
            if numeros_9:
                df_9n = pd.DataFrame({'Numeros_9N': numeros_9})
                df_9n.to_excel(writer, sheet_name='TOP_9N', index=False)
                
            # Aba Validação (se houver)
            if validacao and 'resultados' in validacao:
                 df_val = pd.DataFrame(validacao['resultados'])
                 df_val.to_excel(writer, sheet_name='VALIDACAO_HISTORICA', index=False)
                 
        print(f"{Fore.GREEN}✅ Excel Completo salvo: {arquivo_excel.name}{Style.RESET_ALL}")
        
    except Exception as e:
         print(f"{Fore.RED}❌ Erro ao salvar Excel: {e}{Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}✅ ANÁLISE V6 CONCLUÍDA!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
