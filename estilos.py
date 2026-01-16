# ==========================================
# ARCHIVO: estilos.py | PROYECTO: TicketV1
# DESCRIPCIÓN: CSS Corporativo Swarco.
# ==========================================
import streamlit as st

def cargar_estilos():
    st.markdown("""
        <style>
        .swarco-title { color: #00549F; font-size: 26px; font-weight: bold; text-align: center; }
        .swarco-subtitle { color: #00549F; font-size: 18px; text-align: center; margin-top: -10px; }
        
        /* Botones Naranjas TicketV1 */
        div.stButton > button, div.stForm submit_button > button {
            background-color: #F29400 !important;
            color: white !important;
            border-radius: 5px !important;
            font-weight: bold !important;
            width: 100% !important;
            padding: 0.7rem !important;
            border: none !important;
            text-transform: uppercase;
        }
        
        /* Formulario Cuadro Blanco */
        div[data-testid="stForm"] {
            border: 1px solid #eee !important;
            border-radius: 10px !important;
            padding: 20px !important;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try: st.image("logo.png", use_container_width=True)
        except: st.write("### SWARCO")
