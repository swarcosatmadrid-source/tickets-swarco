# =============================================================================
# ARCHIVO: estilos.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 1.0.0 (Restauración Estable)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Gestiona la identidad visual corporativa base.
# =============================================================================

import streamlit as st

def cargar_estilos():
    """Carga el CSS base de Swarco."""
    st.markdown("""
        <style>
        .swarco-title {
            color: #FF5D00;
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        .stButton>button {
            background-color: #FF5D00;
            color: white;
            border-radius: 5px;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    """Muestra el logo de Swarco."""
    try:
        st.image("logo_swarco.png", width=200)
    except:
        st.write("### SWARCO")

