"""
Gerenciador Centralizado de Paths - MegaCLI v5.1

Este módulo fornece uma única fonte de verdade para todos os paths do projeto.
Todos os scripts devem usar esta classe para obter caminhos.

Uso:
    from src.core.paths import ProjectPaths
    
    excel_path = ProjectPaths.EXCEL_RESULTADO
    yaml_path = ProjectPaths.YAML_ESTRUTURA

Autor: Thefeus
Data: 31/12/2024
"""

from pathlib import Path

class ProjectPaths:
    """
    Gerenciador centralizado de paths do projeto MegaCLI
    
    Todos os paths são Path objects do pathlib.
    Paths relativos à raiz do projeto.
    """
    
    # ========================================================================
    # RAIZ DO PROJETO
    # ========================================================================
    
    ROOT = Path(__file__).parent.parent.parent.resolve()
    
    # ========================================================================
    # DIRETÓRIOS PRINCIPAIS
    # ========================================================================
    
    SRC = ROOT / 'src'
    CONFIG_DIR = ROOT / 'config'
    DADOS = ROOT / 'Dados'
    RESULTADO = ROOT / 'Resultado'
    DOC = ROOT / 'doc'
    LOGS = ROOT / 'logs'
    
    # Subdiretórios src/
    CORE = SRC / 'core'
    VALIDACAO = SRC / 'validacao'
    UTILS = SRC / 'utils'
    SCRIPTS = SRC / 'scripts'
    FERRAMENTAS = SRC / 'ferramentas'
    INDICADORES = SRC / 'utils' / 'indicadores'
    
    # ========================================================================
    # ARQUIVOS DE CONFIGURAÇÃO
    # ========================================================================
    
    YAML_ESTRUTURA = CONFIG_DIR / 'estrutura_planilha.yaml'
    ENV_FILE = ROOT / '.env'
    
    # ========================================================================
    # ARQUIVOS EXCEL
    # ========================================================================
    
    EXCEL_DADOS = DADOS / 'ANALISE_HISTORICO_COMPLETO.xlsx'
    EXCEL_RESULTADO = RESULTADO / 'ANALISE_HISTORICO_COMPLETO.xlsx'
    
    # ========================================================================
    # HISTÓRICO E VERSIONAMENTO
    # ========================================================================
    
    HISTORICO_PESOS = RESULTADO / 'historico_pesos'
    
    # ========================================================================
    # DOCUMENTAÇÃO
    # ========================================================================
    
    DOC_RAG = DOC / 'RAG'
    DOC_SPEC = DOC_RAG / 'ESPECIFICACAO_TECNICA.md'
    DOC_STATUS = DOC_RAG / 'STATUS_PROJETO.md'
    DOC_HISTORICO = DOC_RAG / 'HISTORICO_IMPLEMENTACAO.md'
    
    # ========================================================================
    # MÉTODOS UTILITÁRIOS
    # ========================================================================
    
    @classmethod
    def criar_diretorios(cls):
        """
        Cria todos os diretórios necessários se não existirem
        """
        diretorios = [
            cls.RESULTADO,
            cls.HISTORICO_PESOS,
            cls.LOGS,
            cls.FERRAMENTAS,
        ]
        
        for diretorio in diretorios:
            diretorio.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def existe(cls, path):
        """
        Verifica se um path existe
        
        Args:
            path: Path object ou string
            
        Returns:
            bool: True se existe
        """
        return Path(path).exists()
    
    @classmethod
    def obter_versao_pesos(cls):
        """
        Retorna a próxima versão disponível para pesos
        
        Returns:
            int: Próxima versão (1 se nenhum arquivo existe)
        """
        if not cls.HISTORICO_PESOS.exists():
            return 1
        
        arquivos = list(cls.HISTORICO_PESOS.glob('pesos_v*.json'))
        
        if not arquivos:
            return 1
        
        # Extrair versões
        versoes = []
        for arquivo in arquivos:
            try:
                # pesos_v8_20241230_203117.json → 8
                versao = int(arquivo.stem.split('_')[1].replace('v', ''))
                versoes.append(versao)
            except (IndexError, ValueError):
                continue
        
        return max(versoes) + 1 if versoes else 1
    
    @classmethod
    def obter_ultimo_pesos_json(cls):
        """
        Retorna o path do último arquivo de pesos
        
        Returns:
            Path | None: Path do último arquivo ou None se não existe
        """
        if not cls.HISTORICO_PESOS.exists():
            return None
        
        arquivos = sorted(
            cls.HISTORICO_PESOS.glob('pesos_v*.json'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        return arquivos[0] if arquivos else None
    
    @classmethod
    def validar_estrutura(cls):
        """
        Valida se a estrutura de diretórios está correta
        
        Returns:
            tuple: (bool, list) - (válido, lista de erros)
        """
        erros = []
        
        # Verificar diretórios essenciais
        essenciais = [
            (cls.ROOT, 'Raiz do projeto'),
            (cls.SRC, 'Diretório src/'),
            (cls.CONFIG_DIR, 'Diretório config/'),
            (cls.DADOS, 'Diretório Dados/'),
        ]
        
        for path, nome in essenciais:
            if not path.exists():
                erros.append(f'{nome} não encontrado: {path}')
        
        # Verificar arquivos críticos
        criticos = [
            (cls.YAML_ESTRUTURA, 'YAML de estrutura'),
            (cls.EXCEL_DADOS, 'Excel de dados (opcional)'),
        ]
        
        for path, nome in criticos:
            if not path.exists() and 'opcional' not in nome:
                erros.append(f'{nome} não encontrado: {path}')
        
        return (len(erros) == 0, erros)
    
    @classmethod
    def info(cls):
        """
        Retorna informações sobre os paths do projeto
        
        Returns:
            dict: Dicionário com informações
        """
        return {
            'root': str(cls.ROOT),
            'src': str(cls.SRC),
            'dados': str(cls.DADOS),
            'resultado': str(cls.RESULTADO),
            'excel_resultado': str(cls.EXCEL_RESULTADO),
            'yaml': str(cls.YAML_ESTRUTURA),
            'historico_pesos': str(cls.HISTORICO_PESOS),
            'versao_proxima': cls.obter_versao_pesos(),
        }


# Criar diretórios ao importar (seguro, não sobrescreve)
ProjectPaths.criar_diretorios()


if __name__ == '__main__':
    # Testes
    print("="*80)
    print("VALIDAÇÃO DE PATHS - MegaCLI v5.1")
    print("="*80)
    
    # Info  
    print("\n📂 Informações de Paths:")
    for chave, valor in ProjectPaths.info().items():
        print(f"   {chave}: {valor}")
    
    # Validar
    print("\n🔍 Validando Estrutura:")
    valido, erros = ProjectPaths.validar_estrutura()
    
    if valido:
        print("   ✅ Estrutura válida!")
    else:
        print("   ❌ Erros encontrados:")
        for erro in erros:
            print(f"      - {erro}")
    
    # Verificar último pesos
    print("\n📊 Histórico de Pesos:")
    ultimo = ProjectPaths.obter_ultimo_pesos_json()
    if ultimo:
        print(f"   ✅ Último arquivo: {ultimo.name}")
    else:
        print("   ℹ️  Nenhum arquivo de pesos encontrado")
    
    print(f"\n   Próxima versão: v{ProjectPaths.obter_versao_pesos()}")
    
    print("\n" + "="*80)
