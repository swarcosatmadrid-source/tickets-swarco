# ==========================================
# ARCHIVO: main.py
# PROYECTO: TicketV1
# VERSIÓN: v1.1 (Modo Diagnóstico) 🛠️
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Código principal completo. Incluye sistema de
#              reporte de errores detallado para saber por qué falla la conexión.
# ==========================================

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- IMPORTACIÓN DE MÓDULOS PROPIOS ---
# Usamos try/except para saber si falta algún archivo local
try:
    import estilos
    import usuarios
    import tickets
    import idiomas
except ImportError as e:
    st.error(f"⚠️ Error crítico: Faltan archivos del sistema. {e}")
    st.stop()

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Swarco Spain SAT", page_icon="🚦", layout="centered")

# --- 2. CONEXIÓN ROBUSTA A GOOGLE (CON DIAGNÓSTICO) ---
def conectar_google_sheets():
    """
    Intenta conectar a Google Sheets.
    Si falla, MUESTRA EL ERROR REAL en pantalla para poder arreglarlo.
    """
    try:
        # A) Verificación de Secrets
        if "connections" not in st.secrets:
            st.error("❌ ERROR CRÍTICO: No se detectan los 'Secrets'. Debes pegarlos en el panel de Streamlit Cloud (Settings -> Secrets).")
            return None

        # B) Definimos permisos
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # C) Autenticación
        creds_dict = dict(st.secrets["connections"]["gsheets"]["service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # D) Abrir Excel
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet = client.open_by_url(url)
        return sheet
        
    except Exception as e:
        # AQUÍ ESTÁ LA CLAVE: Mostramos el mensaje técnico del error
        st.error(f"🔥 ERROR DE CONEXIÓN DETALLADO: {e}")
        st.info("💡 Pista: Si el error dice 'insufficient permissions', comparte el Excel con el email del robot.")
        return None

# Ejecutamos la conexión
conn = conectar_google_sheets()

# Indicador visual en la barra lateral
if conn:
    st.sidebar.success("🟢 Sistema Online")
else:
    st.sidebar.error("🔴 Offline (Ver error arriba)")

# --- 3. GESTIÓN DE IDIOMA ---
if 'codigo_lang' not in st.session_state:
    st.session_state.codigo_lang = 'es'

# Cargamos textos según idioma
t = idiomas.traducir_interfaz(st.session_state.codigo_lang)

# --- 4. CARGAR ESTILOS ---
estilos.cargar_estilos()

# --- 5. CONTROL DE FLUJO (Login vs App) ---
# Inicializamos estado de autenticación
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    # --- PANTALLA DE LOGIN ---
    # Pasamos la conexión 'conn' al módulo de usuarios
    usuarios.gestionar_acceso(conn, t)
else:
    # --- PANTALLA PRINCIPAL (Tickets) ---
    tickets.interfaz_tickets(conn, t)

