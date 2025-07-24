import streamlit as st
import os  
import conciliacao
import consulta_faturas 
import consulta_minuta
import dashboard
import data_loader
import streamlit as st
import financas
import emissoes
import pandas as pd
from conciliacao import mostrar_conciliacao
from consulta_faturas import mostrar_faturas
from consulta_minuta import mostrar_minutas
from dashboard import mostrar_dashboard
from financas import mostrar_financeiro
from emissoes import mostrar_emissao
from data_loader import carregar_base, salvar_base
    
    st.write("Selecione uma fatura para ver os detalhes.")



# Configuração inicial da página
st.set_page_config(page_title="Avila Transportes", layout="wide")
st.title("🚛 Sistema Unificado - Ávila Transportes")

# Menu lateral
aba = st.sidebar.radio("Escolha a funcionalidade:", [
    "Dashboard Geral", 
    "Consulta de Faturas", 
    "Consulta de Minuta", 
    "Financeiro", 
    "Emissões"
])

# Carregamento da base de dados
try:
    base = carregar_base()
except Exception as e:
    st.error(f"Erro ao carregar base de dados: {e}")
    base = None

# Roteamento entre as abas
if aba == "Dashboard Geral":
    if base is not None:
        mostrar_dashboard(base)
    else:
        st.warning("⚠️ Base de dados não carregada.")
elif aba == "Consulta de Faturas":
    if base is not None:
        mostrar_faturas(base)
    else:
        st.warning("⚠️ Base de dados não carregada.")
elif aba == "Consulta de Minuta":
    if base is not None:
        mostrar_minutas(base)
    else:
        st.warning("⚠️ Base de dados não carregada.")
elif aba == "Financeiro":
    mostrar_financeiro()
elif aba == "Emissões":
    mostrar_emissao()



st.set_page_config("Dashboard Financeiro", layout="wide")
st.title("💳 Dashboard Financeiro Integrado")

# Carrega a base
base = carregar_base()

if base.empty:
    st.warning("⚠️ Base de dados vazia. Importe dados para continuar.")
    st.stop()

# Filtros
setores = sorted(base["Setor"].dropna().unique())
centros = sorted(base["Centro de Custo"].dropna().unique())
categorias = sorted(base["Categoria"].dropna().unique())

setor_sel = st.sidebar.multiselect("Setores", setores, default=setores)
centro_sel = st.sidebar.multiselect("Centros de Custo", centros, default=centros)
cat_sel = st.sidebar.multiselect("Categorias", categorias, default=categorias)

df = base[
    base["Setor"].isin(setor_sel) &
    base["Centro de Custo"].isin(centro_sel) &
    base["Categoria"].isin(cat_sel)
]

st.markdown("### 📋 Transações Financeiras")
st.dataframe(df, use_container_width=True)

# Aqui você pode incluir conciliações, atualizações, gráficos, etc.

# Botão para salvar atualizações (exemplo)
if st.button("Salvar alterações"):
    salvar_base(df)
