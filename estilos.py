# =============================================================================
# ARCHIVO: estilos.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 1.1.0 (Inyección de CSS Dinámico)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Gestiona la identidad visual corporativa y la manipulación
#              de elementos DOM para validaciones visuales.
# =============================================================================

import streamlit as st

def cargar_estilos():
    """Carga el CSS base de Swarco (Colores corporativos y fuentes)."""
    st.markdown("""
        <style>
        .swarco-title {
            color: #FF5D00;
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        /* Botón Naranja Corporativo */
        .stButton>button {
            background-color: #FF5D00;
            color: white;
            border-radius: 5px;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    """Muestra el logo de Swarco en el encabezado."""
    st.image("logo_swarco.png", width=200)

def aplicar_bordes_rojos():
    """
    Inyecta CSS específico para resaltar en rojo los campos 
    que fallan la validación en el formulario de registro.
    """
    st.markdown("""
        <style>
        /* Selecciona los inputs de Streamlit que el usuario dejó vacíos */
        div[data-testid="stForm"] div[data-baseweb="input"] {
            transition: border 0.3s ease;
        }
        
        /* Aplicamos el borde rojo sangre cuando la lógica lo requiera */
        .field-error input {
            border: 2px solid #FF0000 !important;
            background-color: #FFF5F5 !important;
        }
        
        .error-text {
            color: #FF0000;
            font-weight: bold;
            font-size: 0.8rem;
        }
        </style>
    """, unsafe_allow_html=True)

