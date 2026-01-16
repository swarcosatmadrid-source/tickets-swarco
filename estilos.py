# ==========================================
# ARCHIVO: estilos.py
# PROYECTO: TicketV0
# VERSIÓN: v1.0 (ORIGINAL DE HOY)
# FECHA: 16-Ene-2026
# ==========================================
import streamlit as st

def cargar_estilos():
    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #F29400 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            padding: 0.6rem 2rem !important;
        }
        h1, h2, h3 { color: #00549F !important; text-align: center !important; }
        
        div[data-baseweb="input"] > div {
            background-color: #f0f2f6 !important;
            border-radius: 6px !important;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        try:
            st.image("logo.png", width=300)
        except:
            pass
