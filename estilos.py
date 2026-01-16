# ==========================================
# ARCHIVO: estilos.py
# PROYECTO: TicketV0 -> DISEÑO CORPORATIVO
# VERSIÓN: v1.2 (Recuperación de Cabecera y Candado)
# COMPARACIÓN: Añade el banner superior y mejora los rectángulos.
# ==========================================
import streamlit as st

def cargar_estilos():
    st.markdown("""
        <style>
        /* Fondo de la cabecera con el diseño que viste */
        .main-header {
            background-color: #00549F;
            padding: 20px;
            border-radius: 10px 10px 0px 0px;
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }
        
        /* Los rectángulos naranja bien puestos */
        div.stButton > button {
            background-color: #F29400 !important;
            color: white !important;
            border: 2px solid #d68300 !important;
            border-radius: 8px !important;
            font-weight: bold !important;
            height: 3em !important;
            width: 100% !important;
            text-transform: uppercase;
        }

        /* Estilo para el contenedor del login */
        .login-box {
            border: 1px solid #e6e9ef;
            border-radius: 10px;
            padding: 25px;
            background-color: #ffffff;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        h1, h2, h3 { color: #00549F !important; }
        </style>
    """, unsafe_allow_html=True)

def mostrar_cabecera_login():
    """Muestra el diseño con el candado y el título que viste en la foto."""
    st.markdown("""
        <div class="main-header">
            <h1 style="color: white !important; margin:0;">🔒 SISTEMA DE ACCESO</h1>
            <p style="margin:0;">Swarco Traffic Spain - SAT Portal</p>
        </div>
    """, unsafe_allow_html=True)

def mostrar_logo():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        try:
            st.image("logo.png", width=250)
        except:
            pass
