# =============================================================================
# ARCHIVO: estilos.py
# VERSIÓN: 3.5.0 (Carga Robusta con PIL para evitar MediaFileStorageError)
# =============================================================================

import streamlit as st
import os
from PIL import Image # Usamos PIL para abrir la imagen directamente

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
        /* Bordes rojos para errores */
        div[data-testid="stForm"] .stTextInput input[aria-invalid="true"] {
            border: 2px solid #FF0000 !important;
            background-color: #FFF5F5 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        ruta = "logo/logo.png"
        
        # 1. Verificamos existencia física
        if os.path.exists(ruta):
            try:
                # 2. Abrimos con PIL (Esto evita el error de MediaFileStorage)
                img = Image.open(ruta)
                st.image(img, use_container_width=True)
            except Exception as e:
                # Si la imagen está corrupta, mostramos texto sin romper la app
                st.markdown("<h2 class='swarco-title'>SWARCO</h2>", unsafe_allow_html=True)
                st.caption(f"Error formato imagen: {e}")
        else:
            # Si no existe, mostramos texto y debug
            st.markdown("<h2 class='swarco-title'>SWARCO</h2>", unsafe_allow_html=True)
            # Solo para que sepas qué está pasando (puedes borrar esto luego)
            st.error(f"El sistema no ve el archivo en: {os.path.abspath(ruta)}")
            if os.path.exists("logo"):
                st.info(f"Contenido carpeta 'logo': {os.listdir('logo')}")

