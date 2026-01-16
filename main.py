# ARCHIVO: main.py
# PROYECTO: TicketV0
# VERSIÓN: v2.0-GSPREAD (Conexión Nativa)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Usa la librería 'gspread' directa. Más robusta y sin errores de instalación.

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- IMPORTACIÓN DE MÓDULOS ---
import estilos
import usuarios
import tickets
from idiomas import traducir_interfaz

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Swarco Spain SAT", page_icon="🚦", layout="centered")

# --- 2. CONEXIÓN NATIVA A GOOGLE (LA SOLUCIÓN) ---
def conectar_google_sheets():
    """Conecta a Google Sheets usando gspread directo"""
    try:
        # Definimos el alcance de los permisos
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Cargamos las credenciales desde los Secrets
        creds_dict = dict(st.secrets["connections"]["gsheets"]["service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # Abrimos la hoja de cálculo
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet = client.open_by_url(url)
        return sheet
    except Exception as e:
        return None

# Intentamos conectar
conn = conectar_google_sheets()
CONEXION_DISPONIBLE = True if conn else False

# --- 3. GESTIÓN DE ESTADO ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'codigo_lang' not in st.session_state: st.session_state.codigo_lang = 'es' 

# --- 4. CALLBACK IDIOMA ---
def actualizar_idioma_callback():
    seleccion = st.session_state.selector_idioma_key
    nuevo_codigo = seleccion.split('(')[-1].split(')')[0]
    st.session_state.codigo_lang = nuevo_codigo

# --- 5. BARRA LATERAL ---
with st.sidebar:
    opciones_idioma = [
        "Castellano (es)", "English (en)", "Deutsch (de)", 
        "Français (fr)", "Italiano (it)", "Português (pt)",
        "Hebrew (he)", "Chinese (zh)"
    ]
    indice_actual = 0
    for i, op in enumerate(opciones_idioma):
        if f"({st.session_state.codigo_lang})" in op:
            indice_actual = i
            break
            
    st.selectbox(
        "Idioma", opciones_idioma, index=indice_actual,
        key="selector_idioma_key", on_change=actualizar_idioma_callback 
    )
    st.markdown("---")
    st.caption(f"Swarco Traffic Spain \nSAT Portal TicketV0")

    if CONEXION_DISPONIBLE:
        st.success("🟢 Sistema Online")
    else:
        st.error("🔴 Error Conexión")

# --- 6. NAVEGACIÓN ---
t = traducir_interfaz(st.session_state.codigo_lang)
estilos.cargar_estilos() 

if not st.session_state.autenticado:
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t) # Pasamos el objeto 'sheet'
    else:
        usuarios.gestionar_acceso(conn, t)
else:
    tickets.interfaz_tickets(conn, t)

