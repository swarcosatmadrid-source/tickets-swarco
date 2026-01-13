import streamlit as st

def cargar_estilos():
    st.markdown("""
        <style>
        /* 1. BAJAMOS EL CONTENIDO PARA QUE EL LOGO NO SE CORTE */
        .block-container {
            padding-top: 3.5rem !important; 
            max-width: 850px !important;
        }
        
        /* 2. TÍTULOS CON EL NARANJA SWARCO (#F29400) */
        .section-header {
            border-bottom: 3px solid #F29400; /* La línea naranja de su web */
            color: #00549F;
            font-weight: 700;
            font-size: 1.1rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
            text-transform: uppercase;
        }

        /* 3. BOTÓN PRINCIPAL NARANJA (Igual a los de swarco.com) */
        div.stButton > button:first-child {
            background-color: #F29400 !important;
            color: white !important;
            border: none !important;
            border-radius: 2px !important; /* Bordes más rectos, más serios */
            font-weight: bold !important;
            padding: 0.6rem 2rem !important;
        }

        /* 4. AJUSTE DEL LOGO Y HEADER */
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0); /* Hace la barra de arriba transparente */
        }
        </style>
    """, unsafe_allow_html=True)