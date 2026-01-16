import streamlit as st

def cargar_estilos():
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
            border-radius: 5px;
            border: none;
            font-weight: bold;
            height: 45px;
        }
        div[data-testid="stForm"] .stTextInput input[aria-invalid="true"] {
            border: 2px solid #FF0000 !important;
            background-color: #FFF5F5 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        try:
            # RUTA EXACTA GITHUB
            st.image("logo/logo.png", use_container_width=True)
        except:
            st.markdown("<h2 style='text-align:center; color:#FF5D00'>SWARCO</h2>", unsafe_allow_html=True)

