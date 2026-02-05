"""
[CONTINUAÇÃO] Validador Retroativo Expandido - MegaCLI v6.1
Função principal de execução e integração
"""

# (Continação do validador_retroativo_v2.py)

# Adicionar imports para a segunda parte
from src.validacao.valid ador_retroativo import (
    ler_ultimo_sorteio,
    extrair_previsoes_excel,
    extrair_ranking_indicadores
)
from src.validacao.analisador_grupos_indicadores import analisar_grupos_indicadores


# ============================================================================
# FUNÇÃO PRINCIPAL DE EXECUÇÃO
# ============================================================================

def executar_validacao_completa_v2(n_ultimos_sorteios: int = 5, usar_ia: bool = True, analisar_grupos: bool = False) -> Dict[str, Any]:
    """
    Função principal que orquestra toda a validação retroativa expandida.
    
    Args:
        n_ultimos_sorteios: Número de últimos sorteios a analisar
        usar_ia: Se True, consulta IA para análise de indicadores
        analisar_grupos: Se True, executa análise combinatória de grupos
        
    Returns:
        Dicionário com resultado completo da validação
    """
    print("\\n" + "="*80)
    print("🚀 VALIDAÇÃO RETROATIVA INTELIGENTE v2.0")
    print("="*80 + "\\n")
    
    try:
        # 1. Ler dados
        print("📂 Passo 1: Lendo dados...")
        df_sorteios, nome_arquivo = ler_ultimo_sorteio()
        df_ranking = extrair_ranking_indicadores()
        
        # Converter ranking para formato de lista de dicts
        ranking_list = []
        for _, row in df_ranking.iterrows():
            ranking_list.append({
                'indicador': row['Indicador'],
                'relevancia': row.get('Peso_Atual', row.get('Relevancia', 50.0))
            })
        
        print(f"   ✅ {len(df_sorteios)} sorteios carregados")
        print(f"   ✅ {len(ranking_list)} indicadores no ranking\\n")
        
        # 2. Processar últimos N sorteios
        print(f"🎯 Passo 2: Validando últimos {n_ultimos_sorteios} sorteios...\\n")
        
        resultados_validacao = []
        inicio = max(150, len(df_sorteios) - n_ultimos_sorteios)  # Margem para indicadores
        
        for i in range(inicio, len(df_sorteios)):
            concurso = df_sorteios.iloc[i]['Concurso']
            data = df_sorteios.iloc[i].get('Data Sorteio', df_sorteios.iloc[i].get('Data', 'N/A'))
            
            # Extrair números sorteados
            numeros_sorteados = [int(df_sorteios.iloc[i][f'Bola{k}']) for k in range(1, 7)]
            
            print(f"   📍 Concurso {concurso} ({data})")
            print(f"      Números: {'-'.join(f'{n:02d}' for n in sorted(numeros_sorteados))}")
            
            # Histórico até este sorteio
            df_historico_ate_sorteio = df_sorteios.iloc[:i]
            
            # 2.1 Validação multi-nível
            validacao = validar_multi_nivel(numeros_sorteados, df_historico_ate_sorteio, ranking_list)
            
            print(f"      ✅ TOP 30: {validacao['top_30']['acertos']}/6 acertos")
            print(f"      ✅ TOP 9: {validacao['top_9']['acertos']}/6 acertos")
            
            resultado_sorteio = {
                'concurso': concurso,
                'data': str(data),
                'numeros_sorteados': numeros_sorteados,
                'validacao': validacao
            }
            
            # 2.2 Consultar IA (se habilitado e não acertou 100%)
            if usar_ia and validacao['top_30']['acertos'] < 6:
                sugestoes = consultar_ia_analise_retroativa(
                    concurso,
                    numeros_sorteados,
                    validacao,
                    ranking_list
                )
                
                if sugestoes:
                    resultado_sorteio['ia_sugestoes'] = sugestoes
                    
                    # 2.3 Reavaliar com IA
                    reavaliacao = reavaliar_com_ia(
                        numeros_sorteados,
                        df_historico_ate_sorteio,
                        ranking_list,
                        sugestoes
                    )
                    
                    resultado_sorteio['reavaliacao'] = reavaliacao
                    
                    melhoria = reavaliacao['acertos_top_30_ia'] - validacao['top_30']['acertos']
                    if melhoria > 0:
                        print(f"      🌟 Com IA: +{melhoria} acertos! ({reavaliacao['acertos_top_30_ia']}/6)")
                    elif melhoria < 0:
                        print(f"      ⚠️  Com IA: {melhoria} acertos ({reavaliacao['acertos_top_30_ia']}/6)")
                    else:
                        print(f"      ➡️  Com IA: mesmo resultado ({reavaliacao['acertos_top_30_ia']}/6)")
            
            resultados_validacao.append(resultado_sorteio)
            print()
        
        # 3. Análise de grupos (se habilitado)
        melhores_grupos = None
        if analisar_grupos:
            print("\\n🔬 Passo 3: Analisando grupos de indicadores...")
            melhores_grupos = analisar_grupos_indicadores(
                df_sorteios,
                ranking_list,
                tamanho_grupo=5,
                n_jogos_teste=min(50, len(df_sorteios) // 2)
            )
            
            print("\\n📊 Top 5 Melhores Grupos de Indicadores:")
            for i, grupo in enumerate(melhores_grupos[:5], 1):
                print(f"   {i}. Taxa: {grupo['taxa_acerto_top30']*100:.1f}% - {', '.join(grupo['grupo'])}")
        
        # 4. Atualizar Excel
        print("\\n💾 Passo 4: Atualizando Excel...")
        atualizar_excel_validacao(resultados_validacao)
        
        # 5. Gerar relatório final
        print("\\n" + "="*80)
        print("📈 RESUMO DA VALIDAÇÃO")
        print("="*80)
        
        total_analisados = len(resultados_validacao)
        acertos_30 = [r['validacao']['top_30']['acertos'] for r in resultados_validacao]
        acertos_9 = [r['validacao']['top_9']['acertos'] for r in resultados_validacao]
        
        print(f"\\nSorteios analisados: {total_analisados}")
        print(f"\\nTOP 30:")
        print(f"   • Média de acertos: {np.mean(acertos_30):.2f}/6")
        print(f"   • Taxa 4+ acertos: {sum(a >= 4 for a in acertos_30)/total_analisados*100:.1f}%")
        print(f"\\nTOP 9:")
        print(f"   • Média de acertos: {np.mean(acertos_9):.2f}/6")
        print(f"   • Taxa 3+ acertos: {sum(a >= 3 for a in acertos_9)/total_analisados*100:.1f}%")
        
        if usar_ia:
            melhorias = [r.get('reavaliacao', {}).get('acertos_top_30_ia', r['validacao']['top_30']['acertos']) - r['validacao']['top_30']['acertos'] 
                         for r in resultados_validacao]
            print(f"\\n🤖 IA:")
            print(f"   • Melhoria média: {np.mean([m for m in melhorias if m != 0]):.2f} números")
            print(f"   • Jogos melhorados: {sum(m > 0 for m in melhorias)}/{total_analisados}")
        
        print("\\n" + "="*80)
        print("✅ Validação concluída com sucesso!")
        print("="*80 + "\\n")
        
        analise_completa = {
            'timestamp': datetime.now().isoformat(),
            'arquivo_sorteios': nome_arquivo,
            'n_sorteios_analisados': total_analisados,
            'resultados': resultados_validacao,
            'melhores_grupos': melhores_grupos,
            'resumo': {
                'media_acertos_top30': np.mean(acertos_30),
                'media_acertos_top9': np.mean(acertos_9),
                'taxa_sucesso_top30': sum(a >= 4 for a in acertos_30)/total_analisados,
                'melhorias_ia': melhorias if usar_ia else []
            }
        }
        
        # Salvar JSON
        arquivo_json = RESULTADO_DIR / 'validacao_retroativa' / f'analise_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        arquivo_json.parent.mkdir(exist_ok=True)
        
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(analise_completa, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📁 Análise detalhada salva em: {arquivo_json.name}\\n")
        
        return analise_completa
        
    except Exception as e:
        print(f"\\n❌ Erro durante validação: {e}")
        import traceback
        traceback.print_exc()
        return None


# Exports
__all__ = [
    'validar_multi_nivel',
    'consultar_ia_analise_retroativa',
    'reavaliar_com_ia',
    'atualizar_excel_validacao',
    'executar_validacao_completa_v2'
]


# Teste standalone
if __name__ == "__main__":
    print("\\n🧪 Testando Validador Retroativo v2.0...\\n")
    resultado = executar_validacao_completa_v2(
        n_ultimos_sorteios=3,
        usar_ia=True,
        analisar_grupos=False
    )
    
    if resultado:
        print("\\n✅ Teste concluído com sucesso!")
    else:
        print("\\n❌ Erro no teste!")
