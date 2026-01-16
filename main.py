# ==========================================
# ARCHIVO: main.py
# PROYECTO: TicketV1
# VERSIÓN: v1.3 (Debug Avanzado + Fix) 🛠️
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Mantiene TODA la lógica original.
#              Mejora el reporte de error para que no salga en blanco.
# ==========================================

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- IMPORTACIÓN DE MÓDULOS ---
try:
    import estilos
    import usuarios
    import tickets
    from idiomas import traducir_interfaz
except ImportError as e:
    st.error(f"⚠️ Faltan archivos: {e}")
    st.stop()

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Swarco Spain SAT", page_icon="🚦", layout="centered")

# --- 2. CONEXIÓN NATIVA A GOOGLE (CON DIAGNÓSTICO PROFUNDO) ---
def conectar_google_sheets():
    """Conecta a Google Sheets y avisa si falla."""
    try:
        # Definimos el alcance
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Verificamos si existen los secrets
        if "connections" not in st.secrets:
            st.error("❌ ERROR CRÍTICO: 'connections' no está en st.secrets.")
            return None

        # Intento de lectura de credenciales con chivatos
        try:
            creds_dict = dict(st.secrets["connections"]["gsheets"]["service_account"])
        except KeyError as k:
            st.error(f"❌ ERROR EN SECRETS: Falta la clave {k}. Revisa el formato TOML.")
            return None

        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # Abrimos la hoja
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet = client.open_by_url(url)
        return sheet

    except Exception as e:
        # AQUÍ ESTÁ EL CAMBIO: Imprimimos el TIPO de error también
        st.error(f"🔥 ERROR TÉCNICO ({type(e).__name__}): {e}")
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
    st.caption(f"Swarco Traffic Spain \nSAT Portal TicketV1")

    if CONEXION_DISPONIBLE:
        st.success("🟢 Sistema Online")
    else:
        st.error("🔴 Error Conexión")

# --- 6. NAVEGACIÓN ---
t = traducir_interfaz(st.session_state.codigo_lang)
estilos.cargar_estilos() 

if not st.session_state.autenticado:
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t) 
    else:
        usuarios.gestionar_acceso(conn, t)
else:
    tickets.interfaz_tickets(conn, t)
