# =============================================================================
# ARCHIVO: estilos.py
# VERSIÓN: 3.0.0 (ARQUITECTURA RÍGIDA)
# =============================================================================
import streamlit as st
import os

def cargar_estilos():
    """Define la identidad visual crítica."""
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
            border: none;
            border-radius: 5px;
            height: 45px;
            font-weight: bold;
        }
        /* Corrección para que los inputs se vean bien */
        .stTextInput>div>div>input {
            border: 1px solid #ddd;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    """Muestra el logo sin hacer preguntas complejas al sistema."""
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        # Intenta cargar la ruta exacta. Si falla, pone texto para no romper la app.
        try:
            st.image("logo/logo.png", use_container_width=True)
        except:
            st.markdown("<h2 style='text-align:center; color:#FF5D00'>SWARCO</h2>", unsafe_allow_html=True)
