import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_javascript import st_javascript

# Importamos el ADN de los otros archivos
from idiomas import traducir_interfaz
import usuarios
import tickets

# --- 1. CONFIGURACIÓN ESTRICTA ---
st.set_page_config(page_title="SWARCO SAT", layout="centered", page_icon="🚥")

# --- 2. CONEXIÓN MAESTRA A LA DB ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. INICIALIZACIÓN DE SESIÓN (Blindaje) ---
if 'autenticado' not in st.session_state: 
    st.session_state.autenticado = False
if 'codigo_lang' not in st.session_state:
    # Detectamos el idioma del navegador solo la primera vez
    js_lang = st_javascript('window.navigator.language || window.navigator.userLanguage')
    st.session_state.codigo_lang = js_lang.split('-')[0] if js_lang else 'es'

# --- 4. MAPEO Y SELECTOR DE IDIOMAS (El Blindaje que pediste) ---
MAPA_IDIOMAS = {
    "Castellano": "es", "English": "en", "Euskera": "eu", 
    "Hebreo": "he", "Slovenský": "sk", "Français": "fr"
}

st.sidebar.markdown("### 🌐 Configuración")
nombres_idiomas = list(MAPA_IDIOMAS.keys())

# Aseguramos que el selector sepa en qué idioma estamos
try:
    idx_actual = nombres_idiomas.index([k for k, v in MAPA_IDIOMAS.items() if v == st.session_state.codigo_lang][0])
except:
    idx_actual = 0

seleccion = st.sidebar.selectbox("Idioma / Language", nombres_idiomas, index=idx_actual)
st.session_state.codigo_lang = MAPA_IDIOMAS[seleccion]

# --- 5. CARGA DEL DICCIONARIO 't' ---
t = traducir_interfaz(st.session_state.codigo_lang)

# --- 6. CONTROLADOR DE FLUJO (ADN Modular) ---
if not st.session_state.autenticado:
    # Si no está logueado, vamos a usuarios.py
    # El logo y la lógica de login/registro viven allá
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t)
    else:
        if usuarios.gestionar_acceso(conn, t):
            st.rerun()
else:
    # Si está logueado, vamos a tickets.py
    tickets.interfaz_tickets(conn, t)
