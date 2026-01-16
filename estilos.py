# =============================================================================
# ARCHIVO: estilos.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 1.0.4 (Lectura Directa de Directorio)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Carga de logo basada en la estructura real de carpetas de GitHub.
# =============================================================================

import streamlit as st
import os

def cargar_estilos():
    """Carga el CSS base de Swarco."""
    st.markdown("""
        <style>
        .swarco-title {
            color: #FF5D00;
            font-size: 30px;
            font-weight: bold;
            text-align: center;
            margin-top: -10px;
            margin-bottom: 25px;
        }
        .stButton>button {
            background-color: #FF5D00;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            height: 3em;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    """Detecta el archivo dentro de la carpeta logo/ y lo muestra."""
    ruta_carpeta = "logo"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            # Listamos archivos en la carpeta que me indicaste
            if os.path.exists(ruta_carpeta):
                archivos = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                if archivos:
                    # Usamos el primer archivo de imagen que aparezca en tu carpeta
                    st.image(f"{ruta_carpeta}/{archivos[0]}", use_container_width=True)
                else:
                    st.warning("Carpeta 'logo' vacía.")
            else:
                st.error(f"No encuentro la carpeta: {ruta_carpeta}")
        except Exception as e:
            st.markdown("<h1 style='text-align: center; color: #FF5D00;'>SWARCO</h1>", unsafe_allow_html=True)
