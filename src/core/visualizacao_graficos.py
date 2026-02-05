"""
Visualização Gráfica - MegaCLI v6.3

Gera gráficos para visualização de probabilidades e análise.

Autor: MegaCLI Team
Data: 02/02/2026
Versão: 1.0.0
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any
import warnings

warnings.filterwarnings('ignore')

# Configurar estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def criar_grafico_top20_scores(
    numeros: List[int],
    scores: Dict[int, float],
    output_path: Path,
    top_9: List[int] = None
):
    """
    Cria gráfico de barras com scores do TOP 20.
    
    Args:
        numeros: Lista dos 20 números
        scores: Dict com scores de cada número
        output_path: Caminho para salvar PNG
        top_9: Lista opcional dos TOP 9 para destacar
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    valores = [scores.get(n, 0) for n in numeros]
    cores = ['#2ecc71' if (top_9 and n in top_9) else '#3498db' for n in numeros]
    
    bars = ax.bar(range(len(numeros)), valores, color=cores, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Customização
    ax.set_xticks(range(len(numeros)))
    ax.set_xticklabels([f'{n:02d}' for n in numeros], fontsize=11, fontweight='bold')
    ax.set_xlabel('Número', fontsize=13, fontweight='bold')
    ax.set_ylabel('Score de Probabilidade', fontsize=13, fontweight='bold')
    ax.set_title('TOP 20 Números - Scores de Probabilidade', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Adicionar valores nas barras
    for i, (bar, val) in enumerate(zip(bars, valores)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{val:.0f}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Legenda
    if top_9:
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#2ecc71', label='TOP 9 (Melhores)'),
            Patch(facecolor='#3498db', label='TOP 10-20')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Gráfico TOP 20 salvo: {output_path.name}")


def criar_heatmap_probabilidades(
    scores: Dict[int, float],
    output_path: Path
):
    """
    Cria heatmap 6x10 com todos os 60 números.
    
    Args:
        scores: Dict com scores de cada número (1-60)
        output_path: Caminho para salvar PNG
    """
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Criar matriz 6x10
    matriz = np.zeros((6, 10))
    anotacoes = []
    
    for num in range(1, 61):
        row = (num - 1) // 10
        col = (num - 1) % 10
        score = scores.get(num, 0)
        matriz[row, col] = score
        anotacoes.append(f'{num:02d}\n{score:.0f}')
    
    anotacoes = np.array(anotacoes).reshape((6, 10))
    
    # Criar heatmap
    sns.heatmap(matriz, annot=anotacoes, fmt='', cmap='RdYlGn',
                cbar_kws={'label': 'Score de Probabilidade'},
                linewidths=1.5, linecolor='black',
                vmin=0, vmax=100,
                ax=ax)
    
    ax.set_title('Heatmap de Probabilidades - Todos os Números (1-60)',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Coluna', fontsize=13, fontweight='bold')
    ax.set_ylabel('Linha', fontsize=13, fontweight='bold')
    
    # Remover ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Heatmap salvo: {output_path.name}")


def criar_grafico_historico_acertos(
    analise_correlacao: Dict[str, Any],
    output_path: Path
):
    """
    Cria gráfico de linha com histórico de acertos.
    
    Args:
        analise_correlacao: Resultado da análise de correlação
        output_path: Caminho para salvar PNG
    """
    if not analise_correlacao or not analise_correlacao.get('sucesso'):
        print("   ⚠️ Análise de correlação não disponível para gráfico")
        return
    
    detalhes = analise_correlacao.get('detalhes', [])
    if not detalhes:
        print("   ⚠️ Sem dados históricos suficientes")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Gráfico 1: Linha de acertos
    concursos = [d['concurso'] for d in detalhes]
    acertos = [d['acertos'] for d in detalhes]
    
    ax1.plot(range(len(acertos)), acertos, marker='o', linewidth=2, 
             markersize=8, color='#3498db', label='Acertos')
    ax1.axhline(y=analise_correlacao['acertos_medio'], color='#e74c3c', 
                linestyle='--', linewidth=2, label=f'Média: {analise_correlacao["acertos_medio"]:.1f}')
    ax1.fill_between(range(len(acertos)), acertos, alpha=0.3, color='#3498db')
    
    ax1.set_xlabel('Sorteios Analisados', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Número de Acertos', fontsize=12, fontweight='bold')
    ax1.set_title('Histórico de Acertos - TOP 9 vs Sorteios Reais',
                  fontsize=14, fontweight='bold', pad=15)
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=10)
    ax1.set_ylim(-0.5, 6.5)
    ax1.set_yticks(range(7))
    
    # Gráfico 2: Distribuição (barras)
    dist = analise_correlacao['distribuicao_acertos']
    categorias = [f'{i} acertos' for i in range(7)]
    valores = [dist[f'{i}_acertos'] for i in range(7)]
    cores_dist = ['#e74c3c', '#e67e22', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60', '#16a085']
    
    bars = ax2.bar(categorias, valores, color=cores_dist, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax2.set_xlabel('Categoria', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Frequência', fontsize=12, fontweight='bold')
    ax2.set_title('Distribuição de Acertos',
                  fontsize=14, fontweight='bold', pad=15)
    ax2.grid(axis='y', alpha=0.3)
    
    # Adicionar percentuais
    n_total = sum(valores)
    for bar, val in zip(bars, valores):
        height = bar.get_height()
        if val > 0:
            pct = val / n_total * 100
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                    f'{val}\n({pct:.1f}%)',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Gráfico histórico salvo: {output_path.name}")


def criar_grafico_distribuicao_top9(
    top_9: List[int],
    output_path: Path
):
    """
    Cria visualização da distribuição do TOP 9 na grade 1-60.
    
    Args:
        top_9: Lista dos 9 números no TOP 9
        output_path: Caminho para salvar PNG
    """
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Criar matriz 6x10
    matriz = np.zeros((6, 10))
    
    for num in range(1, 61):
        row = (num - 1) // 10
        col = (num - 1) % 10
        if num in top_9:
            matriz[row, col] = 1
    
    # Criar anotações
    anotacoes = []
    for num in range(1, 61):
        if num in top_9:
            anotacoes.append(f'{num:02d}\n⭐')
        else:
            anotacoes.append(f'{num:02d}')
    
    anotacoes = np.array(anotacoes).reshape((6, 10))
    
    # Criar heatmap
    cmap = sns.color_palette(['#ecf0f1', '#2ecc71'], as_cmap=True)
    sns.heatmap(matriz, annot=anotacoes, fmt='', cmap=cmap,
                cbar=False,
                linewidths=2, linecolor='black',
                vmin=0, vmax=1,
                ax=ax)
    
    ax.set_title('Distribuição do TOP 9 na Grade Completa (1-60)',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('', fontsize=13)
    ax.set_ylabel('', fontsize=13)
    
    # Remover ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Adicionar legenda
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ecc71', label='TOP 9 (Maior probabilidade)'),
        Patch(facecolor='#ecf0f1', label='Outros números')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Gráfico distribuição TOP 9 salvo: {output_path.name}")


def gerar_todas_visualizacoes(
    resultado: Dict[str, Any],
    output_dir: Path
) -> List[Path]:
    """
    Gera todas as visualizações do modo conservador.
    
    Args:
        resultado: Resultado completo do modo conservador
        output_dir: Diretório para salvar gráficos
        
    Returns:
        Lista de caminhos dos gráficos gerados
    """
    print("\n📊 Gerando visualizações gráficas...")
    
    # Criar diretório se não existir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    arquivos_gerados = []
    
    try:
        # Extrair dados
        universo = resultado.get('universo', {})
        scores = universo.get('scores', {})
        top_20 = resultado['previsoes']['top_20']['numeros']
        top_9 = resultado['previsoes']['top_9']['numeros']
        analise_corr = resultado.get('analise_correlacao')
        
        # 1. Gráfico TOP 20
        path_top20 = output_dir / 'top20_scores.png'
        criar_grafico_top20_scores(top_20, scores, path_top20, top_9)
        arquivos_gerados.append(path_top20)
        
        # 2. Heatmap completo
        path_heatmap = output_dir / 'heatmap_probabilidades.png'
        criar_heatmap_probabilidades(scores, path_heatmap)
        arquivos_gerados.append(path_heatmap)
        
        # 3. Distribuição TOP 9
        path_dist = output_dir / 'distribuicao_top9.png'
        criar_grafico_distribuicao_top9(top_9, path_dist)
        arquivos_gerados.append(path_dist)
        
        # 4. Histórico de acertos (se disponível)
        if analise_corr and analise_corr.get('sucesso'):
            path_hist = output_dir / 'historico_acertos.png'
            criar_grafico_historico_acertos(analise_corr, path_hist)
            arquivos_gerados.append(path_hist)
        
        print(f"\n✅ {len(arquivos_gerados)} visualizações geradas com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar visualizações: {e}")
        import traceback
        traceback.print_exc()
    
    return arquivos_gerados


# Exports
__all__ = [
    'criar_grafico_top20_scores',
    'criar_heatmap_probabilidades',
    'criar_grafico_historico_acertos',
    'criar_grafico_distribuicao_top9',
    'gerar_todas_visualizacoes'
]


# Teste standalone
if __name__ == "__main__":
    print("\n🧪 Testando Visualização Gráfica...\n")
    print("(Necessita dados reais para teste completo)")
    print("Execute via modo conservador")
