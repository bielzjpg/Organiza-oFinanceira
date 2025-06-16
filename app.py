import streamlit as st
from datetime import datetime
import pandas as pd
from gsheets_utils import autenticar_google_sheets, carregar_planilha, salvar_planilha

# --- CONFIGURE AQUI ---
CAMINHO_CREDENCIAIS = "Credentials.json"  # coloque o nome do seu arquivo JSON aqui
ID_PLANILHA = "1bs20JYhAupfx-tZlhw0Mr86-ThxSg--_smfYJw_3ICg"  # coloque o ID da sua planilha Google aqui
NOME_ABA = "Receitas"  # normalmente é "Sheet1", altere se usar outra aba

# --- Autenticação ---
@st.cache_resource(ttl=3600)
def carregar_cliente_gsheets():
    return autenticar_google_sheets(CAMINHO_CREDENCIAIS)

cliente = carregar_cliente_gsheets()

# --- Carregar dados ---
@st.cache_data(ttl=60)
def carregar_dados():
    df_local, aba_local = carregar_planilha(cliente, ID_PLANILHA, NOME_ABA)
    return df_local, aba_local

df, aba = carregar_dados()

# --- Funções ---
def salvar_dados(df_local):
    salvar_planilha(df_local, aba)

def adicionar_lancamento(df_local, tipo, categoria, descricao, valor, data):
    novo_id = df_local["id"].max() + 1 if not df_local.empty else 1
    novo_lanc = {
        "id": novo_id,
        "tipo": tipo,
        "categoria": categoria,
        "descricao": descricao,
        "valor": valor,
        "data": data.strftime("%Y-%m-%d")
    }
    df_local = df_local.append(novo_lanc, ignore_index=True)
    salvar_dados(df_local)
    return df_local

def deletar_lancamento(df_local, id_lanc):
    df_local = df_local[df_local["id"] != id_lanc]
    salvar_dados(df_local)
    return df_local

# --- Interface Streamlit ---

st.title("📊 Organização Financeira com Google Sheets")

menu = st.sidebar.selectbox("Menu", ["Adicionar Lançamento", "Ver Extrato", "Resumo Financeiro"])

if menu == "Adicionar Lançamento":
    st.header("Adicionar Receita ou Despesa")

    with st.form(key="form_lancamento", clear_on_submit=True):
        tipo = st.radio("Tipo", ["Receita", "Despesa"])
        categoria = st.text_input("Categoria (ex: Salário, Alimentação, Transporte...)")
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
        data = st.date_input("Data", datetime.today())
        submit = st.form_submit_button("Adicionar")

    if submit:
        if not categoria or not descricao:
            st.error("Preencha todos os campos!")
        else:
            df = adicionar_lancamento(df, tipo, categoria, descricao, valor, data)
            st.success(f"{tipo} adicionada com sucesso!")

elif menu == "Ver Extrato":
    st.header("Extrato de Lançamentos")

    tipos = st.multiselect("Filtrar por Tipo", ["Receita", "Despesa"], default=["Receita", "Despesa"])
    categorias = df["categoria"].dropna().unique().tolist()
    filtro_categorias = st.multiselect("Filtrar por Categoria", categorias, default=categorias)
    filtro_data_inicio = st.date_input("Data Início", value=df["data"].min() if not df.empty else datetime.today())
    filtro_data_fim = st.date_input("Data Fim", value=df["data"].max() if not df.empty else datetime.today())

    df_filtrado = df[
        (df["tipo"].isin(tipos)) &
        (df["categoria"].isin(filtro_categorias)) &
        (df["data"] >= pd.to_datetime(filtro_data_inicio)) &
        (df["data"] <= pd.to_datetime(filtro_data_fim))
    ].sort_values(by="data", ascending=False)

    if df_filtrado.empty:
        st.info("Nenhum lançamento encontrado.")
    else:
        st.dataframe(df_filtrado.reset_index(drop=True))

        st.markdown("### Deletar lançamento")
        id_deletar = st.number_input("ID para deletar", min_value=1, step=1, key="id_deletar")

        if st.button("Deletar"):
            if id_deletar in df["id"].values:
                df = deletar_lancamento(df, id_deletar)
                st.success(f"Lançamento ID {id_deletar} deletado!")
            else:
                st.error("ID não encontrado.")

elif menu == "Resumo Financeiro":
    st.header("Resumo Financeiro")

    total_receitas = df[df["tipo"] == "Receita"]["valor"].astype(float).sum()
    total_despesas = df[df["tipo"] == "Despesa"]["valor"].astype(float).sum()
    saldo = total_receitas - total_despesas

    st.metric("Total Receitas (R$)", f"{total_receitas:,.2f}")
    st.metric("Total Despesas (R$)", f"{total_despesas:,.2f}")
    st.metric("Saldo Atual (R$)", f"{saldo:,.2f}")

    st.markdown("### Receitas por Categoria")
    receitas_cat = df[df["tipo"] == "Receita"].groupby("categoria")["valor"].apply(lambda x: x.astype(float).sum()).sort_values(ascending=False)
    st.bar_chart(receitas_cat)

    st.markdown("### Despesas por Categoria")
    despesas_cat = df[df["tipo"] == "Despesa"].groupby("categoria")["valor"].apply(lambda x: x.astype(float).sum()).sort_values(ascending=False)
    st.bar_chart(despesas_cat)
