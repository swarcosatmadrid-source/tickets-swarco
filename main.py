import streamlit as st
from streamlit_gsheets import GSheetsConnection
from idiomas import traducir_interfaz
import usuarios
from streamlit_javascript import st_javascript

st.set_page_config(page_title="SWARCO SAT", layout="centered", page_icon="🚥")

# 1. Detección automática del CÓDIGO de idioma (ej: 'es', 'en', 'sk')
if 'codigo_lang' not in st.session_state:
    js_lang = st_javascript('window.navigator.language || window.navigator.userLanguage')
    if js_lang:
        st.session_state.codigo_lang = js_lang.split('-')[0] # 'es', 'en', 'sk'...
    else:
        st.session_state.codigo_lang = 'es'

# 2. Mapeo para el selector visual
idiomas_mapper = {
    "es": "Castellano / Spanish",
    "en": "English",
    "sk": "Slovenský",
    "he": "עברית (Hebrew)",
    "fr": "Français",
    "de": "Deutsch"
}

# 3. Sidebar: El usuario ve el nombre, nosotros guardamos el código
if not st.session_state.get('autenticado', False):
    st.sidebar.markdown("### 🌐 Language / Idioma")
    
    # Invertimos el mapeo para el selector
    opciones = list(idiomas_mapper.values())
    default_index = list(idiomas_mapper.keys()).index(st.session_state.codigo_lang) if st.session_state.codigo_lang in idiomas_mapper else 1
    
    seleccion = st.sidebar.selectbox("Seleccione:", opciones, index=default_index)
    
    # Actualizamos el código de idioma según la selección
    for cod, nombre in idiomas_mapper.items():
        if nombre == seleccion:
            st.session_state.codigo_lang = cod

# 4. Traducir usando el código
t = traducir_interfaz(st.session_state.codigo_lang)

# 5. Interfaz de Acceso
if not st.session_state.get('autenticado', False):
    # Centrar Logo
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: st.image("logo.png", use_container_width=True)

    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn)
        if st.button("⬅️"):
            st.session_state.mostrar_registro = False
            st.rerun()
    else:
        st.markdown(f"<h2 style='text-align: center;'>{t.get('login_tit')}</h2>", unsafe_allow_html=True)
        if usuarios.gestionar_acceso(conn):
            st.rerun()
        
        st.markdown("---")
        if st.button(t.get("btn_ir_registro"), use_container_width=True):
            st.session_state.mostrar_registro = True
            st.rerun()
    st.stop()
