# =============================================================================
# ARCHIVO: main.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 2.0.0 (Modular & Universal)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Punto de entrada principal (Director de Orquesta). 
#              Gestiona la navegación, el idioma universal y la conexión central 
#              a Google Sheets.
# PROGRAMADOR: Gemini AI Thought Partner
# =============================================================================

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- IMPORTACIÓN DE MÓDULOS PROPIOS ---
import estilos
import usuarios
from idiomas import traducir_interfaz

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser la primera instrucción de Streamlit)
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
    # Buscamos el índice actual para que el selectbox no se resetee
    lista_nombres = list(opciones_idioma.keys())
    lista_codigos = list(opciones_idioma.values())
    indice_actual = lista_codigos.index(st.session_state.codigo_lang)
    
    seleccion = st.selectbox("Seleccione:", lista_nombres, index=indice_actual)
    st.session_state.codigo_lang = opciones_idioma[seleccion]
    
    st.markdown("---")
    st.caption("Swarco Traffic Spain\nPortal Modular v2.0")

# 4. CARGA DEL DICCIONARIO TRADUCIDO (El "Cerebro" de los textos)
t = traducir_interfaz(st.session_state.codigo_lang)

# 5. FUNCIÓN CENTRAL DE CONEXIÓN A DATOS
def conectar_gsheets():
    """Establece conexión con la base de datos en Google Sheets."""
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["connections"]["gsheets"]["service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

conn = conectar_gsheets()

# --- 6. RUTEADOR DE PÁGINAS (Navegación Lógica) ---
if not st.session_state.autenticado:
    # FLUJO: Login -> Registro
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t)
    else:
        usuarios.gestionar_acceso(conn, t)
else:
    # FLUJO: Menú Principal -> Secciones
    if st.session_state.pagina_actual == 'menu':
        import menu_principal
        menu_principal.mostrar_menu(conn, t)
    elif st.session_state.pagina_actual == 'sat':
        import tickets_sat
        tickets_sat.interfaz_tickets(conn, t)
    # Aquí se agregarán: 'repuestos' y 'equipos_nuevos'
