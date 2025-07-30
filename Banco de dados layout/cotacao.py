import streamlit as st
import pandas as pd
from datetime import datetime
import os

def calcular_frete(peso, distancia, tipo_carga="Normal"):
    """
    Calcula o valor do frete baseado em peso, distância e tipo de carga
    """
    # Tabela base de preços por km
    preco_base = {
        "Normal": 2.50,
        "Frágil": 3.00,
        "Perigosa": 3.50,
        "Refrigerada": 4.00
    }
    
    # Fator de peso (R$/kg)
    fator_peso = 0.15
    
    # Cálculo base
    valor_distancia = distancia * preco_base.get(tipo_carga, 2.50)
    valor_peso = peso * fator_peso
    
    # Valor mínimo
    valor_minimo = 150.00
    
    return max(valor_minimo, valor_distancia + valor_peso)

def salvar_cotacao(dados_cotacao):
    """
    Salva a cotação em arquivo CSV
    """
    try:
        # Verifica se arquivo existe
        if os.path.exists("cotacoes.csv"):
            df_existing = pd.read_csv("cotacoes.csv", sep=";")
            df_new = pd.DataFrame([dados_cotacao])
            df_final = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_final = pd.DataFrame([dados_cotacao])
        
        df_final.to_csv("cotacoes.csv", sep=";", index=False, encoding="utf-8")
        return True
    except Exception as e:
        st.error(f"Erro ao salvar cotação: {e}")
        return False

def mostrar_cotacao():
    """
    Interface principal do módulo de cotação
    """
    st.header("💰 Sistema de Cotação de Fretes")
    
    # Criar abas
    tab1, tab2, tab3 = st.tabs(["Nova Cotação", "Histórico", "Configurações"])
    
    with tab1:
        st.subheader("📝 Nova Cotação")
        
        with st.form("form_cotacao"):
            col1, col2 = st.columns(2)
            
            with col1:
                cliente = st.text_input("Cliente *", placeholder="Nome do cliente")
                origem = st.text_input("Origem *", placeholder="Cidade de origem")
                destino = st.text_input("Destino *", placeholder="Cidade de destino")
                distancia = st.number_input("Distância (km) *", min_value=1, value=100)
                
            with col2:
                peso = st.number_input("Peso (kg) *", min_value=0.1, value=10.0, step=0.1)
                tipo_carga = st.selectbox("Tipo de Carga", 
                                        ["Normal", "Frágil", "Perigosa", "Refrigerada"])
                prazo = st.number_input("Prazo (dias)", min_value=1, value=3)
                observacoes = st.text_area("Observações", placeholder="Observações adicionais...")
            
            submitted = st.form_submit_button("🔢 Calcular Cotação", use_container_width=True)
            
            if submitted:
                if cliente and origem and destino:
                    # Calcular valor
                    valor = calcular_frete(peso, distancia, tipo_carga)
                    
                    # Dados da cotação
                    cotacao = {
                        "Data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Cliente": cliente,
                        "Origem": origem,
                        "Destino": destino,
                        "Distância (km)": distancia,
                        "Peso (kg)": peso,
                        "Tipo de Carga": tipo_carga,
                        "Prazo (dias)": prazo,
                        "Valor Cotado (R$)": valor,
                        "Status": "Pendente",
                        "Observações": observacoes
                    }
                    
                    # Exibir resultado
                    st.success("✅ Cotação calculada com sucesso!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Valor do Frete", f"R$ {valor:,.2f}")
                    with col2:
                        st.metric("Prazo", f"{prazo} dias")
                    with col3:
                        st.metric("Preço por kg", f"R$ {valor/peso:.2f}")
                    
                    # Botão para salvar
                    if st.button("💾 Salvar Cotação"):
                        if salvar_cotacao(cotacao):
                            st.success("Cotação salva com sucesso!")
                        else:
                            st.error("Erro ao salvar cotação")
                else:
                    st.error("Preencha todos os campos obrigatórios (*)")
    
    with tab2:
        st.subheader("📊 Histórico de Cotações")
        
        try:
            if os.path.exists("cotacoes.csv"):
                df_cotacoes = pd.read_csv("cotacoes.csv", sep=";")
                
                if not df_cotacoes.empty:
                    # Filtros
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        status_filter = st.selectbox("Filtrar por Status", 
                                                   ["Todos"] + list(df_cotacoes["Status"].unique()))
                    with col2:
                        cliente_filter = st.selectbox("Filtrar por Cliente", 
                                                    ["Todos"] + list(df_cotacoes["Cliente"].unique()))
                    with col3:
                        data_filter = st.date_input("Filtrar por Data", value=None)
                    
                    # Aplicar filtros
                    df_filtered = df_cotacoes.copy()
                    
                    if status_filter != "Todos":
                        df_filtered = df_filtered[df_filtered["Status"] == status_filter]
                    
                    if cliente_filter != "Todos":
                        df_filtered = df_filtered[df_filtered["Cliente"] == cliente_filter]
                    
                    if data_filter:
                        df_filtered["Data_filtro"] = pd.to_datetime(df_filtered["Data"]).dt.date
                        df_filtered = df_filtered[df_filtered["Data_filtro"] == data_filter]
                        df_filtered = df_filtered.drop("Data_filtro", axis=1)
                    
                    # Exibir tabela
                    st.dataframe(df_filtered, use_container_width=True)
                    
                    # Estatísticas
                    if not df_filtered.empty:
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total de Cotações", len(df_filtered))
                        with col2:
                            st.metric("Valor Médio", f"R$ {df_filtered['Valor Cotado (R$)'].mean():,.2f}")
                        with col3:
                            st.metric("Valor Total", f"R$ {df_filtered['Valor Cotado (R$)'].sum():,.2f}")
                        with col4:
                            pendentes = len(df_filtered[df_filtered["Status"] == "Pendente"])
                            st.metric("Pendentes", pendentes)
                    
                    # Download
                    csv = df_filtered.to_csv(index=False, sep=";").encode("utf-8")
                    st.download_button(
                        "📥 Baixar Cotações (CSV)",
                        csv,
                        "cotacoes_filtradas.csv",
                        "text/csv"
                    )
                else:
                    st.info("Nenhuma cotação encontrada.")
            else:
                st.info("Nenhuma cotação salva ainda.")
        except Exception as e:
            st.error(f"Erro ao carregar histórico: {e}")
    
    with tab3:
        st.subheader("⚙️ Configurações de Preços")
        
        st.markdown("**Tabela de Preços por Tipo de Carga (R$/km)**")
        
        col1, col2 = st.columns(2)
        with col1:
            normal = st.number_input("Carga Normal", value=2.50, step=0.10)
            fragil = st.number_input("Carga Frágil", value=3.00, step=0.10)
        with col2:
            perigosa = st.number_input("Carga Perigosa", value=3.50, step=0.10)
            refrigerada = st.number_input("Carga Refrigerada", value=4.00, step=0.10)
        
        fator_peso_config = st.number_input("Fator Peso (R$/kg)", value=0.15, step=0.01)
        valor_minimo_config = st.number_input("Valor Mínimo (R$)", value=150.00, step=10.00)
        
        if st.button("💾 Salvar Configurações"):
            st.success("Configurações salvas! (Funcionalidade em desenvolvimento)")
