# =============================================================================
# ARCHIVO: estilos.py
# VERSIÓN: 5.0.0 (Premium: Bordes Rojos + Naranja Real + Logo Raíz)
# =============================================================================
import streamlit as st
import os
from PIL import Image

def cargar_estilos():
    st.markdown("""
        <style>
        /* 1. NARANJA SWARCO EXACTO */
        :root { --swarco-orange: #FF5D00; }
        
        .swarco-title {
            color: var(--swarco-orange) !important;
            font-size: 2.2rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* 2. BOTONES ESTILIZADOS */
        div.stButton > button {
            background-color: var(--swarco-orange) !important;
            color: white !important;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            height: 3rem;
            width: 100%;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            background-color: #E04E00 !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        /* 3. INPUTS CON BORDE ROJO CUANDO HAY ERROR */
        /* Esta clase se activa cuando inyectamos el error visual */
        .stTextInput input[aria-invalid="true"], .stTextInput div[data-error="true"] input {
            border: 2px solid #FF0000 !important;
            background-color: #FFF0F0 !important;
        }
        
        /* 4. SEPARADORES */
        hr { margin: 2em 0; border-color: #eee; }
        
        /* 5. ENLACES LEGALES */
        a { color: var(--swarco-orange) !important; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        # RUTA CORRECTA: Raíz (logo.png)
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.markdown("<h1 class='swarco-title'>SWARCO</h1>", unsafe_allow_html=True)



