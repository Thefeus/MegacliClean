"""
Análise Reversa de Diferenças - MegaCLI
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import sys
from pathlib import Path
from colorama import Fore, Style
import time

# Imports do projeto
from src.core.config import ARQUIVO_HISTORICO, RESULTADO_DIR
from src.core.conexao_ia import conectar_ia

class AnaliseReversa:
    def __init__(self):
        self.df_historico = None
        self.df_diffs = None
        self.llm = None
        
    def carregar_dados(self) -> bool:
        """Carrega e prepara os dados históricos."""
        try:
            print(f"{Fore.CYAN}📂 Carregando histórico...{Style.RESET_ALL}")
            if not ARQUIVO_HISTORICO.exists():
                print(f"{Fore.RED}❌ Arquivo histórico não encontrado: {ARQUIVO_HISTORICO}{Style.RESET_ALL}")
                return False
                
            self.df_historico = pd.read_excel(ARQUIVO_HISTORICO, sheet_name='MEGA SENA')
            
            # Ordenar reverso (mais recente primeiro)
            self.df_historico.sort_values(by='Concurso', ascending=False, inplace=True)
            self.df_historico.reset_index(drop=True, inplace=True)
            
            print(f"{Fore.GREEN}✅ {len(self.df_historico)} sorteios carregados.{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Erro ao carregar dados: {e}{Style.RESET_ALL}")
            return False
            
    def calcular_diferencas(self):
        """Calcula diferenças reversas (Jogo N - Jogo N-1)."""
        print(f"\n{Fore.CYAN}🧮 Calculando diferenças entre sorteios consecutivos...{Style.RESET_ALL}")
        
        diffs = []
        
        # Iterar do mais recente para o antigo
        # df_historico[0] é o mais recente
        # df_historico[i] vs df_historico[i+1] (que é o anterior cronologicamente)
        
        for i in range(len(self.df_historico) - 1):
            jogo_atual = self.df_historico.iloc[i]
            jogo_anterior = self.df_historico.iloc[i+1] # Jogo cronologicamente anterior
            
            diff_row = {
                'Concurso_Atual': int(jogo_atual['Concurso']),
                'Concurso_Anterior': int(jogo_anterior['Concurso']),
                'Data_Atual': jogo_atual['Data do Sorteio']
            }
            
            # Calcular diferenças bola a bola (assumindo bolas ordenadas)
            numeros_atual = sorted([jogo_atual[f'Bola{k}'] for k in range(1, 7)])
            numeros_anterior = sorted([jogo_anterior[f'Bola{k}'] for k in range(1, 7)])
            
            diff_soma = 0
            diff_abs_total = 0
            
            for k in range(6):
                col = f'Bola{k+1}'
                # Diferença simples: Atual - Anterior
                d = numeros_atual[k] - numeros_anterior[k]
                diff_row[f'Diff_{col}'] = d
                diff_soma += d
                diff_abs_total += abs(d)
                
            diff_row['Diff_Soma_Geral'] = diff_soma
            diff_row['Diff_Absoluta_Total'] = diff_abs_total
            
            # Adicionar também as bolas originais para contexto
            for k in range(6):
                diff_row[f'Num_{k+1}'] = numeros_atual[k]
                
            diffs.append(diff_row)
            
        self.df_diffs = pd.DataFrame(diffs)
        print(f"{Fore.GREEN}✅ Diferenças calculadas para {len(self.df_diffs)} pares de jogos.{Style.RESET_ALL}")
        
    def analisar_com_ia(self, n_amostra: int = 50) -> str:
        """Envia lote de diferenças para análise de padrão da IA."""
        if self.df_diffs is None:
            return "Erro: Diferenças não calculadas."
            
        # Pegar amostra mais recente
        amostra = self.df_diffs.head(n_amostra)
        
        # Formatar prompt
        dados_analise = amostra[[
            'Concurso_Atual', 
            'Diff_Bola1', 'Diff_Bola2', 'Diff_Bola3', 
            'Diff_Bola4', 'Diff_Bola5', 'Diff_Bola6',
            'Diff_Soma_Geral'
        ]].to_string(index=False)
        
        prompt = f"""
        Você é um especialista matemático em padrões de loteria.
        Analise a tabela abaixo que mostra a DIFERENÇA entre os números sorteados de um concurso para o anterior (Jogo Atual - Jogo Anterior).
        Os dados estão em ordem cronológica reversa (topo = mais recente).

        DADOS (Últimos {n_amostra} jogos):
        {dados_analise}

        TAREFA:
        1. Identifique se existe algum padrão consistente nas diferenças (ex: sempre oscila entre -5 e +5?).
        2. Existe alguma "inércia" (números tendem a subir ou descer em conjunto)?
        3. Identifique anomalias recentes.
        4. Sugira uma tendência para o PRÓXIMO sorteio baseada na diferença média recente.

        Responda de forma concisa e direta, focando em insights acionáveis.
        """
        
        try:
            print(f"\n{Fore.CYAN}🤖 Consultando IA sobre padrões (Amostra: {n_amostra} jogos)...{Style.RESET_ALL}")
            if self.llm is None:
                self.llm = conectar_ia(verbose=False)
                if not self.llm:
                    return "Erro: Não foi possível conectar à IA."
            
            resposta = self.llm.invoke(prompt)
            return resposta.content
            
        except Exception as e:
            return f"Erro na análise IA: {e}"

    def exportar_resultado(self):
        """Salva a análise em nova aba do Excel mestre."""
        try:
            print(f"\n{Fore.CYAN}💾 Salvando aba ANALISE_REVERSA_DIFF...{Style.RESET_ALL}")
            
            from openpyxl import load_workbook
            
            path = str(ARQUIVO_HISTORICO)
            
            # Carregar workbook existente
            with pd.ExcelWriter(path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                self.df_diffs.to_excel(writer, sheet_name='ANALISE_REVERSA_DIFF', index=False)
                
            print(f"{Fore.GREEN}✅ Aba atualizada com sucesso em: {ARQUIVO_HISTORICO}{Style.RESET_ALL}")
            
        except Exception as e:
             # Fallback para PermissionError
             print(f"{Fore.RED}❌ Erro ao salvar (Arquivo aberto?): {e}{Style.RESET_ALL}")
             print(f"{Fore.YELLOW}   Tentando salvar em arquivo separado...{Style.RESET_ALL}")
             try:
                 backup_file = RESULTADO_DIR / f'ANALISE_REVERSA_BACKUP_{int(time.time())}.xlsx'
                 self.df_diffs.to_excel(backup_file, index=False)
                 print(f"{Fore.GREEN}✅ Salvo em backup: {backup_file}{Style.RESET_ALL}")
             except Exception as e2:
                 print(f"{Fore.RED}❌ Falha total no salvamento: {e2}{Style.RESET_ALL}")

    def gerar_previsao_reversa(self):
        """
        Gera previsões avançadas (10 Jogos) com base em padrões de diferença
        e valida retroativamente contra 100/500/1000 sorteios.
        """
        if self.df_diffs is None:
            print("Erro: Diferenças não calculadas.")
            return

        # Importar validador sob demanda
        try:
            from src.validacao.validador_1000_jogos import validar_jogos_historico
        except ImportError:
            print(f"{Fore.RED}❌ Erro: Módulo de validação não encontrado.{Style.RESET_ALL}")
            return

        # 1. Preparar dados para o prompt (Últimos 20 jogos)
        n_amostra = 20
        amostra = self.df_diffs.head(n_amostra)
        
        dados_analise = amostra[[
            'Concurso_Atual', 
            'Diff_Bola1', 'Diff_Bola2', 'Diff_Bola3', 
            'Diff_Bola4', 'Diff_Bola5', 'Diff_Bola6'
        ]].to_string(index=False)
        
        ultimo_jogo = self.df_historico.iloc[0]
        numeros_base = sorted([ultimo_jogo[f'Bola{k}'] for k in range(1, 7)])
        
        prompt = f"""
        ATUE COMO UM ESPECIALISTA EM SÉRIES TEMPORAIS DE LOTERIA.

        Tabela de DIFERENÇAS (Jogo Atual - Jogo Anterior) dos últimos {n_amostra} jogos:
        {dados_analise}

        SEU OBJETIVO:
        Identificar padrões de oscilação e gerar 3 CENÁRIOS de Diferenças (Deltas) para o próximo jogo.

        CENÁRIOS:
        1. CONSERVADOR: Segue a média das últimas 5 diferenças.
        2. MODERADO: Segue a tendência de inversão (se subiu, agora desce).
        3. AGRESSIVO: Tenta antecipar quebras de padrão (deltas maiores).

        FORMATO DE RESPOSTA (JSON):
        {{
            "analise": "Resumo dos padrões",
            "cenarios": [
                {{ "tipo": "Conservador", "deltas": [d1, d2, d3, d4, d5, d6] }},
                {{ "tipo": "Moderado", "deltas": [d1, d2, d3, d4, d5, d6] }},
                {{ "tipo": "Agressivo", "deltas": [d1, d2, d3, d4, d5, d6] }}
            ]
        }}
        """
        
        try:
            print(f"\n{Fore.CYAN}🔮 IA Analisando Múltiplos Cenários...{Style.RESET_ALL}")
            if self.llm is None:
                self.llm = conectar_ia(verbose=False)
            
            resposta = self.llm.invoke(prompt)
            raw_content = resposta.content
            
            import json
            import re
            
            # Tentar extrair JSON com regex
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            
            if json_match:
                conteudo = json_match.group(0)
                try:
                    dados = json.loads(conteudo)
                except json.JSONDecodeError:
                    # Fallback: tentar limpar markdown se o regex pegou algo sujo
                    conteudo = conteudo.replace("```json", "").replace("```", "").strip()
                    dados = json.loads(conteudo)
            else:
                # Fallback legado
                conteudo = raw_content.replace("```json", "").replace("```", "").strip()
                dados = json.loads(conteudo)
            
            cenarios = dados.get("cenarios", [])
            
            if not cenarios:
                print(f"{Fore.RED}❌ Nenhuma cenário gerado.{Style.RESET_ALL}")
                return

            print(f"\n{Fore.YELLOW}💡 Análise IA: {dados.get('analise', '...')}{Style.RESET_ALL}")

            # 2. Gerar 10 Jogos (Derivados dos 3 cenários + Variações)
            jogos_candidatos = []
            
            # Helper para aplicar delta e corrigir limites
            def aplicar_delta(base, deltas):
                nums = []
                for i, d in enumerate(deltas):
                    novo = base[i] + d
                    if novo > 60: novo = novo % 60
                    if novo == 0: novo = 60
                    elif novo < 1: novo = 60 + (novo % 60)
                    nums.append(int(novo))
                return sorted(list(set(nums))) # Remove duplicados iniciais

            # Helper para completar jogo
            def completar_jogo(nums):
                while len(nums) < 6:
                    c = (nums[-1] % 60) + 1
                    while c in nums:
                        c = (c % 60) + 1
                    nums.append(c)
                return sorted(nums)

            # A. Adicionar os 3 cenários puros
            for cenario in cenarios:
                nums = aplicar_delta(numeros_base, cenario['deltas'])
                nums = completar_jogo(nums)
                jogos_candidatos.append({
                    'numeros': nums,
                    'origem': f"IA_{cenario['tipo']}"
                })

            # B. Gerar variações (Perturbações leves nos Moderados e Conservadores)
            # Objetivo: Chegar a 10 jogos
            import random
            while len(jogos_candidatos) < 10:
                base_scenario = random.choice(cenarios)
                deltas_var = base_scenario['deltas'].copy()
                
                # Perturbar 1 ou 2 posições
                idx_alt = random.sample(range(6), k=random.randint(1, 2))
                for idx in idx_alt:
                    deltas_var[idx] += random.choice([-1, 1]) # Pequeno ajuste
                
                nums = aplicar_delta(numeros_base, deltas_var)
                nums = completar_jogo(nums)
                
                # Evitar duplicatas exatas de jogos
                if not any(j['numeros'] == nums for j in jogos_candidatos):
                    jogos_candidatos.append({
                        'numeros': nums,
                        'origem': f"Var_{base_scenario['tipo']}"
                    })

            print(f"\n{Fore.CYAN}🔎 Validando {len(jogos_candidatos)} jogos gerados (Retro-Validação)...{Style.RESET_ALL}")
            
            # 3. Validar Jogos (100, 500, 1000)
            # Estrutura para validar_jogos_historico requer lista de dicts com 'numeros' e 'rank'/'score'
            lista_para_validacao = []
            for i, jogo in enumerate(jogos_candidatos):
                lista_para_validacao.append({
                    'rank': i+1,
                    'numeros': jogo['numeros'],
                    'score': 0, # Placeholder
                    'origem': jogo['origem']
                })

            # Validar 1000 (que engloba tudo, mas o validador divide em 500/500).
            # Para validar especificamente 100, teríamos que rodar separado ou adaptar o validador.
            # O usuário pediu "validar se os 100, 500 e 1000 (...) estão coerentes".
            # O validador atual faz 1000 top-down. Vamos usar ele e adicionar uma métrica customizada para 'Recente' (100).
            
            resultado_validacao = validar_jogos_historico(
                lista_para_validacao, 
                self.df_historico, 
                n_sorteios=1000, 
                verbose=False
            )
            
            df_res = resultado_validacao['resultados']
            
            # Adicionar coluna de score ponderado (Peso maior para consistência recente)
            # Recalcular acertos nos últimos 100 e 500 para desempate e demonstração
            print(f"{Fore.CYAN}   Calculando performance recente (100 e 500 jogos)...{Style.RESET_ALL}")
            
            df_100 = self.df_historico.head(100)
            df_500 = self.df_historico.head(500)
            
            scores_finais = []
            metrics_100 = []
            metrics_500 = []
            
            for idx, row in df_res.iterrows():
                nums = row['numeros']
                
                # Análise 100
                q_100 = 0
                qi_100 = 0
                for _, sorteio in df_100.iterrows():
                    s_nums = [sorteio[f'Bola{k}'] for k in range(1, 7)]
                    matches = len(set(nums) & set(s_nums))
                    if matches >= 4: q_100 += 1
                    if matches >= 5: qi_100 += 1

                # Análise 500
                q_500 = 0
                qi_500 = 0
                for _, sorteio in df_500.iterrows():
                    s_nums = [sorteio[f'Bola{k}'] for k in range(1, 7)]
                    matches = len(set(nums) & set(s_nums))
                    if matches >= 4: q_500 += 1
                    if matches >= 5: qi_500 += 1
                        
                # Score Customizado V7: 
                # (Quinas_1k * 5 + Quadras_1k * 1) + 
                # (Quinas_500 * 5 + Quadras_500 * 2) + 
                # (Quinas_100 * 10 + Quadras_100 * 5)
                # Foco em quem "acordou" recentemente
                score_v7 = (row['acertos_5'] * 5) + (row['acertos_4'] * 1) + \
                           (qi_500 * 5) + (q_500 * 2) + \
                           (qi_100 * 10) + (q_100 * 5)
                
                scores_finais.append(score_v7)
                metrics_100.append(f"{q_100}/{qi_100}")
                metrics_500.append(f"{q_500}/{qi_500}")
                
            df_res['Score_V7'] = scores_finais
            df_res['Recente_100'] = metrics_100
            df_res['Recente_500'] = metrics_500
            
            # Reintegrar origem
            df_res['Origem'] = [j['origem'] for j in lista_para_validacao]
            
            # Ordenar por Score V7
            df_res.sort_values(by='Score_V7', ascending=False, inplace=True)
            
            # Exibir Tabela
            print(f"\n{Fore.GREEN}🏆 TOP 10 PREVISÕES (VALIDAÇÃO 100/500/1000){Style.RESET_ALL}")
            print(f"{'Rank':<4} | {'Números':<20} | {'Origem':<15} | {'Score':<6} | {'1k(Q/Qi)':<9} | {'500(Q/Qi)':<9} | {'100(Q/Qi)':<9}")
            print("-" * 95)
            
            for i in range(len(df_res)):
                row = df_res.iloc[i]
                nums_str = str(row['numeros']).replace('[','').replace(']','').replace(',','-')
                hist_1k = f"{row['acertos_4']}/{row['acertos_5']}"
                
                print(f"{i+1:<4} | {nums_str:<20} | {row['Origem']:<15} | {row['Score_V7']:<6} | {hist_1k:<9} | {row['Recente_500']:<9} | {row['Recente_100']:<9}")

            print(f"\n{Fore.YELLOW}Legenda: Q=Quadras, Qi=Quinas (ex: 3/0 = 3 Quadras e 0 Quinas){Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erro na geração avançada: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}⚠️  Conteúdo bruto recebido da IA:{Style.RESET_ALL}")
            print(locals().get('raw_content', 'Não capturado'))
            import traceback
            traceback.print_exc()

def loop_interativo():
    """Loop principal da ferramenta."""
    analise = AnaliseReversa()
    
    if not analise.carregar_dados():
        return
        
    analise.calcular_diferencas()
    
    # Loop de refinamento
    while True:
        print(f"\n{Fore.YELLOW}=== OPÇÕES DE ANÁLISE REVERSA ==={Style.RESET_ALL}")
        print("1. 🤖 Analisar Padrões com IA (Últimos 50)")
        print("2. 🤖 Analisar Padrões com IA (Últimos 100)")
        print("3. 💾 Exportar Dados para Excel")
        print("4. 🔮 Gerar 10 Jogos Validados (IA + Histórico)")
        print("0. 🔙 Voltar")
        
        op = input(f"\n{Fore.CYAN}Escolha: {Style.RESET_ALL}")
        
        if op == '0':
            break
        elif op == '1':
            insight = analise.analisar_com_ia(50)
            print(f"\n{Fore.GREEN}💡 INSIGHTS IA:{Style.RESET_ALL}\n")
            print(insight)
            input("\n[Enter] para continuar...")
        elif op == '2':
            insight = analise.analisar_com_ia(100)
            print(f"\n{Fore.GREEN}💡 INSIGHTS IA (+Histórico):{Style.RESET_ALL}\n")
            print(insight)
            input("\n[Enter] para continuar...") 
        elif op == '3':
            analise.exportar_resultado()
            input("\n[Enter] para continuar...")
        elif op == '4':
            analise.gerar_previsao_reversa()
            input("\n[Enter] para continuar...")
            
if __name__ == "__main__":
    from colorama import init
    init()
    loop_interativo()
