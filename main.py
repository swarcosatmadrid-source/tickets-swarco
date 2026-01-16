# ==========================================
# ARCHIVO: main.py | PROYECTO: TicketV1
# DESCRIPCIÓN: Punto de entrada principal.
# ==========================================
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

import estilos
import usuarios
import tickets
from idiomas import traducir_interfaz

st.set_page_config(page_title="Swarco Spain SAT", page_icon="🚦", layout="centered")

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

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'codigo_lang' not in st.session_state: st.session_state.codigo_lang = 'es' 

def actualizar_idioma_callback():
    seleccion = st.session_state.selector_idioma_key
    st.session_state.codigo_lang = seleccion.split('(')[-1].split(')')[0]

with st.sidebar:
    st.markdown("### Idioma / Language")
    opciones = ["Castellano (es)", "English (en)", "Deutsch (de)", "Français (fr)"]
    st.selectbox("Seleccione", opciones, key="selector_idioma_key", on_change=actualizar_idioma_callback)
    st.markdown("---")
    st.caption("Swarco Traffic Spain \nSAT Portal TicketV1")

t = traducir_interfaz(st.session_state.codigo_lang)
estilos.cargar_estilos() 

if not st.session_state.autenticado:
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t) 
    else:
        usuarios.gestionar_acceso(conn, t)
else:
    tickets.interfaz_tickets(conn, t)

