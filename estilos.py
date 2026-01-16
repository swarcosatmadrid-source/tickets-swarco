# =============================================================================
# ARCHIVO: estilos.py
# VERSIÓN: CORREGIDA POR EL USUARIO (Ruta: logo.png)
# =============================================================================

import streamlit as st
import os
from PIL import Image

def cargar_estilos():
    """CSS Corporativo Naranja Swarco #FF5D00"""
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
        div[data-testid="stForm"] .stTextInput input[aria-invalid="true"] {
            border: 2px solid #FF0000 !important;
            background-color: #FFF5F5 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        # RUTA CORRECTA CONFIRMADA POR TI
        ruta = "logo.png"
        
        if os.path.exists(ruta):
            try:
                img = Image.open(ruta)
                st.image(img, use_container_width=True)
            except:
                st.image(ruta, use_container_width=True)
        else:
            # Si por alguna razón mágica desaparece, texto de respaldo
            st.markdown("<h2 class='swarco-title'>SWARCO</h2>", unsafe_allow_html=True)



