# ARCHIVO: estilos.py
# VERSIÓN: v1.2 (Corrección Nuclear de Botones)
# FECHA: 15-Ene-2026
# DESCRIPCIÓN: Se fuerza el color naranja con selectores CSS agresivos y !important para sobreescribir el tema por defecto.

import streamlit as st

def cargar_estilos():
    st.markdown("""
        <style>
        /* --- 1. ATAQUE DIRECTO A TODOS LOS BOTONES --- */
        
        /* Selector General para botones normales */
        div.stButton > button {
            background-color: #F29400 !important; /* Naranja Swarco */
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            padding: 0.6rem 2rem !important;
        }

        /* Selector Específico por Atributo (Para saltarse la seguridad de Streamlit en botones primarios y secundarios) */
        button[kind="secondary"], button[kind="primary"] {
            background-color: #F29400 !important;
            color: white !important;
            border: none !important;
        }

        /* Texto dentro del botón (A veces el texto hereda otro color) */
        div.stButton > button > div > p, div.stButton > button > div {
            color: white !important;
        }

        /* --- 2. HOVER (Efecto al pasar el mouse) --- */
        div.stButton > button:hover, button[kind="secondary"]:hover, button[kind="primary"]:hover {
            background-color: #d68300 !important; /* Naranja más oscuro */
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
            color: #00549F; /* Azul Swarco */
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

# --- FUNCIÓN DE LOGO CENTRADO ---
def mostrar_logo():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            # Si no hay imagen, no rompe la app
            pass
