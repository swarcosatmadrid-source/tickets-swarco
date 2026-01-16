# ARCHIVO: main.py
# PROYECTO: TicketV0
# VERSIÓN: v1.4-FORCE (Con Autoinstalación)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Incluye un bloque de 'Autoreparación' para instalar librerías faltantes.

import streamlit as st
import pandas as pd
import subprocess
import sys

# --- 0. BLOQUE DE AUTO-REPARACIÓN (EL PARCHE) ---
# Si el servidor dice que no tiene la librería, la instalamos aquí mismo.
try:
    from streamlit_gsheets_connection import GSheetsConnection
except ImportError:
    st.warning("⚠️ Librería faltante detectada. Intentando instalación automática...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "st-gsheets-connection"])
        from streamlit_gsheets_connection import GSheetsConnection
        st.success("✅ Librería instalada. Recargando...")
        st.rerun()
    except Exception as e:
        st.error(f"❌ No se pudo instalar la librería automáticamente: {e}")
        st.stop()

# --- IMPORTACIÓN DE MÓDULOS ---
import estilos
import usuarios
import tickets
from idiomas import traducir_interfaz

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="Swarco Spain SAT",
    page_icon="🚦",
    layout="centered"
)

# --- 2. GESTIÓN DE ESTADO ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if 'codigo_lang' not in st.session_state:
    st.session_state.codigo_lang = 'es' 

# --- 3. CALLBACK IDIOMA ---
def actualizar_idioma_callback():
    seleccion = st.session_state.selector_idioma_key
    nuevo_codigo = seleccion.split('(')[-1].split(')')[0]
    st.session_state.codigo_lang = nuevo_codigo

# --- 4. BARRA LATERAL ---
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
        "Idioma del Portal / Portal Language",
        opciones_idioma,
        index=indice_actual,
        key="selector_idioma_key",
        on_change=actualizar_idioma_callback 
    )
    st.markdown("---")
    st.caption(f"Swarco Traffic Spain \nSAT Portal TicketV0")

# --- 5. CARGA TRADUCCIONES ---
t = traducir_interfaz(st.session_state.codigo_lang)

# --- 6. CONEXIÓN A GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"⚠️ Error Crítico de Conexión: {e}")
    st.info("Verifique sus Secrets o la conexión a internet.")
    st.stop()

# --- 7. NAVEGACIÓN ---
estilos.cargar_estilos() 

if not st.session_state.autenticado:
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t)
    else:
        usuarios.gestionar_acceso(conn, t)
else:
    tickets.interfaz_tickets(conn, t)
