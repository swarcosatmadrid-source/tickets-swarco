# ==========================================
# ARCHIVO: main.py
# PROYECTO: TicketV0
# VERSIÓN: v1.0 (Original Hoy 16-Ene)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Punto de entrada principal. Gestiona la conexión 
#              a Google Sheets y la navegación por módulos.
# ==========================================

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Importación de módulos locales
import estilos
import usuarios
import tickets
from idiomas import traducir_interfaz

# 1. Configuración de página
st.set_page_config(page_title="Swarco Spain SAT", page_icon="🚦", layout="centered")

# 2. Conexión a Google Sheets
def conectar_google_sheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["connections"]["gsheets"]["service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        return client.open_by_url(url)
    except:
        return None

conn = conectar_google_sheets()

# 3. Estado del idioma
if 'codigo_lang' not in st.session_state:
    st.session_state.codigo_lang = 'es'

def actualizar_idioma_callback():
    seleccion = st.session_state.selector_idioma_key
    st.session_state.codigo_lang = seleccion.split('(')[-1].split(')')[0]

# 4. Sidebar (Barra Lateral)
with st.sidebar:
    st.markdown("### Seleccione Idioma")
    opciones = ["Castellano (es)", "English (en)", "Deutsch (de)", "Français (fr)"]
    st.selectbox("Idioma", opciones, key="selector_idioma_key", on_change=actualizar_idioma_callback)
    st.markdown("---")
    st.caption("Swarco Traffic Spain \nSAT Portal TicketV0")
    if conn:
        st.success("🟢 Sistema Online")
    else:
        st.error("🔴 Error Conexión")

# 5. Carga de Estilos y Traducción
t = traducir_interfaz(st.session_state.codigo_lang)
estilos.cargar_estilos()

# 6. Lógica de Navegación
if not st.session_state.get('autenticado', False):
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t)
    else:
        usuarios.gestionar_acceso(conn, t)
else:
    tickets.interfaz_tickets(conn, t)

