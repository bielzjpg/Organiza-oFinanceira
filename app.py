import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# Carregar JSON da chave do Secrets do Streamlit
json_creds = st.secrets["gcp_service_account"]

# Definir escopo para acessar Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Criar credenciais com escopo correto
credentials = service_account.Credentials.from_service_account_info(
    json_creds,
    scopes=SCOPES
)

# Autenticar cliente gspread
cliente = gspread.authorize(credentials)

# ID da planilha e aba que você quer acessar
ID_PLANILHA = "d/1bs20JYhAupfx-tZlhw0Mr86-ThxSg--_smfYJw_3ICg"
NOME_ABA = "Dados"

@st.cache_data(ttl=300)
def carregar_planilha():
    try:
        planilha = cliente.open_by_key(ID_PLANILHA)
        aba = planilha.worksheet(NOME_ABA)
        dados = aba.get_all_records()
        df = pd.DataFrame(dados)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados da planilha: {e}")
        return pd.DataFrame()

def main():
    st.title("App Organização Financeira - Google Sheets")

    df = carregar_planilha()

    if df.empty:
        st.write("Nenhum dado carregado.")
    else:
        st.write("Dados carregados da planilha:")
        st.dataframe(df)

    # Exemplo simples para adicionar uma receita
    with st.form("nova_receita"):
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Adicionar Receita")

        if submitted:
            if descricao and valor > 0:
                # Adiciona na planilha
                try:
                    planilha = cliente.open_by_key(ID_PLANILHA)
                    aba = planilha.worksheet(NOME_ABA)
                    nova_linha = [descricao, valor]
                    aba.append_row(nova_linha)
                    st.success("Receita adicionada com sucesso!")
                    st.experimental_rerun()  # Recarrega o app para atualizar os dados
                except Exception as e:
                    st.error(f"Erro ao adicionar receita: {e}")
            else:
                st.warning("Preencha todos os campos corretamente.")

if __name__ == "__main__":
    main()
