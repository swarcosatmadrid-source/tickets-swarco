import streamlit as st
from streamlit_gsheets import GSheetsConnection
from idiomas import traducir_interfaz
from streamlit_javascript import st_javascript
import usuarios
import tickets  # Importamos el nuevo módulo

# Configuración básica
st.set_page_config(page_title="SWARCO SAT", layout="centered", page_icon="🚥")
conn = st.connection("gsheets", type=GSheetsConnection)

# Estados de sesión
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'mostrar_registro' not in st.session_state: st.session_state.mostrar_registro = False
if 'codigo_lang' not in st.session_state:
    js_lang = st_javascript('window.navigator.language || window.navigator.userLanguage')
    st.session_state.codigo_lang = js_lang.split('-')[0] if js_lang else 'es'

# Diccionario de idiomas
t = traducir_interfaz(st.session_state.codigo_lang)

# --- FLUJO DE PANTALLAS ---

# 1. SI NO ESTÁ AUTENTICADO
if not st.session_state.autenticado:
    # Mostramos Logo centrado
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: st.image("logo.png", use_container_width=True)
    
    # Sidebar de idioma (Solo en la portada)
    st.sidebar.markdown("### 🌐 Language")
    idiomas_soporte = {"es": "Castellano", "en": "English", "sk": "Slovak", "he": "Hebrew"}
    sel = st.sidebar.selectbox("Seleccione:", list(idiomas_soporte.values()))
    for k, v in idiomas_soporte.items():
        if v == sel: st.session_state.codigo_lang = k

    if st.session_state.mostrar_registro:
        usuarios.interfaz_registro_legal(conn)
    else:
        if usuarios.gestionar_acceso(conn):
            st.rerun()
        st.markdown("---")
        if st.button(t.get("btn_ir_registro", "Registro"), use_container_width=True):
            st.session_state.mostrar_registro = True
            st.rerun()

# 2. SI ESTÁ AUTENTICADO (Cargamos el módulo de Tickets)
else:
    tickets.interfaz_tickets(t) # Llamamos a la función del nuevo archivo
