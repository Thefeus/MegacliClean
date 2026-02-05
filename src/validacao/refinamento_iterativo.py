"""
Sistema de Refinamento Iterativo de Indicadores e Frequências

Executa múltiplas iterações:
1. Calcula performance de cada indicador
2. Ajusta pesos baseado em resultados
3. Refina frequências de aplicação
4. Itera até convergência ou máximo de iterações
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import sys
import warnings
import json
warnings.filterwarnings('ignore')

sys.path.insert(0, 'd:\\MegaCLI')
from src.mega_final_de_ano_v2 import FILE_PATH, SOURCE_SHEET, BALL_COLS

print("="*130)
print("SISTEMA DE REFINAMENTO ITERATIVO - AJUSTE AUTOMÁTICO DE INDICADORES E FREQUÊNCIAS")
print("="*130)
print()

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

MAX_ITERACOES = 5
TAXA_APRENDIZADO = 0.1

# Pesos iniciais (da IA)
pesos_atuais = {
    'Quadrantes': 100,
    'Div9': 66,
    'Fibonacci': 64,
    'Div6': 62,
    'Mult5': 60,
    'Div3': 56,
    'Gap': 56,
    'Primos': 53,
    'Simetria': 53,
    'ParImpar': 52,
    'Amplitude': 35,
    'Soma': 22,
}

historico_refinamento = []

# ============================================================================
# FUNÇÕES
# ============================================================================

def get_quadrante(num):
    if 1 <= num <= 15: return 1
    elif 16 <= num <= 30: return 2
    elif 31 <= num <= 45: return 3
    else: return 4

def is_primo(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

FIBONACCI = {1, 2, 3, 5, 8, 13, 21, 34, 55}

def raiz_digital(n):
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n

def calcular_indicadores_basicos(numeros):
    """Calcula indicadores principais"""
    nums = sorted(numeros)
    
    quadrantes = [get_quadrante(n) for n in nums]
    dist_quad = Counter(quadrantes)
    
    return {
        'Q': tuple(dist_quad.get(i, 0) for i in range(1, 5)),
        'Pares': sum(1 for n in nums if n % 2 == 0),
        'Div3': sum(1 for n in nums if n % 3 == 0),
        'Div6': sum(1 for n in nums if n % 6 == 0),
        'Div9': sum(1 for n in nums if n % 9 == 0),
        'Soma': sum(nums),
        'Primos': sum(1 for n in nums if is_primo(n)),
        'Fibonacci': sum(1 for n in nums if n in FIBONACCI),
        'Mult5': sum(1 for n in nums if n % 5 == 0),
        'Gap': np.mean([nums[i+1] - nums[i] for i in range(5)]),
        'Amplitude': nums[-1] - nums[0],
        'Simetria': sum(1 for n in nums if abs(n - 30.5) < 15),
    }

def calcular_similaridade(real, prev, pesos):
    """Calcula similaridade ponderada por pesos"""
    score = 0
    total_peso = 0
    
    # Quadrantes
    diff_q = sum(abs(real['Q'][i] - prev['Q'][i]) for i in range(4))
    score += pesos['Quadrantes'] * (1 - diff_q / 12)
    total_peso += pesos['Quadrantes']
    
    # Outros indicadores
    for ind in ['Pares', 'Div3', 'Div6', 'Div9', 'Primos', 'Fibonacci', 'Mult5', 'Simetria']:
        key_map = {'Pares': 'ParImpar', 'Mult5': 'Mult5'}
        peso_key = key_map.get(ind, ind)
        if peso_key in pesos:
            diff = abs(real[ind] - prev[ind])
            score += pesos[peso_key] * (1 - diff / 6)
            total_peso += pesos[peso_key]
    
    # Soma
    if 'Soma' in pesos:
        diff_soma = abs(real['Soma'] - prev['Soma'])
        score += pesos['Soma'] * max(0, 1 - diff_soma / 100)
        total_peso += pesos['Soma']
    
    # Gap e Amplitude
    for ind, peso_key in [('Gap', 'Gap'), ('Amplitude', 'Amplitude')]:
        if peso_key in pesos:
            diff = abs(real[ind] - prev[ind])
            max_diff = 10 if ind == 'Gap' else 30
            score += pesos[peso_key] * max(0, 1 - diff / max_diff)
            total_peso += pesos[peso_key]
    
    return score / total_peso if total_peso > 0 else 0

# ============================================================================
# CARREGAR DADOS
# ============================================================================

print("📊 Carregando dados...")
df = pd.read_excel(FILE_PATH, sheet_name=SOURCE_SHEET).sort_values('Concurso').reset_index(drop=True)
print(f"   ✅ {len(df)} sorteios")
print()

# Usar últimos 200 jogos para iteração rápida
inicio = len(df) - 200

print("="*130)
print("INICIANDO REFINAMENTO ITERATIVO")
print("="*130)
print()

# ============================================================================
# LOOP DE REFINAMENTO
# ============================================================================

for iteracao in range(1, MAX_ITERACOES + 1):
    print(f"\n{'='*130}")
    print(f"ITERAÇÃO {iteracao}/{MAX_ITERACOES}")
    print(f"{'='*130}\n")
    
    print(f"Pesos atuais (Top 5):")
    for ind, peso in sorted(pesos_atuais.items(), key=lambda x: -x[1])[:5]:
        print(f"   {ind:15s}: {peso:6.1f}")
    print()
    
    # Executar validação com pesos atuais
    resultados = []
    performance_indicadores = defaultdict(list)
    
    for idx in range(inicio, len(df)):
        df_treino = df.iloc[:idx]
        row_real = df.iloc[idx]
        
        nums_reais = sorted([int(row_real[col]) for col in BALL_COLS if pd.notna(row_real[col])])
        if len(nums_reais) != 6:
            continue
        
        # Previsão simples baseada em frequência
        freq = Counter()
        for col in BALL_COLS:
            freq.update(df_treino[col].dropna().astype(int).tolist())
        
        pool = list(range(1, 61))
        pesos_pool = [freq.get(n, 0) + 1 for n in pool]
        candidatos = np.random.choice(pool, size=8, replace=False, p=np.array(pesos_pool)/sum(pesos_pool))
        previsao = sorted(candidatos[:6].tolist())
        
        # Calcular indicadores
        ind_real = calcular_indicadores_basicos(nums_reais)
        ind_prev = calcular_indicadores_basicos(previsao)
        
        # Calcular similaridade
        similaridade = calcular_similaridade(ind_real, ind_prev, pesos_atuais)
        
        # Acertos
        acertos = len(set(previsao).intersection(set(nums_reais)))
        
        # Registrar performance por indicador
        for ind in ['Quadrantes', 'ParImpar', 'Div3', 'Div6', 'Div9', 'Soma', 'Primos', 'Fibonacci', 'Mult5', 'Gap', 'Amplitude', 'Simetria']:
            if ind == 'Quadrantes':
                diff = sum(abs(ind_real['Q'][i] - ind_prev['Q'][i]) for i in range(4)) / 12
            elif ind == 'ParImpar':
                diff = abs(ind_real['Pares'] - ind_prev['Pares']) / 6
            elif ind == 'Soma':
                diff = abs(ind_real['Soma'] - ind_prev['Soma']) / 100
            elif ind in ['Gap', 'Amplitude']:
                key = ind
                max_val = 10 if ind == 'Gap' else 30
                diff = abs(ind_real[key] - ind_prev[key]) / max_val
            else:
                key = ind if ind in ind_real else {'Mult5': 'Mult5'}.get(ind, ind)
                diff = abs(ind_real.get(key, 0) - ind_prev.get(key, 0)) / 6
            
            performance = 1 - min(1, diff)
            performance_indicadores[ind].append(performance)
        
        resultados.append({
            'acertos': acertos,
            'similaridade': similaridade,
        })
    
    # Calcular métricas da iteração
    media_acertos = np.mean([r['acertos'] for r in resultados])
    media_similaridade = np.mean([r['similaridade'] for r in resultados])
    taxa_3plus = sum(1 for r in resultados if r['acertos'] >= 3) / len(resultados) * 100
    
    print(f"📊 Resultados da Iteração {iteracao}:")
    print(f"   Média de acertos: {media_acertos:.3f}")
    print(f"   Similaridade média: {media_similaridade:.3f}")
    print(f"   Taxa >= 3 acertos: {taxa_3plus:.1f}%")
    print()
    
    # Registrar histórico
    historico_refinamento.append({
        'iteracao': iteracao,
        'media_acertos': media_acertos,
        'similaridade': media_similaridade,
        'taxa_3plus': taxa_3plus,
        'pesos': pesos_atuais.copy(),
    })
    
    # AJUSTAR PESOS baseado na performance
    print(f"🔧 Ajustando pesos...")
    
    novos_pesos = {}
    for ind, perfs in performance_indicadores.items():
        perf_media = np.mean(perfs)
        
        # Ajuste: aumentar peso se performance boa, diminuir se ruim
        if ind in pesos_atuais:
            peso_atual = pesos_atuais[ind]
            
            # Fator de ajuste baseado em performance (0.5 a 1.5)
            fator = 0.5 + perf_media
            
            # Aplicar ajuste gradual
            novo_peso = peso_atual * (1 + (fator - 1) * TAXA_APRENDIZADO)
            
            # Limitar entre 10 e 100
            novo_peso = max(10, min(100, novo_peso))
            
            novos_pesos[ind] = novo_peso
    
    # Atualizar pesos
    pesos_anteriores = pesos_atuais.copy()
    pesos_atuais = novos_pesos
    
    # Mostrar maiores mudanças
    mudancas = []
    for ind in pesos_atuais:
        if ind in pesos_anteriores:
            delta = pesos_atuais[ind] - pesos_anteriores[ind]
            if abs(delta) > 0.1:
                mudancas.append((ind, delta))
    
    if mudancas:
        print(f"   Maiores ajustes:")
        for ind, delta in sorted(mudancas, key=lambda x: -abs(x[1]))[:5]:
            print(f"      {ind:15s}: {delta:+6.1f}")
    else:
        print(f"   Convergiu! Sem mudanças significativas.")
        break
    
    print()

# ============================================================================
# RESULTADOS FINAIS
# ============================================================================

print("\n" + "="*130)
print("RESULTADOS DO REFINAMENTO")
print("="*130)
print()

print("📈 Evolução das Métricas:")
print()
print("| Iteração | Média Acertos | Similaridade | Taxa >=3 | Melhoria |")
print("|----------|---------------|--------------|----------|----------|")

for i, hist in enumerate(historico_refinamento):
    if i == 0:
        melhoria = "baseline"
    else:
        delta = hist['media_acertos'] - historico_refinamento[i-1]['media_acertos']
        melhoria = f"{delta:+.3f}"
    
    print(f"| {hist['iteracao']:8d} | {hist['media_acertos']:13.3f} | {hist['similaridade']:12.3f} | {hist['taxa_3plus']:7.1f}% | {melhoria:8s} |")

print()

# Pesos finais
print("🎯 PESOS FINAIS REFINADOS:")
print()
for ind, peso in sorted(pesos_atuais.items(), key=lambda x: -x[1]):
    print(f"   {ind:15s}: {peso:6.1f}")

print()

# Salvar resultados
excel_file = 'd:\\MegaCLI\\Resultado\\ANALISE_HISTORICO_COMPLETO.xlsx'

with pd.ExcelFile(excel_file) as xls:
    abas_existentes = {}
    for sheet_name in xls.sheet_names:
        if sheet_name not in ['REFINAMENTO ITERATIVO', 'PESOS REFINADOS']:
            abas_existentes[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)

# Aba de evolução
df_evolucao = pd.DataFrame(historico_refinamento)
df_evolucao = df_evolucao[['iteracao', 'media_acertos', 'similaridade', 'taxa_3plus']]
abas_existentes['REFINAMENTO ITERATIVO'] = df_evolucao

# Aba de pesos refinados
pesos_data = []
for ind, peso in sorted(pesos_atuais.items(), key=lambda x: -x[1]):
    pesos_data.append({
        'Indicador': ind,
        'Peso_Final': round(peso, 1),
        'Peso_IA_Original': PESOS_IA.get(ind, 0) if 'PESOS_IA' in dir() else 0,
        'Ajuste': round(peso - PESOS_IA.get(ind, 0), 1) if 'PESOS_IA' in dir() else 0,
    })

# Adicionar pesos da IA se não existir
if 'PESOS_IA' not in dir():
    PESOS_IA = {
        'Quadrantes': 100, 'Div9': 66, 'Fibonacci': 64, 'Div6': 62, 'Mult5': 60,
        'Div3': 56, 'Gap': 56, 'Primos': 53, 'Simetria': 53, 'ParImpar': 52,
        'Amplitude': 35, 'Soma': 22,
    }
    
    # Recalcular ajuste
    for item in pesos_data:
        item['Peso_IA_Original'] = PESOS_IA.get(item['Indicador'], 0)
        item['Ajuste'] = round(item['Peso_Final'] - item['Peso_IA_Original'], 1)

abas_existentes['PESOS REFINADOS'] = pd.DataFrame(pesos_data)

with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    for sheet_name, df_sheet in abas_existentes.items():
        df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)

print("="*130)
print("💾 SALVANDO RESULTADOS")
print("="*130)
print()
print(f"   ✅ Planilha atualizada: {excel_file}")
print(f"   📊 REFINAMENTO ITERATIVO: Evolução das métricas")
print(f"   📊 PESOS REFINADOS: Pesos finais após {len(historico_refinamento)} iterações")
print()

melhoria_total = historico_refinamento[-1]['media_acertos'] - historico_refinamento[0]['media_acertos']
print(f"✨ Melhoria total: {melhoria_total:+.3f} acertos")
print()

print("="*130)
print("✅ REFINAMENTO ITERATIVO CONCLUÍDO!")
print("="*130)
