# ==========================================
# ARCHIVO: estilos.py
# PROYECTO: TicketV1
# VERSIÓN: v1.4 (Consola Limpia)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Eliminación definitiva de parámetros obsoletos
#              para limpiar los logs de Streamlit Cloud.
# ==========================================

import streamlit as st

def cargar_estilos():
    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #F29400 !important;
            color: white !important;
            border-radius: 6px !important;
            font-weight: bold !important;
        }
        button[kind="secondary"], button[kind="primary"] {
            background-color: #F29400 !important;
            color: white !important;
        }
        .section-header {
            border-bottom: 3px solid #F29400;
            color: #00549F;
            font-weight: 700;
            text-transform: uppercase;
        }
        h1, h2, h3 { color: #00549F !important; text-align: center !important; }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        try:
            # v1.4: Uso de width estricto para evitar warnings en 2026
            st.image("logo.png", width=240)
        except:
            pass
