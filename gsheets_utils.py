import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Escopo da API
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def autenticar_google_sheets(caminho_credenciais_json):
    creds = ServiceAccountCredentials.from_json_keyfile_name(caminho_credenciais_json, SCOPE)
    cliente = gspread.authorize(creds)
    return cliente

def carregar_planilha(cliente, id_planilha, nome_aba="Sheet1"):
    planilha = cliente.open_by_key(id_planilha)
    aba = planilha.worksheet(nome_aba)
    dados = aba.get_all_records()
    df = pd.DataFrame(dados)
    if df.empty:
        # Cria colunas padrão se estiver vazia
        df = pd.DataFrame(columns=["id", "tipo", "categoria", "descricao", "valor", "data"])
    else:
        # Converte coluna data para datetime
        df["data"] = pd.to_datetime(df["data"], errors='coerce')
    return df, aba

def salvar_planilha(df, aba):
    # Converte o dataframe para lista de listas (com cabeçalho)
    dados = [df.columns.values.tolist()] + df.fillna("").astype(str).values.tolist()
    aba.clear()
    aba.update(dados)
