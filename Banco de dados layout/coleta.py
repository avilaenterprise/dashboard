import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os

def salvar_coleta(dados_coleta):
    """
    Salva a ordem de coleta em arquivo CSV
    """
    try:
        # Verifica se arquivo existe
        if os.path.exists("coletas.csv"):
            df_existing = pd.read_csv("coletas.csv", sep=";")
            df_new = pd.DataFrame([dados_coleta])
            df_final = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_final = pd.DataFrame([dados_coleta])
        
        df_final.to_csv("coletas.csv", sep=";", index=False, encoding="utf-8")
        return True
    except Exception as e:
        st.error(f"Erro ao salvar coleta: {e}")
        return False

def gerar_numero_coleta():
    """
    Gera número sequencial para a coleta
    """
    try:
        if os.path.exists("coletas.csv"):
            df = pd.read_csv("coletas.csv", sep=";")
            if not df.empty:
                ultimo_num = df["Número Coleta"].max()
                return ultimo_num + 1
        return 1001  # Número inicial
    except:
        return 1001

def mostrar_coleta():
    """
    Interface principal do módulo de ordem de coleta
    """
    st.header("📦 Sistema de Ordem de Coleta")
    
    # Criar abas
    tab1, tab2, tab3 = st.tabs(["Nova Coleta", "Agendar Coleta", "Histórico"])
    
    with tab1:
        st.subheader("📝 Nova Ordem de Coleta")
        
        with st.form("form_coleta"):
            # Número da coleta
            numero_coleta = gerar_numero_coleta()
            st.info(f"**Número da Coleta:** {numero_coleta}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📍 Dados do Remetente**")
                remetente_nome = st.text_input("Nome/Empresa *", key="rem_nome")
                remetente_endereco = st.text_input("Endereço *", key="rem_end")
                remetente_cidade = st.text_input("Cidade *", key="rem_cidade")
                remetente_telefone = st.text_input("Telefone *", key="rem_tel")
                remetente_contato = st.text_input("Pessoa de Contato", key="rem_contato")
                
                st.markdown("**⏰ Dados da Coleta**")
                data_coleta = st.date_input("Data da Coleta *", value=date.today() + timedelta(days=1))
                horario_inicio = st.time_input("Horário Início", value=datetime.now().time())
                horario_fim = st.time_input("Horário Fim", value=(datetime.now() + timedelta(hours=2)).time())
                
            with col2:
                st.markdown("**📍 Dados do Destinatário**")
                destinatario_nome = st.text_input("Nome/Empresa *", key="dest_nome")
                destinatario_endereco = st.text_input("Endereço *", key="dest_end")
                destinatario_cidade = st.text_input("Cidade *", key="dest_cidade")
                destinatario_telefone = st.text_input("Telefone *", key="dest_tel")
                destinatario_contato = st.text_input("Pessoa de Contato", key="dest_contato")
                
                st.markdown("**📦 Dados da Carga**")
                tipo_mercadoria = st.selectbox("Tipo de Mercadoria", 
                                             ["Documentos", "Eletrônicos", "Roupas", "Alimentos", 
                                              "Materiais de Construção", "Outros"])
                quantidade_volumes = st.number_input("Quantidade de Volumes", min_value=1, value=1)
                peso_total = st.number_input("Peso Total (kg)", min_value=0.1, value=1.0, step=0.1)
                valor_mercadoria = st.number_input("Valor da Mercadoria (R$)", min_value=0.0, value=0.0, step=0.01)
            
            observacoes = st.text_area("Observações Especiais", 
                                     placeholder="Instruções especiais, restrições de horário, etc.")
            
            urgente = st.checkbox("🚨 Coleta Urgente")
            
            submitted = st.form_submit_button("📋 Criar Ordem de Coleta", use_container_width=True)
            
            if submitted:
                # Validar campos obrigatórios
                campos_obrigatorios = [
                    remetente_nome, remetente_endereco, remetente_cidade, remetente_telefone,
                    destinatario_nome, destinatario_endereco, destinatario_cidade, destinatario_telefone
                ]
                
                if all(campos_obrigatorios):
                    # Criar dados da coleta
                    coleta = {
                        "Número Coleta": numero_coleta,
                        "Data Criação": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Data Coleta": data_coleta.strftime("%Y-%m-%d"),
                        "Horário Início": horario_inicio.strftime("%H:%M"),
                        "Horário Fim": horario_fim.strftime("%H:%M"),
                        "Remetente Nome": remetente_nome,
                        "Remetente Endereço": remetente_endereco,
                        "Remetente Cidade": remetente_cidade,
                        "Remetente Telefone": remetente_telefone,
                        "Remetente Contato": remetente_contato,
                        "Destinatário Nome": destinatario_nome,
                        "Destinatário Endereço": destinatario_endereco,
                        "Destinatário Cidade": destinatario_cidade,
                        "Destinatário Telefone": destinatario_telefone,
                        "Destinatário Contato": destinatario_contato,
                        "Tipo Mercadoria": tipo_mercadoria,
                        "Quantidade Volumes": quantidade_volumes,
                        "Peso Total (kg)": peso_total,
                        "Valor Mercadoria (R$)": valor_mercadoria,
                        "Observações": observacoes,
                        "Urgente": "Sim" if urgente else "Não",
                        "Status": "Agendada",
                        "Motorista": "",
                        "Veículo": ""
                    }
                    
                    # Salvar coleta
                    if salvar_coleta(coleta):
                        st.success(f"✅ Ordem de Coleta {numero_coleta} criada com sucesso!")
                        
                        # Exibir resumo
                        st.markdown("### 📋 Resumo da Coleta")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Número", numero_coleta)
                        with col2:
                            st.metric("Data", data_coleta.strftime("%d/%m/%Y"))
                        with col3:
                            st.metric("Volumes", quantidade_volumes)
                        
                        # Informações detalhadas
                        with st.expander("📄 Detalhes da Coleta"):
                            st.write(f"**Remetente:** {remetente_nome}")
                            st.write(f"**Endereço:** {remetente_endereco}, {remetente_cidade}")
                            st.write(f"**Destinatário:** {destinatario_nome}")
                            st.write(f"**Endereço:** {destinatario_endereco}, {destinatario_cidade}")
                            st.write(f"**Mercadoria:** {tipo_mercadoria}")
                            st.write(f"**Peso:** {peso_total} kg")
                            if observacoes:
                                st.write(f"**Observações:** {observacoes}")
                else:
                    st.error("❌ Preencha todos os campos obrigatórios (*)")
    
    with tab2:
        st.subheader("📅 Agendar Coletas do Dia")
        
        try:
            if os.path.exists("coletas.csv"):
                df_coletas = pd.read_csv("coletas.csv", sep=";")
                
                # Filtrar coletas agendadas
                coletas_agendadas = df_coletas[df_coletas["Status"] == "Agendada"]
                
                if not coletas_agendadas.empty:
                    data_selecionada = st.date_input("Selecionar Data", value=date.today())
                    
                    # Filtrar por data
                    coletas_dia = coletas_agendadas[
                        pd.to_datetime(coletas_agendadas["Data Coleta"]).dt.date == data_selecionada
                    ]
                    
                    if not coletas_dia.empty:
                        st.markdown(f"### 📦 Coletas para {data_selecionada.strftime('%d/%m/%Y')}")
                        
                        for idx, coleta in coletas_dia.iterrows():
                            with st.expander(f"Coleta #{coleta['Número Coleta']} - {coleta['Remetente Nome']}"):
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.write("**Remetente:**")
                                    st.write(f"{coleta['Remetente Nome']}")
                                    st.write(f"{coleta['Remetente Endereço']}")
                                    st.write(f"{coleta['Remetente Cidade']}")
                                    st.write(f"Tel: {coleta['Remetente Telefone']}")
                                
                                with col2:
                                    st.write("**Destinatário:**")
                                    st.write(f"{coleta['Destinatário Nome']}")
                                    st.write(f"{coleta['Destinatário Endereço']}")
                                    st.write(f"{coleta['Destinatário Cidade']}")
                                    st.write(f"Tel: {coleta['Destinatário Telefone']}")
                                
                                with col3:
                                    st.write("**Detalhes:**")
                                    st.write(f"Horário: {coleta['Horário Início']} - {coleta['Horário Fim']}")
                                    st.write(f"Volumes: {coleta['Quantidade Volumes']}")
                                    st.write(f"Peso: {coleta['Peso Total (kg)']} kg")
                                    st.write(f"Tipo: {coleta['Tipo Mercadoria']}")
                                    
                                    if coleta['Urgente'] == "Sim":
                                        st.error("🚨 URGENTE")
                                
                                # Ações
                                col_act1, col_act2, col_act3 = st.columns(3)
                                with col_act1:
                                    if st.button(f"✅ Executar", key=f"exec_{coleta['Número Coleta']}"):
                                        # Atualizar status para "Em Execução"
                                        df_coletas.loc[idx, "Status"] = "Em Execução"
                                        df_coletas.to_csv("coletas.csv", sep=";", index=False)
                                        st.success("Status atualizado!")
                                        st.rerun()
                                
                                with col_act2:
                                    if st.button(f"✅ Concluir", key=f"conc_{coleta['Número Coleta']}"):
                                        # Atualizar status para "Concluída"
                                        df_coletas.loc[idx, "Status"] = "Concluída"
                                        df_coletas.to_csv("coletas.csv", sep=";", index=False)
                                        st.success("Coleta concluída!")
                                        st.rerun()
                                
                                with col_act3:
                                    if st.button(f"❌ Cancelar", key=f"canc_{coleta['Número Coleta']}"):
                                        # Atualizar status para "Cancelada"
                                        df_coletas.loc[idx, "Status"] = "Cancelada"
                                        df_coletas.to_csv("coletas.csv", sep=";", index=False)
                                        st.warning("Coleta cancelada!")
                                        st.rerun()
                    else:
                        st.info(f"Nenhuma coleta agendada para {data_selecionada.strftime('%d/%m/%Y')}")
                else:
                    st.info("Nenhuma coleta agendada.")
            else:
                st.info("Nenhuma coleta cadastrada ainda.")
        except Exception as e:
            st.error(f"Erro ao carregar coletas: {e}")
    
    with tab3:
        st.subheader("📊 Histórico de Coletas")
        
        try:
            if os.path.exists("coletas.csv"):
                df_coletas = pd.read_csv("coletas.csv", sep=";")
                
                if not df_coletas.empty:
                    # Filtros
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        status_filter = st.selectbox("Status", 
                                                   ["Todos"] + list(df_coletas["Status"].unique()))
                    with col2:
                        cidade_filter = st.selectbox("Cidade Origem", 
                                                   ["Todas"] + list(df_coletas["Remetente Cidade"].unique()))
                    with col3:
                        periodo = st.selectbox("Período", ["Últimos 7 dias", "Últimos 30 dias", "Todos"])
                    
                    # Aplicar filtros
                    df_filtered = df_coletas.copy()
                    
                    if status_filter != "Todos":
                        df_filtered = df_filtered[df_filtered["Status"] == status_filter]
                    
                    if cidade_filter != "Todas":
                        df_filtered = df_filtered[df_filtered["Remetente Cidade"] == cidade_filter]
                    
                    if periodo != "Todos":
                        dias = 7 if periodo == "Últimos 7 dias" else 30
                        data_limite = (datetime.now() - timedelta(days=dias)).date()
                        df_filtered["Data_filtro"] = pd.to_datetime(df_filtered["Data Coleta"]).dt.date
                        df_filtered = df_filtered[df_filtered["Data_filtro"] >= data_limite]
                        df_filtered = df_filtered.drop("Data_filtro", axis=1)
                    
                    # Exibir dados
                    st.dataframe(df_filtered, use_container_width=True)
                    
                    # Estatísticas
                    if not df_filtered.empty:
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total de Coletas", len(df_filtered))
                        with col2:
                            concluidas = len(df_filtered[df_filtered["Status"] == "Concluída"])
                            st.metric("Concluídas", concluidas)
                        with col3:
                            agendadas = len(df_filtered[df_filtered["Status"] == "Agendada"])
                            st.metric("Agendadas", agendadas)
                        with col4:
                            peso_total = df_filtered["Peso Total (kg)"].sum()
                            st.metric("Peso Total", f"{peso_total:.1f} kg")
                    
                    # Download
                    csv = df_filtered.to_csv(index=False, sep=";").encode("utf-8")
                    st.download_button(
                        "📥 Baixar Histórico (CSV)",
                        csv,
                        "historico_coletas.csv",
                        "text/csv"
                    )
                else:
                    st.info("Nenhuma coleta encontrada.")
            else:
                st.info("Nenhuma coleta cadastrada ainda.")
        except Exception as e:
            st.error(f"Erro ao carregar histórico: {e}")
