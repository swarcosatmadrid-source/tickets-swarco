# =============================================================================
# ARCHIVO: estilos.py
# VERSIÓN: 1.0.1 (Restauración de Identidad Visual)
# =============================================================================

import streamlit as st
import os

def cargar_estilos():
    st.markdown("""
        <style>
        .swarco-title {
            color: #FF5D00;
            font-size: 30px;
            font-weight: bold;
            text-align: center;
            margin-top: -20px;
            margin-bottom: 20px;
        }
        .stButton>button {
            background-color: #FF5D00;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            border: none;
            padding: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    """Busca el logo y lo centra."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo_swarco.png"):
            st.image("logo_swarco.png", use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center; color: #FF5D00;'>SWARCO</h1>", unsafe_allow_html=True)

