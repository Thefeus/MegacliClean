"""
Mapeamento e Limpeza de Arquivos Python

Mapeia todos os .py na raiz e src/, identifica utilizados vs não utilizados,
e move os obsoletos para src/obsoletos/
"""

from pathlib import Path
import shutil
from datetime import datetime

print("="*130)
print("MAPEAMENTO E LIMPEZA DE ARQUIVOS PYTHON")
print("="*130)
print()

BASE = Path("d:/MegaCLI")

# ============================================================================
# 1. MAPEAR TODOS OS .PY
# ============================================================================

print("📋 Mapeando todos os arquivos .py...")
print()

# Raiz
py_raiz = list(BASE.glob("*.py"))
print(f"   Raiz: {len(py_raiz)} arquivos")

# src e subpastas (exceto obsoletos)
py_src = []
for pasta in ['src', 'src/analise', 'src/previsao', 'src/validacao', 'src/utils']:
    pasta_path = BASE / pasta
    if pasta_path.exists():
        arquivos = list(pasta_path.glob("*.py"))
        arquivos = [f for f in arquivos if '__init__' not in f.name and '__pycache__' not in str(f)]
        py_src.extend(arquivos)
        print(f"   {pasta}: {len(arquivos)} arquivos")

print()
print(f"   Total: {len(py_raiz) + len(py_src)} arquivos Python")
print()

# ============================================================================
# 2. DEFINIR PROGRAMAS UTILIZADOS
# ============================================================================

print("🔍 Identificando programas utilizados...")
print()

# Programas UTILIZADOS (núcleo do sistema)
UTILIZADOS_CORE = {
    # Sistema principal
    'mega_final_de_ano_v2.py': 'Sistema v2 com 4 estratégias',
    'run_mega_final_v2.py': 'Executor do sistema v2',
    'app_config.py': 'Configurações',
    
    # Análise
    'analise_historico_completo.py': 'Análise de 2.954 sorteios',
    
    # Previsão
    'organizar_e_prever_final.py': 'Previsão final para 2955',
    
    # Validação
    'validacao_multi_indicadores.py': 'Validação com 17 indicadores',
    'validacao_refinada_ia.py': 'Validação com 22 indicadores',
    'refinamento_iterativo.py': 'Refinamento automático',
    
    # Utils
    'consultar_ia_refinamento.py': 'Consulta à IA',
}

# Scripts de suporte/teste (podem ficar em src/)
UTILIZADOS_SUPORTE = {
    'utils.py',
    'feature_engineer.py',
    'advanced_ml.py',
}

# Scripts na raiz que são utilizados
RAIZ_UTILIZADOS = {
    'finalizar_projeto.py',
    'reorganizar_projeto.py',
    'limpar_documentos.py',
    'mapear_e_limpar_python.py',  # Este script
}

# ============================================================================
# 3. CLASSIFICAR ARQUIVOS
# ============================================================================

print("📊 Classificando arquivos...")
print()

utilizados = []
nao_utilizados = []

# Verificar raiz
for arquivo in py_raiz:
    if arquivo.name in RAIZ_UTILIZADOS or arquivo.name.startswith('test_'):
        print(f"   ✅ RAIZ (usado): {arquivo.name}")
        utilizados.append(arquivo)
    else:
        print(f"   ⚠️  RAIZ (não usado): {arquivo.name}")
        nao_utilizados.append(arquivo)

# Verificar src
for arquivo in py_src:
    rel_path = arquivo.relative_to(BASE / 'src')
    rel_str = str(rel_path).replace('\\', '/')
    
    is_used = False
    
    # Verificar se está na lista de utilizados
    if arquivo.name in UTILIZADOS_CORE.keys():
        is_used = True
    
    # Verificar se é arquivo de suporte
    if arquivo.name in UTILIZADOS_SUPORTE:
        is_used = True
    
    # Verificar se é teste
    if arquivo.name.startswith('test_'):
        is_used = True
    
    if is_used:
        print(f"   ✅ SRC (usado): {rel_str}")
        utilizados.append(arquivo)
    else:
        print(f"   ⚠️  SRC (não usado): {rel_str}")
        nao_utilizados.append(arquivo)

print()
print(f"   Total utilizados: {len(utilizados)}")
print(f"   Total não utilizados: {len(nao_utilizados)}")
print()

# ============================================================================
# 4. MOVER NÃO UTILIZADOS PARA OBSOLETOS
# ============================================================================

print("="*130)
print("📦 Movendo arquivos não utilizados para src/obsoletos/...")
print("="*130)
print()

obsoletos_dir = BASE / 'src' / 'obsoletos'
obsoletos_dir.mkdir(exist_ok=True)

movidos = 0
erros = 0

for arquivo in nao_utilizados:
    destino = obsoletos_dir / arquivo.name
    
    try:
        # Se já existe, fazer backup
        if destino.exists():
            backup = destino.with_suffix(destino.suffix + '.bak')
            if backup.exists():
                backup.unlink()
            shutil.move(str(destino), str(backup))
        
        shutil.move(str(arquivo), str(destino))
        print(f"   ✅ {arquivo.name:50s} → src/obsoletos/")
        movidos += 1
    except Exception as e:
        print(f"   ❌ ERRO: {arquivo.name} - {e}")
        erros += 1

print()
print(f"   Movidos: {movidos}")
if erros > 0:
    print(f"   Erros: {erros}")
print()

# ============================================================================
# 5. GERAR DOCUMENTAÇÃO
# ============================================================================

print("📝 Gerando documentação...")

doc_content = f"""# Mapeamento de Arquivos Python - MegaCLI

Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

## Arquivos Utilizados ({len(utilizados)})

"""

# Listar por nome
for arquivo in sorted(utilizados, key=lambda x: x.name):
    loc = "raiz" if arquivo.parent.name == "MegaCLI" else str(arquivo.relative_to(BASE / 'src'))
    desc = UTILIZADOS_CORE.get(arquivo.name, '')
    if desc:
        doc_content += f"- **{arquivo.name}** ({loc}) - {desc}\n"
    else:
        doc_content += f"- {arquivo.name} ({loc})\n"

doc_content += f"""

## Arquivos Obsoletos ({len(nao_utilizados)})

Movidos para `src/obsoletos/`:

"""

for arquivo in sorted(nao_utilizados, key=lambda x: x.name):
    doc_content += f"- {arquivo.name}\n"

# Salvar
doc_path = BASE / 'doc' / 'MAPEAMENTO_PYTHON.md'
doc_path.write_text(doc_content, encoding='utf-8')

print(f"   ✅ Documentação salva: doc/MAPEAMENTO_PYTHON.md")
print()

# ============================================================================
# RESUMO
# ============================================================================

print("="*130)
print("✅ LIMPEZA CONCLUÍDA!")
print("="*130)
print()

print("📊 Resumo:")
print(f"   • Total de arquivos .py: {len(utilizados) + len(nao_utilizados)}")
print(f"   • Utilizados: {len(utilizados)}")
print(f"   • Movidos para obsoletos: {movidos}")
print(f"   • Documentação: doc/MAPEAMENTO_PYTHON.md")
print()

print("🎯 Projeto organizado e documentado!")
