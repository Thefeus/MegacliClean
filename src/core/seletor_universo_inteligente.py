"""
Seletor de Universo Inteligente - MegaCLI v6.0

Módulo para seleção inteligente de universo reduzido (20 números)
com validação histórica e interação com usuário.

Autor: MegaCLI Team
Data: 22/01/2026
Versão: 1.0.0
"""

import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from src.utils.indicador_probabilidade_universo import IndicadorProbabilidadeUniverso


def selecionar_universo_inteligente(
    df_historico: pd.DataFrame,
    ranking: List[Dict],
    janela_analise: int = 100,
    janela_validacao: int = 100,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Seleciona 20 números com maior probabilidade de cobertura.
    
    Args:
        df_historico: DataFrame com histórico de sorteios
        ranking: Lista com ranking de indicadores
        janela_analise: Janela para análise de probabilidade
        janela_validacao: Janela para validação histórica
        verbose: Se True, exibe informações
        
    Returns:
        Dicionário com:
        - numeros: Lista com 20 números
        - scores: Dicionário {número: score}
        - cobertura_6: Taxa de cobertura com 6 acertos
        - cobertura_5: Taxa de cobertura com 5+ acertos
        - cobertura_4: Taxa de cobertura com 4+ acertos
        - recomendacao: 'ALTA', 'MÉDIA' ou 'BAIXA'
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"🎯 SELEÇÃO DE UNIVERSO REDUZIDO INTELIGENTE")
        print(f"{'='*70}")
    
    # Criar indicador
    indicador = IndicadorProbabilidadeUniverso(janela=janela_analise)
    
    # Calcular scores
    scores = indicador.calcular_scores(df_historico, verbose=verbose)
    
    # Selecionar top 20
    numeros_20, scores_20 = indicador.selecionar_top_20(scores, verbose=verbose)
    
    # Validar cobertura histórica
    validacao = indicador.validar_cobertura(
        numeros_20,
        df_historico,
        janela_validacao=janela_validacao,
        verbose=verbose
    )
    
    resultado = {
        'numeros': numeros_20,
        'scores': scores_20,
        'cobertura_6': validacao['cobertura_6'],
        'cobertura_5': validacao['cobertura_5'],
        'cobertura_4': validacao['cobertura_4'],
        'recomendacao': validacao['recomendacao'],
        'janela_validacao': janela_validacao
    }
    
    return resultado


def apresentar_universo_usuario(
    resultado: Dict[str, Any],
    verbose: bool = True
) -> None:
    """
    Apresenta universo reduzido ao usuário de forma visual.
    
    Args:
        resultado: Dicionário retornado por selecionar_universo_inteligente
        verbose: Se True, exibe informações
    """
    if not verbose:
        return
    
    numeros = resultado['numeros']
    scores = resultado['scores']
    
    print(f"\n{'='*70}")
    print(f"📊 UNIVERSO REDUZIDO SELECIONADO")
    print(f"{'='*70}\n")
    
    # Tabela de números
    print(f"{'#':<4} {'Número':<8} {'Score':<10} {'Barra':<30}")
    print("-"*70)
    
    max_score = max(scores.values())
    for i, num in enumerate(numeros, 1):
        score = scores[num]
        barra_len = int((score / max_score) * 25)
        barra = '█' * barra_len
        print(f"{i:<4} {num:02d}       {score:>6.2f}     {barra}")
    
    # Resumo
    print(f"\n{'='*70}")
    print(f"📈 VALIDAÇÃO HISTÓRICA ({resultado['janela_validacao']} jogos)")
    print(f"{'='*70}\n")
    
    print(f"   • Cobertura 6 números: {resultado['cobertura_6']:.1f}%")
    print(f"   • Cobertura 5+ números: {resultado['cobertura_5']:.1f}%")
    print(f"   • Cobertura 4+ números: {resultado['cobertura_4']:.1f}%")
    
    # Recomendação
    rec = resultado['recomendacao']
    if rec == 'ALTA':
        print(f"\n   ✅ RECOMENDAÇÃO: {rec} - Excelente probabilidade de cobertura!")
    elif rec == 'MÉDIA':
        print(f"\n   ⚠️  RECOMENDAÇÃO: {rec} - Probabilidade moderada de cobertura")
    else:
        print(f"\n   ❌ RECOMENDAÇÃO: {rec} - Baixa probabilidade de cobertura")
    
    # Universo formatado
    print(f"\n📋 Universo Reduzido (20 números):")
    print(f"   {'-'.join(f'{n:02d}' for n in numeros)}")
    print(f"\n{'='*70}\n")


def solicitar_escolha_usuario(
    permitir_cancelar: bool = True
) -> Optional[int]:
    """
    Solicita ao usuário escolha entre TOP 10, TOP 15 ou cancelar.
    
    Args:
        permitir_cancelar: Se True, permite opção de cancelar
        
    Returns:
        10, 15 ou None (se cancelar)
    """
    print(f"\n🎯 Escolha o nível de refinamento dos indicadores:\n")
    print(f"   1. TOP 10 indicadores (mais focado)")
    print(f"   2. TOP 15 indicadores (mais diversificado)")
    
    if permitir_cancelar:
        print(f"   0. Cancelar e usar universo completo (60 números)\n")
    
    while True:
        try:
            escolha = input(f"Sua escolha: ").strip()
            
            if escolha == '1':
                print(f"\n✅ Selecionado: TOP 10 indicadores")
                return 10
            elif escolha == '2':
                print(f"\n✅ Selecionado: TOP 15 indicadores")
                return 15
            elif escolha == '0' and permitir_cancelar:
                print(f"\n⚠️  Cancelado - usando universo completo")
                return None
            else:
                opcoes = "1, 2" + (", 0" if permitir_cancelar else "")
                print(f"❌ Opção inválida! Escolha: {opcoes}")
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Operação cancelada pelo usuário")
            return None
        except Exception as e:
            print(f"❌ Erro: {e}")


def gerar_relatorio_universo(
    resultado: Dict[str, Any],
    arquivo: str
) -> None:
    """
    Gera relatório do universo reduzido em arquivo texto.
    
    Args:
        resultado: Dicionário com dados do universo
        arquivo: Caminho do arquivo de saída
    """
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("UNIVERSO REDUZIDO - RELATÓRIO DE SELEÇÃO\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"20 Números Selecionados:\n")
        f.write(f"{'-'.join(f'{n:02d}' for n in resultado['numeros'])}\n\n")
        
        f.write("Scores Individuais:\n")
        f.write("-"*70 + "\n")
        f.write(f"{'#':<4} {'Número':<8} {'Score':<10}\n")
        f.write("-"*70 + "\n")
        
        for i, num in enumerate(resultado['numeros'], 1):
            score = resultado['scores'][num]
            f.write(f"{i:<4} {num:02d}       {score:>6.2f}\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write(f"VALIDAÇÃO HISTÓRICA ({resultado['janela_validacao']} jogos)\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Cobertura 6 números: {resultado['cobertura_6']:.1f}%\n")
        f.write(f"Cobertura 5+ números: {resultado['cobertura_5']:.1f}%\n")
        f.write(f"Cobertura 4+ números: {resultado['cobertura_4']:.1f}%\n")
        f.write(f"\nRecomendação: {resultado['recomendacao']}\n")
        
        f.write("\n" + "="*70 + "\n")


# Exports
__all__ = [
    'selecionar_universo_inteligente',
    'apresentar_universo_usuario',
    'solicitar_escolha_usuario',
    'gerar_relatorio_universo'
]


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando Seletor de Universo Inteligente...\n")
    
    import sys
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(PROJECT_ROOT))
    
    from src.core.config import ARQUIVO_HISTORICO, RESULTADO_DIR
    
    # Carregar histórico
    df_historico = pd.read_excel(str(ARQUIVO_HISTORICO), sheet_name='MEGA SENA')
    print(f"✅ {len(df_historico)} sorteios carregados")
    
    # Ranking de teste
    ranking_teste = [
        {'indicador': f'Ind{i}', 'relevancia': 100-i*5}
        for i in range(1, 43)
    ]
    
    # Selecionar universo
    resultado = selecionar_universo_inteligente(
        df_historico,
        ranking_teste,
        janela_analise=100,
        janela_validacao=100,
        verbose=True
    )
    
    # Apresentar ao usuário
    apresentar_universo_usuario(resultado, verbose=True)
    
    # Gerar relatório
    arquivo = RESULTADO_DIR / "teste_universo_reduzido.txt"
    gerar_relatorio_universo(resultado, str(arquivo))
    print(f"✅ Relatório salvo em: {arquivo}")
    
    print("\n✅ Seletor funcionando corretamente!\n")
