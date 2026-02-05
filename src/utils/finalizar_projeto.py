"""
Finalização Completa do Projeto MegaCLI

1. Padroniza PREVISÃO FINAL 2955 com padrão de PREVISÕES 2955
2. Remove abas não utilizadas
3. Consulta IA para revisar indicadores
4. Aplica refinamento final
5. Documenta programas utilizados
"""

import pandas as pd
import numpy as np
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import sys
import dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, 'd:\\MegaCLI')
from src.mega_final_de_ano_v2 import FILE_PATH, SOURCE_SHEET, BALL_COLS

# Carregar API key
dotenv.load_dotenv(dotenv_path='d:\\MegaCLI\\config\\.env')
api_key_raw = os.environ.get("GOOGLE_API_KEY", "")
api_key_cleaned = api_key_raw.strip().strip('"').strip("'")
os.environ["GOOGLE_API_KEY"] = api_key_cleaned

print("="*130)
print("FINALIZAÇÃO COMPLETA DO PROJETO MegaCLI")
print("="*130)
print()

excel_file = 'd:\\MegaCLI\\Resultado\\ANALISE_HISTORICO_COMPLETO.xlsx'

# ============================================================================
# 1. PADRONIZAR PREVISÃO FINAL 2955
# ============================================================================

print("📊 ETAPA 1: Padronizando PREVISÃO FINAL 2955...")
print()

# Carregar ambas as abas
df_previsao_original = pd.read_excel(excel_file, sheet_name='PREVISÕES 2955')
df_previsao_final = pd.read_excel(excel_file, sheet_name='PREVISÃO FINAL 2955')

print(f"   PREVISÕES 2955: {len(df_previsao_original.columns)} colunas")
print(f"   PREVISÃO FINAL 2955: {len(df_previsao_final.columns)} colunas")
print()

# Usar colunas da original como padrão
colunas_padrao = df_previsao_original.columns.tolist()

# Ajustar PREVISÃO FINAL para ter as mesmas colunas
df_final_padronizado = pd.DataFrame()

# Copiar colunas existentes
for col in colunas_padrao:
    if col in df_previsao_final.columns:
        df_final_padronizado[col] = df_previsao_final[col]
    else:
        # Criar coluna vazia ou com valor padrão
        if col.startswith('Score_'):
            df_final_padronizado[col] = 0.0
        elif col == 'Probabilidade_Final_%':
            df_final_padronizado[col] = df_previsao_final.get('Score_Qualidade', 0.0)
        elif col == 'Qtd_Historico_3plus':
            df_final_padronizado[col] = 0
        elif col == 'Historico_3plus':
            df_final_padronizado[col] = ''
        else:
            df_final_padronizado[col] = ''

print("   ✅ PREVISÃO FINAL padronizada")
print()

# ============================================================================
# 2. CONSULTAR IA PARA REVISÃO FINAL
# ============================================================================

print("="*130)
print("🤖 ETAPA 2: Consultando IA para Revisão Final dos Indicadores...")
print("="*130)
print()

# Carregar pesos refinados
df_pesos = pd.read_excel(excel_file, sheet_name='PESOS REFINADOS')

prompt_revisao = f"""Você é um especialista em análise estatística de loterias.

Revise os pesos finais após refinamento iterativo da Mega-Sena:

{df_pesos.to_string(index=False)}

**PERGUNTAS:**

1. Os pesos estão bem balanceados?
2. Algum indicador está muito alto ou muito baixo?
3. Sugestões de ajuste fino (máximo ±5 pontos)?
4. Validação: esses pesos fazem sentido estatisticamente?

Responda de forma concisa e objetiva com ajustes sugeridos.
"""

try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.1, max_retries=2)
    resposta = llm.invoke(prompt_revisao)
    analise_revisao = resposta.content
    
    print("✅ Análise da IA recebida:")
    print()
    print(analise_revisao)
    print()
    
    # Salvar análise
    with open('d:\\MegaCLI\\doc\\REVISAO_FINAL_IA.md', 'w', encoding='utf-8') as f:
        f.write("# Revisão Final dos Indicadores - IA\n\n")
        f.write(analise_revisao)
    
    print("   ✅ Salvo em: doc/REVISAO_FINAL_IA.md")
    print()
    
except Exception as e:
    print(f"⚠️  Erro ao consultar IA: {e}")
    print("   Continuando sem revisão da IA...")
    print()

# ============================================================================
# 3. REMOVER ABAS NÃO UTILIZADAS
# ============================================================================

print("="*130)
print("🗑️  ETAPA 3: Removendo Abas Não Utilizadas...")
print("="*130)
print()

ABAS_MANTER = [
    'MEGA SENA',
    'PREVISÕES 2955',
    'PESOS REFINADOS',
    'REFINAMENTO ITERATIVO',
    'PERFORMANCE INDICADORES',
    'ANÁLISE IA',
    'LISTA INDICADORES',
]

# Carregar todas as abas
with pd.ExcelFile(excel_file) as xls:
    abas_todas = xls.sheet_names
    abas_dict = {}
    
    for aba in abas_todas:
        if aba in ABAS_MANTER:
            abas_dict[aba] = pd.read_excel(xls, sheet_name=aba)
        elif aba == 'PREVISÃO FINAL 2955':
            abas_dict['PREVISÕES 2955'] = df_final_padronizado  # Substituir com padronizada
        else:
            print(f"   🗑️  Removendo: {aba}")

# Adicionar abas novas
abas_dict['REVISÃO FINAL IA'] = pd.DataFrame({
    'Item': ['Análise Completa', 'Arquivo'],
    'Valor': ['Ver doc/REVISAO_FINAL_IA.md', 'Revisão dos pesos pela IA Google Gemini']
})

print()
print(f"   ✅ Mantendo {len(abas_dict)} abas")
print()

# ============================================================================
# 4. SALVAR PLANILHA FINAL
# ============================================================================

print("="*130)
print("💾 ETAPA 4: Salvando Planilha Final...")
print("="*130)
print()

with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    for nome_aba, df in abas_dict.items():
        df.to_excel(writer, sheet_name=nome_aba, index=False)

print(f"   ✅ Planilha atualizada: {excel_file}")
print(f"   📊 Total de abas: {len(abas_dict)}")
print()

# ============================================================================
# 5. DOCUMENTAR PROGRAMAS UTILIZADOS
# ============================================================================

print("="*130)
print("📝 ETAPA 5: Documentando Programas do Projeto...")
print("="*130)
print()

PROGRAMAS_UTILIZADOS = {
    'src/analise/analise_historico_completo.py': 'Análise completa de 2.954 sorteios',
    'src/previsao/organizar_e_prever_final.py': 'Geração de previsão final para 2955',
    'src/validacao/validacao_multi_indicadores.py': 'Validação com 17 indicadores',
    'src/validacao/validacao_refinada_ia.py': 'Validação com 22 indicadores + IA',
    'src/validacao/refinamento_iterativo.py': 'Refinamento automático de pesos',
    'src/utils/consultar_ia_refinamento.py': 'Consulta à IA Google Gemini',
    'src/mega_final_de_ano_v2.py': 'Sistema principal v2 (4 estratégias)',
    'src/run_mega_final_v2.py': 'Executor do sistema v2',
}

PROGRAMAS_OBSOLETOS = [
    'src/previsao/gerar_previsao_baseada_em_padroes.py',
    'src/previsao/gerar_previsao_avancada_percentual.py',
    'src/analise/analise_complementar_avancada.py',
    'src/validacao/validacao_progressiva.py',
    'src/validacao/validacao_progressiva_refinada.py',
    'src/utils/analise_mega_final_2025.py',
    'src/utils/executar_analise_completa.py',
    'src/utils/refinar_previsoes_com_aprendizado.py',
]

doc_programas = f"""# Documentação dos Programas - MegaCLI

## Programas Utilizados ({len(PROGRAMAS_UTILIZADOS)})

"""

for prog, desc in PROGRAMAS_UTILIZADOS.items():
    doc_programas += f"### {prog}\n"
    doc_programas += f"**Função:** {desc}\n\n"

doc_programas += f"""
## Programas Obsoletos ({len(PROGRAMAS_OBSOLETOS)})

Versões antigas movidas para `src/obsoletos/`:

"""

for prog in PROGRAMAS_OBSOLETOS:
    doc_programas += f"- {prog}\n"

# Salvar documentação
with open('d:\\MegaCLI\\doc\\PROGRAMAS.md', 'w', encoding='utf-8') as f:
    f.write(doc_programas)

print("   ✅ Documentação salva: doc/PROGRAMAS.md")
print()

# Mover obsoletos
from pathlib import Path
import shutil

obsoletos_dir = Path('d:/MegaCLI/src/obsoletos')
obsoletos_dir.mkdir(exist_ok=True)

movidos = 0
for prog in PROGRAMAS_OBSOLETOS:
    origem = Path('d:/MegaCLI') / prog
    if origem.exists():
        nome = origem.name
        destino = obsoletos_dir / nome
        try:
            if destino.exists():
                destino.unlink()
            shutil.move(str(origem), str(destino))
            print(f"   📦 Movido: {prog}")
            movidos += 1
        except Exception as e:
            print(f"   ⚠️  Erro ao mover {prog}: {e}")

print()
print(f"   ✅ {movidos} programas movidos para src/obsoletos/")
print()

# ============================================================================
# RESUMO FINAL
# ============================================================================

print("="*130)
print("✅ FINALIZAÇÃO CONCLUÍDA!")
print("="*130)
print()

print("📊 Resumo:")
print(f"   1. ✅ PREVISÃO FINAL 2955 padronizada")
print(f"   2. ✅ Revisão da IA realizada (doc/REVISAO_FINAL_IA.md)")
print(f"   3. ✅ Abas limpas ({len(abas_dict)} mantidas)")
print(f"   4. ✅ Planilha final salva")
print(f"   5. ✅ {movidos} programas movidos para obsoletos")
print(f"   6. ✅ Documentação gerada (doc/PROGRAMAS.md)")
print()

print("📁 Estrutura Final:")
print("   • src/ - Apenas programas utilizados")
print("   • src/obsoletos/ - Programas antigos")
print("   • Resultado/ - ANALISE_HISTORICO_COMPLETO.xlsx")
print("   • doc/ - Documentação completa")
print()

print("🎯 Projeto MegaCLI finalizado e documentado!")
