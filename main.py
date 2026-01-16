# ==========================================
# ARCHIVO: main.py
# PROYECTO: TicketV0
# VERSIÓN: v1.4 (Pacto de Comparación)
# FECHA: 16-Ene-2026
# ==========================================
import streamlit as st
import pandas as pd
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
        sheet = client.open_by_url(url)
        return sheet
    except:
        return None

conn = conectar_google_sheets()

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'codigo_lang' not in st.session_state: st.session_state.codigo_lang = 'es' 

def actualizar_idioma_callback():
    seleccion = st.session_state.selector_idioma_key
    nuevo_codigo = seleccion.split('(')[-1].split(')')[0]
    st.session_state.codigo_lang = nuevo_codigo

with st.sidebar:
    st.markdown("### Idioma / Language")
    opciones_idioma = ["Castellano (es)", "English (en)", "Deutsch (de)", "Français (fr)", "Italiano (it)", "Português (pt)", "Hebrew (he)", "Chinese (zh)"]
    indice_actual = 0
    for i, op in enumerate(opciones_idioma):
        if f"({st.session_state.codigo_lang})" in op:
            indice_actual = i
            break
            
    st.selectbox("Seleccione", opciones_idioma, index=indice_actual, key="selector_idioma_key", on_change=actualizar_idioma_callback)
    st.markdown("---")
    st.caption(f"Swarco Traffic Spain \nSAT Portal TicketV0")
    # PACTO: Se eliminó el indicador visual de conexión aquí.

t = traducir_interfaz(st.session_state.codigo_lang)
estilos.cargar_estilos() 

if not st.session_state.autenticado:
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t) 
    else:
        usuarios.gestionar_acceso(conn, t)
else:
    tickets.interfaz_tickets(conn, t)
