import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_javascript import st_javascript
import pycountry

# Importamos nuestros módulos machete
from idiomas import traducir_interfaz
import usuarios
import tickets

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SWARCO SAT", layout="centered", page_icon="🚥")

# --- 2. CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. INICIALIZACIÓN DE ESTADOS (Session State) ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'codigo_lang' not in st.session_state:
    # Detectamos el idioma del navegador como sugerencia inicial
    js_lang = st_javascript('window.navigator.language || window.navigator.userLanguage')
    st.session_state.codigo_lang = js_lang.split('-')[0] if js_lang else 'es'

# --- 4. BUSCADOR UNIVERSAL DE IDIOMAS (Eficiencia Pura) ---
st.sidebar.markdown("### 🌐 Configuración / Settings")

# Creamos la lista dinámica de todos los idiomas con código ISO 639-1 (2 letras)
idiomas_mundo = sorted([
    f"{i.name} ({i.alpha_2})" 
    for i in pycountry.languages 
    if hasattr(i, 'alpha_2')
])

# Buscamos la posición del idioma actual para que el selector no se mueva solo
try:
    # Intenta encontrar el que coincida con el código guardado (ej: 'es')
    idx_defecto = [i for i, x in enumerate(idiomas_mundo) if f"({st.session_state.codigo_lang})" in x][0]
except:
    # Si no lo encuentra (o es primera vez), ponemos 'Spanish (es)'
    idx_defecto = [i for i, x in enumerate(idiomas_mundo) if "(es)" in x][0]

idioma_seleccionado = st.sidebar.selectbox(
    "Seleccione Idioma / Select Language",
    idiomas_mundo,
    index=idx_defecto
)

# Extraemos el código ISO del paréntesis: "Russian (ru)" -> "ru"
st.session_state.codigo_lang = idioma_seleccionado.split('(')[-1].split(')')[0]

# --- 5. CARGA DE TRADUCCIONES ---
# 't' es el diccionario que usarán todos los demás archivos
t = traducir_interfaz(st.session_state.codigo_lang)

# --- 6. CONTROLADOR DE FLUJO (Login vs. App) ---
if not st.session_state.autenticado:
    # Si no está logueado, vamos a usuarios.py
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t)
    else:
        if usuarios.gestionar_acceso(conn, t):
            st.rerun()
else:
    # Si ya entró, vamos al portal de reportes
    tickets.interfaz_tickets(conn, t)

# Pie de página corporativo
st.sidebar.markdown("---")
st.sidebar.caption(f"Swarco SAT Portal v1.0 | Language: {st.session_state.codigo_lang.upper()}")
