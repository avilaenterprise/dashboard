import streamlit as st

def mostrar_minutas(base):
    st.header("🔍 Consulta de Minuta")
    filtro = st.text_input("Digite número, nome, cidade ou pagador:")
    if filtro:
        resultado = base[
            base["Número"].astype(str).str.contains(filtro) |
            base["Remetente - Nome"].astype(str).str.contains(filtro, case=False, na=False) |
            base["Destinatário - Nome"].astype(str).str.contains(filtro, case=False, na=False) |
            base["Pagador do Frete - Nome"].astype(str).str.contains(filtro, case=False, na=False) |
            base["Destinatário - Cidade"].astype(str).str.contains(filtro, case=False, na=False)
        ]
        st.dataframe(resultado, use_container_width=True)
