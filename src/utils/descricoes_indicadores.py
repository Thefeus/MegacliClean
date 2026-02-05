"""
Descrições e Categorias dos Indicadores - MegaCLI v6.1

Centraliza informações descritivas completas sobre os 42 indicadores do sistema.
Usado para enriquecer a aba LISTA INDICADORES com documentação técnica.
"""

def criar_dicionario_completo() -> dict:
    """
    Retorna documentação completa de cada indicador.
    
    Returns:
        Dict {nome_indicador: {descricao, categoria, aplicacao, parametros, formula}}
    """
    return {
        # === BÁSICOS (12) ===
        'Quadrantes': {
            'descricao': 'Distribuição pelos 4 quadrantes (1-15, 16-30, 31-45, 46-60)',
            'categoria': 'Geométrico',
            'aplicacao': 'Verificar se o jogo está bem distribuído espacialmente no volante.',
            'parametros': 'Q1=[01-15], Q2=[16-30], Q3=[31-45], Q4=[46-60]',
            'formula': 'Count(n in Qi) para i=1..4'
        },
        'Div9': {
            'descricao': 'Quantidade de números divisíveis por 9',
            'categoria': 'Numerológico',
            'aplicacao': 'Filtrar jogos com excesso ou falta de múltiplos de 9.',
            'parametros': 'Conjunto M9 = {9, 18, 27, 36, 45, 54}',
            'formula': 'Count(n % 9 == 0)'
        },
        'Fibonacci': {
            'descricao': 'Números da sequência de Fibonacci presentes no jogo',
            'categoria': 'Numerológico',
            'aplicacao': 'Identificar presença de números da sequência áurea.',
            'parametros': 'Seq = {1, 2, 3, 5, 8, 13, 21, 34, 55}',
            'formula': 'Count(n in Fibonacci_Set)'
        },
        'Div6': {
            'descricao': 'Quantidade de números divisíveis por 6',
            'categoria': 'Numerológico',
            'aplicacao': 'Análise de multiplicidade por 6.',
            'parametros': 'M6 = {6, 12, 18, 24, 30, 36, 42, 48, 54, 60}',
            'formula': 'Count(n % 6 == 0)'
        },
        'Mult5': {
            'descricao': 'Múltiplos de 5 presentes no jogo',
            'categoria': 'Numerológico',
            'aplicacao': 'Verificar números terminados em 0 ou 5.',
            'parametros': 'M5 = {5, 10, ..., 60}',
            'formula': 'Count(n % 5 == 0)'
        },
        'Div3': {
            'descricao': 'Quantidade de números divisíveis por 3',
            'categoria': 'Numerológico',
            'aplicacao': 'Balanço de múltiplos de 3.',
            'parametros': 'M3 = {3, 6, ..., 60}',
            'formula': 'Count(n % 3 == 0)'
        },
        'Gap': {
            'descricao': 'Distância média entre números consecutivos ordenados',
            'categoria': 'Estatístico',
            'aplicacao': 'Evitar jogos muito aglomerados ou muito dispersos.',
            'parametros': 'Lista ordenada L = [n1, n2, ..., n6]',
            'formula': 'Mean(L[i+1] - L[i]) para i=0..4'
        },
        'Primos': {
            'descricao': 'Quantidade de números primos no jogo',
            'categoria': 'Numerológico',
            'aplicacao': 'Equilíbrio de números primos (geralmente 1 a 3).',
            'parametros': 'Primos = {2, 3, 5, 7, 11, ..., 59}',
            'formula': 'Count(n in Primos_Set)'
        },
        'Simetria': {
            'descricao': 'Equilíbrio de números em torno do centro (30.5)',
            'categoria': 'Estatístico',
            'aplicacao': 'Medir se o jogo pende para números baixos ou altos.',
            'parametros': 'Centro = 30.5',
            'formula': 'Count(n > 30.5) vs Count(n < 30.5)'
        },
        'ParImpar': {
            'descricao': 'Equilíbrio entre números pares e ímpares',
            'categoria': 'Numerológico',
            'aplicacao': 'Busca pelo padrão mais comum (3P-3I ou 4P-2I/2P-4I).',
            'parametros': 'Nenhum',
            'formula': 'Count(n % 2 == 0) vs Count(n % 2 != 0)'
        },
        'Amplitude': {
            'descricao': 'Diferença entre o maior e menor número do jogo',
            'categoria': 'Estatístico',
            'aplicacao': 'Avaliar a dispersão total do jogo.',
            'parametros': 'Max(L), Min(L)',
            'formula': 'Max(Jogo) - Min(Jogo)'
        },
        'Soma': {
            'descricao': 'Soma total dos 6 números do jogo',
            'categoria': 'Estatístico',
            'aplicacao': 'Métrica fundamental para corte (faixa ideal 150-240).',
            'parametros': 'Faixa típica: 120 a 270',
            'formula': 'Sum(n) for n in Jogo'
        },
        
        # === AVANÇADOS (5) ===
        'RaizDigital': {
            'descricao': 'Soma iterativa dos dígitos até chegar a um único número',
            'categoria': 'Numerológico',
            'aplicacao': 'Padrões místicos/matemáticos de redução.',
            'parametros': 'Ex: 59 -> 5+9=14 -> 1+4=5',
            'formula': '((n - 1) % 9) + 1'
        },
        'VariacaoSoma': {
            'descricao': 'Desvio da soma em relação à média histórica',
            'categoria': 'Estatístico',
            'aplicacao': 'Detectar se a soma está anômala comparada à série.',
            'parametros': 'Média Histórica Global',
            'formula': 'Abs(Soma(Jogo) - Média_Hist)'
        },
        'Conjugacao': {
            'descricao': 'Relação entre números conjugados (soma = 61)',
            'categoria': 'Numerológico',
            'aplicacao': 'Paridade espelhada (ex: 01 e 60).',
            'parametros': 'Conjugado(n) = 61 - n',
            'formula': 'Count(n in Jogo AND (61-n) in Jogo)'
        },
        'RepeticaoAnterior': {
            'descricao': 'Repetição de números do jogo imediatamente anterior',
            'categoria': 'Temporal',
            'aplicacao': 'Análise de persistência de sorteio.',
            'parametros': 'Jogo Anterior (t-1)',
            'formula': 'Count(n in Jogo_t-1)'
        },
        'FrequenciaMensal': {
            'descricao': 'Padrão de frequência em ciclos mensais',
            'categoria': 'Frequência',
            'aplicacao': 'Identificar "números do mês" ou sazonais.',
            'parametros': 'Mês corrente',
            'formula': 'Freq(n) in Month(Data)'
        },
        
        # === EXTRAS (5) ===
        'Sequencias': {
            'descricao': 'Quantidade de números consecutivos no jogo',
            'categoria': 'Padrões',
            'aplicacao': 'Rastrear sequências (ex: 01-02, 10-11-12).',
            'parametros': 'Adjacência +/- 1',
            'formula': 'Count(Sort(L)[i+1] == Sort(L)[i] + 1)'
        },
        'DistanciaMedia': {
            'descricao': 'Distância média entre todos os pares de números',
            'categoria': 'Estatístico',
            'aplicacao': 'Métrica de espalhamento global.',
            'parametros': 'N=6',
            'formula': 'Sum(Dist(ni, nj)) / Combinations(6,2)'
        },
        'NumerosExtremos': {
            'descricao': 'Análise de números extremos (muito baixos ou altos)',
            'categoria': 'Padrões',
            'aplicacao': 'Detectar bordas do volante (1-5 e 55-60).',
            'parametros': 'Faixas [1,5] e [56,60]',
            'formula': 'Count(n < 6 OR n > 55)'
        },
        'PadraoDezena': {
            'descricao': 'Distribuição pelas dezenas (0-9, 10-19, ...)',
            'categoria': 'Padrões',
            'aplicacao': 'Verificar linhas do volante.',
            'parametros': 'L0, L1, L2, L3, L4, L5',
            'formula': 'Histograma(Floor(n/10))'
        },
        'CicloAparicao': {
            'descricao': 'Ciclo de aparição dos números (periodicidade)',
            'categoria': 'Temporal',
            'aplicacao': 'Identificar números atrasados ou quentes.',
            'parametros': 'Atraso Atual',
            'formula': 'Concurso_Atual - Ultima_Aparicao(n)'
        },
        
        # === TEMPORAIS (4) ===
        'TendenciaQuadrantes': {
            'descricao': 'Tendência de evolução dos quadrantes no tempo',
            'categoria': 'Temporal',
            'aplicacao': 'Análise de momentum de setores.',
            'parametros': 'Janela Móvel (ex: 10 jogos)',
            'formula': 'Slope(LinReg(Freq_Quadrante, tempo))'
        },
        'CiclosSemanais': {
            'descricao': 'Padrões relacionados ao dia da semana do sorteio',
            'categoria': 'Temporal',
            'aplicacao': 'Verificar se terças/quintas/sábados têm viés.',
            'parametros': 'Dia da Semana (0-6)',
            'formula': 'Freq(n) group directly by WeekDay'
        },
        'AcumulacaoConsecutiva': {
            'descricao': 'Acumulação de sorteios em concursos seguidos',
            'categoria': 'Temporal',
            'aplicacao': 'Detectar anomalias de repetição em curto prazo.',
            'parametros': 'Lag 1, 2, 3',
            'formula': 'Sum(Repeated_Elements) over Window'
        },
        'JanelaDeslizante': {
            'descricao': 'Análise estatística em janelas temporais deslizantes',
            'categoria': 'Temporal',
            'aplicacao': 'Média móvel de indicadores.',
            'parametros': 'Window Size (10, 50, 100)',
            'formula': 'Avg(Score) over [t-W, t]'
        },
        
        # === GEOMÉTRICOS (3) ===
        'MatrizPosicional': {
            'descricao': 'Análise da posição dos números em matriz 6x10',
            'categoria': 'Geométrico',
            'aplicacao': 'Reconhecimento de formas visuais no volante.',
            'parametros': 'Grid 6x10',
            'formula': 'Mapping(n -> (row, col))'
        },
        'ClusterEspacial': {
            'descricao': 'Agrupamento espacial dos números (K-Means like)',
            'categoria': 'Geométrico',
            'aplicacao': 'Detectar "bolhas" de números sorteados juntos.',
            'parametros': 'Distância Euclidiana',
            'formula': 'Density(n) in Grid'
        },
        'SimetriaCentral': {
            'descricao': 'Simetria em relação ao ponto central geográfico',
            'categoria': 'Geométrico',
            'aplicacao': 'Equilíbrio visual Radial.',
            'parametros': 'Centro Geom (3.5, 5.5)',
            'formula': 'Dist(Point, Center)'
        },
        
        # === FREQUÊNCIA (4) ===
        'FrequenciaRelativa': {
            'descricao': 'Frequência relativa de aparições recentes',
            'categoria': 'Frequência',
            'aplicacao': 'Peso base para "números quentes".',
            'parametros': 'Total Sorteios',
            'formula': 'Count(n) / Total_Concursos'
        },
        'DesvioFrequencia': {
            'descricao': 'Desvio da frequência atual em relação à teórica',
            'categoria': 'Frequência',
            'aplicacao': 'Identificar números que saem mais que a probabilidade estatística.',
            'parametros': 'Prob Teórica = 1/60',
            'formula': '(Freq_Real - Freq_Teorica) / Freq_Teorica'
        },
        'EntrópiaDistribuicao': {
            'descricao': 'Entropia (Shannon) da distribuição dos números',
            'categoria': 'Frequência',
            'aplicacao': 'Medir a "desordem" ou imprevisibilidade.',
            'parametros': 'P(x)',
            'formula': '-Sum(p(x) * log(p(x)))'
        },
        'CorrelacaoTemporal': {
            'descricao': 'Correlação temporal entre sorteios (Autocorrelação)',
            'categoria': 'Frequência',
            'aplicacao': 'Detectar dependência entre t e t-k.',
            'parametros': 'Lag k',
            'formula': 'Corr(Serie_t, Serie_t-k)'
        },
        
        # === NUMEROLÓGICOS (2) ===
        'SomaDigitos': {
            'descricao': 'Soma dos dígitos individuais de todos os números',
            'categoria': 'Numerológico',
            'aplicacao': 'Redução dimensional numérica.',
            'parametros': 'Dezenas 0-9',
            'formula': 'Sum(Digit1(n) + Digit2(n))'
        },
        'PadraoModular': {
            'descricao': 'Padrão modular (resto da divisão) dos números',
            'categoria': 'Numerológico',
            'aplicacao': 'Análise de congruência (ex: Mod 3, Mod 4).',
            'parametros': 'Módulo K',
            'formula': '[n % K for n in Jogo]'
        },
        
        # === MACHINE LEARNING (3) ===
        'ScoreAnomalia': {
            'descricao': 'Score de detecção de anomalias por Isolation Forest',
            'categoria': 'Machine Learning',
            'aplicacao': 'Filtrar jogos "estranhos" que fogem do padrão aprendido.',
            'parametros': 'Contamination=0.01',
            'formula': 'IsolationForest.decision_function(X)'
        },
        'ProbabilidadeCondicional': {
            'descricao': 'Probabilidade condicional (Bayes/Markov) baseada em histórico',
            'categoria': 'Machine Learning',
            'aplicacao': 'Prever próximo número dado os atuais.',
            'parametros': 'Matriz de Transição',
            'formula': 'P(A|B) = P(B|A)*P(A)/P(B)'
        },
        'ImportanciaFeature': {
            'descricao': 'Importância de features extraída de Random Forest',
            'categoria': 'Machine Learning',
            'aplicacao': 'Ponderação dinâmica de quais regras importam mais.',
            'parametros': 'Gini Importance',
            'formula': 'RF.feature_importances_'
        },
        
        # === ANÁLISE IA (4) ===
        'PadroesSubconjuntos': {
            'descricao': 'Padrões de subconjuntos complexos detectados pela IA',
            'categoria': 'Análise IA',
            'aplicacao': 'Deep Learning para sets de 3 ou 4 números.',
            'parametros': 'Neural Network Layers',
            'formula': 'NN(Input_Subset)'
        },
        'MicroTendencias': {
            'descricao': 'Micro-tendências de curto prazo identificadas pela IA',
            'categoria': 'Análise IA',
            'aplicacao': 'Ajuste fino para os próximos 1-3 concursos.',
            'parametros': 'Janela Curta (5-10)',
            'formula': 'LSTM_Prediction(Sequence)'
        },
        'AnaliseContextual': {
            'descricao': 'Análise contextual completa (dados externos + histórico) pela IA',
            'categoria': 'Análise IA',
            'aplicacao': 'Fusion de múltiplas fontes de sinal.',
            'parametros': 'Context Vector',
            'formula': 'Transformer_Model(Context)'
        },
        'Embedding': {
            'descricao': 'Representação vetorial (embedding) latente dos padrões',
            'categoria': 'Análise IA',
            'aplicacao': 'Similaridade vetorial entre jogos.',
            'parametros': 'Dimensão (ex: 64d)',
            'formula': 'Embedding_Layer(Jogo)'
        }
    }

def obter_info_completa(nome: str) -> dict:
    """Wrapper para compatibilidade"""
    tudo = criar_dicionario_completo()
    return tudo.get(nome, {
        'descricao': 'Descrição não disponível',
        'categoria': 'Outro',
        'aplicacao': '-',
        'parametros': '-',
        'formula': '-'
    })

def criar_dicionario_descricoes() -> dict:
    """Compatibilidade Legado"""
    return {k: v['descricao'] for k, v in criar_dicionario_completo().items()}

def criar_dicionario_categorias() -> dict:
    """Compatibilidade Legado"""
    return {k: v['categoria'] for k, v in criar_dicionario_completo().items()}

