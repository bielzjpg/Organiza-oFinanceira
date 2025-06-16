import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread

# --- Função para autenticar no Google Sheets usando o secret ---
def autenticar_google_sheets():
    # Pega o JSON da conta de serviço do secret
    cred_json = st.secrets["google_credentials"]
    
    # Cria um arquivo temporário com o conteúdo do JSON
    with open("credenciais.json", "w") as f:
        f.write(cred_json)
    
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("credenciais.json", scopes=scopes)
    client = gspread.authorize(creds)
    return client

# --- Função para carregar dados da planilha ---
def carregar_planilha(client, spreadsheet_id, nome_aba):
    planilha = client.open_by_key(spreadsheet_id)
    aba = planilha.worksheet(nome_aba)
    dados = aba.get_all_records()
    df = pd.DataFrame(dados)
    return df, aba

# --- Função para salvar dados na planilha ---
def salvar_planilha(aba, df):
    # Limpa a aba antes de salvar
    aba.clear()
    # Atualiza a planilha com os dados do dataframe
    aba.update([df.columns.values.tolist()] + df.values.tolist())

# --- Configurações principais ---
SPREADSHEET_ID = "1bs20JYhAupfx-tZlhw0Mr86-ThxSg--_smfYJw_3ICg"
NOME_ABA = "Dados"

st.title("App de Organização Financeira com Google Sheets")

# Autentica e carrega dados
client = autenticar_google_sheets()
df, aba = carregar_planilha(client, SPREADSHEET_ID, NOME_ABA)

st.subheader("Dados atuais")
st.dataframe(df)

# Formulário para adicionar uma nova linha
st.subheader("Adicionar nova entrada")

with st.form("form_novo"):
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor", format="%.2f")
    tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
    enviado = st.form_submit_button("Adicionar")

if enviado:
    nova_linha = {"Descrição": descricao, "Valor": valor, "Tipo": tipo}
    df = df.append(nova_linha, ignore_index=True)
    salvar_planilha(aba, df)
    st.success("Entrada adicionada com sucesso! Recarregue a página para ver as mudanças.")
