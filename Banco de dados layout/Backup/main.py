import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Carregar dados
@st.cache_data
def carregar_base():
    df = pd.read_csv("base.csv", sep=";", encoding="utf-8")
    df.columns = [c.strip() for c in df.columns]
    df["Valor do frete"] = df["Valor do frete"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".").astype(float)
    df["Soma dos Volumes"] = pd.to_numeric(df["Soma dos Volumes"], errors="coerce")
    df["Data de Emissão"] = pd.to_datetime(df["Data de Emissão"], dayfirst=True)
    df["Quinzena"] = df["Data de Emissão"].apply(lambda x: f"{x.month:02d}/1ª" if x.day <= 15 else f"{x.month:02d}/2ª")
    return df

def salvar_emissao(tipo, dados):
    cliente = dados.get("cliente", "Generico").replace("/", "-")
    data = dados.get("data", datetime.today().strftime("%Y-%m-%d"))
    nome_pasta = f"documentos/{cliente}_{data}"
    os.makedirs(nome_pasta, exist_ok=True)
    with open(f"{nome_pasta}/{tipo}.txt", "w", encoding="utf-8") as f:
        for k, v in dados.items():
            f.write(f"{k}: {v}\n")
    return nome_pasta

# App
st.set_page_config(page_title="Avila Transportes", layout="wide")
st.title("Sistema Unificado - Ávila Transportes")

aba = st.sidebar.radio("Escolha a funcionalidade:", [
    "Dashboard Geral", "Consulta de Faturas", "Consulta de Minuta", "Financeiro", "Emissões"
])

base = carregar_base()

if aba == "Dashboard Geral":
    st.header("📊 Dashboard Geral")
    st.metric("Total de Frete", f"R${base['Valor do frete'].sum():,.2f}")
    st.metric("Total de Volumes", int(base["Soma dos Volumes"].sum()))
    st.bar_chart(base.groupby("Quinzena")["Valor do frete"].sum())

elif aba == "Consulta de Faturas":
    st.header("📄 Consulta de Faturas")
    faturas = base.groupby("Nº Fatura", as_index=False).agg({
        "Pagador do Frete - Nome": "first",
        "Valor do frete": "sum",
        "Número": "max",
        "Quinzena": "first"
    }).rename(columns={
        "Pagador do Frete - Nome": "Empresa Pagadora",
        "Valor do frete": "Total do Frete",
        "Número": "Número Fatura"
    })
    st.dataframe(faturas, use_container_width=True)
    fat = st.selectbox("Selecione uma fatura:", faturas["Nº Fatura"])
    dados = base[base["Nº Fatura"] == fat][["Número", "Remetente", "Destinatário", "Soma dos Volumes", "Nota", "Valor do frete"]]
    st.dataframe(dados, use_container_width=True)

elif aba == "Consulta de Minuta":
    st.header("🔍 Consulta de Minuta")
    num = st.text_input("Digite o número da minuta:")
    if num:
        resultado = base[base["Número"].astype(str) == num.strip()]
        if not resultado.empty:
            st.dataframe(resultado, use_container_width=True)
        else:
            st.warning("Minuta não encontrada")

elif aba == "Financeiro":
    st.header("💳 Financeiro")
    try:
        extrato = pd.read_csv("extrato.csv", sep=";", encoding="utf-8")
        extrato["Data"] = pd.to_datetime(extrato["Data"], dayfirst=True)
        st.dataframe(extrato, use_container_width=True)
        st.bar_chart(extrato.groupby("Categoria")["Valor"].sum())
    except Exception as e:
        st.error(f"Erro ao carregar extrato: {e}")

elif aba == "Emissões":
    st.header("🔖 Emissão de Documentos")
    tipo = st.selectbox("Tipo de documento:", ["Fatura", "CT-e", "Nota Fiscal", "Minuta"])
    with st.form("form_emissao"):
        cliente = st.text_input("Cliente")
        origem = st.text_input("Origem")
        destino = st.text_input("Destino")
        valor = st.text_input("Valor")
        data = st.date_input("Data", value=datetime.today())
        enviado = st.form_submit_button("Emitir")
        if enviado:
            info = {
                "cliente": cliente,
                "origem": origem,
                "destino": destino,
                "valor": valor,
                "data": data.strftime("%Y-%m-%d"),
                "tipo": tipo
            }
            pasta = salvar_emissao(tipo.lower(), info)
            st.success(f"Documento salvo em: {pasta}")
