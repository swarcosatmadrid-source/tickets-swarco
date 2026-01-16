# ==========================================
# ARCHIVO: estilos.py
# PROYECTO: TicketV0
# VERSIÓN: v1.5 (LOOK RECUPERADO DE FOTO)
# ==========================================
import streamlit as st

def cargar_estilos():
    st.markdown("""
        <style>
        /* Títulos Azules Estilo Foto */
        .swarco-title { color: #00549F; font-size: 28px; font-weight: bold; text-align: center; margin-bottom: 0px; }
        .swarco-subtitle { color: #00549F; font-size: 20px; font-weight: bold; text-align: center; margin-top: 0px; }
        
        /* Botones NARANJAS GRANDES (Ambos iguales como en la foto) */
        div.stButton > button, div.stForm submit_button > button {
            background-color: #F29400 !important;
            color: white !important;
            border: none !important;
            border-radius: 4px !important;
            font-weight: bold !important;
            width: 100% !important;
            padding: 0.75rem !important;
            text-transform: uppercase !important;
        }
        
        /* Inputs */
        div[data-baseweb="input"] > div {
            background-color: #f0f2f6 !important;
            border-radius: 4px !important;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try: st.image("logo.png", use_container_width=True)
        except: pass
