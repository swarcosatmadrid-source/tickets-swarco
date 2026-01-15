import streamlit as st

def cargar_estilos():
    st.markdown("""
        <style>
        /* 1. ESTRUCTURA GLOBAL (Lo tuyo) */
        .block-container {
            padding-top: 2rem !important; 
            max-width: 850px !important;
        }
        
        /* 2. TEXTOS Y TÍTULOS (Nuevo: Para centrar el Login) */
        h1, h2, h3 {
            text-align: center;
            color: #00549F; /* Tu Azul Swarco */
            font-family: sans-serif;
            font-weight: 700;
        }
        h4, h5 {
            text-align: center;
            color: #666;
            font-weight: 400;
        }

        /* 3. CLASE ESPECIAL PARA TÍTULOS CON LÍNEA (Lo tuyo, mantenido) */
        .section-header {
            border-bottom: 3px solid #F29400; /* Tu Naranja Swarco */
            color: #00549F;
            font-weight: 700;
            font-size: 1.1rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
            text-transform: uppercase;
        }

        /* 4. BOTONES (Lo tuyo + Hover para efecto moderno) */
        div.stButton > button:first-child {
            background-color: #F29400 !important; /* Tu Naranja */
            color: white !important;
            border: none !important;
            border-radius: 6px !important; /* Un poco más redondeado queda mejor */
            font-weight: bold !important;
            padding: 0.6rem 2rem !important;
            width: 100%;
            transition: all 0.3s ease;
        }
        div.stButton > button:first-child:hover {
            background-color: #d68300 !important; /* Efecto al pasar el mouse */
            transform: scale(1.02);
        }

        /* 5. INPUTS MODERNOS (Nuevo: El toque "Sexy" que te gustó) */
        div[data-baseweb="input"] > div {
            border-radius: 6px;
            background-color: #f8f9fa; /* Fondo gris suave */
            border: 1px solid #e0e0e0;
        }
        
        /* 6. EXPANDERS (Nuevo: Para que el registro se vea limpio) */
        div[data-testid="stExpander"] {
            border: 1px solid #eee;
            border-radius: 8px;
            background-color: white;
        }

        /* 7. LIMPIEZA HEADER (Lo tuyo) */
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0);
        }
        </style>
    """, unsafe_allow_html=True)

# --- NUEVO: FUNCIÓN PARA EL LOGO CENTRADO ---
# Esto es vital para no repetir código en cada página
def mostrar_logo():
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.warning("⚠️ Falta logo.png")
