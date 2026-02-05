"""
Limpeza Final - Move documentos restantes para doc/
"""

import shutil
from pathlib import Path

print("="*130)
print("LIMPEZA FINAL - ORGANIZANDO DOCUMENTOS")
print("="*130)
print()

BASE = Path("d:/MegaCLI")

# Garantir que pasta doc existe
(BASE / "doc").mkdir(exist_ok=True)

# Documentos que devem ficar na raiz
MANTER_RAIZ = {
    "README.md",
    "ANALISE_IA_REFINAMENTO.md",
    "requirements.txt",
    "requirements2.txt",
    "pyproject.toml",
}

# Encontrar todos os .md e .txt na raiz
arquivos_raiz = list(BASE.glob("*.md")) + list(BASE.glob("*.txt"))

print("📋 Arquivos .md e .txt encontrados na raiz:")
print()

movidos = 0
mantidos = 0

for arquivo in arquivos_raiz:
    if arquivo.name in MANTER_RAIZ:
        print(f"   ✅ MANTER: {arquivo.name}")
        mantidos += 1
    else:
        destino = BASE / "doc" / arquivo.name
        try:
            # Se já existe, fazer backup
            if destino.exists():
                backup = destino.with_suffix(destino.suffix + '.bak')
                shutil.move(str(destino), str(backup))
            
            shutil.move(str(arquivo), str(destino))
            print(f"   📦 MOVIDO: {arquivo.name:50s} → doc/")
            movidos += 1
        except Exception as e:
            print(f"   ⚠️  ERRO: {arquivo.name} - {e}")

print()
print("="*130)
print("RESUMO")
print("="*130)
print()
print(f"   ✅ Mantidos na raiz: {mantidos}")
print(f"   📦 Movidos para doc/: {movidos}")
print()

# Listar o que ficou na raiz
print("📁 Arquivos na raiz após limpeza:")
arquivos_finais = sorted(list(BASE.glob("*.md")) + list(BASE.glob("*.txt")))
for arq in arquivos_finais:
    print(f"   • {arq.name}")

print()
print("✅ Limpeza concluída!")
