# ARCHIVO: estilos.py
# VERSIÓN: v1.1 (Naranja Reforzado)
# DESCRIPCIÓN: Usa selectores CSS más agresivos para garantizar el color.

import streamlit as st

def cargar_estilos():
    st.markdown("""
        <style>
        /* --- 1. BOTONES SWARCO (FUERZA BRUTA) --- */
        /* Apunta a todos los botones de Streamlit */
        div.stButton > button {
            background-color: #F29400 !important; /* Naranja Swarco */
            color: white !important;
            border: none !important;
            border-radius: 5px !important;
            font-weight: bold !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.3s ease;
        }

        /* Efecto al pasar el mouse */
        div.stButton > button:hover {
            background-color: #d68300 !important; /* Naranja más oscuro */
            color: white !important;
            transform: scale(1.02);
            border: none !important;
        }

        /* --- 2. INPUTS (Cajas de Texto) --- */
        div[data-baseweb="input"] > div {
            background-color: #f0f2f6 !important; /* Gris suave */
            border-radius: 5px !important;
            border: 1px solid #ccc !important;
        }

        /* --- 3. TÍTULOS Y LÍNEAS --- */
        /* Títulos centrados y azules */
        h1, h2, h3 { 
            color: #00549F !important; /* Azul Swarco */
            text-align: center !important;
        }
        h4, h5 {
            color: #666 !important;
            text-align: center !important;
        }

        /* Tu línea naranja divisoria */
        .section-header {
            border-bottom: 3px solid #F29400;
            color: #00549F;
            font-weight: 700;
            font-size: 1.1rem;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            text-transform: uppercase;
        }

        /* --- 4. HEADER INVISIBLE --- */
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0);
        }
        </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DE LOGO (Mantenemos la que funciona) ---
def mostrar_logo():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            # Si falla, no muestra nada para no ensuciar
            pass
