# ARCHIVO: main.py
# VERSIÓN: v1.1 (Fix Doble Clic)
# FECHA: 15-Ene-2026
# DESCRIPCIÓN: Usa 'on_change' para cambiar el idioma instantáneamente sin lag.

import streamlit as st
import pandas as pd
from streamlit_gsheets_connection import GSheetsConnection

# Importamos nuestros módulos (El equipo completo)
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

# --- 2. GESTIÓN DE ESTADO (MEMORIA) ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if 'codigo_lang' not in st.session_state:
    st.session_state.codigo_lang = 'es' # Por defecto Español

# --- 3. CALLBACK PARA EL IDIOMA (La solución al Bug) ---
def actualizar_idioma_callback():
    """
    Se ejecuta INMEDIATAMENTE cuando el usuario cambia el selector.
    Actualiza la variable de sesión antes de recargar la página.
    """
    seleccion = st.session_state.selector_idioma_key
    # Extraemos el código: "English (en)" -> "en"
    nuevo_codigo = seleccion.split('(')[-1].split(')')[0]
    st.session_state.codigo_lang = nuevo_codigo

# --- 4. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    # Definimos las opciones
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
    
    # Buscamos en qué posición está el idioma actual para que el selectbox no se resetee
    # Si el código es 'en', buscamos cuál opción contiene '(en)'
    indice_actual = 0
    for i, op in enumerate(opciones_idioma):
        if f"({st.session_state.codigo_lang})" in op:
            indice_actual = i
            break
            
    st.selectbox(
        "Idioma del Portal / Portal Language",
        opciones_idioma,
        index=indice_actual,
        key="selector_idioma_key",  # Llave única
        on_change=actualizar_idioma_callback # <--- AQUÍ ESTÁ LA MAGIA
    )
    
    st.markdown("---")
    st.caption(f"Swarco Traffic Spain \nSAT Portal vTicketV0")

# --- 5. CARGA DE TRADUCCIONES ---
# Ahora 't' se cargará con el idioma correcto desde el primer milisegundo
t = traducir_interfaz(st.session_state.codigo_lang)

# --- 6. CONEXIÓN A GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("⚠️ Error: No se detectó la conexión a Google Sheets (.streamlit/secrets.toml)")
    st.stop()

# --- 7. NAVEGACIÓN PRINCIPAL ---
estilos.cargar_estilos() # Cargamos CSS Naranja

if not st.session_state.autenticado:
    # Si quiere registrarse
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t)
    else:
        # Si va a hacer login
        usuarios.gestionar_acceso(conn, t)
else:
    # Si ya entró
    tickets.interfaz_tickets(conn, t)
