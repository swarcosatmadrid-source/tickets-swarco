# ARCHIVO: estilos.py
# VERSIÓN: v1.3 (Compatibilidad 2026)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Se eliminó 'use_container_width' en el logo porque causaba
#              error fatal en versiones de Streamlit posteriores a 2025.

import streamlit as st

def cargar_estilos():
    st.markdown("""
        <style>
        /* --- 1. ATAQUE DIRECTO A TODOS LOS BOTONES --- */
        div.stButton > button {
            background-color: #F29400 !important; /* Naranja Swarco */
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            padding: 0.6rem 2rem !important;
        }

        /* Selector Específico por Atributo */
        button[kind="secondary"], button[kind="primary"] {
            background-color: #F29400 !important;
            color: white !important;
            border: none !important;
        }

        /* Texto dentro del botón */
        div.stButton > button > div > p, div.stButton > button > div {
            color: white !important;
        }

        /* --- 2. HOVER (Efecto al pasar el mouse) --- */
        div.stButton > button:hover, button[kind="secondary"]:hover, button[kind="primary"]:hover {
            background-color: #d68300 !important; 
            color: white !important;
            border: none !important;
            transform: scale(1.02);
        }

        /* --- 3. INPUTS (Cajas de texto grises) --- */
        div[data-baseweb="input"] > div {
            background-color: #f0f2f6 !important;
            border: 1px solid #ccc !important;
            border-radius: 6px !important;
        }

        /* --- 4. TÍTULOS Y CABECERAS --- */
        .section-header {
            border-bottom: 3px solid #F29400;
            color: #00549F; 
            font-weight: 700;
            font-size: 1.1rem;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            text-transform: uppercase;
        }
        
        h1, h2, h3, h4, h5 { 
            color: #00549F !important; 
            text-align: center !important; 
        }

        /* Ocultar Header de Streamlit para limpieza */
        [data-testid="stHeader"] { 
            background: rgba(0,0,0,0); 
        }
        
        </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE LOGO CENTRADO (CORREGIDA PARA 2026) ---
def mostrar_logo():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        try:
            # CAMBIO AQUÍ: Quitamos use_container_width=True y ponemos width fijo
            st.image("logo.png", width=200)
        except:
            # Si no hay imagen, no rompe la app
            pass
