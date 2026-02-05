"""
Script para exportar jogos TOP 9 para arquivo TXT
"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime


def exportar_jogos_top9_txt(jogos: List[Dict], output_path: Path):
    """
    Exporta jogos TOP 9 para arquivo TXT formatado.
    
    Args:
        jogos: Lista de jogos do TOP 9
        output_path: Caminho do arquivo de saída
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("JOGOS AUTOMÁTICOS TOP 9 - MegaCLI v6.3\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Total de jogos: {len(jogos)}\n")
        f.write(f"Combinações: C(9,6) = 84\n\n")
        
        f.write("="*70 + "\n")
        f.write("LISTA DE JOGOS\n")
        f.write("="*70 + "\n\n")
        
        for jogo in jogos:
            numeros_formatados = ' - '.join([f'{n:02d}' for n in jogo['numeros']])
            f.write(f"Jogo {jogo['id']:02d}: {numeros_formatados}\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("💡 DICA: Estes jogos usam apenas os 9 números com maior probabilidade!\n")
        f.write("="*70 + "\n")
    
    print(f"✅ Jogos exportados para: {output_path.name}")


if __name__ == "__main__":
    # Teste
    jogos_teste = [
        {'id': 1, 'numeros': [3, 5, 10, 23, 27, 33]},
        {'id': 2, 'numeros': [3, 5, 10, 23, 27, 41]},
    ]
    
    output = Path("d:/MegaCLI/Resultado/jogos_top9_teste.txt")
    exportar_jogos_top9_txt(jogos_teste, output)
    print(f"\n✅ Teste concluído! Verifique: {output}")
