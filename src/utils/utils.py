from openpyxl import load_workbook, Workbook
from typing import Dict, Any
import pandas as pd
import logging

def get_ball_columns():
    return [f'Bola{i}' for i in range(1, 7)]

def add_static_indicators(df: pd.DataFrame) -> pd.DataFrame:
    logging.info("Calculando indicadores estáticos...")
    balls = get_ball_columns()
    df_indicators = df.copy()
    df_indicators['Soma'] = df_indicators[balls].sum(axis=1)
    df_indicators['Pares'] = df_indicators[balls].apply(lambda r: sum(1 for x in r if x % 2 == 0), axis=1)
    df_indicators['Impares'] = 6 - df_indicators['Pares']
    df_indicators['Primos'] = df_indicators[balls].apply(lambda r: sum(1 for x in r if is_prime(int(x))), axis=1)
    df_indicators['Tesla_Div_3'] = df_indicators[balls].apply(lambda r: sum(1 for x in r if x % 3 == 0), axis=1)
    df_indicators['Tesla_DR_369'] = df_indicators[balls].apply(lambda r: sum(1 for x in r if get_digital_root(int(x)) in [3, 6, 9]), axis=1)
    df_indicators['Tesla_Soma_DR'] = df_indicators['Soma'].apply(lambda x: get_digital_root(int(x)))
    return df_indicators

def setup_refinement_sheet(file_path: str):
    """
    Garante que a aba 'ANALISE_REFINAMENTO' exista no arquivo Excel.
    Se não existir, cria a aba com os cabeçalhos necessários.
    """
    sheet_name = "ANALISE_REFINAMENTO"
    headers = [
        "Concurso", "Data_Predicao", 
        "Predicao_Gemini", "Estrategia_Gemini", "Acertos_Gemini",
        "Predicao_Ollama", "Estrategia_Ollama", "Acertos_Ollama",
        "Resultado_Real", "Refinamento_IA"
    ]

    try:
        workbook = load_workbook(file_path)
        if sheet_name not in workbook.sheetnames:
            print(f"Criando nova aba '{sheet_name}'...")
            sheet = workbook.create_sheet(sheet_name)
            sheet.append(headers)
            workbook.save(file_path)
    except FileNotFoundError:
        print(f"Arquivo {file_path} não encontrado. Uma nova planilha será criada com a aba de refinamento.")
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = sheet_name
        sheet.append(headers)
        # Remove a aba 'Sheet' padrão que é criada automaticamente
        if 'Sheet' in workbook.sheetnames and len(workbook.sheetnames) > 1:
            del workbook['Sheet']
        workbook.save(file_path)
    except Exception as e:
        logging.error(f"Erro ao configurar a aba de refinamento: {e}", exc_info=True)
        print(f"Ocorreu um erro ao configurar a aba '{sheet_name}': {e}")
