# =============================================================================
# ARCHIVO: estilos.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 3.2.0 (Estilo Corporativo #FF5D00 + Ruta GitHub)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Definición de CSS y carga segura de recursos visuales.
# =============================================================================

import streamlit as st

def cargar_estilos():
    """Aplica el CSS corporativo."""
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
            border-radius: 5px;
            border: none;
            height: 45px;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    """Muestra el logo desde la carpeta logo/."""
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        # Ruta directa a tu carpeta de GitHub
        st.image("logo/logo.png", use_container_width=True)
