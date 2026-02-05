"""
Parâmetros de Configuração para Análise MegaCLI v5.1.5

Este módulo centraliza todos os parâmetros configuráveis do sistema de análise.
Facilita ajustes e experimentação sem modificar o código principal.

Autor: MegaCLI Team
Data: 21/01/2026
Versão: 1.0.0
"""



from src.core.config import MEGA_CONFIG

class AnaliseConfig:
    """
    Classe de configuração para parâmetros de análise do MegaCLI.
    
    Os valores são carregados dinamicamente de 'config/config.yaml' via src.core.config.MEGA_CONFIG.
    """
    
    # Helper seguro
    @staticmethod
    def _get(path, default):
        try:
            val = MEGA_CONFIG
            for key in path.split('.'):
                val = val.get(key, {})
            return val if isinstance(val, (int, float, list, str)) else default
        except:
            return default

    # ========================================================================
    # ETAPA 0: AVALIAÇÃO DE EFICÁCIAS INDIVIDUAIS
    # ========================================================================
    
    EFICACIA_N_SORTEIOS = _get.__func__('analise.eficacia_n_sorteios', 200)
    """Número de sorteios históricos para avaliar eficácia de cada indicador."""
    
    # ========================================================================
    # ETAPA 1: BATIMENTO HISTÓRICO
    # ========================================================================
    
    BATIMENTO_MAX_JOGOS = _get.__func__('analise.batimento.max_jogos', 200)
    BATIMENTO_JANELA_OFFSET = _get.__func__('analise.batimento.janela_offset', 250)
    BATIMENTO_PASSO = _get.__func__('analise.batimento.passo', 1)
    
    # ========================================================================
    # FASE 4: GERAÇÃO DE JOGOS DATA-DRIVEN
    # ========================================================================
    
    GERACAO_N_JOGOS = _get.__func__('analise.geracao.n_jogos', 210)
    GERACAO_TOP_INDICADORES = _get.__func__('analise.geracao.top_indicadores', 10)
    
    # ========================================================================
    # VALIDAÇÃO HISTÓRICA ESTENDIDA
    # ========================================================================
    
    VALIDACAO_N_SORTEIOS = _get.__func__('analise.validacao.n_sorteios', 1000)
    VALIDACAO_SPLIT_SERIES = _get.__func__('analise.validacao.split_series', [500, 500])
    VALIDACAO_OFFSET_INICIAL = _get.__func__('analise.validacao.offset_inicial', 15)
    
    # ========================================================================
    # FASE 5: ANÁLISE GANHADORES - TOP 10 INDICADORES
    # ========================================================================
    
    FASE5_N_JOGOS_ANALISE = _get.__func__('analise.fase5.n_jogos_analise', 50)
    FASE5_MULTIPLICADOR_CANDIDATOS = _get.__func__('analise.fase5.multiplicador_candidatos', 20)
    
    # ========================================================================
    # METADADOS
    # ========================================================================
    
    VERSAO_CONFIG = _get.__func__('sistema.versao_config', "1.0.0")
    DESCRICAO = _get.__func__('sistema.descricao', "Configuração Dinâmica")
    
    # ========================================================================
    # MÉTODOS UTILITÁRIOS
    # ========================================================================
    
    @classmethod
    def exibir_configuracao(cls):
        """Exibe todas as configurações atuais de forma formatada."""
        print("\n" + "="*80)
        print("⚙️  CONFIGURAÇÃO MEGACLI v5.1.5")
        print("="*80)
        print(f"\n📊 ETAPA 0 - Avaliação de Eficácias:")
        print(f"   • Sorteios por indicador: {cls.EFICACIA_N_SORTEIOS}")
        
        print(f"\n📊 ETAPA 1 - BATIMENTO Histórico:")
        print(f"   • Jogos para validação: {cls.BATIMENTO_MAX_JOGOS}")
        print(f"   • Janela offset: {cls.BATIMENTO_JANELA_OFFSET}")
        print(f"   • Passo: {cls.BATIMENTO_PASSO}")
        
        print(f"\n🎯 FASE 4 - Geração de Jogos:")
        print(f"   • Jogos a gerar: {cls.GERACAO_N_JOGOS}")
        print(f"   • Top indicadores: {cls.GERACAO_TOP_INDICADORES}")
        
        print(f"\n🏆 FASE 5 - Análise Ganhadores:")
        print(f"   • Jogos para análise: {cls.FASE5_N_JOGOS_ANALISE}")
        print(f"   • Multiplicador candidatos: {cls.FASE5_MULTIPLICADOR_CANDIDATOS}x")
        print(f"   • Total candidatos: {cls.FASE5_N_JOGOS_ANALISE * cls.FASE5_MULTIPLICADOR_CANDIDATOS}")
        
        print(f"\n📋 Metadados:")
        print(f"   • Versão: {cls.VERSAO_CONFIG}")
        print(f"   • Descrição: {cls.DESCRICAO}")
        print("="*80 + "\n")
    
    @classmethod
    def validar_parametros(cls):
        """
        Valida se os parâmetros estão em ranges aceitáveis.
        
        Returns:
            bool: True se todos parâmetros válidos, False caso contrário
        """
        erros = []
        
        # Validar ETAPA 0
        if not (50 <= cls.EFICACIA_N_SORTEIOS <= 500):
            erros.append(f"EFICACIA_N_SORTEIOS deve estar entre 50 e 500 (atual: {cls.EFICACIA_N_SORTEIOS})")
        
        # Validar ETAPA 1
        if not (50 <= cls.BATIMENTO_MAX_JOGOS <= 500):
            erros.append(f"BATIMENTO_MAX_JOGOS deve estar entre 50 e 500 (atual: {cls.BATIMENTO_MAX_JOGOS})")
        
        if cls.BATIMENTO_JANELA_OFFSET < cls.BATIMENTO_MAX_JOGOS:
            erros.append(f"BATIMENTO_JANELA_OFFSET ({cls.BATIMENTO_JANELA_OFFSET}) deve ser >= BATIMENTO_MAX_JOGOS ({cls.BATIMENTO_MAX_JOGOS})")
        
        # Validar FASE 4
        if not (1 <= cls.GERACAO_N_JOGOS <= 1000):
            erros.append(f"GERACAO_N_JOGOS deve estar entre 1 e 1000 (atual: {cls.GERACAO_N_JOGOS})")
        
        if not (5 <= cls.GERACAO_TOP_INDICADORES <= 42):
            erros.append(f"GERACAO_TOP_INDICADORES deve estar entre 5 e 42 (atual: {cls.GERACAO_TOP_INDICADORES})")
        
        if erros:
            print("\n❌ ERROS DE VALIDAÇÃO:")
            for erro in erros:
                print(f"   • {erro}")
            return False
        
        print("\n✅ Todos os parâmetros são válidos!")
        return True


# Exports
__all__ = ['AnaliseConfig']


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando módulo de configuração...\n")
    
    # Exibir configuração
    AnaliseConfig.exibir_configuracao()
    
    # Validar parâmetros
    AnaliseConfig.validar_parametros()
    
    # Teste de acesso
    print("\n🔍 Teste de acesso aos parâmetros:")
    print(f"   • Jogos a gerar: {AnaliseConfig.GERACAO_N_JOGOS}")
    print(f"   • Sorteios BATIMENTO: {AnaliseConfig.BATIMENTO_MAX_JOGOS}")
    print(f"   • Sorteios eficácia: {AnaliseConfig.EFICACIA_N_SORTEIOS}")
    
    print("\n✅ Módulo de configuração funcionando corretamente!\n")
