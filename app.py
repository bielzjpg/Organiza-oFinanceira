import streamlit as st
import json
from google.oauth2 import service_account
import gspread
from datetime import datetime

# Configurações iniciais do app
st.set_page_config(page_title="Organização Financeira", layout="centered")

st.title("📊 Organização Financeira")

# Carregar credenciais do Google Sheets via secrets
json_str = st.secrets["google_credentials"]
credentials_info = json.loads(json_str)
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Autenticar e acessar Google Sheets
client = gspread.authorize(credentials)

# ID da planilha e nome da aba
SPREADSHEET_ID = "1bs20JYhAupfx-tZlhw0Mr86-ThxSg--_smfYJw_3ICg"
WORKSHEET_NAME = "Dados"

# Função para carregar dados da planilha
@st.cache_data(ttl=300)
def carregar_dados():
    try:
        planilha = client.open_by_key(SPREADSHEET_ID)
        aba = planilha.worksheet(WORKSHEET_NAME)
        dados = aba.get_all_records()
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar dados da planilha: {e}")
        return []

# Função para adicionar nova receita/despesa
def adicionar_lancamento(tipo, valor, descricao):
    try:
        planilha = client.open_by_key(SPREADSHEET_ID)
        aba = planilha.worksheet(WORKSHEET_NAME)
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nova_linha = [data_hora, tipo, descricao, valor]
        aba.append_row(nova_linha)
        st.success(f"{tipo.capitalize()} adicionada com sucesso!")
    except Exception as e:
        st.error(f"Erro ao adicionar lançamento: {e}")

# Interface do app
dados = carregar_dados()

if dados:
    df = st.experimental_data_editor(dados, num_rows="dynamic")
else:
    st.info("Nenhum dado encontrado na planilha.")

st.write("---")

st.subheader("Adicionar Receita / Despesa")

with st.form("form_lancamento"):
    tipo = st.selectbox("Tipo", ["receita", "despesa"])
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor", min_value=0.01, format="%.2f")
    enviar = st.form_submit_button("Adicionar")

    if enviar:
        if descricao.strip() == "":
            st.warning("Por favor, informe a descrição.")
        else:
            adicionar_lancamento(tipo, valor, descricao)

# Exibir resumo simples
if dados:
    total_receitas = sum(item["valor"] for item in dados if item["tipo"] == "receita")
    total_despesas = sum(item["valor"] for item in dados if item["tipo"] == "despesa")
    saldo = total_receitas - total_despesas

    st.write("---")
    st.subheader("Resumo Financeiro")
    st.metric("Total Receitas", f"R$ {total_receitas:.2f}")
    st.metric("Total Despesas", f"R$ {total_despesas:.2f}")
    st.metric("Saldo", f"R$ {saldo:.2f}")

