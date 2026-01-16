# =============================================================================
# ARCHIVO: equipos_nuevos.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 0.1.0 (Coming Soon)
# DESCRIPCIÓN: Módulo para el registro de nuevas instalaciones (En desarrollo).
# =============================================================================
import streamlit as st
import estilos

def mostrar_equipos_nuevos(t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">🚜 {t.get("btn_equipos_nuevos", "Equipos Nuevos")}</p>', unsafe_allow_html=True)
    
    st.warning("### 🏗️ Coming Soon / Próximamente")
    st.info("Este espacio está reservado para el registro técnico de nuevas puestas en marcha e instalaciones.")
    
    if st.button(f"⬅️ {t.get('btn_volver', 'VOLVER')}"):
        st.session_state.pagina_actual = 'menu'
        st.rerun()
