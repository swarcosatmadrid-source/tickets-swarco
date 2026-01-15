import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from idiomas import traducir_interfaz
import usuarios
from streamlit_javascript import st_javascript # Necesitas instalar esta librería

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="SWARCO SAT | Portal", layout="centered", page_icon="🚥")

# --- 2. DETECCIÓN AUTOMÁTICA DEL IDIOMA DEL NAVEGADOR ---
if 'idioma' not in st.session_state:
    # Este pequeño código JS le pregunta al navegador su idioma (ej: 'es-ES', 'en-US', 'sk')
    lang_navegador = st_javascript('window.navigator.language || window.navigator.userLanguage')
    
    if lang_navegador:
        codigo = lang_navegador.split('-')[0] # Nos quedamos con 'es', 'en', 'sk', etc.
        
        # Mapeo rápido de códigos a nombres que entiende tu idiomas.py
        mapeo_inicial = {
            'es': 'Castellano',
            'en': 'English',
            'sk': 'Slovak',
            'he': 'Hebrew',
            'fr': 'French',
            'de': 'German'
        }
        st.session_state.idioma = mapeo_inicial.get(codigo, 'English') # Por defecto English si no lo conocemos
    else:
        st.session_state.idioma = 'Castellano' # Backup por si falla el JS

# Resto de estados
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'mostrar_registro' not in st.session_state: st.session_state.mostrar_registro = False

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. SELECTOR MANUAL (Por si quiere cambiar el que vino por defecto) ---
if not st.session_state.autenticado:
    st.sidebar.markdown("### 🌐 Language / Idioma")
    # Lista extendida para que Google Translate sepa qué buscar
    idiomas_del_mundo = ["Castellano", "English", "Slovak", "Hebrew", "French", "German", "Chinese", "Arabic"]
    
    # El selector se posiciona automáticamente en el idioma detectado
    idx_auto = idiomas_del_mundo.index(st.session_state.idioma) if st.session_state.idioma in idiomas_del_mundo else 1
    
    st.session_state.idioma = st.sidebar.selectbox(
        "🌏 Change Language / Cambiar Idioma:", 
        idiomas_del_mundo, 
        index=idx_auto
    )

# --- 4. TRADUCCIÓN ---
t = traducir_interfaz(st.session_state.idioma)

# --- 5. LÓGICA DE ACCESO (Logo centrado y navegación) ---
if not st.session_state.autenticado:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: st.image("logo.png", use_container_width=True)

    if st.session_state.mostrar_registro:
        usuarios.interfaz_registro_legal(conn)
        if st.button("⬅️ " + ("Volver" if st.session_state.idioma == "Castellano" else "Back")):
            st.session_state.mostrar_registro = False
            st.rerun()
    else:
        st.markdown(f"<h2 style='text-align: center;'>{t.get('login_tit', 'Acceso')}</h2>", unsafe_allow_html=True)
        if usuarios.gestionar_acceso(conn):
            st.rerun()
        
        st.markdown("---")
        if st.button(t.get("btn_ir_registro", "Registro"), use_container_width=True):
            st.session_state.mostrar_registro = True
            st.rerun()
    st.stop()

# --- 6. INTERFAZ TICKET (Ya autenticado) ---
# (Aquí sigue el resto de tu código de tickets...)
