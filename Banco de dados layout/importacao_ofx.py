import streamlit as st
import pandas as pd
from parser_ofx import extrair_transacoes, classificar_transacao
from data_loader import salvar_base, carregar_base
import os

def mostrar_importacao_ofx():
    """
    Interface para importação de extratos bancários OFX
    """
    st.header("🏦 Importação de Extratos Bancários (OFX)")
    
    st.markdown("""
    Este módulo permite importar extratos bancários no formato **OFX** e integrá-los 
    automaticamente ao sistema financeiro com classificação automática de transações.
    """)
    
    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "📁 Selecione o arquivo OFX do extrato bancário",
        type=['ofx', 'qfx'],
        help="Arquivo de extrato bancário no formato OFX/QFX baixado do seu banco"
    )
    
    if uploaded_file is not None:
        try:
            # Exibir informações do arquivo
            st.info(f"📄 **Arquivo:** {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            # Processar arquivo
            with st.spinner("Processando extrato bancário..."):
                df_transacoes = extrair_transacoes(uploaded_file)
            
            if not df_transacoes.empty:
                st.success(f"✅ **{len(df_transacoes)} transações** extraídas com sucesso!")
                
                # Mostrar preview das transações
                st.subheader("👀 Preview das Transações Extraídas")
                st.dataframe(df_transacoes.head(10), use_container_width=True)
                
                # Estatísticas
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Transações", len(df_transacoes))
                with col2:
                    receitas = df_transacoes[df_transacoes["Tipo"] == "Receita"]["Valor"].sum()
                    st.metric("Receitas", f"R$ {receitas:,.2f}")
                with col3:
                    despesas = abs(df_transacoes[df_transacoes["Tipo"] == "Despesa"]["Valor"].sum())
                    st.metric("Despesas", f"R$ {despesas:,.2f}")
                with col4:
                    saldo = receitas - despesas
                    st.metric("Saldo Líquido", f"R$ {saldo:,.2f}")
                
                # Classificação automática
                st.subheader("🤖 Classificação Automática")
                
                categorias_count = df_transacoes["Categoria"].value_counts()
                st.bar_chart(categorias_count)
                
                # Transações não classificadas
                nao_classificadas = df_transacoes[df_transacoes["Categoria"] == "Outros"]
                if not nao_classificadas.empty:
                    st.warning(f"⚠️ **{len(nao_classificadas)} transações** não foram classificadas automaticamente")
                    
                    with st.expander("📝 Editar Classificações Manuais"):
                        st.markdown("**Transações que precisam de classificação manual:**")
                        
                        # Editor de dados para classificação manual
                        df_editavel = nao_classificadas[["Descrição", "Memo", "Valor", "Categoria", "Centro de Custo", "Setor"]].copy()
                        df_editado = st.data_editor(
                            df_editavel,
                            column_config={
                                "Categoria": st.column_config.SelectboxColumn(
                                    "Categoria",
                                    options=["Transferência", "Pagamento", "Recebimento", "Cartão de Crédito", 
                                            "Transporte", "Viagem", "Alimentação", "Combustível", "Outros"],
                                    required=True
                                ),
                                "Centro de Custo": st.column_config.SelectboxColumn(
                                    "Centro de Custo",
                                    options=["Financeiro", "Logística", "Administrativo", "Comercial", "❗Definir"],
                                    required=True
                                ),
                                "Setor": st.column_config.SelectboxColumn(
                                    "Setor",
                                    options=["Administrativo", "Operacional", "Comercial", "❗Definir"],
                                    required=True
                                )
                            },
                            use_container_width=True,
                            key="editor_classificacao"
                        )
                        
                        if st.button("✅ Aplicar Classificações Manuais"):
                            # Aplicar classificações editadas
                            for idx, row in df_editado.iterrows():
                                original_idx = nao_classificadas.index[idx]
                                df_transacoes.loc[original_idx, "Categoria"] = row["Categoria"]
                                df_transacoes.loc[original_idx, "Centro de Custo"] = row["Centro de Custo"]
                                df_transacoes.loc[original_idx, "Setor"] = row["Setor"]
                            
                            st.success("Classificações aplicadas!")
                            st.rerun()
                
                # Opções de importação
                st.subheader("💾 Opções de Importação")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    importar_tudo = st.checkbox("Importar todas as transações", value=True)
                    substituir_existentes = st.checkbox("Substituir transações existentes com mesmo ID")
                
                with col2:
                    apenas_novas = st.checkbox("Importar apenas transações novas", value=True)
                    backup_antes = st.checkbox("Criar backup antes de importar", value=True)
                
                # Botões de ação
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("💾 Importar para Sistema", type="primary", use_container_width=True):
                        try:
                            # Carregar base existente
                            try:
                                base_existente = carregar_base()
                            except:
                                base_existente = pd.DataFrame()
                            
                            # Criar backup se solicitado
                            if backup_antes and not base_existente.empty:
                                backup_filename = f"backup_base_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
                                base_existente.to_csv(backup_filename, sep=";", index=False, encoding="utf-8")
                                st.info(f"✅ Backup criado: {backup_filename}")
                            
                            # Processar importação
                            if apenas_novas and not base_existente.empty:
                                # Filtrar apenas IDs que não existem
                                ids_existentes = set(base_existente.get("ID Transação", []).astype(str))
                                df_para_importar = df_transacoes[~df_transacoes["ID Transação"].astype(str).isin(ids_existentes)]
                                
                                if df_para_importar.empty:
                                    st.warning("⚠️ Todas as transações já existem na base!")
                                    return
                                else:
                                    st.info(f"📥 Importando {len(df_para_importar)} transações novas")
                            else:
                                df_para_importar = df_transacoes
                            
                            # Combinar com base existente
                            if not base_existente.empty:
                                if substituir_existentes:
                                    # Remover transações com IDs duplicados da base existente
                                    ids_novos = set(df_para_importar["ID Transação"].astype(str))
                                    base_filtrada = base_existente[~base_existente.get("ID Transação", pd.Series()).astype(str).isin(ids_novos)]
                                    base_final = pd.concat([base_filtrada, df_para_importar], ignore_index=True)
                                else:
                                    base_final = pd.concat([base_existente, df_para_importar], ignore_index=True)
                            else:
                                base_final = df_para_importar
                            
                            # Salvar base atualizada
                            if salvar_base(base_final):
                                st.success(f"✅ **{len(df_para_importar)} transações** importadas com sucesso!")
                                
                                # Estatísticas da importação
                                with st.expander("📊 Resumo da Importação"):
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Transações Importadas", len(df_para_importar))
                                    with col2:
                                        total_valor = df_para_importar["Valor"].sum()
                                        st.metric("Valor Total", f"R$ {total_valor:,.2f}")
                                    with col3:
                                        st.metric("Total na Base", len(base_final))
                            else:
                                st.error("❌ Erro ao salvar as transações importadas!")
                                
                        except Exception as e:
                            st.error(f"❌ Erro durante a importação: {str(e)}")
                
                with col2:
                    # Download das transações processadas
                    csv_data = df_transacoes.to_csv(index=False, sep=";").encode("utf-8")
                    st.download_button(
                        "📥 Baixar Transações (CSV)",
                        csv_data,
                        f"transacoes_ofx_{uploaded_file.name}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                
                with col3:
                    if st.button("🗑️ Limpar", use_container_width=True):
                        st.rerun()
                
            else:
                st.error("❌ Nenhuma transação encontrada no arquivo OFX!")
                
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo OFX: {str(e)}")
            st.error("Verifique se o arquivo está no formato OFX válido.")
    
    # Seção de ajuda
    with st.expander("❓ Como obter arquivo OFX do seu banco"):
        st.markdown("""
        ### 📋 Passos para baixar extrato OFX:
        
        **Bancos principais:**
        - **Banco do Brasil**: Internet Banking → Extratos → Exportar → Formato OFX
        - **Itaú**: iToken → Extratos → Baixar → Formato OFX/Money
        - **Bradesco**: Conta Corrente → Extratos → Exportar → Money/OFX
        - **Santander**: Extrato → Exportar → Formato OFX
        - **Caixa**: Internet Banking → Extratos → Baixar → OFX
        - **Nubank**: Extrato → Exportar → OFX (disponível no app)
        
        ### ⚙️ Configurações recomendadas:
        - Período: Últimos 30-90 dias
        - Formato: OFX 2.0 ou superior
        - Conta: Conta corrente principal
        
        ### 🔒 Segurança:
        - Sempre baixe extratos de fontes oficiais
        - Exclua arquivos após importação
        - Mantenha senhas seguras
        """)
    
    # Seção de regras de classificação
    with st.expander("🤖 Regras de Classificação Automática"):
        st.markdown("""
        ### 📋 Regras Atuais de Classificação:
        
        | Palavra-chave | Categoria | Centro de Custo | Setor |
        |---------------|-----------|-----------------|-------|
        | PIX, TED, DOC | Transferência | Financeiro | Administrativo |
        | BOLETO | Pagamento | Financeiro | Administrativo |
        | NU PAGAMENTOS | Recebimento | Financeiro | Administrativo |
        | PAG* | Cartão de Crédito | Financeiro | Administrativo |
        | UBER, 99 | Transporte | Logística | Operacional |
        | GOL, LATAM | Viagem | Logística | Operacional |
        
        ### ✏️ Personalização:
        As regras podem ser editadas no arquivo `parser_ofx.py` para adequar às necessidades da empresa.
        """)
