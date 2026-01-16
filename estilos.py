# ==========================================
# ARCHIVO: estilos.py
# PROYECTO: TicketV0
# VERSIÓN: v1.0 (Original Hoy 16-Ene)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Definición de CSS corporativo y centrado de logo.
# ==========================================

import streamlit as st

def cargar_estilos():
    """Carga el CSS para los botones naranja y títulos azules."""
    st.markdown("""
        <style>
        /* Botón Naranja Swarco */
        div.stButton > button {
            background-color: #F29400 !important;
            color: white !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            width: 100% !important;
            border: none !important;
            padding: 0.6rem 2rem !important;
        }
        
        /* Efecto Hover */
        div.stButton > button:hover {
            background-color: #d68300 !important;
        }

        /* Títulos en Azul Swarco */
        h1, h2, h3, h4 { 
            color: #00549F !important; 
            text-align: center !important; 
        }
        
        /* Inputs con fondo suave */
        div[data-baseweb="input"] > div {
            background-color: #f0f2f6 !important;
            border-radius: 6px !important;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    """Muestra el logo centrado usando columnas."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            # v1.0: Carga del logo local
            st.image("logo.png", width=300)
        except:
            st.write("### 🚦 SWARCO TRAFFIC SPAIN")
