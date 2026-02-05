"""
Script de Reorganização do Projeto MegaCLI

Estrutura nova:
- /doc/                    # Documentos antigos
- /src/                    # Códigos Python organizados
  - /analise/              # Scripts de análise
  - /previsao/             # Scripts de previsão
  - /validacao/            # Scripts de validação
  - /utils/                # Utilitários
- /Resultado/              # Planilhas e resultados
- /                        # Root: apenas docs principais
"""

import os
import shutil
from pathlib import Path

print("="*130)
print("REORGANIZAÇÃO DO PROJETO MegaCLI")
print("="*130)
print()

BASE = Path("d:/MegaCLI")

# ============================================================================
# CRIAR ESTRUTURA DE PASTAS
# ============================================================================

print("📁 Criando estrutura de pastas...")

pastas = [
    "doc",
    "doc/analises_antigas",
    "src/analise",
    "src/previsao", 
    "src/validacao",
    "src/utils",
]

for pasta in pastas:
    path = BASE / pasta
    path.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ {pasta}")

print()

# ============================================================================
# MAPEAMENTO DE ARQUIVOS
# ============================================================================

print("📋 Mapeando arquivos para reorganização...")
print()

# Documentos - manter na raiz
DOCS_PRINCIPAIS = [
    "README.md",
    "ANALISE_IA_REFINAMENTO.md",
]

# Documentos - mover para doc/
DOCS_ANTIGOS = [
    "ANALISE_MEGA_FINAL_2025.md",
    "ANALISE_COMPLEMENTAR_AVANCADA.md",
    "RESUMO_MEGA_FINAL_V2.md",
]

# Scripts Python - reorganizar em src/
SCRIPTS_ANALISE = [
    "analise_historico_completo.py",
    "analise_complementar_avancada.py",
]

SCRIPTS_PREVISAO = [
    "gerar_previsao_baseada_em_padroes.py",
    "gerar_previsao_avancada_percentual.py",
    "organizar_e_prever_final.py",
]

SCRIPTS_VALIDACAO = [
    "validacao_progressiva.py",
    "validacao_progressiva_refinada.py",
    "validacao_multi_indicadores.py",
    "validacao_refinada_ia.py",
    "refinamento_iterativo.py",
]

SCRIPTS_UTILS = [
    "analise_mega_final_2025.py",
    "executar_analise_completa.py",
    "consultar_ia_refinamento.py",
    "refinar_previsoes_com_aprendizado.py",
]

# Resultados
RESULTADO_FILES = [
    "ANALISE_HISTORICO_COMPLETO.xlsx",
    "DESDOBRAMENTO_AVANCADO_2025.xlsx",
    "DESDOBRAMENTO_2025_TEMP.xlsx",
]

# Arquivos temporários/obsoletos para doc
TEMP_FILES = [
    "PREVISAO_MEGA_FINAL_2025.txt",
]

# ============================================================================
# MOVER ARQUIVOS
# ============================================================================

print("🚚 Movendo arquivos...")
print()

movimentos = {
    # Docs antigos
    **{f: "doc/analises_antigas" for f in DOCS_ANTIGOS},
    **{f: "doc" for f in TEMP_FILES},
    
    # Scripts Python
    **{f: "src/analise" for f in SCRIPTS_ANALISE},
    **{f: "src/previsao" for f in SCRIPTS_PREVISAO},
    **{f: "src/validacao" for f in SCRIPTS_VALIDACAO},
    **{f: "src/utils" for f in SCRIPTS_UTILS},
    
    # Resultados
    **{f: "Resultado" for f in RESULTADO_FILES},
}

for arquivo, destino_pasta in movimentos.items():
    origem = BASE / arquivo
    destino_dir = BASE / destino_pasta
    destino = destino_dir / arquivo
    
    if origem.exists():
        try:
            # Se destino existe, fazer backup
            if destino.exists():
                backup = destino.with_suffix(destino.suffix + '.bak')
                shutil.move(str(destino), str(backup))
            
            shutil.move(str(origem), str(destino))
            print(f"   ✅ {arquivo:50s} → {destino_pasta}/")
        except Exception as e:
            print(f"   ⚠️  {arquivo:50s} → ERRO: {e}")
    else:
        print(f"   ⏭️  {arquivo:50s} → Não encontrado")

print()

# ============================================================================
# CRIAR ARQUIVO __init__.py
# ============================================================================

print("📝 Criando arquivos __init__.py...")

for pasta in ["src", "src/analise", "src/previsao", "src/validacao", "src/utils"]:
    init_file = BASE / pasta / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# -*- coding: utf-8 -*-\n")
        print(f"   ✅ {pasta}/__init__.py")

print()

# ============================================================================
# ATUALIZAR IMPORTS NOS SCRIPTS
# ============================================================================

print("🔧 Atualizando imports nos scripts...")
print()

# Função para atualizar imports
def atualizar_imports(arquivo_path):
    """Atualiza imports para nova estrutura"""
    if not arquivo_path.exists():
        return False
    
    conteudo = arquivo_path.read_text(encoding='utf-8')
    conteudo_original = conteudo
    
    # Atualizar caminho do Excel
    conteudo = conteudo.replace(
        "d:\\\\MegaCLI\\\\ANALISE_HISTORICO_COMPLETO.xlsx",
        "d:\\\\MegaCLI\\\\Resultado\\\\ANALISE_HISTORICO_COMPLETO.xlsx"
    )
    conteudo = conteudo.replace(
        "'ANALISE_HISTORICO_COMPLETO.xlsx'",
        "'../Resultado/ANALISE_HISTORICO_COMPLETO.xlsx'"
    )
    conteudo = conteudo.replace(
        '"ANALISE_HISTORICO_COMPLETO.xlsx"',
        '"../Resultado/ANALISE_HISTORICO_COMPLETO.xlsx"'
    )
    
    # Atualizar caminho do ANALISE_IA_REFINAMENTO.md
    conteudo = conteudo.replace(
        "d:\\\\MegaCLI\\\\ANALISE_IA_REFINAMENTO.md",
        "d:\\\\MegaCLI\\\\ANALISE_IA_REFINAMENTO.md"
    )
    
    if conteudo != conteudo_original:
        arquivo_path.write_text(conteudo, encoding='utf-8')
        return True
    return False

# Atualizar todos os scripts movidos
scripts_atualizados = 0
for categoria in [SCRIPTS_ANALISE, SCRIPTS_PREVISAO, SCRIPTS_VALIDACAO, SCRIPTS_UTILS]:
    for script in categoria:
        # Determinar pasta
        if script in SCRIPTS_ANALISE:
            pasta = "src/analise"
        elif script in SCRIPTS_PREVISAO:
            pasta = "src/previsao"
        elif script in SCRIPTS_VALIDACAO:
            pasta = "src/validacao"
        else:
            pasta = "src/utils"
        
        script_path = BASE / pasta / script
        if atualizar_imports(script_path):
            print(f"   ✅ {pasta}/{script}")
            scripts_atualizados += 1

if scripts_atualizados == 0:
    print("   ℹ️  Nenhum script precisou de atualização")

print()

# ============================================================================
# CRIAR README ATUALIZADO
# ============================================================================

print("📖 Criando README.md atualizado...")

readme_content = """# MegaCLI - Sistema Avançado de Análise da Mega-Sena

Sistema completo de análise estatística e previsão da Mega-Sena com IA e aprendizado adaptativo.

## 📊 Estrutura do Projeto

```
MegaCLI/
├── src/                          # Código fonte
│   ├── analise/                  # Scripts de análise histórica
│   ├── previsao/                 # Scripts de geração de previsões
│   ├── validacao/                # Scripts de validação e refinamento
│   └── utils/                    # Utilitários diversos
├── Resultado/                    # Planilhas geradas
│   └── ANALISE_HISTORICO_COMPLETO.xlsx
├── doc/                          # Documentação
│   └── analises_antigas/         # Análises anteriores
├── config/                       # Configurações
└── ANALISE_IA_REFINAMENTO.md    # Análise principal da IA

```

## 🎯 Funcionalidades

- ✅ Análise de 2.954 sorteios históricos
- ✅ 22 indicadores estatísticos
- ✅ Sistema de refinamento iterativo
- ✅ Pesos otimizados por IA (Google Gemini)
- ✅ Previsões para concurso 2955
- ✅ Validação progressiva com aprendizado

## 🚀 Como Usar

### 1. Gerar Análise Completa
```bash
python src/analise/analise_historico_completo.py
```

### 2. Validar com Indicadores
```bash
python src/validacao/validacao_multi_indicadores.py
```

### 3. Refinamento Iterativo
```bash
python src/validacao/refinamento_iterativo.py
```

### 4. Gerar Previsão Final
```bash
python src/previsao/organizar_e_prever_final.py
```

## 📈 Resultados

Todos os resultados são salvos em `Resultado/ANALISE_HISTORICO_COMPLETO.xlsx` com múltiplas abas:

- **PREVISÃO FINAL 2955** - 84 jogos otimizados
- **PESOS REFINADOS** - Pesos ajustados automaticamente
- **REFINAMENTO ITERATIVO** - Evolução das métricas
- **VALIDAÇÃO IA REFINADA** - Sistema com 22 indicadores
- **ANÁLISE IA** - Recomendações Google Gemini

## 🔧 Tecnologias

- Python 3.x
- Pandas, NumPy, OpenPyXL
- LangChain + Google Gemini AI
- Análise estatística avançada

## 📝 Licença

Projeto pessoal de análise estatística.
"""

readme_path = BASE / "README.md"
readme_path.write_text(readme_content, encoding='utf-8')
print("   ✅ README.md criado/atualizado")
print()

# ============================================================================
# RESUMO
# ============================================================================

print("="*130)
print("✅ REORGANIZAÇÃO CONCLUÍDA!")
print("="*130)
print()

print("📊 Resumo:")
print(f"   • Documentos principais na raiz: {len(DOCS_PRINCIPAIS)}")
print(f"   • Documentos movidos para doc/: {len(DOCS_ANTIGOS) + len(TEMP_FILES)}")
print(f"   • Scripts em src/analise: {len(SCRIPTS_ANALISE)}")
print(f"   • Scripts em src/previsao: {len(SCRIPTS_PREVISAO)}")
print(f"   • Scripts em src/validacao: {len(SCRIPTS_VALIDACAO)}")
print(f"   • Scripts em src/utils: {len(SCRIPTS_UTILS)}")
print(f"   • Resultados em Resultado/: {len(RESULTADO_FILES)}")
print(f"   • Scripts atualizados: {scripts_atualizados}")
print()

print("📁 Nova estrutura:")
print("   MegaCLI/")
print("   ├── src/")
print("   │   ├── analise/")
print("   │   ├── previsao/")
print("   │   ├── validacao/")
print("   │   └── utils/")
print("   ├── Resultado/")
print("   ├── doc/")
print("   │   └── analises_antigas/")
print("   └── README.md")
print()

print("🎯 Próximos passos:")
print("   1. Revisar a nova estrutura")
print("   2. Testar scripts na nova estrutura")
print("   3. Commitar mudanças no Git (se aplicável)")
