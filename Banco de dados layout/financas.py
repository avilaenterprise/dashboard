import streamlit as st
import pandas as pd
import os
from parser_ofx import extrair_transacoes  # Função que você deve ter para extrair OFX

import streamlit as st
import pandas as pd
import os
from datetime import datetime

ARQ_BASE = "data/base_financeira.csv"
ARQ_EXTRATO = "extrato.csv"  # Arquivo de extrato bancário adicional

# Garantir pasta 'data' para salvar arquivos
os.makedirs("data", exist_ok=True)

# Função para carregar base CSV
def carregar_base():
    try:
        if os.path.exists(ARQ_BASE):
            return pd.read_csv(ARQ_BASE, sep=";")
        else:
            cols = ["Data", "Descrição", "Valor", "Tipo", "Categoria",
                    "Setor", "Centro de Custo", "ID Transação", "Conciliado com"]
            return pd.DataFrame(columns=cols)
    except Exception as e:
        st.error(f"Erro ao carregar a base: {e}")
        return pd.DataFrame()

# Função para carregar extrato bancário
def carregar_extrato():
    """
    Carrega dados do extrato bancário
    """
    try:
        if os.path.exists(ARQ_EXTRATO):
            df = pd.read_csv(ARQ_EXTRATO, sep=";", encoding="utf-8")
            df.columns = [c.strip() for c in df.columns]
            
            # Tratar data
            if "Data Lançamento" in df.columns:
                df["Data Lançamento"] = pd.to_datetime(df["Data Lançamento"], dayfirst=True, errors="coerce")
            
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar extrato: {e}")
        return pd.DataFrame()

# Função para salvar base CSV
def salvar_base(df):
    try:
        df.to_csv(ARQ_BASE, sep=";", index=False)
    except Exception as e:
        st.error(f"Erro ao salvar a base: {e}")

# Atualiza base com transações novas do OFX
def atualizar_com_ofx(df_ofx):
    base = carregar_base()
    if df_ofx.empty:
        st.warning("⚠️ Nenhum dado OFX carregado.")
        return base, 0
    # Evita duplicidade pela chave "ID Transação"
    novos = df_ofx[~df_ofx["ID Transação"].isin(base["ID Transação"])]
    if novos.empty:
        return base, 0
    final = pd.concat([base, novos], ignore_index=True)
    salvar_base(final)
    return final, len(novos)

# Upload OFX e processamento
uploaded_file = st.file_uploader("📥 Importar arquivo OFX", type=["ofx"])
if uploaded_file:
    df_ofx = extrair_transacoes(uploaded_file)
    st.success(f"{len(df_ofx)} transações lidas.")
    base, novos = atualizar_com_ofx(df_ofx)
    st.info(f"{novos} novas transações adicionadas.")
else:
    base = carregar_base()

if base.empty:
    st.warning("⚠️ Base de dados vazia. Carregue um arquivo OFX.")
    st.stop()

# Filtros na sidebar
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

# Exibição tabela
st.markdown(f"### 📋 Transações Financeiras (Total: {len(df)})")
st.dataframe(df, use_container_width=True)

# Conciliação manual com documento interno
transacoes_nao_conciliadas = df[df["Conciliado com"].isna() | (df["Conciliado com"] == "")]
if not transacoes_nao_conciliadas.empty:
    with st.form("form_conciliacao"):
        id_escolhido = st.selectbox("Escolha uma transação para conciliar", transacoes_nao_conciliadas["ID Transação"].tolist())
        doc = st.text_input("Número da Minuta ou CT-e")
        submit_conciliar = st.form_submit_button("Conciliar")

    if submit_conciliar:
        idx = base[base["ID Transação"] == id_escolhido].index
        base.loc[idx, "Conciliado com"] = doc
        salvar_base(base)
        st.success(f"Transação {id_escolhido} conciliada com documento {doc}")

# Resumo financeiro
st.markdown("### 📊 Resumo Financeiro")
total_receitas = base[base["Tipo"] == "Receita"]["Valor"].sum()
total_despesas = base[base["Tipo"] == "Despesa"]["Valor"].sum()
saldo_total = base["Valor"].sum()
st.markdown(f"**Total Receitas:** R$ {total_receitas:,.2f}")
st.markdown(f"**Total Despesas:** R$ {total_despesas:,.2f}")
st.markdown(f"**Saldo Total:** R$ {saldo_total:,.2f}")

# Resumo por Categoria (markdown)
st.markdown("### 📊 Resumo por Categoria")
st.markdown(base.groupby("Categoria")["Valor"].sum().to_markdown())

# Transações sem Centro de Custo ou Setor definidos
faltando = base[(base["Centro de Custo"] == "❗Definir") | (base["Setor"] == "❗Definir")]
if not faltando.empty:
    st.markdown("### ⚠️ Transações sem Centro de Custo ou Setor definidos")
    st.markdown("Complete os dados abaixo:")

    edit_df = st.data_editor(faltando, num_rows="dynamic", key="editor_cc_setor")

    if st.button("✅ Confirmar Classificações Manuais"):
        for idx, row in edit_df.iterrows():
            base.loc[row.name, "Centro de Custo"] = row["Centro de Custo"]
            base.loc[row.name, "Setor"] = row["Setor"]
        salvar_base(base)
        st.success("Dados atualizados com sucesso!")

# Gráfico resumo por Categoria
st.markdown("### 📈 Gráfico por Categoria")
st.bar_chart(base.groupby("Categoria")["Valor"].sum())

def mostrar_financeiro():
    """
    Interface principal do módulo financeiro
    """
    st.header("💳 Dashboard Financeiro Integrado")
    
    # Criar abas
    tab1, tab2, tab3 = st.tabs(["Transações Principais", "Extrato Bancário", "Conciliação"])
    
    with tab1:
        # Código existente das transações principais
        try:
            from parser_ofx import extrair_transacoes
        except ImportError:
            st.warning("⚠️ Módulo OFX não disponível. Upload OFX desabilitado.")
            extrair_transacoes = None

        # Upload OFX e processamento
        if extrair_transacoes:
            uploaded_file = st.file_uploader("📥 Importar arquivo OFX", type=["ofx"])
            if uploaded_file:
                df_ofx = extrair_transacoes(uploaded_file)
                st.success(f"{len(df_ofx)} transações lidas.")
                base, novos = atualizar_com_ofx(df_ofx)
                if novos > 0:
                    st.success(f"{novos} transações novas importadas.")

        # Carregar base de transações
        base = carregar_base()

        if base.empty:
            st.warning("⚠️ Nenhuma transação encontrada. Importe um arquivo OFX.")
        else:
            # Mostrar dados
            st.dataframe(base, use_container_width=True)

            # Conciliação de transações
            trans_nao_conciliadas = base[base["Conciliado com"].isna() | (base["Conciliado com"] == "")]
            if not trans_nao_conciliadas.empty:
                st.markdown("### 🔗 Conciliação de Transações")
                with st.form("form_conciliacao"):
                    id_escolhido = st.selectbox("Escolha ID para conciliar", trans_nao_conciliadas["ID Transação"].tolist())
                    doc = st.text_input("Documento/Minuta/CT-e")
                    submit = st.form_submit_button("Conciliar")
                if submit and doc:
                    idx = base[base["ID Transação"] == id_escolhido].index
                    base.loc[idx, "Conciliado com"] = doc
                    salvar_base(base)
                    st.success(f"Transação {id_escolhido} conciliada com documento {doc}")

            # Resumo financeiro
            st.markdown("### 📊 Resumo Financeiro")
            total_receitas = base[base["Tipo"] == "Receita"]["Valor"].sum()
            total_despesas = base[base["Tipo"] == "Despesa"]["Valor"].sum()
            saldo_total = base["Valor"].sum()
            st.markdown(f"**Total Receitas:** R$ {total_receitas:,.2f}")
            st.markdown(f"**Total Despesas:** R$ {total_despesas:,.2f}")
            st.markdown(f"**Saldo Total:** R$ {saldo_total:,.2f}")

            # Resumo por Categoria (markdown)
            st.markdown("### 📊 Resumo por Categoria")
            st.markdown(base.groupby("Categoria")["Valor"].sum().to_markdown())

            # Transações sem Centro de Custo ou Setor definidos
            faltando = base[(base["Centro de Custo"] == "❗Definir") | (base["Setor"] == "❗Definir")]
            if not faltando.empty:
                st.markdown("### ⚠️ Transações sem Centro de Custo ou Setor definidos")
                st.markdown("Complete os dados abaixo:")

                edit_df = st.data_editor(faltando, num_rows="dynamic", key="editor_cc_setor")

                if st.button("✅ Confirmar Classificações Manuais"):
                    for idx, row in edit_df.iterrows():
                        base.loc[row.name, "Centro de Custo"] = row["Centro de Custo"]
                        base.loc[row.name, "Setor"] = row["Setor"]
                    salvar_base(base)
                    st.success("Dados atualizados com sucesso!")

            # Gráfico resumo por Categoria
            st.markdown("### 📈 Gráfico por Categoria")
            st.bar_chart(base.groupby("Categoria")["Valor"].sum())
    
    with tab2:
        st.subheader("🏦 Dados do Extrato Bancário")
        
        # Carregar extrato
        extrato = carregar_extrato()
        
        if not extrato.empty:
            st.success(f"✅ Extrato carregado: {len(extrato)} registros encontrados")
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                if "Cliente" in extrato.columns:
                    clientes = ["Todos"] + list(extrato["Cliente"].dropna().unique())
                    cliente_selecionado = st.selectbox("Filtrar por Cliente", clientes)
            
            with col2:
                if "Conciliação" in extrato.columns:
                    status_conciliacao = ["Todos"] + list(extrato["Conciliação"].dropna().unique())
                    status_selecionado = st.selectbox("Status Conciliação", status_conciliacao)
            
            # Aplicar filtros
            extrato_filtrado = extrato.copy()
            
            if cliente_selecionado != "Todos":
                extrato_filtrado = extrato_filtrado[extrato_filtrado["Cliente"] == cliente_selecionado]
            
            if status_selecionado != "Todos":
                extrato_filtrado = extrato_filtrado[extrato_filtrado["Conciliação"] == status_selecionado]
            
            # Exibir dados
            st.dataframe(extrato_filtrado, use_container_width=True)
            
            # Estatísticas
            if not extrato_filtrado.empty:
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_registros = len(extrato_filtrado)
                    st.metric("Total Registros", total_registros)
                
                with col2:
                    if "Conciliação" in extrato_filtrado.columns:
                        conciliados = len(extrato_filtrado[extrato_filtrado["Conciliação"] == "Conciliado"])
                        st.metric("Conciliados", conciliados)
                
                with col3:
                    if "Valor Fatura Sistema" in extrato_filtrado.columns:
                        # Tentar extrair valores numéricos
                        valores_str = extrato_filtrado["Valor Fatura Sistema"].astype(str)
                        valores_num = valores_str.str.replace("R$", "").str.replace(" ", "").str.replace(",", ".")
                        valores_float = pd.to_numeric(valores_num, errors='coerce').fillna(0)
                        total_valor = valores_float.sum()
                        st.metric("Valor Total", f"R$ {total_valor:,.2f}")
            
            # Download
            csv = extrato_filtrado.to_csv(index=False, sep=";").encode("utf-8")
            st.download_button(
                "📥 Baixar Extrato Filtrado (CSV)",
                csv,
                "extrato_filtrado.csv",
                "text/csv"
            )
        else:
            st.info("📋 Nenhum dado encontrado no arquivo extrato.csv")
            st.markdown("""
            **Para visualizar dados do extrato:**
            1. Certifique-se de que o arquivo `extrato.csv` existe na pasta principal
            2. Verifique se o formato está correto (separado por `;`)
            3. Recarregue a página após adicionar o arquivo
            """)
    
    with tab3:
        st.subheader("🔗 Conciliação Completa")
        
        # Carregar ambas as bases
        base_transacoes = carregar_base()
        extrato = carregar_extrato()
        
        if not base_transacoes.empty and not extrato.empty:
            st.markdown("### 📊 Comparação entre Bases")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Transações (OFX)", len(base_transacoes))
                st.metric("Conciliadas", len(base_transacoes[base_transacoes["Conciliado com"].notna()]))
            
            with col2:
                st.metric("Registros Extrato", len(extrato))
                if "Conciliação" in extrato.columns:
                    conciliados_extrato = len(extrato[extrato["Conciliação"] == "Conciliado"])
                    st.metric("Conciliados (Extrato)", conciliados_extrato)
            
            # Divergências
            st.markdown("### ⚠️ Transações Não Conciliadas")
            nao_conciliadas = base_transacoes[
                base_transacoes["Conciliado com"].isna() | 
                (base_transacoes["Conciliado com"] == "")
            ]
            
            if not nao_conciliadas.empty:
                st.dataframe(nao_conciliadas[["Data", "Descrição", "Valor", "Tipo", "Categoria"]], 
                           use_container_width=True)
            else:
                st.success("✅ Todas as transações estão conciliadas!")
        else:
            st.info("💡 Carregue dados nas outras abas para ver a conciliação completa")
