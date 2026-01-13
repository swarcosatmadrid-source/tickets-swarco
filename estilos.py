import streamlit as st

def cargar_estilos():
    st.markdown("""
        <style>
        /* Ajuste para que el encabezado no se corte */
        .block-container {
            padding-top: 3.5rem !important; 
            max-width: 850px !important;
        }
        
        /* Títulos de sección con línea naranja Swarco */
        .section-header {
            border-bottom: 3px solid #F29400;
            color: #00549F;
            font-weight: 700;
            font-size: 1.1rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
            text-transform: uppercase;
        }

        /* Botón principal en Naranja Swarco */
        div.stButton > button:first-child {
            background-color: #F29400 !important;
            color: white !important;
            border: none !important;
            border-radius: 2px !important;
            font-weight: bold !important;
            padding: 0.6rem 2rem !important;
            width: 100%;
        }

        /* Encabezado transparente */
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0);
        }
        </style>
    """, unsafe_allow_html=True)