"""
Teste de Leitura de Indicadores - MegaCLI
Verifica se o sistema consegue ler as abas de indicadores corretamente.
"""
import pandas as pd
import sys
from pathlib import Path

# Adicionar raiz ao path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import ARQUIVO_HISTORICO

def testar_leitura():
    print(f"\n🧪 TESTE DE LEITURA: {ARQUIVO_HISTORICO.name}")
    print("="*60)
    
    if not ARQUIVO_HISTORICO.exists():
        print("❌ Arquivo não encontrado!")
        return

    # 1. Ler LISTA INDICADORES
    print("\n📑 Lendo 'LISTA INDICADORES'...")
    try:
        df_lista = pd.read_excel(ARQUIVO_HISTORICO, sheet_name='LISTA INDICADORES')
        print(f"   ✅ Sucesso! {len(df_lista)} registros encontrados.")
        print("   🔍 Colunas detectadas:", df_lista.columns.tolist())
        
        if not df_lista.empty:
            print("\n   🔎 Exemplo (Primeiro registro):")
            row = df_lista.iloc[0]
            print(f"      - Indicador: {row.get('Indicador', 'N/A')}")
            print(f"      - Categoria: {row.get('Categoria', 'N/A')}")
            print(f"      - Descrição: {str(row.get('Descrição', 'N/A'))[:50]}...")
    except Exception as e:
        print(f"   ❌ Erro ao ler LISTA INDICADORES: {e}")

    # 2. Ler RANKING INDICADORES
    print("\n📊 Lendo 'RANKING INDICADORES'...")
    try:
        df_ranking = pd.read_excel(ARQUIVO_HISTORICO, sheet_name='RANKING INDICADORES')
        print(f"   ✅ Sucesso! {len(df_ranking)} registros encontrados.")
        print("   🔍 Colunas detectadas:", df_ranking.columns.tolist())
        
        if not df_ranking.empty:
            print(f"\n   📈 Distribuição de Pesos (Top 3):")
            if 'Peso_Atual' in df_ranking.columns:
                top3 = df_ranking.sort_values('Peso_Atual', ascending=False).head(3)
                for _, row in top3.iterrows():
                    print(f"      - {row.get('Indicador', 'N/A')}: {row.get('Peso_Atual', 0)}")
            else:
                print("      ⚠️  Coluna 'Peso_Atual' não encontrada!")
                
    except Exception as e:
        print(f"   ❌ Erro ao ler RANKING INDICADORES: {e}")

    print("\n" + "="*60)
    print("✅ Teste concluído.")

if __name__ == "__main__":
    testar_leitura()
