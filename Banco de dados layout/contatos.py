import streamlit as st
import pandas as pd
import os

ARQ_CONTATOS = "contatos.csv"

def carregar_contatos():
    """
    Carrega a lista de contatos do CSV
    """
    try:
        if os.path.exists(ARQ_CONTATOS):
            df = pd.read_csv(ARQ_CONTATOS, encoding="utf-8")
            df.columns = [c.strip() for c in df.columns]
            return df
        else:
            return pd.DataFrame(columns=["Nome", "Número", "Email", "Cidade", "Observação"])
    except Exception as e:
        st.error(f"Erro ao carregar contatos: {e}")
        return pd.DataFrame(columns=["Nome", "Número", "Email", "Cidade", "Observação"])

def salvar_contatos(df):
    """
    Salva a lista de contatos no CSV
    """
    try:
        df.to_csv(ARQ_CONTATOS, index=False, encoding="utf-8")
        return True
    except Exception as e:
        st.error(f"Erro ao salvar contatos: {e}")
        return False

def mostrar_contatos():
    """
    Interface principal do módulo de contatos
    """
    st.header("📞 Gerenciamento de Contatos")
    
    # Criar abas
    tab1, tab2, tab3 = st.tabs(["Lista de Contatos", "Adicionar Contato", "Importar/Exportar"])
    
    with tab1:
        st.subheader("📋 Lista de Contatos")
        
        # Carregar contatos
        contatos = carregar_contatos()
        
        if not contatos.empty:
            # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                busca_nome = st.text_input("🔍 Buscar por Nome", placeholder="Digite o nome...")
            with col2:
                if "Cidade" in contatos.columns:
                    cidades = ["Todas"] + sorted(contatos["Cidade"].dropna().unique().tolist())
                    cidade_filtro = st.selectbox("Filtrar por Cidade", cidades)
            with col3:
                mostrar_vazios = st.checkbox("Mostrar campos vazios", value=False)
            
            # Aplicar filtros
            contatos_filtrados = contatos.copy()
            
            if busca_nome:
                contatos_filtrados = contatos_filtrados[
                    contatos_filtrados["Nome"].str.contains(busca_nome, case=False, na=False)
                ]
            
            if cidade_filtro != "Todas":
                contatos_filtrados = contatos_filtrados[contatos_filtrados["Cidade"] == cidade_filtro]
            
            if not mostrar_vazios:
                # Filtrar registros com pelo menos nome e número
                contatos_filtrados = contatos_filtrados[
                    (contatos_filtrados["Nome"].notna()) & 
                    (contatos_filtrados["Nome"] != "") &
                    (contatos_filtrados["Número"].notna()) & 
                    (contatos_filtrados["Número"] != "")
                ]
            
            # Exibir resultados
            st.metric("Total de Contatos", len(contatos_filtrados))
            
            if not contatos_filtrados.empty:
                # Editor de dados para permitir edições
                contatos_editados = st.data_editor(
                    contatos_filtrados,
                    column_config={
                        "Nome": st.column_config.TextColumn("Nome", width="medium", required=True),
                        "Número": st.column_config.TextColumn("Telefone", width="medium"),
                        "Email": st.column_config.TextColumn("E-mail", width="medium"),
                        "Cidade": st.column_config.TextColumn("Cidade", width="small"),
                        "Observação": st.column_config.TextColumn("Observações", width="large")
                    },
                    use_container_width=True,
                    num_rows="dynamic",
                    key="editor_contatos"
                )
                
                # Botão para salvar alterações
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Salvar Alterações", type="primary"):
                        if salvar_contatos(contatos_editados):
                            st.success("✅ Contatos salvos com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao salvar contatos")
                
                with col2:
                    # Download dos contatos filtrados
                    csv = contatos_editados.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Baixar Lista (CSV)",
                        csv,
                        "contatos_filtrados.csv",
                        "text/csv"
                    )
                
                # Estatísticas
                st.markdown("### 📊 Estatísticas")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    com_email = len(contatos_filtrados[contatos_filtrados["Email"].notna() & (contatos_filtrados["Email"] != "")])
                    st.metric("Com E-mail", com_email)
                
                with col2:
                    com_cidade = len(contatos_filtrados[contatos_filtrados["Cidade"].notna() & (contatos_filtrados["Cidade"] != "")])
                    st.metric("Com Cidade", com_cidade)
                
                with col3:
                    com_obs = len(contatos_filtrados[contatos_filtrados["Observação"].notna() & (contatos_filtrados["Observação"] != "")])
                    st.metric("Com Observações", com_obs)
                
                with col4:
                    completos = len(contatos_filtrados[
                        (contatos_filtrados["Nome"].notna()) & (contatos_filtrados["Nome"] != "") &
                        (contatos_filtrados["Número"].notna()) & (contatos_filtrados["Número"] != "") &
                        (contatos_filtrados["Email"].notna()) & (contatos_filtrados["Email"] != "")
                    ])
                    st.metric("Completos", completos)
                
            else:
                st.info("📭 Nenhum contato encontrado com os filtros aplicados")
        else:
            st.info("📭 Nenhum contato encontrado. Adicione contatos na aba 'Adicionar Contato'")
    
    with tab2:
        st.subheader("➕ Adicionar Novo Contato")
        
        with st.form("form_novo_contato"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome *", placeholder="Nome ou empresa")
                numero = st.text_input("Telefone *", placeholder="(16) 99999-9999")
                email = st.text_input("E-mail", placeholder="contato@empresa.com")
            
            with col2:
                cidade = st.text_input("Cidade", placeholder="Ribeirão Preto")
                observacao = st.text_area("Observações", placeholder="Observações importantes...")
            
            submitted = st.form_submit_button("➕ Adicionar Contato", use_container_width=True)
            
            if submitted:
                if nome and numero:
                    # Carregar contatos existentes
                    contatos = carregar_contatos()
                    
                    # Criar novo contato
                    novo_contato = {
                        "Nome": nome,
                        "Número": numero,
                        "Email": email,
                        "Cidade": cidade,
                        "Observação": observacao
                    }
                    
                    # Adicionar à lista
                    novo_df = pd.DataFrame([novo_contato])
                    contatos_atualizados = pd.concat([contatos, novo_df], ignore_index=True)
                    
                    # Salvar
                    if salvar_contatos(contatos_atualizados):
                        st.success(f"✅ Contato '{nome}' adicionado com sucesso!")
                        st.balloons()
                    else:
                        st.error("❌ Erro ao adicionar contato")
                else:
                    st.error("❌ Nome e telefone são obrigatórios")
    
    with tab3:
        st.subheader("📤 Importar / Exportar Contatos")
        
        # Exportar
        st.markdown("### 📥 Exportar Contatos")
        contatos = carregar_contatos()
        
        if not contatos.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV completo
                csv_completo = contatos.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📊 Baixar Todos (CSV)",
                    csv_completo,
                    "contatos_completos.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Apenas contatos completos
                contatos_completos = contatos[
                    (contatos["Nome"].notna()) & (contatos["Nome"] != "") &
                    (contatos["Número"].notna()) & (contatos["Número"] != "") &
                    (contatos["Email"].notna()) & (contatos["Email"] != "")
                ]
                if not contatos_completos.empty:
                    csv_completos = contatos_completos.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "✅ Baixar Completos (CSV)",
                        csv_completos,
                        "contatos_completos.csv",
                        "text/csv",
                        use_container_width=True
                    )
        
        # Importar
        st.markdown("### 📤 Importar Contatos")
        uploaded_file = st.file_uploader(
            "📁 Selecione arquivo CSV para importar",
            type=['csv'],
            help="O arquivo deve conter as colunas: Nome, Número, Email, Cidade, Observação"
        )
        
        if uploaded_file is not None:
            try:
                # Ler arquivo
                df_importado = pd.read_csv(uploaded_file)
                
                st.success(f"✅ Arquivo lido: {len(df_importado)} registros encontrados")
                st.subheader("👀 Preview dos Dados")
                st.dataframe(df_importado.head(10), use_container_width=True)
                
                # Validar colunas
                colunas_esperadas = ["Nome", "Número", "Email", "Cidade", "Observação"]
                colunas_arquivo = df_importado.columns.tolist()
                
                st.markdown("### 🔍 Mapeamento de Colunas")
                mapeamento = {}
                for col_esperada in colunas_esperadas:
                    opcoes = ["-- Não mapear --"] + colunas_arquivo
                    col_selecionada = st.selectbox(
                        f"Mapear '{col_esperada}' para:",
                        opcoes,
                        index=opcoes.index(col_esperada) if col_esperada in opcoes else 0
                    )
                    if col_selecionada != "-- Não mapear --":
                        mapeamento[col_esperada] = col_selecionada
                
                # Opções de importação
                col1, col2 = st.columns(2)
                with col1:
                    sobrescrever = st.checkbox("Sobrescrever arquivo atual", value=False)
                with col2:
                    apenas_novos = st.checkbox("Apenas registros novos", value=True)
                
                # Botão de importação
                if st.button("📥 Importar Contatos", type="primary"):
                    try:
                        # Aplicar mapeamento
                        df_mapeado = pd.DataFrame()
                        for col_destino, col_origem in mapeamento.items():
                            if col_origem in df_importado.columns:
                                df_mapeado[col_destino] = df_importado[col_origem]
                            else:
                                df_mapeado[col_destino] = ""
                        
                        # Preencher colunas faltantes
                        for col in colunas_esperadas:
                            if col not in df_mapeado.columns:
                                df_mapeado[col] = ""
                        
                        # Carregar contatos existentes
                        if sobrescrever:
                            contatos_final = df_mapeado
                        else:
                            contatos_existentes = carregar_contatos()
                            if apenas_novos and not contatos_existentes.empty:
                                # Filtrar duplicados por Nome+Número
                                chaves_existentes = contatos_existentes["Nome"] + "|" + contatos_existentes["Número"]
                                chaves_novas = df_mapeado["Nome"] + "|" + df_mapeado["Número"]
                                df_novos = df_mapeado[~chaves_novas.isin(chaves_existentes)]
                                contatos_final = pd.concat([contatos_existentes, df_novos], ignore_index=True)
                            else:
                                contatos_final = pd.concat([contatos_existentes, df_mapeado], ignore_index=True)
                        
                        # Salvar
                        if salvar_contatos(contatos_final):
                            novos_importados = len(contatos_final) - len(carregar_contatos()) if not sobrescrever else len(df_mapeado)
                            st.success(f"✅ Importação concluída! {novos_importados} contatos adicionados.")
                            st.balloons()
                        else:
                            st.error("❌ Erro ao salvar contatos importados")
                    
                    except Exception as e:
                        st.error(f"❌ Erro durante a importação: {str(e)}")
            
            except Exception as e:
                st.error(f"❌ Erro ao ler arquivo: {str(e)}")
        
        # Informações de formato
        with st.expander("ℹ️ Formato do Arquivo CSV"):
            st.markdown("""
            ### 📋 Formato Esperado:
            ```
            Nome,Número,Email,Cidade,Observação
            João Silva,16999999999,joao@email.com,Ribeirão Preto,Cliente importante
            Empresa XYZ,1133334444,contato@xyz.com,São Paulo,Fornecedor
            ```
            
            ### ✅ Dicas:
            - Use vírgula (,) como separador
            - Nome e Número são obrigatórios
            - Outros campos são opcionais
            - Encode em UTF-8 para caracteres especiais
            """)
