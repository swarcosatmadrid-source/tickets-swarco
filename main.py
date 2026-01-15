import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_javascript import st_javascript
import pycountry

# Importamos los módulos del ADN Swarco
from idiomas import traducir_interfaz
import usuarios
import tickets

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SWARCO SAT", layout="centered", page_icon="🚥")

# --- 2. CONEXIÓN A DATABASE (Google Sheets) ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. INICIALIZACIÓN DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'codigo_lang' not in st.session_state:
    # Intento de detección automática del navegador
    js_lang = st_javascript('window.navigator.language || window.navigator.userLanguage')
    st.session_state.codigo_lang = js_lang.split('-')[0] if js_lang else 'es'

# --- 4. BUSCADOR UNIVERSAL DE IDIOMAS CON NOMBRES CORREGIDOS ---
st.sidebar.markdown("### 🌐 Configuración / Settings")

# Diccionario de corrección: Inglés ISO -> Nombre Nativo/Preferido
nombres_pro = {
    "Spanish": "Castellano",
    "Basque": "Euskera",
    "Russian": "Pусский",
    "Slovak": "Slovenský",
    "French": "Français",
    "German": "Deutsch",
    "Hebrew": "Hebreo",
    "Italian": "Italiano",
    "Chinese": "Chino"
}

# Generamos la lista de idiomas del mundo (ISO 639-1)
idiomas_mundo = []
for i in pycountry.languages:
    if hasattr(i, 'alpha_2'):
        nombre_iso = i.name
        # Aplicamos el filtro de nombres bonitos
        nombre_final = nombres_pro.get(nombre_iso, nombre_iso)
        idiomas_mundo.append(f"{nombre_final} ({i.alpha_2})")

idiomas_mundo = sorted(idiomas_mundo)

# Buscamos el índice del idioma actual para que no se resetee el selector
try:
    # Buscamos el que coincida con el código de sesión (ej: 'es')
    idx_defecto = [idx for idx, texto in enumerate(idiomas_mundo) if f"({st.session_state.codigo_lang})" in texto][0]
except:
    # Si no existe, buscamos Castellano por defecto
    try:
        idx_defecto = [idx for idx, texto in enumerate(idiomas_mundo) if "(es)" in texto][0]
    except:
        idx_defecto = 0

idioma_seleccionado = st.sidebar.selectbox(
    "Idioma del Portal / Portal Language",
    idiomas_mundo,
    index=idx_defecto
)

# Extraemos el código ISO: "Castellano (es)" -> "es"
st.session_state.codigo_lang = idioma_seleccionado.split('(')[-1].split(')')[0]

# --- 5. CARGA DEL DICCIONARIO DE TRADUCCIÓN 't' ---
t = traducir_interfaz(st.session_state.codigo_lang)

# --- 6. CONTROLADOR DE FLUJO ---
if not st.session_state.autenticado:
    # Pantalla de Acceso o Registro
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t)
    else:
        if usuarios.gestionar_acceso(conn, t):
            st.rerun()
else:
    # Portal de Tickets (Técnico Logueado)
    tickets.interfaz_tickets(conn, t)

# Pie de página lateral
st.sidebar.markdown("---")
st.sidebar.caption(f"Swarco SAT v1.0 | ISO: {st.session_state.codigo_lang.upper()}")
