"""
Configuração de Paths e Variáveis de Ambiente - MegaCLI

Define o PYTHONPATH e paths importantes do projeto.
Deve ser importado no início de todos os scripts principais.
"""

import os
import sys
from pathlib import Path

# Diretório raiz do projeto (D:\MegaCLI)
# Este arquivo está em src/core/config.py, então:
# Path(__file__) = D:\MegaCLI\src\core\config.py
# Path(__file__).parent = D:\MegaCLI\src\core
# Path(__file__).parent.parent = D:\MegaCLI\src
# Path(__file__).parent.parent.parent = D:\MegaCLI
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()

# Diretório src
SRC_DIR = PROJECT_ROOT / "src"

# Adicionar src ao PYTHONPATH se não estiver
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Outros diretórios importantes
DADOS_DIR = PROJECT_ROOT / "Dados"  # Fonte histórica (maiúsculo!)
RESULTADO_DIR = PROJECT_ROOT / "Resultado"  # Outputs
LOGS_DIR = PROJECT_ROOT / "logs"

# Criar diretórios se não existirem
DADOS_DIR.mkdir(exist_ok=True)
RESULTADO_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Arquivos de dados
ARQUIVO_FONTE = DADOS_DIR / "Mega-Sena.xlsx"  # Fonte original (somente leitura)
ARQUIVO_HISTORICO = RESULTADO_DIR / "ANALISE_HISTORICO_COMPLETO.xlsx"  # Working copy

# AnaliseConfig removido daqui para evitar ciclo. Importar onde for necessário.
# from src.core.analise_params import AnaliseConfig

# --- Carregamento de Configuração YAML ---
import yaml

CONFIG_FILE = PROJECT_ROOT / "config" / "config.yaml"
MEGA_CONFIG = {}

def load_config():
    """Carrega configuração do arquivo YAML."""
    global MEGA_CONFIG
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                MEGA_CONFIG = yaml.safe_load(f)
            # print(f"🔧 Configuração carregada de {CONFIG_FILE.name}")
        except Exception as e:
            print(f"❌ Erro ao carregar config.yaml: {e}")
    else:
        print(f"⚠️  Configuração não encontrada em: {CONFIG_FILE}")

# Carregar imediatamente
load_config()

# Exports
__all__ = [
    'PROJECT_ROOT',
    'SRC_DIR',
    'DADOS_DIR',
    'RESULTADO_DIR',
    'LOGS_DIR',
    'ARQUIVO_FONTE',
    'ARQUIVO_HISTORICO',
    # 'AnaliseConfig',
    'MEGA_CONFIG', # Exportar dicionário raw
    'load_config'
]

if __name__ == "__main__":
    print("🔧 Configuração de Paths MegaCLI")
    print(f"   PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"   SRC_DIR: {SRC_DIR}")
    print(f"   PYTHONPATH configurado: {SRC_DIR in sys.path}")
    print(f"   Config YAML carregada: {bool(MEGA_CONFIG)}")
