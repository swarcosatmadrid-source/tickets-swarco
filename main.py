# =============================================================================
# ARCHIVO: main.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 2.1.0 (Director de Orquesta Completo)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Punto de entrada principal. Gestiona el login, el idioma 
#              universal y la navegación hacia todas las sub-páginas.
# =============================================================================

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- IMPORTACIÓN DE MÓDULOS PROPIOS ---
import estilos
import usuarios
import idiomas
import menu_principal
import tickets_sat
import repuestos
import equipos_nuevos

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Swarco Portal SAT", 
    page_icon="🚦", 
    layout="centered"
)

# 2. CARGA DE ESTILOS CORPORATIVOS
estilos.cargar_estilos()

# 3. GESTIÓN DE ESTADOS (Navegación e Idioma)
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = 'login'
if 'codigo_lang' not in st.session_state:
    st.session_state.codigo_lang = 'es'

# --- SIDEBAR: CONTROL UNIVERSAL DE IDIOMA ---
with st.sidebar:
    st.markdown("### 🌍 Language / Idioma")
    opciones_idioma = {
        "Castellano (es)": "es", 
        "English (en)": "en", 
        "Deutsch (de)": "de", 
        "Français (fr)": "fr"
    }
    lista_nombres = list(opciones_idioma.keys())
    lista_codigos = list(opciones_idioma.values())
    
    # Intentamos mantener el índice actual
    try:
        idx = lista_codigos.index(st.session_state.codigo_lang)
    except:
        idx = 0
        
    seleccion = st.selectbox("Seleccione:", lista_nombres, index=idx)
    st.session_state.codigo_lang = opciones_idioma[seleccion]
    
    st.markdown("---")
    st.caption("Swarco Traffic Spain\nPortal Modular v2.1")

# 4. CARGA DEL DICCIONARIO TRADUCIDO
t = idiomas.traducir_interfaz(st.session_state.codigo_lang)

# 5. FUNCIÓN CENTRAL DE CONEXIÓN A DATOS
def conectar_gsheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["connections"]["gsheets"]["service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    except:
        return None

conn = conectar_gsheets()

# --- 6. RUTEADOR DE PÁGINAS (Navegación Lógica) ---
# Si no está autenticado, solo mostramos Login o Registro
if not st.session_state.autenticado:
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t)
    else:
        usuarios.gestionar_acceso(conn, t)

# Si ya entró, cargamos la página que indique 'pagina_actual'
else:
    if st.session_state.pagina_actual == 'menu':
        menu_principal.mostrar_menu(conn, t)
        
    elif st.session_state.pagina_actual == 'sat':
        tickets_sat.interfaz_tickets(conn, t)
        
    elif st.session_state.pagina_actual == 'repuestos':
        repuestos.mostrar_repuestos(t)
        
    elif st.session_state.pagina_actual == 'equipos_nuevos':
        equipos_nuevos.mostrar_equipos_nuevos(t)

