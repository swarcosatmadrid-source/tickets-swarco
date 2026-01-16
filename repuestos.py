# =============================================================================
# ARCHIVO: repuestos.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 0.1.0 (Coming Soon)
# DESCRIPCIÓN: Módulo para la gestión de piezas y repuestos (En desarrollo).
# =============================================================================
import streamlit as st
import estilos

def mostrar_repuestos(t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">📦 {t.get("btn_repuestos", "Repuestos")}</p>', unsafe_allow_html=True)
    
    st.warning("### 🏗️ Coming Soon / Próximamente")
    st.info("Estamos trabajando en el módulo de gestión de stock y pedidos de piezas originales Swarco.")
    
    if st.button(f"⬅️ {t.get('btn_volver', 'VOLVER')}"):
        st.session_state.pagina_actual = 'menu'
        st.rerun()
