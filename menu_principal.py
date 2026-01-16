import streamlit as st
import estilos

def mostrar_menu(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("menu_tit", "Menú")}</p>', unsafe_allow_html=True)
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
