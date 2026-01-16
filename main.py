# ==========================================
# ARCHIVO: main.py
# PROYECTO: TicketV1
# VERSIÓN: v1.4 (Final Connection Check)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Mantiene selector de idiomas y lógica de v1.2/1.3.
#              Preparado para recibir la conexión una vez habilitadas las APIs.
# ==========================================

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

try:
    import estilos
    import usuarios
    import tickets
    from idiomas import traducir_interfaz
except ImportError as e:
    st.error(f"Faltan archivos: {e}")
    st.stop()

st.set_page_config(page_title="Swarco Spain SAT", page_icon="🚦", layout="centered")

def conectar_google_sheets():
    try:
        if "connections" not in st.secrets:
            st.error("Configuración 'Secrets' no encontrada.")
            return None

        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["connections"]["gsheets"]["service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet = client.open_by_url(url)
        return sheet
    except Exception as e:
        # v1.4: Reporte simplificado si persiste el error de API
        st.error(f"🔥 Error de Acceso: {e}")
        return None

conn = conectar_google_sheets()
CONEXION_DISPONIBLE = True if conn else False

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'codigo_lang' not in st.session_state: st.session_state.codigo_lang = 'es' 

def actualizar_idioma_callback():
    seleccion = st.session_state.selector_idioma_key
    st.session_state.codigo_lang = seleccion.split('(')[-1].split(')')[0]

with st.sidebar:
    opciones = ["Castellano (es)", "English (en)", "Deutsch (de)", "Français (fr)", "Italiano (it)", "Português (pt)", "Hebrew (he)", "Chinese (zh)"]
    idx = next((i for i, op in enumerate(opciones) if f"({st.session_state.codigo_lang})" in op), 0)
    st.selectbox("Idioma", opciones, index=idx, key="selector_idioma_key", on_change=actualizar_idioma_callback)
    st.markdown("---")
    if CONEXION_DISPONIBLE: st.success("🟢 Sistema Online")
    else: st.error("🔴 Error Conexión")

t = traducir_interfaz(st.session_state.codigo_lang)
estilos.cargar_estilos() 

if not st.session_state.autenticado:
    if st.session_state.get('mostrar_registro', False): usuarios.interfaz_registro_legal(conn, t) 
    else: usuarios.gestionar_acceso(conn, t)
else:
    tickets.interfaz_tickets(conn, t)
