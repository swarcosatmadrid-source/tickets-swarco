import streamlit as st

def aplicar_estilos_swarco():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
        .stApp { background-color: #ffffff; }
        .block-container { padding-top: 1rem; max-width: 850px; }
        
        .section-header {
            color: #00549F;
            font-size: 20px;
            font-weight: 700;
            text-align: center;
            margin-top: 30px;
            margin-bottom: 10px;
            text-transform: uppercase;
            border-bottom: 2px solid #009FE3;
            padding-bottom: 5px;
        }

        /* Contenedores de botones personalizados */
        .btn-generar > button {
            background-color: #00549F !important;
            color: white !important;
            border-radius: 4px !important;
            height: 50px !important;
            width: 100% !important;
        }
        .btn-cerrar > button {
            background-color: #D32F2F !important;
            color: white !important;
            border-radius: 4px !important;
            height: 50px !important;
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)