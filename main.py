# ARCHIVO: main.py
# PROYECTO: TicketV0
# VERSIÓN: v1.3-ONLINE (Producción)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Archivo principal. Gestiona la navegación, el selector de idioma rápido y la conexión a BD.

import streamlit as st
import pandas as pd
from streamlit_gsheets_connection import GSheetsConnection

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

# --- 3. CALLBACK IDIOMA (Fix Doble Clic) ---
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


