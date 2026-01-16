# ARCHIVO: main.py
# PROYECTO: TicketV0
# VERSIÓN: v1.5-INDESTRUCTIBLE (Recuperación Visual)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Carga la interfaz incluso si faltan librerías (Modo a prueba de fallos).

import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="Swarco Spain SAT",
    page_icon="🚦",
    layout="centered"
)

# --- 2. GESTIÓN DE IMPORTACIÓN SEGURA (EL ESCUDO 🛡️) ---
try:
    from streamlit_gsheets_connection import GSheetsConnection
    CONEXION_DISPONIBLE = True
except ImportError:
    CONEXION_DISPONIBLE = False
    # Definimos un valor nulo para que el código no rompa abajo
    GSheetsConnection = type(None) 

# --- IMPORTACIÓN DE MÓDULOS PROPIOS ---
import estilos
import usuarios
import tickets
from idiomas import traducir_interfaz

# --- 3. GESTIÓN DE ESTADO ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if 'codigo_lang' not in st.session_state:
    st.session_state.codigo_lang = 'es' 

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
        "Idioma del Portal / Portal Language",
        opciones_idioma,
        index=indice_actual,
        key="selector_idioma_key",
        on_change=actualizar_idioma_callback 
    )
    st.markdown("---")
    st.caption(f"Swarco Traffic Spain \nSAT Portal TicketV0")

    # AVISO DE ESTADO
    if CONEXION_DISPONIBLE:
        st.success("🟢 Online")
    else:
        st.warning("🟠 Modo Offline (Visual)")

# --- 6. CARGA TRADUCCIONES ---
t = traducir_interfaz(st.session_state.codigo_lang)

# --- 7. CONEXIÓN A GOOGLE SHEETS (PROTEGIDA) ---
conn = None
if CONEXION_DISPONIBLE:
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        CONEXION_DISPONIBLE = False

# --- 8. NAVEGACIÓN ---
estilos.cargar_estilos() 

if not st.session_state.autenticado:
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t)
    else:
        usuarios.gestionar_acceso(conn, t)
else:
    tickets.interfaz_tickets(conn, t)

