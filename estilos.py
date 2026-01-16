# =============================================================================
# ARCHIVO: estilos.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 1.1.0 (Color #FF5D00 | Ruta logo/logo.png)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Identidad visual corporativa.
# =============================================================================

import streamlit as st

def cargar_estilos():
    """Configura el CSS con el naranja oficial de Swarco."""
    st.markdown("""
        <style>
        .swarco-title {
            color: #FF5D00 !important;
            font-size: 28px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 25px;
        }
        .stButton>button {
            background-color: #FF5D00 !important;
            color: white !important;
            font-weight: bold;
            border-radius: 8px;
            height: 3em;
            border: none;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    """Muestra el logo centrado desde la carpeta de GitHub."""
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image("logo/logo.png", use_container_width=True)
