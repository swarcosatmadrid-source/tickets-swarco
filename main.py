# ARCHIVO: main.py
# PROYECTO: TicketV0
# VERSIÓN: v1.3-ONLINE (Producción)
# FECHA: 15-Ene-2026
# DESCRIPCIÓN: Archivo principal. Gestiona la navegación, el idioma y la conexión a BD.

import streamlit as st
import pandas as pd
from streamlit_gsheets_connection import GSheetsConnection

# --- IMPORTACIÓN DE MÓDULOS DEL SISTEMA ---
import estilos
import usuarios
import tickets
from idiomas import traducir_interfaz

# --- 1. CONFIGURACIÓN INICIAL DE LA PÁGINA ---
st.set_page_config(
    page_title="Swarco Spain SAT",
    page_icon="🚦",
    layout="centered"
)

# --- 2. GESTIÓN DE ESTADO (MEMORIA DE SESIÓN) ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if 'codigo_lang' not in st.session_state:
    st.session_state.codigo_lang = 'es' # Por defecto Español

# --- 3. CALLBACK PARA CAMBIO DE IDIOMA INSTANTÁNEO ---
def actualizar_idioma_callback():
    """
    Se ejecuta inmediatamente al cambiar el selector, actualizando
    la variable de estado antes de recargar la página.
    """
    seleccion = st.session_state.selector_idioma_key
    # Extraemos el código: "English (en)" -> "en"
    nuevo_codigo = seleccion.split('(')[-1].split(')')[0]
    st.session_state.codigo_lang = nuevo_codigo

# --- 4. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    opciones_idioma = [
        "Castellano (es)", 
        "English (en)", 
        "Deutsch (de)", 
        "Français (fr)", 
        "Italiano (it)", 
        "Português (pt)",
        "Hebrew (he)", 
        "Chinese (zh)"
    ]
    
    # Sincronizamos el selector con el estado actual
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
        on_change=actualizar_idioma_callback # <--- ESTO EVITA EL DOBLE CLIC
    )
    
    st.markdown("---")
    st.caption(f"Swarco Traffic Spain \nSAT Portal TicketV0")

# --- 5. CARGA DE TRADUCCIONES ---
# Cargamos el diccionario 't' según el idioma seleccionado
t = traducir_interfaz(st.session_state.codigo_lang)

# --- 6. CONEXIÓN A GOOGLE SHEETS (ACTIVADA) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    # Si falla la conexión (ej: faltan Secrets), mostramos error y paramos
    st.error(f"⚠️ Error Crítico de Conexión: {e}")
    st.info("Por favor, verifique el archivo .streamlit/secrets.toml en la configuración de la App.")
    st.stop()

# --- 7. NAVEGACIÓN Y LÓGICA PRINCIPAL ---
estilos.cargar_estilos() # Cargamos el tema Naranja Swarco

if not st.session_state.autenticado:
    # MODO: NO LOGUEADO
    if st.session_state.get('mostrar_registro', False):
        # Pantalla de Registro (Ahora con Manualito y Pasos Ordenados)
        usuarios.interfaz_registro_legal(conn, t)
    else:
        # Pantalla de Login
        usuarios.gestionar_acceso(conn, t)
else:
    # MODO: LOGUEADO
    # Pantalla Principal de Tickets
    tickets.interfaz_tickets(conn, t)

