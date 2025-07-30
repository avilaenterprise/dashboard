import streamlit as st
import os  
import conciliacao
import consulta_faturas 
import consulta_minuta
import dashboard
import data_loader
import financas
import emissoes
import cotacao
import coleta
import importacao_ofx
import contatos
import pandas as pd
import auth
import azure_integration
from conciliacao import mostrar_conciliacao
from consulta_faturas import mostrar_faturas
from consulta_minuta import mostrar_minutas
from dashboard import mostrar_dashboard
from financas import mostrar_financeiro
from emissoes import mostrar_emissao
from cotacao import mostrar_cotacao
from coleta import mostrar_coleta
from importacao_ofx import mostrar_importacao_ofx
from contatos import mostrar_contatos
from data_loader import carregar_base, salvar_base
from auth import check_authentication, show_user_info, show_user_management
from azure_integration import show_azure_status, backup_to_azure, show_email_test

# Configuração inicial da página
st.set_page_config(page_title="Avila Transportes", layout="wide")

# Check authentication first
if not check_authentication():
    st.stop()

st.title("🚛 Sistema Unificado - Ávila Transportes")

# Show user info and Azure status in sidebar
show_user_info()
show_azure_status()

# Menu lateral
menu_options = [
    "Dashboard Geral", 
    "Consulta de Faturas", 
    "Consulta de Minuta", 
    "Financeiro", 
    "Emissões",
    "Cotação",
    "Ordem de Coleta",
    "Importação OFX",
    "Contatos"
]

# Add admin options for admin users
if st.session_state.get("user_role") == "admin":
    menu_options.extend([
        "---",
        "👥 Gerenciar Usuários",
        "☁️ Backup Azure",
        "📧 Teste de Email"
    ])

aba = st.sidebar.radio("Escolha a funcionalidade:", menu_options)

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
elif aba == "Cotação":
    mostrar_cotacao()
elif aba == "Ordem de Coleta":
    mostrar_coleta()
elif aba == "Importação OFX":
    mostrar_importacao_ofx()
elif aba == "Contatos":
    mostrar_contatos()
elif aba == "� Gerenciar Usuários":
    show_user_management()
elif aba == "☁️ Backup Azure":
    backup_to_azure()
elif aba == "📧 Teste de Email":
    show_email_test()
elif aba == "---":
    st.info("Selecione uma opção válida do menu")
