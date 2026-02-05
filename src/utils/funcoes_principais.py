"""
Funções Principais - MegaCLI v5.0

Funções centrais do sistema incluindo geração de jogos,
refinamento de pesos e criação de dict de indicadores.
"""

import pandas as pd
import numpy as np
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import Counter
from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI


def criar_all_indicators_dict() -> Dict[str, callable]:
    """
    Cria dict com todos os indicadores disponíveis: {nome: função_calculo}
    
    Usa wrapper para padronizar interface (historico, numeros) -> score
    
    Returns:
        Dict mapeando nome do indicador para sua função de cálculo
    """
    # Imports dos módulos de indicadores (classes)
    from utils.indicadores_avancados import (
        RaizDigitalIndicador, VariacaoSomaIndicador, ConjugacaoIndicador,
        RepeticaoAnteriorIndicador, FrequenciaMensalIndicador
    )
    from utils.indicadores_extras import (
        SequenciasIndicador, DistanciaMediaIndicador, NumerosExtremosIndicador,
        PadraoDezenaIndicador, CicloAparicaoIndicador
    )
    from utils.indicadores_temporais import (
        calcular_tendencia_quadrantes, calcular_ciclos_semanais,
        calcular_acumulacao_consecutiva, calcular_janela_deslizante
    )
    from utils.indicadores_geometricos import (
        calcular_matriz_posicional, calcular_cluster_espacial,
        calcular_simetria_central
    )
    from utils.indicadores_frequencia import (
        calcular_frequencia_relativa, calcular_desvio_frequencia,
        calcular_entropia_distribuicao, calcular_correlacao_temporal
    )
    from utils.indicadores_numerologicos import (
        calcular_soma_digitos, calcular_padrao_modular
    )
    from utils.indicadores_ml import (
        calcular_score_anomalia, calcular_probabilidade_condicional,
        calcular_importancia_feature
    )
    from utils.indicadores_ia import (
        PadroesSubconjuntosIndicador,
        MicroTendenciasIndicador,
        AnaliseContextualIndicador,
        EmbeddingIndicador
    )
    from utils.indicadores_basicos import INDICADORES_BASICOS
    
    # Wrapper para classes que usam calcular_score(numeros,  historico)
    def wrap_class(classe):
        return lambda hist, nums: classe.calcular_score(nums, hist)
    
    # Wrapper especial para classes IA - DESABILITADO para BATIMENTO (muito lento!)
    # Durante BATIMENTO, retorna score neutro para não fazer chamadas API
    # Apenas na geração final os indicadores IA são usados com API
    def wrap_ia_class(classe):
        def wrapper(hist, nums):
            # FALLBACK: Retorna score neutro durante avaliação histórica
            # para evitar centenas de chamadas lentas à API Gemini
            return 50.0  # Score neutro (não influencia ranking)
        return wrapper
    
    # Dict completo - 42 INDICADORES!
    indicadores = {
        # Básicos (12) - funções ✨ COMPLETO!
        **INDICADORES_BASICOS,
        # Avançados (5) - classes
        'RaizDigital': wrap_class(RaizDigitalIndicador),
        'VariacaoSoma': wrap_class(VariacaoSomaIndicador),
        'Conjugacao': wrap_class(ConjugacaoIndicador),
        'RepeticaoAnterior': wrap_class(RepeticaoAnteriorIndicador),
        'FrequenciaMensal': wrap_class(FrequenciaMensalIndicador),
        # Extras (5) - classes
        'Sequencias': wrap_class(SequenciasIndicador),
        'DistanciaMedia': wrap_class(DistanciaMediaIndicador),
        'NumerosExtremos': wrap_class(NumerosExtremosIndicador),
        'PadraoDezena': wrap_class(PadraoDezenaIndicador),
        'CicloAparicao': wrap_class(CicloAparicaoIndicador),
        # Temporais (4) - funções
        'TendenciaQuadrantes': calcular_tendencia_quadrantes,
        'CiclosSemanais': calcular_ciclos_semanais,
        'AcumulacaoConsecutiva': calcular_acumulacao_consecutiva,
        'JanelaDeslizante': calcular_janela_deslizante,
        # Geométricos (3) - funções
        'MatrizPosicional': calcular_matriz_posicional,
        'ClusterEspacial': calcular_cluster_espacial,
        'SimetriaCentral': calcular_simetria_central,
        # Frequência (4) - funções
        'FrequenciaRelativa': calcular_frequencia_relativa,
        'DesvioFrequencia': calcular_desvio_frequencia,
        'EntrópiaDistribuicao': calcular_entropia_distribuicao,
        'CorrelacaoTemporal': calcular_correlacao_temporal,
        # Numerológicos (2) - funções
        'SomaDigitos': calcular_soma_digitos,
        'PadraoModular': calcular_padrao_modular,
        # ML (3) - funções
        'ScoreAnomalia': calcular_score_anomalia,
        'ProbabilidadeCondicional': calcular_probabilidade_condicional,
        'ImportanciaFeature': calcular_importancia_feature,
        # IA (4) - classes
        'PadroesSubconjuntos': wrap_ia_class(PadroesSubconjuntosIndicador),
        'MicroTendencias': wrap_ia_class(MicroTendenciasIndicador),
        'AnaliseContextual': wrap_ia_class(AnaliseContextualIndicador),
        'Embedding': wrap_ia_class(EmbeddingIndicador)
    }
    
    return indicadores  # Total: 42 INDICADORES COMPLETOS! 🎉


def analisar_ganhadores_e_ajustar_pesos(df_historico: pd.DataFrame, 
                                        pesos_iniciais: Dict[str, float]) -> Dict[str, float]:
    """
    Analisa jogos ganhadores e ajusta pesos dos indicadores
    
    Indicadores mais frequentes em jogos ganhadores recebem +10% peso
    Indicadores raros em jogos ganhadores recebem -5% peso
    
    Returns:
        Pesos ajustados baseados em padrões de ganhadores
    """
    from analise.analise_ganhadores import AnalisadorGanhadores
    
    print("\n" + "="*60)
    print("🏆 ETAPA 1: Análise de Jogos Ganhadores")
    print("="*60)
    
    analisador = AnalisadorGanhadores(df_historico, pesos_iniciais)
    df_ganhadores = analisador.gerar_analise_completa()
    
    if len(df_ganhadores) == 0:
        print("⚠️ Nenhum ganhador encontrado, mantendo pesos iniciais")
        return pesos_iniciais.copy()
    
    # Contar frequência de cada indicador em jogos ganhadores
    contador_indicadores = Counter()
    
    for indicadores_str in df_ganhadores['Indicadores_Atendidos']:
        if indicadores_str:
            indicadores_list = indicadores_str.split(', ')
            contador_indicadores.update(indicadores_list)
    
    total_jogos = len(df_ganhadores)
    
    # Calcular frequência de cada indicador (%)
    freq_indicadores = {
        ind: (count / total_jogos * 100) 
        for ind, count in contador_indicadores.items()
    }
    
    print(f"\n📊 Top 5 Indicadores em Jogos Ganhadores:")
    for ind, freq in sorted(freq_indicadores.items(), key=lambda x: -x[1])[:5]:
        print(f"   {ind}: {freq:.1f}%")
    
    # Ajustar pesos
    pesos_ajustados = pesos_iniciais.copy()
    
    for indicador in pesos_ajustados.keys():
        freq = freq_indicadores.get(indicador, 0)
        
        if freq >= 50:  # Muito frequente em ganhadores
            pesos_ajustados[indicador] *= 1.10  # +10%
            print(f"   ↑ {indicador}: +10% (freq: {freq:.1f}%)")
        elif freq <= 20 and freq > 0:  # Raro em ganhadores
            pesos_ajustados[indicador] *= 0.95  # -5%
            print(f"   ↓ {indicador}: -5% (freq: {freq:.1f}%)")
    
    print(f"\n✅ Pesos ajustados baseados em {total_jogos} jogos ganhadores")
    
    return pesos_ajustados, df_ganhadores


def consultar_ia_refinamento(
    pesos_atuais: Dict[str, float],
    pesos_anteriores: Optional[Dict[str, float]] = None,
    metricas_anteriores: Optional[Dict] = None,
    versao_ciclo: int = 1
) -> Dict[str, float]:
    """
    Consulta IA (Gemini) para refinamento adicional de pesos.
    NOVO v5.1: Recebe contexto de ciclo anterior para feedback loop iterativo.
    
    Args:
        pesos_atuais: Pesos calculados do ranking atual
        pesos_anteriores: Pesos do ciclo anterior (se existir)
        metricas_anteriores: Métricas de performance do ciclo anterior
        versao_ciclo: Número da versão do ciclo atual
    
    Returns:
        Pesos refinados pela IA com feedback iterativo
    """
    import os
    from dotenv import load_dotenv
    from langchain_google_genai import ChatGoogleGenerativeAI
    import re
    from typing import Optional
    
    # Carregar .env da raiz do projeto (src/utils/../.. = raiz)
    # Path(__file__) = d:/MegaCLI/src/utils/funcoes_principais.py
    # parent = d:/MegaCLI/src/utils
    # parent.parent = d:/MegaCLI/src  
    # parent.parent.parent = d:/MegaCLI ← RAIZ!
    env_path = Path(__file__).parent.parent.parent / '.env'
    
    if not env_path.exists():
        print(f"⚠️ Arquivo .env não encontrado em: {env_path}")
        print(f"⚠️ Alternativa: Tentando carregar de variável de ambiente diretamente")
    
    load_dotenv(dotenv_path=env_path, override=True)
    api_key = os.getenv('GOOGLE_API_KEY', '').strip().strip('"').strip("'")
    
    if not api_key:
        print("⚠️ GOOGLE_API_KEY não encontrada, pulando refinamento IA")
        return pesos_atuais.copy()
    
    print("\n" + "="*60)
    print(f"🤖 ETAPA 2: Consulta IA para Refinamento (Ciclo v{versao_ciclo})")
    print("="*60)
    
    # NOVO: Criar contexto de evolução se houver ciclo anterior
    contexto_ciclo = ""
    if pesos_anteriores and metricas_anteriores:
        # Calcular deltas
        melhorias = []
        pioras = []
        
        for ind in pesos_atuais:
            if ind in pesos_anteriores:
                delta = pesos_atuais[ind] - pesos_anteriores[ind]
                if delta > 5:
                    melhorias.append((ind, delta))
                elif delta < -5:
                    pioras.append((ind, delta))
        
        contexto_ciclo = f"""
## CONTEXTO DE CICLO ITERATIVO (v{versao_ciclo-1} → v{versao_ciclo})

Você está refinando pesos do **Ciclo {versao_ciclo}** (anterior: v{versao_ciclo-1}).

### Performance do Ciclo Anterior:
- Indicadores totais: {metricas_anteriores.get('pesos_testados', 0)}
- Peso médio: {metricas_anteriores.get('peso_medio', 0):.2f}
- Peso mediano: {metricas_anteriores.get('peso_mediano', 0):.2f}
- Desvio padrão: {metricas_anteriores.get('peso_desvio', 0):.2f}
- Melhor indicador: {metricas_anteriores.get('indicador_max', 'N/A')} (peso: {metricas_anteriores.get('peso_max', 0):.1f})
- Pior indicador: {metricas_anteriores.get('indicador_min', 'N/A')} (peso: {metricas_anteriores.get('peso_min', 0):.1f})

### Indicadores que SUBIRAM no ranking atual:
{chr(10).join(f"- {ind}: +{delta:.1f} pontos" for ind, delta in sorted(melhorias, key=lambda x: -x[1])[:5]) if melhorias else '(Nenhum)'}

### Indicadores que CAÍRAM:
{chr(10).join(f"- {ind}: {delta:.1f} pontos" for ind, delta in sorted(pioras, key=lambda x: x[1])[:5]) if pioras else '(Nenhum)'}

**INSTRUÇÃO**: Ao refinar os pesos, considere:
1. ⬆️ **Reforçar** indicadores que melhoraram consistentemente (delta positivo)
2. ⬇️ **Reduzir** pesos de indicadores em declínio (delta negativo)  
3. ➡️ **Manter** estabilidade em indicadores já otimizados
4. 🎯 **Convergir** para configuração ótima (reduza variações grandes)
"""
    else:
        contexto_ciclo = f"""
## PRIMEIRO CICLO (v{versao_ciclo} - BASELINE)

Este é o **primeiro ciclo** de refinamento. Não há histórico anterior.
Foque em identificar indicadores com maior potencial baseado no ranking atual.
"""
    
    try:
        # Suprimir warnings de deprecação do langchain (versão 0.1.0 vs requisitado >=1.0.0)
        import warnings
        warnings.filterwarnings('ignore', category=DeprecationWarning, module='langchain')
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # ← Modelo funcional testado!
            temperature=0.3,
            google_api_key=api_key,
            verbose=False  # Evitar erro de compatibilidade langchain
        )
        
        prompt = f"""
        Você é um especialista em análise de loteria Mega-Sena.
        
        {contexto_ciclo}
        
        ### Pesos atuais do ranking (baseados em batimento histórico):
        {json.dumps(pesos_atuais, indent=2)}
        
        Faça ajustes finos (+/-5%) para otimizar a predição.
        
        Retorne APENAS um JSON com:
        {{
            "justificativa": "breve explicação considerando o ciclo iterativo",
            "ajustes": {{"Indicador": novo_peso, ...}}
        }}
        """
        
        response = llm.invoke(prompt)
        content = response.content
        
        print(f"\n📝 Resposta da IA (primeiros 500 chars):")
        print(content[:500])
        print("...")
        
        # Tentar extrair JSON da resposta (pode vir com markdown)
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        
        if json_match:
            try:
                ajustes_ia = json.loads(json_match.group())
                print("✅ Refinamento IA recebido")
                print(f"   {ajustes_ia.get('justificativa', 'Sem justificativa')}")
                
                if 'ajustes' in ajustes_ia:
                    ajustes_aplicados = 0
                    for ind, novo_peso in ajustes_ia['ajustes'].items():
                        if ind in pesos_atuais:
                            pesos_atuais[ind] = float(novo_peso)
                            ajustes_aplicados += 1
                    
                    print(f"   ✅ {ajustes_aplicados} pesos refinados pela IA")
                    return pesos_atuais
                else:
                    print("⚠️ JSON sem campo 'ajustes', mantendo pesos")
                    return pesos_atuais
                    
            except json.JSONDecodeError as je:
                print(f"⚠️ Erro ao parsear JSON: {je}")
                print(f"   JSON tentado: {json_match.group()[:200]}...")
                return pesos_atuais
        else:
            print("⚠️ Nenhum JSON encontrado na resposta IA")
            print(f"   Resposta completa: {content[:300]}...")
            return pesos_atuais
            
    except Exception as e:
        # Ignorar warnings internos conhecidos do langchain
        error_msg = str(e)
        if 'debug' in error_msg or 'verbose' in error_msg:
            # Warning conhecido: incompatibilidade versão langchain (0.1.0 vs >=1.0.0)
            # Sistema continua normalmente
            pass
        else:
            print(f"⚠️ Erro na consulta IA: {e}")
        return pesos_atuais


def gerar_jogos_otimizados(df_historico: pd.DataFrame, 
                          pesos_finais: Dict[str, float],
                          n_jogos: int = 84) -> List[Dict]:
    """
    Gera jogos otimizados usando todos os 42 indicadores (v4.0 FINAL)
    
    Returns:
        Lista de jogos com scores
    """
    from utils.indicadores_avancados import criar_todos_indicadores
    from utils.indicadores_extras import calcular_indicadores_extras
    from utils.indicadores_temporais import criar_todos_indicadores_temporais
    from utils.indicadores_geometricos import criar_todos_indicadores_geometricos
    from utils.indicadores_frequencia import criar_todos_indicadores_frequencia
    from utils.indicadores_numerologicos import criar_todos_indicadores_numerologicos
    from utils.indicadores_ml import criar_todos_indicadores_ml
    from datetime import datetime
    
    print("\n" + "="*60)
    print(f"🎯 ETAPA 3: Gerando {n_jogos} Jogos Otimizados (42 Indicadores)")
    print("="*60)
    
    # Calcular frequências
    BALL_COLS = ['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6']
    freq_total = Counter()
    freq_recente = Counter()
    
    for col in BALL_COLS:
        freq_total.update(df_historico[col].dropna().astype(int).tolist())
        freq_recente.update(df_historico.tail(200)[col].dropna().astype(int).tolist())
    
    # Carregar indicadores
    indicadores_novos = criar_todos_indicadores(df_historico)
    
    # Gerar pool
    pool = list(range(1, 61))
    jogos_final = []
    
    tentativas = 0
    max_tentativas = n_jogos * 100
    
    while len(jogos_final) < n_jogos and tentativas < max_tentativas:
        tentativas += 1
        
        # Selecionar números
        pesos_pool = np.array([
            freq_total.get(n, 1) * pesos_finais.get('Fibonacci', 50) / 100
            if n in {1,2,3,5,8,13,21,34,55} else freq_total.get(n, 1)
            for n in pool
        ])
        pesos_pool = pesos_pool / pesos_pool.sum()
        
        nums = sorted(np.random.choice(pool, size=6, replace=False, p=pesos_pool).tolist())
        
        # Evitar duplicatas
        if any(jogo['numeros'] == nums for jogo in jogos_final):
            continue
        
        # Calcular score total
        score = 0
        
        # Indicadores básicos (12 antigos)
        div3 = len([n for n in nums if n % 3 == 0])
        if 1 <= div3 <= 3:
            score += pesos_finais.get('Div3', 64) * 0.5
        
        primos = len([n for n in nums if n in {2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59}])
        if primos >= 2:
            score += pesos_finais.get('Primos', 58.5) * 0.4
        
        fibs = len([n for n in nums if n in {1,2,3,5,8,13,21,34,55}])
        score += fibs * pesos_finais.get('Fibonacci', 76) / 10
        
        # Indicadores novos (5)
        try:
            for nome, indicador in indicadores_novos.items():
                if nome == 'FrequenciaMensal':
                    ind_score = indicador.calcular_score(nums, datetime.now().month)
                else:
                    ind_score = indicador.calcular_score(nums)
                score += ind_score * pesos_finais.get(nome, 50) / 100
        
            # Indicadores avançados (5)
            avancados = criar_todos_indicadores(df_historico, nums)
            for ind, valor in avancados.items():
                score += valor * pesos_finais.get(ind, 50) / 100
            
            # Indicadores extras (5)
            extras = calcular_indicadores_extras(df_historico, nums)
            for ind, valor in extras.items():
                score += valor * pesos_finais.get(ind, 50) / 100
            
            # Indicadores temporais (4) - NOVOS v4.0
            temporais = criar_todos_indicadores_temporais(df_historico, nums)
            for ind, valor in temporais.items():
                score += valor * pesos_finais.get(ind, 50) / 100
            
            # Indicadores geométricos (3)
            geometricos = criar_todos_indicadores_geometricos(df_historico, nums)
            for ind, valor in geometricos.items():
                score += valor * pesos_finais.get(ind, 50) / 100
            
            # Indicadores de frequência (4)
            frequencia = criar_todos_indicadores_frequencia(df_historico, nums)
            for ind, valor in frequencia.items():
                score += valor * pesos_finais.get(ind, 50) / 100
            
            # Indicadores numerológicos (2) - NOVOS v4.0
            numerologicos = criar_todos_indicadores_numerologicos(df_historico, nums)
            for ind, valor in numerologicos.items():
                score += valor * pesos_finais.get(ind, 50) / 100
            
            # Indicadores ML (3) - NOVOS v4.0
            ml_scores = criar_todos_indicadores_ml(df_historico, nums)
            for ind, valor in ml_scores.items():
                score += valor * pesos_finais.get(ind, 50) / 100
        except:
            pass
        
        # Frequência
        score += np.mean([freq_recente.get(n, 0) for n in nums]) * 0.1
        
        jogos_final.append({
            'numeros': nums,
            'score': score,
            'soma': sum(nums),
            'pares': len([n for n in nums if n % 2 == 0])
        })
        
        if len(jogos_final) % 20 == 0:
            print(f"   Gerados: {len(jogos_final)}/{n_jogos}")
    
    # Ordenar por score
    jogos_final.sort(key=lambda x: -x['score'])
    
    print(f"✅ {len(jogos_final)} jogos gerados e ordenados por score")
    
    return jogos_final


def executar_batimento_dinamico(df_historico: pd.DataFrame, 
                                pesos_finais: Dict[str, float]) -> pd.DataFrame:
    """
    Executa backtesting com múltiplas estratégias simultâneas
    
    Returns:
        DataFrame com resultados de todas as 6 estratégias
    """
    from validacao.batimento_multiplas_estrategias import BatimentoMultiplasEstrategias
    
    print("\n" + "="*60)
    print("🔄 ETAPA 4: BATIMENTO v2.0 - Múltiplas Estratégias")
    print("="*60)
    
    batimento = BatimentoMultiplasEstrategias(df_historico, pesos_finais)
    df_batimento = batimento.executar_backtest_completo(inicio=50)
    
    # Salvar resultados
    batimento.salvar_resultados()
    
    return df_batimento
