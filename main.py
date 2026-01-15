import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_javascript import st_javascript

# Importamos tus módulos (El ADN separado)
from idiomas import traducir_interfaz
import usuarios
import tickets

# --- 1. CONFIGURACIÓN ESTRUCTURAL ---
st.set_page_config(
    page_title="SWARCO SAT | Portal Global", 
    layout="centered", 
    page_icon="🚥"
)

# --- 2. CONEXIÓN MAESTRA ---
# La definimos aquí una sola vez y se la pasamos a quien la necesite
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. GESTIÓN DE SESIÓN (Memoria del ADN) ---
if 'autenticado' not in st.session_state: 
    st.session_state.autenticado = False
if 'mostrar_registro' not in st.session_state: 
    st.session_state.mostrar_registro = False
if 'codigo_lang' not in st.session_state:
    # Detección inteligente del navegador
    js_lang = st_javascript('window.navigator.language || window.navigator.userLanguage')
    st.session_state.codigo_lang = js_lang.split('-')[0] if js_lang else 'es'

# --- 4. SELECTOR DE IDIOMA UNIVERSAL ---
# Solo aparece en la portada para no estorbar la carga de tickets
if not st.session_state.autenticado:
    st.sidebar.markdown("### 🌐 Language / Idioma")
    idiomas_opciones = {
        "es": "Castellano / Spanish",
        "en": "English",
        "sk": "Slovenský (Slovak)",
        "he": "עברית (Hebrew)",
        "fr": "Français",
        "de": "Deutsch",
        "zh": "中文 (Chinese)"
    }
    
    # Buscamos el índice por defecto
    lista_codigos = list(idiomas_opciones.keys())
    try:
        idx_defecto = lista_codigos.index(st.session_state.codigo_lang)
    except:
        idx_defecto = 0

    seleccion = st.sidebar.selectbox(
        "🌍 Language:", 
        list(idiomas_opciones.values()), 
        index=idx_defecto
    )
    
    # Actualizamos el código según la selección manual
    for cod, nombre in idiomas_opciones.items():
        if nombre == seleccion:
            st.session_state.codigo_lang = cod

# --- 5. CARGA DE TRADUCCIONES ---
# 't' es el diccionario que usarán todos los módulos
t = traducir_interfaz(st.session_state.codigo_lang)

# --- 6. CONTROLADOR DE PANTALLAS (El Corazón del ADN) ---
if not st.session_state.autenticado:
    # PANTALLA DE ACCESO (Logo centrado)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: 
        st.image("logo.png", use_container_width=True)

    if st.session_state.mostrar_registro:
        # Llamamos al módulo de registro
        usuarios.interfaz_registro_legal(conn)
        # Botón para abortar registro
        if st.button("⬅️ " + ("Volver" if st.session_state.codigo_lang == "es" else "Back")):
            st.session_state.mostrar_registro = False
            st.rerun()
    else:
        # Título dinámico
        st.markdown(f"<h3 style='text-align: center;'>{t.get('login_tit', 'Acceso')}</h3>", unsafe_allow_html=True)
        
        # Llamamos al login pasando la conexión
        if usuarios.gestionar_acceso(conn):
            st.rerun()
        
        st.markdown("---")
        # Botón para saltar al registro
        if st.button(t.get("btn_ir_registro", "Registro"), use_container_width=True):
            st.session_state.mostrar_registro = True
            st.rerun()
else:
    # PANTALLA DE TRABAJO (Portal de Tickets)
    # Le pasamos 't' para que hable el idioma correcto
    tickets.interfaz_tickets(t)
