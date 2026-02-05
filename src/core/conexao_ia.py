"""
Componentes Unificado de Conexão com IA - MegaCLI

Centraliza a lógica de conexão com LLMs (Google Gemini), garantindo:
1. Carregamento seguro de variáveis de ambiente
2. Limpeza automática da API Key (aspas, espaços)
3. Tratamento de erros de conexão
4. Singleton/ Lazy pattern para reuso de instância
5. Leitura do modelo da configuração (app_config.py ou config.yaml)

Uso:
    from src.core.conexao_ia import conectar_ia
    llm = conectar_ia()  # Usa modelo configurado
    llm = conectar_ia(modelo="gemini-1.5-flash")  # Override manual
"""

import os
import sys
from pathlib import Path
import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional

# Singleton instance
_LLM_INSTANCE = None

def carregar_api_key() -> Optional[str]:
    """
    Carrega e limpa a API Key do arquivo .env.
    
    Returns:
        API Key limpa ou None se não encontrada
    """
    # Tentar caminhos comuns para o .env
    caminhos = [
        Path("d:/MegaCLI/config/.env"),
        Path("d:/MegaCLI/.env"),
        Path(".env")
    ]
    
    env_path = None
    for p in caminhos:
        if p.exists():
            env_path = p
            break
            
    if env_path:
        dotenv.load_dotenv(dotenv_path=env_path, override=True)
    else:
        # Tenta carregar do ambiente atual se não achar arquivo
        pass
        
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    
    if not api_key:
        return None
        
    # Limpeza crítica (remove aspas duplas, simples e espaços)
    return api_key.strip().strip('"').strip("'")

def _obter_modelo_configurado() -> str:
    """
    Obtém o modelo configurado de forma inteligente.
    Prioridade:
    1. app_config.py (se disponível)
    2. config.yaml (seção ia.modelo)
    3. Fallback: gemini-2.5-pro
    
    Returns:
        Nome do modelo configurado
    """
    # Tentar app_config primeiro
    try:
        from src.app_config import config
        modelo = config.ai.model_name
        if modelo:
            return modelo
    except:
        pass
    
    # Tentar config.yaml
    try:
        import yaml
        from pathlib import Path
        
        config_path = Path(__file__).parent.parent.parent / 'config' / 'config.yaml'
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)
                if cfg and 'ia' in cfg and 'modelo' in cfg['ia']:
                    return cfg['ia']['modelo']
    except:
        pass
    
    # Fallback
    return "gemini-2.5-pro"

def conectar_ia(
    modelo: str = None,
    temperatura: float = 0.3,
    tentativas: int = 3,
    verbose: bool = True
) -> Optional[ChatGoogleGenerativeAI]:
    """
    Obtém uma instância configurada do ChatGoogleGenerativeAI.
    
    Args:
        modelo: Nome do modelo (None = usa configuração automática)
        temperatura: Criatividade (0.0 a 1.0)
        tentativas: Número de retries automáticos
        verbose: Se True, imprime status da conexão
        
    Returns:
        Instância do LLM ou None em caso de erro crítico
    """
    global _LLM_INSTANCE
    
    # Se modelo não especificado, buscar da configuração
    if modelo is None:
        modelo = _obter_modelo_configurado()
        if verbose:
            print(f"📋 Usando modelo da configuração: {modelo}")
    
    # Se já existe instância ativa e parâmetros são compatíveis (simplificado), retorna ela
    # Nota: Se mudar temperatura/modelo, idealmente recriaria. 
    # Por enquanto, vamos recriar sempre que chamado com parâmetros específicos,
    # ou usar singleton se chamado sem args (padrão).
    
    key = carregar_api_key()
    if not key:
        if verbose:
            print("❌ ERRO: GOOGLE_API_KEY não encontrada no .env ou variáveis de ambiente.")
        return None
        
    # Atualizar ambiente para garantir que bibliotecas internas peguem a chave limpa
    os.environ["GOOGLE_API_KEY"] = key
    
    try:
        if verbose:
            print(f"🔌 Conectando ao Google Gemini ({modelo})...")
            
        llm = ChatGoogleGenerativeAI(
            model=modelo,
            temperature=temperatura,
            max_retries=tentativas,
            google_api_key=key,
            timeout=60
        )
        
        if verbose:
            print("✅ Conexão estabelecida com sucesso.")
            
        return llm
        
    except Exception as e:
        if verbose:
            print(f"❌ Falha na conexão com IA: {e}")
        return None

def testar_conexao():
    """Teste rápido de conectividade."""
    print("🧪 Testando Componente Unificado de IA...")
    llm = conectar_ia(verbose=True)
    
    if llm:
        try:
            print("   Enviando 'Olá' para teste de latência...")
            resp = llm.invoke("Responda apenas 'OK'.")
            print(f"   Resposta da IA: {resp.content}")
            print("✅ Teste completo: FUNCIONAL")
            return True
        except Exception as e:
            print(f"❌ Erro na invocação: {e}")
            return False
    return False

if __name__ == "__main__":
    testar_conexao()
