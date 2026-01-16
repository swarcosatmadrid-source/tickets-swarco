# ==========================================
# ARCHIVO: estilos.py
# PROYECTO: TicketV0
# VERSIÓN: v1.4 (Pacto de Comparación)
# FECHA: 16-Ene-2026
# ==========================================
import streamlit as st

def cargar_estilos():
    st.markdown("""
        <style>
        /* Botón discreto dentro del Form (ENTRAR) */
        div.stForm submit_button > button {
            background-color: #ffffff !important;
            color: #00549F !important;
            border: 1px solid #00549F !important;
            border-radius: 4px !important;
            width: 100% !important;
        }
        
        /* Botón Naranja Resaltado (REGISTRO) */
        div.stButton > button {
            background-color: #F29400 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            padding: 0.6rem 2rem !important;
            width: 100% !important;
            text-transform: uppercase;
        }
        
        /* Títulos */
        h1, h2, h3 { color: #00549F !important; text-align: center !important; }
        
        /* Contenedor del form */
        div[data-testid="stForm"] {
            border: 1px solid #ddd !important;
            border-radius: 8px !important;
            padding: 1.5rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_cabecera_swarco():
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="margin:0;">🔒 ACCESO A CREACIÓN DE TICKETS</h2>
            <p style="color: #666; font-size: 14px;">Swarco Traffic Spain - Portal SAT</p>
        </div>
    """, unsafe_allow_html=True)

def mostrar_logo():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        try:
            st.image("logo.png", width=250)
        except:
            pass
