"""
Organizar arquivos .py soltos em src/

Classifica e move arquivos que estão diretamente em src/ 
para as pastas apropriadas
"""

from pathlib import Path
import shutil

print("="*130)
print("ORGANIZANDO ARQUIVOS SOLTOS EM src/")
print("="*130)
print()

BASE = Path("d:/MegaCLI")
SRC = BASE / "src"

# Listar apenas arquivos diretamente em src/ (não recursivo)
arquivos_src = [f for f in SRC.glob("*.py") if f.is_file() and f.name != '__init__.py']

print(f"📋 Encontrados {len(arquivos_src)} arquivos .py em src/:")
print()

for arq in sorted(arquivos_src):
    print(f"   • {arq.name}")

print()

# Classificar arquivos
PRINCIPAIS = {
    'mega_final_de_ano_v2.py': 'MANTER - Sistema principal',
    'run_mega_final_v2.py': 'MANTER - Executor',
    'app_config.py': 'MANTER - Configurações',
    'main.py': 'MANTER - Entry point',
}

MOVER_UTILS = {
    'utils.py',
    'feature_engineer.py',
    'advanced_ml.py',
    'pair_predictor.py',
    'sequence_validator.py',
}

MOVER_OBSOLETOS = {
    'mega_final_de_ano.py',  # v1 antiga
    'ai_feature_generator.py',
    'ai_formula_suggester.py',
    'ai_function_generator.py',
    'ai_neuron_analyzer.py',
    'ai_post_mortem.py',
    'ollama_analyzer.py',
    'ollama_direct_predictor.py',
}

# Arquivos de teste - mover para pasta tests
TESTES = set()
for arq in arquivos_src:
    if arq.name.startswith('test_'):
        TESTES.add(arq.name)

print("="*130)
print("CLASSIFICAÇÃO")
print("="*130)
print()

print("✅ Manter em src/:")
for arq in arquivos_src:
    if arq.name in PRINCIPAIS:
        print(f"   • {arq.name:40s} - {PRINCIPAIS[arq.name]}")

print()
print("📦 Mover para src/utils/:")
for arq in arquivos_src:
    if arq.name in MOVER_UTILS:
        print(f"   • {arq.name}")

print()
print("🗑️  Mover para src/obsoletos/:")
for arq in arquivos_src:
    if arq.name in MOVER_OBSOLETOS:
        print(f"   • {arq.name}")

if TESTES:
    print()
    print("🧪 Mover para src/tests/ (a criar):")
    for nome in sorted(TESTES):
        print(f"   • {nome}")

print()
print("="*130)
print("MOVIMENTANDO ARQUIVOS")
print("="*130)
print()

# Criar pastas se necessário
(SRC / "utils").mkdir(exist_ok=True)
(SRC / "obsoletos").mkdir(exist_ok=True)
if TESTES:
    (SRC / "tests").mkdir(exist_ok=True)
    (SRC / "tests" / "__init__.py").touch()

movidos = 0

# Mover para utils
for arq in arquivos_src:
    if arq.name in MOVER_UTILS:
        destino = SRC / "utils" / arq.name
        if not destino.exists():
            try:
                shutil.move(str(arq), str(destino))
                print(f"   ✅ {arq.name:40s} → src/utils/")
                movidos += 1
            except Exception as e:
                print(f"   ❌ Erro ao mover {arq.name}: {e}")
        else:
            print(f"   ⏭️  {arq.name:40s} → Já existe em utils/")

# Mover para obsoletos
for arq in arquivos_src:
    if arq.name in MOVER_OBSOLETOS:
        destino = SRC / "obsoletos" / arq.name
        try:
            if destino.exists():
                destino.unlink()
            shutil.move(str(arq), str(destino))
            print(f"   ✅ {arq.name:40s} → src/obsoletos/")
            movidos += 1
        except Exception as e:
            print(f"   ❌ Erro ao mover {arq.name}: {e}")

# Mover testes
for arq in arquivos_src:
    if arq.name in TESTES:
        destino = SRC / "tests" / arq.name
        try:
            if destino.exists():
                destino.unlink()
            shutil.move(str(arq), str(destino))
            print(f"   ✅ {arq.name:40s} → src/tests/")
            movidos += 1
        except Exception as e:
            print(f"   ❌ Erro ao mover {arq.name}: {e}")

print()
print("="*130)
print("✅ ORGANIZAÇÃO CONCLUÍDA")
print("="*130)
print()

# Verificar o que ficou em src/
arquivos_finais = [f for f in SRC.glob("*.py") if f.is_file() and f.name != '__init__.py']

print(f"📁 Arquivos restantes em src/ ({len(arquivos_finais)}):")
for arq in sorted(arquivos_finais):
    status = PRINCIPAIS.get(arq.name, "❓ Verificar manualmente")
    print(f"   • {arq.name:40s} - {status}")

print()
print(f"📊 Total movido: {movidos} arquivos")
print()
print("🎯 src/ organizado!")
