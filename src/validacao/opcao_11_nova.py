"""
Nova implementação da opcao_11 para menu_interativo.py
Copie esta função para substituir a atual
"""

def opcao_11_validacao_retroativa(df_historico: pd.DataFrame):
    """Opção 11: Validação Retroativa e Auto-Aprendizado v2.0."""
    limpar_tela()
    exibir_banner()
    
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"OPÇÃO 11: VALIDAÇÃO RETROATIVA E AUTO-APRENDIZADO v2.0")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}🔍 Esta função irá:{Style.RESET_ALL}\n")
    print(f"   1. Ler últimos sorteios da Mega-Sena (Dados/)")
    print(f"   2. Validar previsões em 4 níveis (TOP 30, 20, 10, 9)")
    print(f"   3. Calcular taxa de acerto detalhada")
    print(f"   4. {Fore.GREEN}[NOVO]{Style.RESET_ALL} Consultar IA para identificar melhores indicadores")
    print(f"   5. {Fore.GREEN}[NOVO]{Style.RESET_ALL} Reavaliar: 'E se tivéssemos usado os indicadores da IA?'")
    print(f"   6. {Fore.GREEN}[NOVO]{Style.RESET_ALL} Analisar grupos de indicadores ótimos")
    print(f"   7. Atualizar Excel com resultados (aba VALIDACAO_RETROATIVA)")
    print(f"   8. Ajustar pesos automaticamente para próximas previsões\n")
    
    print(f"{Fore.CYAN}📊 Novidades v2.0:{Style.RESET_ALL}")
    print(f"   • Validação multi-nível automática")
    print(f"   • IA analisa cada sorteio e sugere melhorias")
    print(f"   • Sistema testa se com IA teria acertado 100%")
    print(f"   • Identifica melhores combinações de indicadores\n")
    
    confirmar = input(f"{Fore.CYAN}Deseja continuar? (s/n): {Style.RESET_ALL}").strip().lower()
    
    if confirmar != 's':
        print(f"\n{Fore.YELLOW}⚠️  Operação cancelada{Style.RESET_ALL}")
        input(f"\n{Fore.CYAN}Pressione ENTER para continuar...{Style.RESET_ALL}")
        return
    
    # Perguntar quantos sorteios analisar
    print(f"\n{Fore.CYAN}Quantos sorteios deseja analisar?{Style.RESET_ALL}")
    print(f"   Recomendação: 3-5 para análise rápida com IA")
    
    try:
        n_sorteios = int(input(f"{Fore.CYAN}Número de sorteios (padrão: 3): {Style.RESET_ALL}") or "3")
        n_sorteios = max(1, min(20, n_sorteios))
    except ValueError:
        n_sorteios = 3
        print(f"{Fore.YELLOW}⚠️  Valor inválido, usando padrão: 3{Style.RESET_ALL}")
    
    # Perguntar sobre IA
    print(f"\n{Fore.CYAN}Deseja usar IA para análise retroativa?{Style.RESET_ALL}")
    print(f"   (A IA identificará quais indicadores teriam dado melhor resultado)")
    usar_ia_input = input(f"{Fore.CYAN}Usar IA? (s/n, padrão: s): {Style.RESET_ALL}").strip().lower()
    usar_ia = usar_ia_input != 'n'
    
    # Perguntar sobre análise de grupos
    analisar_grupos = False
    if usar_ia and n_sorteios <= 5:
        print(f"\n{Fore.CYAN}Deseja analisar grupos de indicadores?{Style.RESET_ALL}")
        print(f"   (Identifica melhores combinações - pode demorar alguns minutos)")
        grupos_input = input(f"{Fore.CYAN}Analisar grupos? (s/n, padrão: n): {Style.RESET_ALL}").strip().lower()
        analisar_grupos = grupos_input == 's'
    
    # Executar validação
    try:
        print(f"\n{Fore.CYAN}⚙️  Executando validação retroativa v2.0...{Style.RESET_ALL}\n")
        
        # Tentar importar validador v2
        try:
            from src.validacao.validador_retroativo_v2_completo import executar_validacao_completa_v2
            versao_v2 = True
        except ImportError:
            print(f"{Fore.YELLOW}⚠️  Validador v2 não encontrado, usando v1...{Style.RESET_ALL}\n")
            from src.validacao.validador_retroativo import executar_validacao_completa
            versao_v2 = False
        
        if versao_v2:
            # Executar v2
            resultado = executar_validacao_completa_v2(
                n_ultimos_sorteios=n_sorteios,
                usar_ia=usar_ia,
                analisar_grupos=analisar_grupos
            )
        else:
            # Fallback v1
            resultado = executar_validacao_completa(n_ultimos_sorteios=n_sorteios)
        
        if resultado:
            print(f"\n{Fore.GREEN}{'='*70}")
            print(f"✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
            print(f"{'='*70}{Style.RESET_ALL}\n")
            
            if versao_v2 and usar_ia:
                # Mostrar insights da IA
                melhorias = resultado.get('resumo', {}).get('melhorias_ia', [])
                if melhorias:
                    jogos_melhorados = sum(1 for m in melhorias if m > 0)
                    print(f"{Fore.CYAN}🤖 Análise com IA:{Style.RESET_ALL}")
                    print(f"   • Jogos melhorados: {jogos_melhorados}/{n_sorteios}")
                    if any(m > 0 for m in melhorias):
                        print(f"   • Melhoria média: +{np.mean([m for m in melhorias if m > 0]):.2f} números\n")
                
                if analisar_grupos:
                    grupos = resultado.get('melhores_grupos', [])
                    if grupos:
                        melhor = grupos[0]
                        print(f"{Fore.CYAN}🔬 Melhor Grupo Encontrado:{Style.RESET_ALL}")
                        print(f"   • Taxa: {melhor['taxa_acerto_top30']*100:.1f}%")
                        print(f"   • {', '.join(melhor['grupo'])}\n")
        else:
            print(f"\n{Fore.RED}❌ ERRO NA VALIDAÇÃO{Style.RESET_ALL}\n")
    
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro: {e}{Style.RESET_ALL}\n")
        import traceback
        traceback.print_exc()
    
    input(f"\n{Fore.CYAN}Pressione ENTER para continuar...{Style.RESET_ALL}")
